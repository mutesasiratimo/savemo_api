import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt

from app.core.config import settings

# Bcrypt only accepts up to 72 bytes. Pre-hash longer passwords with SHA256
# so we never exceed that (64-char hex digest).
_BCRYPT_MAX_BYTES = 72


def _normalize_password_for_bcrypt(password: str) -> bytes:
    raw = password.encode("utf-8")
    if len(raw) <= _BCRYPT_MAX_BYTES:
        return raw
    return hashlib.sha256(raw).hexdigest().encode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized = _normalize_password_for_bcrypt(plain_password)
    return bcrypt.checkpw(normalized, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    normalized = _normalize_password_for_bcrypt(password)
    return bcrypt.hashpw(normalized, bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    subject: Any, expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "type": "access",
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(subject: Any) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def decode_access_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    if payload.get("type") not in ("access", None):
        raise ValueError("Invalid token type")
    return payload

