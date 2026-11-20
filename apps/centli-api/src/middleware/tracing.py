from contextvars import ContextVar

from starlette.types import ASGIApp, Message, Receive, Scope, Send
from uuid6 import uuid7

trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)


class TracingMiddleware:
    """Request tracing pure ASGI Middleware

    Meant to track errors and normal requests to make
    error reports easier and administration faster.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app: ASGIApp = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Attaches the `trace_id` to the context."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        trace_id = str(uuid7())
        scope.setdefault("state", {})["trace_id"] = trace_id
        token = trace_id_ctx.set(trace_id)

        async def send_with_header(message: Message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).append(
                    (b"x-trace-id", trace_id.encode())
                )
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            trace_id_ctx.reset(token)
