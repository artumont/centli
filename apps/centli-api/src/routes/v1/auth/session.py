import logging

from fastapi import APIRouter, Body, Depends, HTTPException

from src.routes.v1.auth.schemas import NewSession
from src.routes.v1.deps import get_auth_service
from src.services.auth import AuthService
from src.services.auth.errors import IncorrectPassword, UserNotFound

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session")


@router.post("/")
def create_new_session(
    auth_service: AuthService = Depends(get_auth_service), payload: NewSession = Body()
) -> None:
    tokens = None
    try:
        tokens = auth_service.generate_session(payload.username, payload.password)
    except (UserNotFound, IncorrectPassword):
        raise HTTPException(401, detail="Invalid credentials.") from None
