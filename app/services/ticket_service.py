from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import redis_client, mongo_db
from app.models.sql_models import TicketOwnership, User
from app.models.schemas import TicketPurchase
from sqlalchemy.future import select
from bson import ObjectId
import uuid

class TicketService:
    @staticmethod
    async def purchase_ticket(purchase: TicketPurchase, db: AsyncSession):
        # 1. Fetch Event & Get Ticket Price from MongoDB
        event = await mongo_db.events.find_one({"_id": ObjectId(purchase.event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
            
        tier = next((t for t in event["ticket_tiers"] if t["tier_name"] == purchase.tier_name), None)
        if not tier:
            raise HTTPException(status_code=400, detail="Invalid ticket tier")
            
        ticket_price = tier["price_cents"]

        # 2. The Bank Check (PostgreSQL Row-Level Lock)
        # We lock the user row so they can't double-spend in parallel requests!
        result = await db.execute(
            select(User).where(User.id == purchase.user_id).with_for_update()
        )
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.balance_cents < ticket_price:
            raise HTTPException(status_code=400, detail="Insufficient funds in wallet!")

        # 3. The Bouncer (Redis)
        redis_key = f"event:{purchase.event_id}:tier:{purchase.tier_name}:available"
        seats_left = await redis_client.decr(redis_key)
        
        if seats_left < 0:
            await redis_client.incr(redis_key) # Put it back
            raise HTTPException(status_code=400, detail="SOLD OUT!")

        # 4. The Receipt & Payment (PostgreSQL Atomic Transaction)
        try:
            # Deduct the money
            user.balance_cents -= ticket_price
            
            # Generate the ticket
            seat_num = f"{purchase.tier_name[:3].upper()}-{str(uuid.uuid4())[:6]}"
            new_ticket = TicketOwnership(
                user_id=purchase.user_id,
                event_id=purchase.event_id,
                tier_name=purchase.tier_name,
                seat_number=seat_num,
                price_paid=ticket_price # <--- ADD THIS LINE!
            )
            db.add(new_ticket)
            
            # Commit BOTH the balance deduction and ticket creation at the exact same time
            await db.commit() 
            await db.refresh(new_ticket)
            return new_ticket
            
        except Exception as e:
            # If the database crashes here, refund the Redis ticket so it isn't lost!
            await redis_client.incr(redis_key)
            await db.rollback()
            raise HTTPException(status_code=500, detail="Transaction failed, refunded.")
