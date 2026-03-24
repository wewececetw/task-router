"""
Spec Kit Smart Router — LiteLLM-powered proxy

A lightweight proxy that sits between Claude Code and your models.
Routes requests to oMLX (local) or Claude (cloud) based on Spec Kit phases.

Usage:
  OMLX_API_KEY=xxx python speckit_router.py --port 4000

Claude Code setup:
  ANTHROPIC_BASE_URL=http://127.0.0.1:4000
"""

from __future__ import annotations

import os
import re
import time
from typing import Optional

import litellm
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

# Suppress LiteLLM noise
litellm.set_verbose = False
os.environ.setdefault("LITELLM_LOG", "ERROR")

app = FastAPI(title="Spec Kit Router")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OMLX_MODEL = "openai/Qwen3.5-9B-MLX-4bit"
OMLX_BASE = os.environ.get("OMLX_BASE_URL", "http://127.0.0.1:9000/v1")
OMLX_KEY = os.environ.get("OMLX_API_KEY", "not-needed")

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
# Claude API key picked up from ANTHROPIC_API_KEY env var by litellm

# ---------------------------------------------------------------------------
# Spec Kit phase detection
# ---------------------------------------------------------------------------

CLOUD_PHASES = re.compile(
    r"(?:speckit\.)?(?:constitution|spec(?:ify)?(?:\s|$)|clarify|plan)\b"
    r"|核心原則|core.?principles"
    r"|需求|requirement|user.?stor"
    r"|釐清|澄清|underspecified"
    r"|架構|architecture.?design"
    r"|implementation.?plan",
    re.I,
)

LOCAL_PHASES = re.compile(
    r"(?:speckit\.)?(?:tasks?\b|checklist|analy[zs]e)"
    r"|task.?list|任務列表|task.?breakdown"
    r"|檢查清單|quality.?check"
    r"|一致性|consistency.?check",
    re.I,
)

COMPLEX_IMPL = re.compile(
    r"auth(?:entication|orization)|OAuth|JWT|session|login"
    r"|security|encrypt|hash|vulnerab|CSRF|XSS"
    r"|core.?logic|business.?logic|algorithm|state.?machine"
    r"|integrat(?:e|ion)|third.?party|external.?api|webhook"
    r"|error.?handling|retry|circuit.?break|fault.?toleran"
    r"|optimi[zs]|cach(?:e|ing)|performance|concurrent"
    r"|pipeline|ETL|data.?flow|stream|queue"
    r"|complex.?query|aggregat|join.*table|analytics",
    re.I,
)

SIMPLE_IMPL = re.compile(
    r"create.*(?:model|schema|entity|config)"
    r"|boilerplate|scaffold|template|project.?structure"
    r"|CRUD|create.*endpoint|basic.*api|simple.*route"
    r"|add.*dependency|install.*package|setup.*tool"
    r"|lint|format|prettier|style"
    r"|document|README|docstring|comment"
    r"|unit.?test|simple.?test|test.*model"
    r"|migration|schema.*change|add.*column"
    r"|environment|\.env|docker.?compose",
    re.I,
)


def extract_text(messages: list[dict]) -> str:
    parts = []
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        parts.append(block.get("text", ""))
    return " ".join(parts)


def decide_backend(text: str) -> str:
    """Returns 'local' or 'cloud'."""
    if LOCAL_PHASES.search(text):
        return "local"
    if CLOUD_PHASES.search(text):
        return "cloud"

    # Implementation sub-classify
    if re.search(r"(?:speckit\.)?implement|執行|實作|write.?code|coding", text, re.I):
        if len(COMPLEX_IMPL.findall(text)) > len(SIMPLE_IMPL.findall(text)):
            return "cloud"
        return "local"

    # Fallback: short=local, long=cloud
    if len(text.split()) < 80 and not COMPLEX_IMPL.search(text):
        return "local"
    return "cloud"


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

stats = {"local": 0, "cloud": 0, "saved_requests": 0}


# ---------------------------------------------------------------------------
# Anthropic Messages API proxy
# ---------------------------------------------------------------------------

