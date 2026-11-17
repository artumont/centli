import datetime
from enum import Enum
from typing import Any, Literal

import jwt
from jwt.types import Options
from uuid6 import uuid7

from src.utils import utc_now


class TokenType(Enum):
    """Known token types."""

    ACCESS = "access"
    REFRESH = "refresh"


def generate_jwt_token(
    secret: str,
    subject: str,
    ttl_seconds: int,
    *,
    algorithm: Literal["HS256"] = "HS256",
    token_type: TokenType = TokenType.ACCESS,
    extra_claims: dict[str, object] | None = None,
    jti: str | None = None,
):
    """Create a signed JWT Token

    Args:
        secret (str): Signing secret for the token.
        subject (str): User or entity the token is for.
        ttl_seconds (int): Time the token is valid in seconds.
        algorithm (Literal["HS256"]): Signing algorithm. Defaults to "HS256".
        token_type (TokenType): Token type. Defaults to TokenType.ACCESS.
        extra_claims (dict[str, object] | None): Extra data embedded into the token. Defaults to None.
        jti (str | None): Token ID. Defaults to None.

    Returns:
        str: Signed token.

    """
    now = utc_now()

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + datetime.timedelta(ttl_seconds),
        "type": str(token_type),
        "jti": jti or str(uuid7()),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_jwt_token(
    secret: str,
    token: str,
    *,
    algorithm: Literal["HS256"] = "HS256",
    expected_type: TokenType | None = None,
    leeway_seconds: int = 0,
) -> dict[str, Any]:
    """Decode and verify a JWT Token.

    Args:
        secret (str): Signing secret for the token.
        token (str): Encoded token.
        algorithm (Literal["HS256"]): Signing algorithm. Defaults to "HS256".
        expected_type (TokenType | None): Type of token to expect. Defaults to None.
        leeway_seconds (int): Expiration tolerance. Defaults to 0.

    Returns:
        dict: Payload of the signed token.

    """
    options: Options = {
        "verify_signature": True,
        "verify_exp": True,
    }

    payload: dict[str, Any] = jwt.decode(
        token, secret, algorithm=algorithm, options=options, leeway=leeway_seconds
    )

    if expected_type is not None and payload.get("type") != expected_type:
        raise ValueError(
            f"Expected token type {expected_type!r}, got {payload.get('type')!r}"
        )

    return payload
