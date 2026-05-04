"""Ticket purchasing HTTP endpoints.

Handles the high-concurrency purchasing flow utilizing Redis for atomic 
locks and PostgreSQL for permanent receipts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import TicketPurchase, TicketResponse
from app.services.ticket_service import TicketService
from app.core.security import get_current_user_id

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/buy", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def buy_ticket(
    purchase: TicketPurchase, 
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id) # <-- 2. ADD THE GUARD!
):
    """Purchase a ticket with atomic concurrency protection."""
    
    # 3. SECURITY CHECK: Make sure the logged-in user isn't trying to buy a ticket for someone else's ID!
    if purchase.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only buy tickets for your own account.")

    try:
        ticket = await TicketService.purchase_ticket(purchase, db)
        return ticket
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))