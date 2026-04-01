"""
oMLX MCP Server — 讓 Claude Code/Desktop 把簡單任務丟給本地模型

Features:
  - Auto-compact: 內容快超過 context window 時自動壓縮再送
  - Chunked processing: 太大的內容自動分段處理再合併
  - Connection pool: 持久化 HTTP 連線
  - Fallback hint: 真的處理不了就回報讓 Claude 自己處理

安裝（Claude Code 全域）:
  claude mcp add omlx-local -s user \
    -e OMLX_API_KEY="your-key" \
    -e OMLX_BASE_URL="http://127.0.0.1:9000/v1" \
    -- uv run --directory /path/to/task-router python mcp_omlx.py
"""

from __future__ import annotations

import os
import re
import subprocess
import httpx
from mcp.server.fastmcp import FastMCP, Context

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OMLX_BASE = os.environ.get("OMLX_BASE_URL", "http://127.0.0.1:9000/v1")
OMLX_KEY = os.environ.get("OMLX_API_KEY", "")
OMLX_MODEL = os.environ.get("OMLX_MODEL", "Qwen3.5-9B-MLX-4bit")

# Context window config (tokens)
CONTEXT_WINDOW = int(os.environ.get("OMLX_CONTEXT_WINDOW", "32768"))
COMPACT_THRESHOLD = 0.70  # 70% 時觸發 compact
CHUNK_THRESHOLD = 0.90    # 90% 時改用分段
MAX_CHUNKS = 6            # 最多分幾段

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
# Token estimation
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """粗估 token 數：中文 ~1.5 char/token，英文 ~4 char/token。"""
    cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - cn_chars
    return int(cn_chars / 1.5 + other_chars / 4)


# ---------------------------------------------------------------------------
# Raw LLM call (no protection, internal use)
# ---------------------------------------------------------------------------

