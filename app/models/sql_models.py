"""SQLAlchemy ORM models for relational data in PostgreSQL.

The service stores authentication and ownership metadata in PostgreSQL, while
event catalog details may be stored elsewhere (e.g. MongoDB).
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base used by all ORM entities."""

    pass


class User(Base):
    """User account record.

    Stores identity and credential hash only; never stores plaintext secrets.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    # Use UTC timestamps to avoid timezone ambiguity across services.
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    # One-to-many: a single user can own multiple ticket records.
    tickets: Mapped[List["TicketOwnership"]] = relationship(back_populates="owner")


class TicketOwnership(Base):
    """Record of a purchased/owned ticket linked to a user."""

    __tablename__ = "ticket_ownership"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # References the event identifier from the event catalog datastore.
    event_id: Mapped[str] = mapped_column(String(50), index=True)

    seat_number: Mapped[str] = mapped_column(String(10))
    # Monetary values are stored in cents to avoid floating-point precision issues.
    price_paid: Mapped[int] = mapped_column()
    purchased_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    # Inverse side of User.tickets.
    owner: Mapped["User"] = relationship(back_populates="tickets")