from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from .config import SECRET_KEY, JWT_ALGORITHM, JWT_EXP_MIN

# Use Argon2 - NO password length restrictions!
pwd_context = CryptContext(
    schemes=["argon2"],  # Only use Argon2
    deprecated="auto",
    argon2__time_cost=2,      # Lower for faster hashing during development
    argon2__memory_cost=1024, # Lower memory usage
    argon2__parallelism=2     # Lower parallelism
)

def hash_password(password: str) -> str:
    """
    Hash a password using Argon2
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"DEBUG: Hash error: {e}")
        # Fallback to SHA256 if Argon2 fails
        import hashlib
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    """
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        import hashlib
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == hashed

def create_token(user_id: int) -> str:
    """
    Create JWT token for authenticated user
    """
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MIN),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