def _notify(title: str, message: str):
    """macOS 系統通知（非阻塞）。"""
    try:
        subprocess.Popen([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}" sound name "Glass"'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass  # 通知失敗不影響主流程


def _strip_thinking(text: str) -> str:
    """移除 <think>...</think> 思考過程。"""
    return re.sub(r"<think>[\s\S]*?</think>\s*", "", text).strip()


async def _raw_call(messages: list[dict], max_tokens: int, temperature: float = 0.7, ctx: Context | None = None) -> str:
    """直接呼叫本地模型，不做任何 token 檢查。"""
    if ctx:
        await ctx.info(f"呼叫本地模型 ({OMLX_MODEL})...")
    resp = await _client.post(
        "/chat/completions",
        json={
            "model": OMLX_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return _strip_thinking(content)


# ---------------------------------------------------------------------------
# Strategy 1: Compact
# ---------------------------------------------------------------------------

async def _compact(text: str, target_tokens: int, ctx: Context | None = None) -> str:
    """用本地模型壓縮內容到目標 token 數。"""
    if ctx:
        await ctx.info(f"壓縮 prompt ({_estimate_tokens(text)} → ~{target_tokens} tokens)...")
    ratio = target_tokens / max(_estimate_tokens(text), 1)
    target_chars = int(len(text) * ratio)

    return await _raw_call(
        messages=[
            {
                "role": "system",
                "content": "你是一個文件壓縮器。保留所有技術細節、API 名稱、檔案路徑、資料結構。刪除冗餘描述和重複內容。輸出必須是結構化的重點摘要。",
            },
            {
                "role": "user",
                "content": f"將以下內容壓縮到約 {target_chars} 字以內，保留所有關鍵技術資訊：\n\n{text}",
            },
        ],
        max_tokens=target_tokens,
        temperature=0.3,
        ctx=ctx,
    )


# ---------------------------------------------------------------------------
# Strategy 2: Chunked map-reduce
# ---------------------------------------------------------------------------

def _split_chunks(text: str, chunk_tokens: int) -> list[str]:
    """按段落或行把文字切成 chunks，每段不超過 chunk_tokens。"""
    # 優先按雙換行（段落）分割，其次按行
    paragraphs = text.split("\n\n")
    if len(paragraphs) < 3:
        paragraphs = text.split("\n")

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = _estimate_tokens(para)
        if current_tokens + para_tokens > chunk_tokens and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_tokens = para_tokens
        else:
            current.append(para)
            current_tokens += para_tokens

    if current:
        chunks.append("\n\n".join(current))

    return chunks[:MAX_CHUNKS]


async def _chunked_process(prompt: str, system: str, task_instruction: str, max_tokens: int, ctx: Context | None = None) -> tuple[str, str]:
    """Map-Reduce：分段處理後合併結果。"""
    # 留空間給 system prompt + task instruction + output
    overhead = _estimate_tokens(system) + _estimate_tokens(task_instruction) + 200
    chunk_tokens = int(CONTEXT_WINDOW * 0.6) - overhead - max_tokens // 2

    if chunk_tokens < 500:
        return "", "⚠️ FALLBACK: context window 扣除 overhead 後空間不足，建議由 Claude 直接處理。"

    chunks = _split_chunks(prompt, chunk_tokens)

    if len(chunks) > MAX_CHUNKS:
        return "", f"⚠️ FALLBACK: 內容分段後超過 {MAX_CHUNKS} 段，太大了，建議由 Claude 直接處理。"

    if ctx:
        await ctx.info(f"Chunked map-reduce：分成 {len(chunks)} 段處理...")

    # Map: 每段分別處理
    chunk_results = []
    for i, chunk in enumerate(chunks):
        if ctx:
            await ctx.info(f"Map 第 {i+1}/{len(chunks)} 段...")
        map_prompt = (
            f"這是第 {i+1}/{len(chunks)} 段內容。\n"
            f"任務：{task_instruction}\n"
            f"只處理這一段，輸出這段的結果：\n\n{chunk}"
        )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": map_prompt})

        result = await _raw_call(messages, max_tokens=max_tokens // 2, temperature=0.5, ctx=ctx)
        chunk_results.append(result)

    # Reduce: 合併所有段的結果
    if len(chunk_results) == 1:
        return chunk_results[0], f"📎 Chunked: 1 段處理"

    if ctx:
        await ctx.info(f"Reduce：合併 {len(chunk_results)} 段結果...")

    reduce_prompt = (
        f"以下是分段處理的結果（共 {len(chunk_results)} 段），請合併成一份完整的輸出。\n"
        f"去除重複，保持一致性：\n\n"
    )
    for i, r in enumerate(chunk_results):
        reduce_prompt += f"--- 第 {i+1} 段結果 ---\n{r}\n\n"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": reduce_prompt})

    final = await _raw_call(messages, max_tokens=max_tokens, temperature=0.5, ctx=ctx)
    note = f"📎 Chunked map-reduce: {len(chunks)} 段 → 合併"
    return final, note


# ---------------------------------------------------------------------------
# Smart prompt preparation (compact → chunk → fallback)
# ---------------------------------------------------------------------------

def _extract_task_instruction(prompt: str) -> tuple[str, str]:
    """嘗試從 prompt 中分離任務指令和內容。"""
    # 常見模式：指令在前，內容在後（用 --- 或 ``` 或「內容：」分隔）
    separators = ["\n---\n", "\n```\n", "\n內容：\n", "\n內容:\n",
                  "\nContent:\n", "\nPlan 內容：\n", "\nSpec:\n",
                  "\nPlan:\n", "\nTasks:\n"]
    for sep in separators:
        if sep in prompt:
            parts = prompt.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    # 找不到分隔，取前 500 字當指令
    if len(prompt) > 500:
        return prompt[:500], prompt[500:]
    return prompt, ""


async def _prepare_prompt(prompt: str, system: str, max_tokens: int, ctx: Context | None = None) -> tuple[str, str, str]:
    """
    三階段策略：
    1. < 70%: 直接送
    2. 70-90%: auto-compact
    3. > 90%: chunked map-reduce
    4. chunk 也失敗: fallback 給 Claude
    """
    total_input = _estimate_tokens(prompt) + _estimate_tokens(system)
    total_needed = total_input + max_tokens
    limit = CONTEXT_WINDOW

    # 1. 安全範圍
    if total_needed < limit * COMPACT_THRESHOLD:
        return prompt, system, ""

    # 2. Compact 範圍 (70-90%)
    if total_needed < limit * CHUNK_THRESHOLD:
        if ctx:
            await ctx.info(f"Prompt 接近 context 上限 ({total_input} tokens)，auto-compacting...")
        target = int(limit * 0.5) - max_tokens
        if target < 500:
            return prompt, system, "⚠️ FALLBACK: 壓縮後空間不足，建議由 Claude 直接處理。"

        compacted = await _compact(prompt, target, ctx=ctx)
        note = (
            f"🗜️ Auto-compacted: {total_input} → ~{_estimate_tokens(compacted)} tokens "
            f"(saved {total_input - _estimate_tokens(compacted)})"
        )
        return compacted, system, note

    # 3. Chunk 範圍 (>90%)
    if ctx:
        await ctx.info(f"Prompt 超過 context 上限 ({total_input} tokens)，chunking...")
    task_instruction, content = _extract_task_instruction(prompt)
    if content:
        result, note = await _chunked_process(content, system, task_instruction, max_tokens, ctx=ctx)
        if result:
            # chunk 成功，直接回傳結果（不用再送一次）
            return "", "", f"CHUNKED_RESULT:{note}\n\n{result}"
        # chunk 失敗，回傳 fallback 訊息
        return prompt, system, note

    # 內容無法分離，嘗試 compact
    target = int(limit * 0.5) - max_tokens
    if target >= 500:
        compacted = await _compact(prompt, target, ctx=ctx)
        note = (
            f"🗜️ Force-compacted: {total_input} → ~{_estimate_tokens(compacted)} tokens"
        )
        return compacted, system, note

    return prompt, system, "⚠️ FALLBACK: 內容太大且無法分段，建議由 Claude 直接處理。"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def local_llm(
    prompt: str,
    system: str = "",
    max_tokens: int = 4096,
    temperature: float = 0.7,
    ctx: Context | None = None,
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

    vibe-lens 整合規則:
    當使用者呼叫 vibe-lens (sdd_*) 的 local 階段時，必須用此 tool 做後處理：
    - sdd_tasks 產出後 → 用 local_llm 加時間估算、格式化、標記可平行任務
    - sdd_analyze 產出後 → 用 local_llm 加嚴重度 (P0/P1/P2)、翻譯成雙語
    - sdd_checklist 產出後 → 用 local_llm 擴展成可執行的測試場景
    - sdd_digest 產出後 → 用 local_llm 翻譯成雙語對照
    - sdd_export 產出後 → 用 local_llm 調整為 stakeholder 友好格式
    - sdd_review_artifact 產出後 → 用 local_llm 展開建議成具體改善步驟
    不需要後處理的 vibe-lens 階段（Cloud，由 Claude 直接處理）:
    - sdd_constitution, sdd_specify, sdd_clarify, sdd_plan, sdd_gate
    不需要後處理的工具類:
    - sdd_status, sdd_guide, sdd_task_next, sdd_task_done, sdd_learn, sdd_explain

    Args:
        prompt: 要送給本地模型的提示詞
        system: 系統提示詞（可選）
        max_tokens: 最大回覆 token 數
        temperature: 溫度參數
    """
    if ctx:
        short_prompt = prompt[:60].replace("\n", " ") + ("..." if len(prompt) > 60 else "")
        await ctx.info(f"準備 prompt: {short_prompt}")

    prompt, system, note = await _prepare_prompt(prompt, system, max_tokens, ctx=ctx)

    # Fallback: 回傳警告讓 Claude 接手
    if note and note.startswith("⚠️"):
        if ctx:
            await ctx.warning("Prompt 太大，fallback 給 Claude")
        _notify("oMLX ⚠️", "內容太大，交給 Claude")
        return note

    # Chunked result: 已經處理完了，直接回傳
    if note and note.startswith("CHUNKED_RESULT:"):
        if ctx:
            await ctx.info("Chunked 處理完成")
        return note.replace("CHUNKED_RESULT:", "", 1)

    # 正常送
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    content = await _raw_call(messages, max_tokens=max_tokens, temperature=temperature, ctx=ctx)
    model_name = OMLX_MODEL
    prefix = f"{note}\n\n" if note else ""
    short = prompt[:40].replace('"', "'") + "..." if len(prompt) > 40 else prompt.replace('"', "'")
    _notify("oMLX ✅", f"{short}")
    if ctx:
        await ctx.info("完成 ✅")
    return f"{prefix}[oMLX | {model_name}]\n\n{content}"


@mcp.tool()
async def local_llm_batch(
    prompts: list[str],
    system: str = "",
    max_tokens: int = 2048,
    ctx: Context | None = None,
) -> str:
    """批量送多個 prompt 給本地模型,適合 tasks 階段一次處理多個小任務。

    Args:
        prompts: 多個 prompt 的列表
        system: 共用的系統提示詞（可選）
        max_tokens: 每個 prompt 的最大回覆 token 數
    """
    if ctx:
        await ctx.info(f"Batch：處理 {len(prompts)} 個任務...")
    results = []
    for i, prompt in enumerate(prompts):
        if ctx:
            await ctx.info(f"Batch 任務 {i+1}/{len(prompts)}...")
        _notify("oMLX 🔄", f"Batch {i+1}/{len(prompts)}")
        result = await local_llm(prompt, system=system, max_tokens=max_tokens, ctx=ctx)
        results.append(f"### Task {i + 1}\n{result}")
    if ctx:
        await ctx.info(f"Batch 完成：{len(prompts)} 個任務 ✅")
    _notify("oMLX ✅", f"Batch 完成: {len(prompts)} 個任務")
    return "\n\n---\n\n".join(results)


@mcp.tool()
async def local_llm_status(ctx: Context | None = None) -> str:
    """檢查 oMLX 本地模型伺服器狀態。"""
    try:
        if ctx:
            await ctx.info(f"檢查 oMLX server ({OMLX_BASE})...")
        resp = await _client.get("/models")
        resp.raise_for_status()
        data = resp.json()

        models = [m["id"] for m in data.get("data", [])]
        return (
            f"oMLX 運作中 ✅\n"
            f"伺服器: {OMLX_BASE}\n"
            f"可用模型: {', '.join(models)}\n"
            f"Context window: {CONTEXT_WINDOW} tokens\n"
            f"Auto-compact: >{int(COMPACT_THRESHOLD*100)}% | "
            f"Chunked: >{int(CHUNK_THRESHOLD*100)}% (max {MAX_CHUNKS} chunks)"
        )
    except Exception as e:
        return f"oMLX 無法連線 ❌\n伺服器: {OMLX_BASE}\n錯誤: {e}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
