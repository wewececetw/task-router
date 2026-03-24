"""
oMLX MCP Server — 讓 Claude Code 把簡單任務丟給本地模型

在 Claude Code 裡註冊這個 MCP server 後，Claude 就多了一個 tool：
  - local_llm: 把 prompt 送到 oMLX 本地模型處理

搭配 Spec Kit 使用時，在 command prompt 裡指示 Claude：
  「這個任務請用 local_llm tool 完成」

安裝：
  claude mcp add omlx-local -- uv run --directory /Users/barronwang/C/task-router python mcp_omlx.py
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

mcp = FastMCP("oMLX Local LLM")


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

    適合的任務：
    - 翻譯短文
    - 生成 boilerplate 程式碼
    - 建立簡單的 model/schema
    - 拆解任務列表
    - 格式轉換（JSON ↔ YAML）
    - 寫文件、註解
    - 簡單問答

    不適合的任務（請 Claude 自己處理）：
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
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    headers = {"Content-Type": "application/json"}
    if OMLX_KEY:
        headers["Authorization"] = f"Bearer {OMLX_KEY}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{OMLX_BASE}/chat/completions",
            headers=headers,
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
    return f"[oMLX | {model}]\n\n{content}"


@mcp.tool()
async def local_llm_batch(
    prompts: list[str],
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """批量送多個 prompt 給本地模型，適合 Spec Kit tasks 階段一次處理多個小任務。

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
    headers = {}
    if OMLX_KEY:
        headers["Authorization"] = f"Bearer {OMLX_KEY}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OMLX_BASE}/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()

        models = [m["id"] for m in data.get("data", [])]
        return f"oMLX 運作中 ✅\n伺服器: {OMLX_BASE}\n可用模型: {', '.join(models)}"
    except Exception as e:
        return f"oMLX 無法連線 ❌\n伺服器: {OMLX_BASE}\n錯誤: {e}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
