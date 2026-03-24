"""Client for oMLX local model (OpenAI-compatible API)."""

from __future__ import annotations

import time
from dataclasses import dataclass

from openai import OpenAI

from .config import OMLXConfig


@dataclass
class LocalResponse:
    content: str
    model: str
    latency_ms: float
    usage: dict


def create_client(config: OMLXConfig) -> OpenAI:
    """Create OpenAI client pointing to oMLX."""
    return OpenAI(
        base_url=config.base_url,
        api_key=config.api_key or "not-needed",
        timeout=config.timeout,
    )


def chat(
    client: OpenAI,
    messages: list[dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> LocalResponse:
    """Send a chat request to the local model."""
    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    latency = (time.perf_counter() - start) * 1000

    choice = response.choices[0]
    usage = {}
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return LocalResponse(
        content=choice.message.content or "",
        model=response.model,
        latency_ms=round(latency, 1),
        usage=usage,
    )
