from uuid import UUID


class InvalidToken(Exception):
    """Raised when an authentication or API token fails validation."""

    def __init__(self, token: str) -> None:
        redacted = f"***{token[-4:]}" if len(token) > 8 else "***"
        super().__init__(f"Token `{redacted}` is invalid")


class UserNotFound(Exception):
    """Raised when a user is not found."""

    def __init__(self, username: str) -> None:
        super().__init__(f"User with username `{username}` was not found")


class IncorrectPassword(Exception):
    """Raised when and incorrect password is provided."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"Given password for {id} is incorrect")
