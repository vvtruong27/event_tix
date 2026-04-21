"""Security helpers for hashing and verifying passwords."""

import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Return a one-way hash for a plaintext password."""
    # 1. Pre-hash the password to a consistent 64-character hex string
    # This ensures emojis, long strings, or special chars never exceed 72 bytes!
    pre_hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # 2. Feed that safe 64-character string into bcrypt
    return pwd_context.hash(pre_hashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when plaintext password matches a stored hash."""
    pre_hashed = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(pre_hashed, hashed_password)