"""Pydantic schema definitions for request/response payloads.

Keep these models focused on API contracts (validation + serialization),
separate from SQLAlchemy persistence models.
"""

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """Payload accepted when registering a new user account."""

    # EmailStr performs RFC-compliant email validation.
    email: EmailStr
    
    # Plain password is accepted only at input time and never returned.
    # FIX: Added max_length=72 to prevent the bcrypt ValueError crash!
    # Also added min_length=8 for basic security best practices.
    password: str = Field(..., max_length=72, min_length=8)


class UserResponse(BaseModel):
    """Safe user representation returned by public endpoints."""

    id: int
    email: EmailStr

    class Config:
        # Enable conversion from ORM instances returned by SQLAlchemy.
        from_attributes = True