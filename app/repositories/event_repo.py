from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.nosql_models import EventDocument
from typing import List

class EventRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # We connect to a specific "collection" (MongoDB's version of a table)
        self.collection = db.events

    async def create_event(self, event: EventDocument) -> EventDocument:
        # 1. Convert Pydantic to a Python dictionary
        event_dict = event.model_dump(exclude={"id"}, by_alias=True) 
        
        # 2. Insert into MongoDB
        result = await self.collection.insert_one(event_dict)
        
        # 3. Attach the generated ObjectId back to the model and return it
        event.id = str(result.inserted_id)
        return event

    async def get_all_events(self) -> List[EventDocument]:
        # Fetch everything, convert the raw BSON dictionaries back into Pydantic models
        events = []
        cursor = self.collection.find({})
        async for document in cursor:
            # Convert ObjectId to string so Pydantic can read it
            document["_id"] = str(document["_id"]) 
            events.append(EventDocument(**document))
        return events