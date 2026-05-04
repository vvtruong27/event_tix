import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import text

from app.core.database import AsyncSessionLocal, mongo_db, redis_client
from app.models.sql_models import User, TicketOwnership
from app.models.nosql_models import EventDocument, TicketTier
from app.repositories.event_repo import EventRepository
from app.core.security import get_password_hash

async def seed():
    print("🌱 Starting database seed...")

    # 1. Clean databases (Start fresh!)
    print("🧹 Cleaning old data from SQL, Mongo, and Redis...")
    async with AsyncSessionLocal() as db:
        await db.execute(text("TRUNCATE TABLE ticket_ownership CASCADE"))
        await db.execute(text("TRUNCATE TABLE users CASCADE"))
        # Reset ID counters back to 1
        await db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
        await db.execute(text("ALTER SEQUENCE ticket_ownership_id_seq RESTART WITH 1"))
        await db.commit()
        
    await mongo_db.events.delete_many({})
    await redis_client.flushdb()

    # 2. Seed Users
    print("👤 Creating test users...")
    async with AsyncSessionLocal() as db:
        # We give them a simple, standard password for testing
        user1 = User(email="alice@test.com", hashed_password=get_password_hash("password123"))
        user2 = User(email="bob@test.com", hashed_password=get_password_hash("password123"))
        db.add_all([user1, user2])
        await db.commit()
        await db.refresh(user1)
        await db.refresh(user2)
        print(f"  -> Created User: {user1.email} (ID: {user1.id})")
        print(f"  -> Created User: {user2.email} (ID: {user2.id})")

    # 3. Seed Events
    print("🎟️ Creating test events...")
    repo = EventRepository(mongo_db)
    
    event1 = EventDocument(
        title="Taylor Swift: The Eras Tour",
        description="The biggest tour in history.",
        artist="Taylor Swift",
        venue="My Dinh National Stadium",
        event_date=datetime.now(timezone.utc) + timedelta(days=60), # 60 days from now
        ticket_tiers=[
            TicketTier(tier_name="VIP Floor", price_cents=50000, total_capacity=500, available_seats=500),
            TicketTier(tier_name="General Admission", price_cents=15000, total_capacity=5000, available_seats=5000)
        ]
    )
    
    # Using repo.create_event automatically saves to MongoDB AND stocks Redis!
    created_event = await repo.create_event(event1)
    print(f"  -> Created Event: '{created_event.title}'")
    print(f"     (Event ID: {created_event.id})")

    print("\n✅ Database successfully seeded! You can now test the API.")

if __name__ == "__main__":
    # Run the async seed function
    asyncio.run(seed())