from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# MongoDB uses a special string called an ObjectId for its _id field
# This is a helper to make Pydantic play nice with it
class MongoBaseModel(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True

# 1. A sub-model to represent a block of seats (e.g., "VIP Section", "General Admission")
class TicketTier(BaseModel):
    tier_name: str
    price_cents: int
    total_capacity: int
    available_seats: int

# 2. The main Event Document!
class EventDocument(MongoBaseModel):
    title: str
    description: str
    artist: str
    venue: str
    event_date: datetime
    
    # Notice this! We can store an array of complex objects directly inside the document.
    # In SQL, this would require a whole separate table and a complex JOIN.
    ticket_tiers: List[TicketTier]