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
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    # FIX: Strip the tzinfo so it matches PostgreSQL's WITHOUT TIME ZONE column!
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    tickets: Mapped[List["TicketOwnership"]] = relationship(back_populates="owner")


class TicketOwnership(Base):
    __tablename__ = "ticket_ownership"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[str] = mapped_column(String(50), index=True)
    seat_number: Mapped[str] = mapped_column(String(10))
    price_paid: Mapped[int] = mapped_column()
    
    # FIX: Strip the tzinfo here too!
    purchased_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    owner: Mapped["User"] = relationship(back_populates="tickets")