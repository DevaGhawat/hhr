import hashlib
import secrets

from app.core.config import settings


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    raw_value = f"{settings.app_secret_key}:{token}"
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()


def verify_token(token: str, token_hash: str) -> bool:
    return hash_token(token) == token_hash
