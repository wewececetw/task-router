"""OpenAI-compatible API server that routes tasks transparently."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import RouterConfig
from .router import TaskRouter


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "auto"  # ignored, routing decides the model
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False


def create_app(config: RouterConfig) -> FastAPI:
    app = FastAPI(title="Task Router", version="0.1.0")
    router = TaskRouter(config)

    @app.post("/v1/chat/completions")
    async def chat_completions(req: ChatRequest):
        if req.stream:
            return JSONResponse(
                {"error": "Streaming not yet supported"},
                status_code=501,
            )

        # Extract the last user message as the task for classification
        task = ""
        for msg in reversed(req.messages):
            if msg.role == "user":
                task = msg.content
                break

        messages = [{"role": m.role, "content": m.content} for m in req.messages]

        result = router.route(task=task, messages=messages)

        # Return OpenAI-compatible response
        return JSONResponse(
            {
                "id": "tr-" + str(hash(task))[-8:],
                "object": "chat.completion",
                "model": result.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result.content,
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": result.usage,
                "x_task_router": {
                    "routed_to": result.routed_to,
                    "complexity": result.classification.complexity.value,
                    "confidence": result.classification.confidence,
                    "reason": result.classification.reason,
                },
            },
            headers={"X-Routed-To": result.routed_to},
        )

    @app.get("/v1/models")
    async def list_models():
        return {
            "data": [
                {"id": "auto", "object": "model", "owned_by": "task-router"},
                {"id": config.omlx.model, "object": "model", "owned_by": "omlx-local"},
                {"id": config.claude.model, "object": "model", "owned_by": "anthropic"},
            ]
        }

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
