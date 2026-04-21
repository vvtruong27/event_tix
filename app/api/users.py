"""User-related HTTP endpoints.

This module currently exposes account creation (signup) logic and demonstrates
the standard route pattern used in the project: validate input with Pydantic,
query the database asynchronously, and return a response schema.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.sql_models import User
from app.models.schemas import UserCreate, UserResponse
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user account.

    Steps:
    1. Guard against duplicate email addresses.
    2. Hash the provided password before persistence.
    3. Persist and refresh the SQLAlchemy instance.
    4. Return a safe response model that excludes password data.
    """
    # Check uniqueness first to provide a clear conflict-style error.
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Store only a one-way hash, never the raw password.
    hashed_pw = get_password_hash(user_in.password)

    # Build ORM object from validated input payload.
    new_user = User(email=user_in.email, hashed_password=hashed_pw)

    # Persist transaction and reload object to retrieve generated columns (e.g. id).
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # FastAPI serializes ORM object using the declared response_model.
    return new_user