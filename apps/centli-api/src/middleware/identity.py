import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from src.db import DatabaseClient
from src.repos.user import UserRepo
from src.services.auth import AuthService
from src.services.auth.errors import InvalidToken

logger = logging.getLogger(__name__)


class IdentityMiddleware(BaseHTTPMiddleware):
    """Caller identification middleware.

    This middleware never blocks a request. Its sole job is to
    resolve *who* is calling, if anyone, and attach it to
    ``request.state.identity``. Authorization decisions belong
    to route dependencies (see ``require_auth`` / ``require_role``).

    Attaches:
        request.state.identity (User | None): the authenticated
            user, or None if there is no valid session.

    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Attaches the identity to the request state."""
        request.state.identity = None
        db_client: DatabaseClient = request.app.state.db
        token = request.cookies.get("access_token")
        if db_client is not None and token is not None:
            async with db_client.session() as session:
                try:
                    auth_service = AuthService(
                        UserRepo(session), request.app.state.config.hmac_secret
                    )
                    request.state.identity = await auth_service.get_user_from_token(
                        token
                    )
                except InvalidToken:
                    logger.warning("Request carried an invalid access token.")
                except Exception:
                    logger.exception("Unexpected error while resolving identity")
        return await call_next(request)
