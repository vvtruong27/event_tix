"""Event catalog HTTP endpoints.

This module handles reading and writing event data (concerts, games) 
to our flexible MongoDB document store.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

# Import our MongoDB database connection
from app.core.database import mongo_db 

# Import our NoSQL schemas and repository
from app.models.nosql_models import EventDocument
from app.repositories.event_repo import EventRepository

router = APIRouter(prefix="/events", tags=["Events Catalog"])

# Instantiate the repository
event_repo = EventRepository(mongo_db)


@router.post("/", response_model=EventDocument, status_code=status.HTTP_201_CREATED)
async def create_event(event_in: EventDocument):
    """Create a new event in the catalog."""
    try:
        created_event = await event_repo.create_event(event_in)
        return created_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.get("/", response_model=List[EventDocument])
async def list_events():
    """Fetch all available events."""
    try:
        events = await event_repo.get_all_events()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")