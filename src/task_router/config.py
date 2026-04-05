"""Configuration for task router."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OMLXConfig(BaseModel):
    """oMLX local model server config."""
    base_url: str = "http://127.0.0.1:9000/v1"
    model: str = "Qwen3.5-9B-MLX-4bit"
    api_key: str = ""
    timeout: float = 120.0


class ClaudeConfig(BaseModel):
    """Claude API config. Supports both OAuth token and API key."""
    api_key: str = ""  # sk-ant-oat01-* (OAuth) or sk-ant-api03-* (API key)
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    timeout: float = 120.0


class RouterConfig(BaseModel):
    """Overall router configuration."""
    omlx: OMLXConfig = Field(default_factory=OMLXConfig)
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)
    # If classifier confidence is below this, use complex (safer)
    confidence_threshold: float = 0.5
    # Force all tasks to a specific backend (bypass classifier)
    force_backend: str | None = None  # "local" or "cloud" or None
    # Workflow toolkit: "vibelens", "speckit", or custom
    workflow: str = "speckit"
    verbose: bool = False
