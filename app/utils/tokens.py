import secrets
import string
from datetime import datetime, timedelta, timezone
import jwt
from config import SECRET_KEY, JWT_ALGORITHM

def generate_reset_token() -> str:
    """
    6-digit numeric token (e.g., for mobile code)
    """
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_jwt_reset_token(user_id: int, email: str, expires_minutes: int = 15) -> str:
    """
    JWT for password reset, default 15 minutes
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "password_reset",
        "exp": now + timedelta(minutes=expires_minutes),
        "iat": now,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_reset_token(token: str) -> dict | None:
    """
    Verify and decode JWT reset token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
