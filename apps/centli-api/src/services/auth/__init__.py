class AuthService:
    def __init__(self, hmac_secret: bytes) -> None:
        self.hmac_secret = hmac_secret


__all__ = ["AuthService"]
