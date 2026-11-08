from fastapi import APIRouter


def create_api_router() -> APIRouter:
    """Build API router from all supported API versions.

    Returns:
        APIRouter: Router containing all versioned API routes.
    """
    router = APIRouter()
    # router.include_router(v1_router)
    return router


api_router = create_api_router()

__all__ = ["api_router", "create_api_router"]
