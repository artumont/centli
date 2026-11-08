from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_config
from .db import DatabaseClient
from .utils import utc_now

APP_NAME = "centli-api"

db: DatabaseClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifecycle shutdown and startup."""
    global db

    settings = get_config()

    if settings.database_url:
        db = DatabaseClient(settings.database_url)

    yield

    if db is not None:
        await db.close()
        db = None


def create_app() -> FastAPI:
    """Build the fastapi application with middleware and API routes.

    Returns:
        FastAPI: Configured application instance.
    """

    app = FastAPI(title=APP_NAME, root_path="/api", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            dict[str, str]: Response containing status ("ok") and current UTC timestamp.
        """
        return {"status": "ok", "timestamp": str(utc_now())}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_config()
    uvicorn.run(
        "src.__main__:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
