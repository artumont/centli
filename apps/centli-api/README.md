# centli-api

The api for the service directly handling users requests and delegating fetch tasks to the scrappers

## Shared resources

Resources that are expensive and safe to share (engine, connection pool, http client) belong to
lifespan/`app.state`.

### Why?

The engine owns the connection pool, so building it per request means a new pool and a new handshake
per request. The lifespan gives one instance for the whole process and one place that closes it.

### Example

```py
# __main__.py
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
```

Note that `app.state.db` stays `None` when no database is configured, so every consumer has to
handle that case.

## Middleware

Middleware should avoid any init args that include shared resources, they should instead fetch them
from the app lifespan/`app.state`.

### Why?

Init args are fine as long as they are plain config. Anything stateful, or anything that already
holds a session or connection, is captured for the life of the app, so it cannot stay request
scoped. Read those from `request.app.state` in `dispatch` instead.

### Example

```py
# middleware/identity.py
async def dispatch(
    self, request: Request, call_next: RequestResponseEndpoint
) -> Response:
    """Dispatcher for the middleware, purpose explained in the actual classmethod."""
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
```

Both `db` and `config` are read from `request.app.state` at dispatch time, and the session is opened
and closed inside the request.

## Services

Build services per request from a dependency. Never store one in `app.state`.

A service may hold collaborators (a repo, config, a secret). It must not hold per-call state: no
cached user, no accumulated results, no session kept for a later request.

### Why?

`get_db_session` hands out one `AsyncSession` per request and owns commit and rollback, so anything
using it has to die with the request. A service in `app.state` lives forever, which leaves it
holding either a shared session, unsafe across concurrent requests, or its own `DatabaseClient`,
which drops the request transaction and `dependency_overrides` in tests.

Middleware is the exception: it has no `Depends`, so it opens its own session from `app.state.db`.

### Example

```py
# routes/auth/deps.py
def get_auth_service(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> AuthService:
    """Get the auth service."""
    return AuthService(UserRepo(session), request.app.state.config.hmac_secret)
```

The session arrives already scoped to the request, so the service never opens or closes one.

```py
# services/auth/__init__.py
class AuthService:
    """Authentication and session generation service."""

    def __init__(
        self,
        user_repo: UserRepo,
        signing_secret: str,
        *,
        access_token_ttl: int = 3600,
        refresh_token_ttl: int = 604800,
    ) -> None:
        self.user_repo = user_repo
        self.signing_secret = signing_secret
        self._access_token_ttl = access_token_ttl
        self._refresh_token_ttl = refresh_token_ttl

    ...
```

Everything on `self` is a collaborator or config, nothing is written while handling a request.
