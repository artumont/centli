import base64
import json
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureVault:
    def __init__(
        self,
        vault_path: str = "/data/secrets.vault",
        master_key_file: str = "/run/secrets/vault_master_key",
    ) -> None:
        self.vault_path = vault_path
        self.master_key_file = master_key_file

        self._secrets: dict[str, Any] = {}

        self._boot_or_unseal()

    def get_hmac_key(self) -> bytes:
        return bytes.fromhex(self._secrets["hmac_key"])

    def _read_master_secret(self) -> bytes:
        if not os.path.exists(self.master_key_file):
            raise RuntimeError(f"Master key file missing at {self.master_key_file}")
        with open(self.master_key_file, "rb") as f:
            secret = f.read().strip()
        if not secret:
            raise RuntimeError("Master key file is empty.")
        return secret

    def _derive_key(self, master_secret: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_secret))

    def _save(self, master_secret: bytes | None = None):
        if master_secret is None:
            master_secret = self._read_master_secret()

        salt = os.urandom(16)
        key = self._derive_key(master_secret, salt)
        json_bytes = json.dumps(self._secrets).encode("utf-8")
        ciphertext = Fernet(key).encrypt(json_bytes)

        with open(self.vault_path, "wb") as f:
            f.write(salt + ciphertext)
        try:
            os.chmod(self.vault_path, 0o600)
        except OSError:
            pass

    def _boot_or_unseal(self):
        master_secret = self._read_master_secret()

        if not os.path.exists(self.vault_path):
            # FIRST STARTUP: Generate fresh 32-byte HMAC key and encrypt vault
            self._secrets = {
                "hmac_key": os.urandom(32).hex(),
            }
            self._save(master_secret)
        else:
            # SUBSEQUENT STARTUPS: Load and decrypt into RAM
            with open(self.vault_path, "rb") as f:
                raw = f.read()
            salt, ciphertext = raw[:16], raw[16:]
            key = self._derive_key(master_secret, salt)
            try:
                decrypted = Fernet(key).decrypt(ciphertext)
                self._secrets = json.loads(decrypted.decode("utf-8"))
            except InvalidToken:
                raise ValueError(
                    "Failed to decrypt vault. Check your master key secret."
                )
