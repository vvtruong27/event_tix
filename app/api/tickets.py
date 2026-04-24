"""Ticket purchasing HTTP endpoints.

Handles the high-concurrency purchasing flow utilizing Redis for atomic 
locks and PostgreSQL for permanent receipts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import TicketPurchase, TicketResponse
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/buy", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def buy_ticket(purchase: TicketPurchase, db: AsyncSession = Depends(get_db)):
    """Purchase a ticket with atomic concurrency protection."""
    try:
        # Hand off the logic to our dedicated service
        ticket = await TicketService.purchase_ticket(purchase, db)
        return ticket
    except HTTPException as e:
        # Re-raise intended HTTP errors (like 400 SOLD OUT or 404 Not Found)
        raise e 
    except Exception as e:
        # Catch any unexpected server crashes
        raise HTTPException(status_code=500, detail=str(e))