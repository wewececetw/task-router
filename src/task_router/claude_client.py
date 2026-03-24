"""Client for Claude API (supports OAuth token and API key)."""

from __future__ import annotations

import time
from dataclasses import dataclass

import anthropic

from .config import ClaudeConfig


@dataclass
class ClaudeResponse:
    content: str
    model: str
    latency_ms: float
    usage: dict
    stop_reason: str


def create_client(config: ClaudeConfig) -> anthropic.Anthropic:
    """Create Anthropic client.

    Supports:
    - OAuth token (sk-ant-oat01-*): billed against Pro/Max subscription
    - API key (sk-ant-api03-*): billed per-token via Console
    - ANTHROPIC_API_KEY env var: auto-detected by SDK
    """
    kwargs = {}
    if config.api_key:
        kwargs["api_key"] = config.api_key
    # If no key provided, SDK will look for ANTHROPIC_API_KEY env var
    return anthropic.Anthropic(**kwargs)


def chat(
    client: anthropic.Anthropic,
    messages: list[dict],
    model: str,
    max_tokens: int = 4096,
    system: str | None = None,
    temperature: float = 0.7,
) -> ClaudeResponse:
    """Send a chat request to Claude API."""
    start = time.perf_counter()

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    latency = (time.perf_counter() - start) * 1000

    content = ""
    for block in response.content:
        if block.type == "text":
            content += block.text

    return ClaudeResponse(
        content=content,
        model=response.model,
        latency_ms=round(latency, 1),
        usage={
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        stop_reason=response.stop_reason or "",
    )