@app.post("/v1/messages")
async def messages_proxy(request: Request):
    """Proxy for Anthropic Messages API — routes to local or cloud."""
    body = await request.json()
    messages = body.get("messages", [])
    text = extract_text(messages)
    backend = decide_backend(text)

    stats[backend] += 1
    start = time.perf_counter()

    try:
        if backend == "local":
            # Use oMLX via OpenAI-compatible endpoint
            response = await litellm.acompletion(
                model=OMLX_MODEL,
                messages=messages,
                api_base=OMLX_BASE,
                api_key=OMLX_KEY,
                max_tokens=body.get("max_tokens", 4096),
                temperature=body.get("temperature", 0.7),
                stream=body.get("stream", False),
            )
            stats["saved_requests"] += 1
        else:
            # Use Claude API
            response = await litellm.acompletion(
                model=CLAUDE_MODEL,
                messages=messages,
                max_tokens=body.get("max_tokens", 4096),
                temperature=body.get("temperature", 0.7),
                stream=body.get("stream", False),
            )

        latency = (time.perf_counter() - start) * 1000
        model_name = OMLX_MODEL if backend == "local" else CLAUDE_MODEL
        icon = "🖥️" if backend == "local" else "☁️"
        print(f"  {icon} [{backend}] {model_name} | {latency:.0f}ms | {text[:60]}...")

        # Convert LiteLLM response to Anthropic Messages format
        content = response.choices[0].message.content or ""
        anthropic_response = {
            "id": f"msg_{response.id}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
            "model": model_name,
            "stop_reason": response.choices[0].finish_reason or "end_turn",
            "usage": {
                "input_tokens": getattr(response.usage, "prompt_tokens", 0) or 0,
                "output_tokens": getattr(response.usage, "completion_tokens", 0) or 0,
            },
        }
        return JSONResponse(anthropic_response)

    except Exception as e:
        print(f"  ❌ [{backend}] Error: {e}")
        # Fallback: try the other backend
        if backend == "local":
            try:
                response = await litellm.acompletion(
                    model=CLAUDE_MODEL,
                    messages=messages,
                    max_tokens=body.get("max_tokens", 4096),
                )
                content = response.choices[0].message.content or ""
                return JSONResponse({
                    "id": f"msg_{response.id}",
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": content}],
                    "model": CLAUDE_MODEL,
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": getattr(response.usage, "prompt_tokens", 0) or 0,
                        "output_tokens": getattr(response.usage, "completion_tokens", 0) or 0,
                    },
                })
            except Exception as e2:
                return JSONResponse({"error": str(e2)}, status_code=500)
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# OpenAI Chat Completions API proxy (for compatibility)
# ---------------------------------------------------------------------------

@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    """Proxy for OpenAI Chat Completions API."""
    body = await request.json()
    messages = body.get("messages", [])
    text = extract_text(messages)
    backend = decide_backend(text)

    stats[backend] += 1
    start = time.perf_counter()

    try:
        if backend == "local":
            response = await litellm.acompletion(
                model=OMLX_MODEL,
                messages=messages,
                api_base=OMLX_BASE,
                api_key=OMLX_KEY,
                max_tokens=body.get("max_tokens", 4096),
                temperature=body.get("temperature", 0.7),
            )
            stats["saved_requests"] += 1
        else:
            response = await litellm.acompletion(
                model=CLAUDE_MODEL,
                messages=messages,
                max_tokens=body.get("max_tokens", 4096),
                temperature=body.get("temperature", 0.7),
            )

        latency = (time.perf_counter() - start) * 1000
        model_name = OMLX_MODEL if backend == "local" else CLAUDE_MODEL
        icon = "🖥️" if backend == "local" else "☁️"
        print(f"  {icon} [{backend}] {model_name} | {latency:.0f}ms | {text[:60]}...")

        return JSONResponse(response.model_dump())

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# Status / health endpoints
# ---------------------------------------------------------------------------

@app.get("/v1/models")
async def list_models():
    return JSONResponse({
        "object": "list",
        "data": [
            {"id": "speckit-router", "object": "model", "owned_by": "speckit"},
            {"id": CLAUDE_MODEL, "object": "model", "owned_by": "anthropic"},
            {"id": OMLX_MODEL, "object": "model", "owned_by": "omlx-local"},
        ],
    })


@app.get("/health")
@app.get("/")
async def health():
    total = stats["local"] + stats["cloud"]
    pct_local = (stats["local"] / total * 100) if total > 0 else 0
    return {
        "status": "ok",
        "router": "speckit",
        "stats": {
            **stats,
            "total": total,
            "local_pct": f"{pct_local:.0f}%",
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════╗
║   Spec Kit Smart Router                          ║
║                                                  ║
║   Cloud:  {CLAUDE_MODEL}
║   Local:  oMLX Qwen3.5-9B @ :9000
║   Proxy:  http://{args.host}:{args.port}
║                                                  ║
║   Phase Routing:                                 ║
║     constitution/specify/plan/clarify → Claude   ║
║     tasks/checklist/analyze           → oMLX     ║
║     implement                         → auto     ║
╚══════════════════════════════════════════════════╝
""")

    uvicorn.run(app, host=args.host, port=args.port)
