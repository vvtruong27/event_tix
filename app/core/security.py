"""Security helpers for hashing and verifying passwords.

Keeping this logic in one module ensures all endpoints use the same hashing
policy and simplifies future algorithm migration.
"""

from passlib.context import CryptContext

# `deprecated="auto"` allows passlib to mark old schemes for transparent upgrades.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Return a one-way hash for a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when plaintext password matches a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)