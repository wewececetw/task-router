"""
oMLX MCP Server — 讓 Claude Code/Desktop 把簡單任務丟給本地模型

Features:
  - Auto-compact: 內容快超過 context window 時自動壓縮再送
  - Connection pool: 持久化 HTTP 連線
  - Fallback hint: 太大的任務回報讓 Claude 自己處理

安裝（Claude Code 全域）:
  claude mcp add omlx-local -s user \
    -e OMLX_API_KEY="your-key" \
    -e OMLX_BASE_URL="http://127.0.0.1:9000/v1" \
    -- uv run --directory /path/to/task-router python mcp_omlx.py
"""

from __future__ import annotations

import os
import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OMLX_BASE = os.environ.get("OMLX_BASE_URL", "http://127.0.0.1:9000/v1")
OMLX_KEY = os.environ.get("OMLX_API_KEY", "")
OMLX_MODEL = os.environ.get("OMLX_MODEL", "Qwen3.5-9B-MLX-4bit")

# Context window config (tokens)
CONTEXT_WINDOW = int(os.environ.get("OMLX_CONTEXT_WINDOW", "32768"))
COMPACT_THRESHOLD = 0.70  # 70% 時觸發 compact
REJECT_THRESHOLD = 0.90   # 90% 直接拒絕

mcp = FastMCP("oMLX Local LLM")

# ---------------------------------------------------------------------------
# Persistent HTTP client
# ---------------------------------------------------------------------------

_headers = {"Content-Type": "application/json"}
if OMLX_KEY:
    _headers["Authorization"] = f"Bearer {OMLX_KEY}"

_client = httpx.AsyncClient(
    base_url=OMLX_BASE,
    headers=_headers,
    timeout=120.0,
    limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
)


# ---------------------------------------------------------------------------
# Token estimation & auto-compact
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """粗估 token 數：中文 ~1.5 char/token，英文 ~4 char/token，取混合平均。"""
    cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - cn_chars
    return int(cn_chars / 1.5 + other_chars / 4)


async def _compact(text: str, target_tokens: int) -> str:
    """用本地模型壓縮內容到目標 token 數。"""
    ratio = target_tokens / max(_estimate_tokens(text), 1)
    target_chars = int(len(text) * ratio)

    resp = await _client.post(
        "/chat/completions",
        json={
            "model": OMLX_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一個文件壓縮器。保留所有技術細節、API 名稱、檔案路徑、資料結構。刪除冗餘描述和重複內容。輸出必須是結構化的重點摘要。",
                },
                {
                    "role": "user",
                    "content": f"將以下內容壓縮到約 {target_chars} 字以內，保留所有關鍵技術資訊：\n\n{text}",
                },
            ],
            "max_tokens": target_tokens,
            "temperature": 0.3,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


async def _prepare_prompt(prompt: str, system: str, max_tokens: int) -> tuple[str, str, str]:
    """檢查 token 用量，必要時自動 compact。回傳 (prompt, system, status_note)。"""
    total_input = _estimate_tokens(prompt) + _estimate_tokens(system)
    total_needed = total_input + max_tokens  # input + output 預留
    limit = CONTEXT_WINDOW

    # 安全範圍內
    if total_needed < limit * COMPACT_THRESHOLD:
        return prompt, system, ""

    # 太大，直接拒絕
    if total_needed > limit * REJECT_THRESHOLD:
        return prompt, system, (
            f"⚠️ INPUT TOO LARGE: ~{total_input} tokens input + {max_tokens} output "
            f"= ~{total_needed} tokens, exceeds {int(limit * REJECT_THRESHOLD)} limit. "
            f"建議由 Claude 直接處理此任務。"
        )

    # 需要 compact
    target = int(limit * 0.5) - max_tokens  # compact 到 50% window，留空間給 output
    if target < 500:
        return prompt, system, "⚠️ 壓縮後空間不足，建議由 Claude 直接處理。"

    compacted = await _compact(prompt, target)
    note = (
        f"🗜️ Auto-compacted: {total_input} → ~{_estimate_tokens(compacted)} tokens "
        f"({total_input - _estimate_tokens(compacted)} tokens saved)"
    )
    return compacted, system, note


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def local_llm(
    prompt: str,
    system: str = "",
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """用本地 oMLX 模型回答問題或執行任務。

    適合的任務:
    - 翻譯短文
    - 生成 boilerplate 程式碼
    - 建立簡單的 model/schema
    - 拆解任務列表
    - 格式轉換(JSON ↔ YAML)
    - 寫文件、註解
    - 簡單問答

    不適合的任務（請 Claude 自己處理）:
    - 架構設計
    - 安全相關程式碼
    - 複雜除錯
    - 程式碼審查

    Args:
        prompt: 要送給本地模型的提示詞
        system: 系統提示詞（可選）
        max_tokens: 最大回覆 token 數
        temperature: 溫度參數
    """
    # Auto-compact check
    prompt, system, note = await _prepare_prompt(prompt, system, max_tokens)

    # If rejected (too large), return the warning
    if note and note.startswith("⚠️"):
        return note

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = await _client.post(
        "/chat/completions",
        json={
            "model": OMLX_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    model = data.get("model", OMLX_MODEL)
    prefix = f"🗜️ {note}\n\n" if note else ""
    return f"{prefix}[oMLX | {model}]\n\n{content}"


@mcp.tool()
async def local_llm_batch(
    prompts: list[str],
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """批量送多個 prompt 給本地模型,適合 Spec Kit tasks 階段一次處理多個小任務。

    Args:
        prompts: 多個 prompt 的列表
        system: 共用的系統提示詞（可選）
        max_tokens: 每個 prompt 的最大回覆 token 數
    """
    results = []
    for i, prompt in enumerate(prompts):
        result = await local_llm(prompt, system=system, max_tokens=max_tokens)
        results.append(f"### Task {i + 1}\n{result}")
    return "\n\n---\n\n".join(results)


@mcp.tool()
async def local_llm_status() -> str:
    """檢查 oMLX 本地模型伺服器狀態。"""
    try:
        resp = await _client.get("/models")
        resp.raise_for_status()
        data = resp.json()

        models = [m["id"] for m in data.get("data", [])]
        return (
            f"oMLX 運作中 ✅\n"
            f"伺服器: {OMLX_BASE}\n"
            f"可用模型: {', '.join(models)}\n"
            f"Context window: {CONTEXT_WINDOW} tokens\n"
            f"Auto-compact: {int(COMPACT_THRESHOLD*100)}% | Reject: {int(REJECT_THRESHOLD*100)}%"
        )
    except Exception as e:
        return f"oMLX 無法連線 ❌\n伺服器: {OMLX_BASE}\n錯誤: {e}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
