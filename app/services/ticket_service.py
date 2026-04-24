from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import redis_client, mongo_db
from app.models.sql_models import TicketOwnership
from app.models.schemas import TicketPurchase
from bson import ObjectId
import uuid

class TicketService:
    @staticmethod
    async def purchase_ticket(purchase: TicketPurchase, db: AsyncSession) -> TicketOwnership:
        # 1. Check if Event Exists in MongoDB
        event = await mongo_db.events.find_one({"_id": ObjectId(purchase.event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Find the requested tier and its price
        target_tier = None
        for tier in event.get("ticket_tiers", []):
            if tier["tier_name"] == purchase.tier_name:
                target_tier = tier
                break
                
        if not target_tier:
            raise HTTPException(status_code=400, detail="Invalid ticket tier")

        # 2. THE REDIS MAGIC (Atomic Decrement)
        # We create a unique Redis key for this specific event and tier
        redis_key = f"event:{purchase.event_id}:tier:{purchase.tier_name}:available"
        
        # We ask Redis to subtract 1 from the available seats. 
        # Redis is single-threaded, meaning it processes this one-by-one safely!
        seats_left = await redis_client.decr(redis_key)

        if seats_left < 0:
            # Too late! Put the counter back to 0 and reject the user
            await redis_client.incr(redis_key)
            raise HTTPException(status_code=400, detail="SOLD OUT!")

        # 3. SUCCESS! Generate a seat number and save to PostgreSQL
        seat_num = f"{purchase.tier_name[:3].upper()}-{str(uuid.uuid4())[:6]}"
        
        new_ticket = TicketOwnership(
            user_id=purchase.user_id,
            event_id=purchase.event_id,
            seat_number=seat_num,
            price_paid=target_tier["price_cents"]
        )
        
        db.add(new_ticket)
        await db.commit()
        await db.refresh(new_ticket)

        return new_ticket