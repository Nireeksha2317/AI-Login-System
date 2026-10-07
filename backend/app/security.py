from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash


# =========================================================
# PASSWORD HASHING
# =========================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password securely."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain-text password against a stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# =========================================================
# JWT AUTHENTICATION
# =========================================================

def create_access_token(
    user_id: int,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    """Create a signed JWT access token."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def decode_access_token(
    token: str,
    secret_key: str,
    algorithm: str,
) -> dict:
    """Decode and validate a JWT access token."""

    try:
        return jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
        )
    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token."
        ) from exc