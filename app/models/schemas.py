"""Pydantic schema definitions for request/response payloads.

Keep these models focused on API contracts (validation + serialization),
separate from SQLAlchemy persistence models.
"""

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Payload accepted when registering a new user account."""

    # EmailStr performs RFC-compliant email validation.
    email: EmailStr
    # Plain password is accepted only at input time and never returned.
    password: str


class UserResponse(BaseModel):
    """Safe user representation returned by public endpoints."""

    id: int
    email: EmailStr

    class Config:
        # Enable conversion from ORM instances returned by SQLAlchemy.
        from_attributes = True