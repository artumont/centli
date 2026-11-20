from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Config, get_config
from .db import DatabaseClient
from .middleware import IdentityMiddleware
from .utils import utc_now

APP_NAME = "centli-api"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifecycle startup and shutdown."""
    app.state.db = None
    config: Config = app.state.config

    if config.database_url:
        app.state.db = DatabaseClient(config.database_url)

    yield

    if app.state.db is not None:
        await app.state.db.close()
        app.state.db = None


def create_app(config: Config | None = None) -> FastAPI:
    """Build the FastAPI application with middleware and API routes."""
    app = FastAPI(title=APP_NAME, root_path="/api", lifespan=lifespan)
    app.state.config = config or get_config()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    app.add_middleware(IdentityMiddleware)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "timestamp": str(utc_now())}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    config: Config = app.state.config
    uvicorn.run(
        "src.__main__:app",
        host=config.host,
        port=config.port,
        reload=False,
    )
