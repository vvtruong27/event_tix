"""User-related HTTP endpoints.

This module currently exposes account creation (signup) logic and demonstrates
the standard route pattern used in the project: validate input with Pydantic,
query the database asynchronously, and return a response schema.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # <-- ADD THIS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.sql_models import User
from app.models.schemas import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token # <-- UPDATE THIS

# Add TicketOwnership to your existing sql_models import
from app.models.sql_models import User, TicketOwnership 

# Add the new schemas to your existing schemas import
from app.models.schemas import UserCreate, UserResponse, UserProfileResponse, DepositRequest, MyTicketResponse

# Make sure you have get_current_user_id imported from security
from app.core.security import get_current_user_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user account.

    Steps:
    1. Guard against duplicate email addresses.
    2. Hash the provided password before persistence.
    3. Persist and refresh the SQLAlchemy instance.
    4. Return a safe response model that excludes password data.
    """
    # Check uniqueness first to provide a clear conflict-style error.
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Store only a one-way hash, never the raw password.
    hashed_pw = get_password_hash(user_in.password)

    # Build ORM object from validated input payload.
    new_user = User(email=user_in.email, hashed_password=hashed_pw)

    # Persist transaction and reload object to retrieve generated columns (e.g. id).
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # FastAPI serializes ORM object using the declared response_model.
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authenticate a user and return a JWT."""
    
    # 1. Find the user in the database (OAuth2 uses 'username' by default, but we map it to email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    # 2. Check if the user exists AND the password matches
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Success! Generate the token (putting the user's ID inside the "sub" field)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 4. Return it in the exact format FastAPI expects
    return {"access_token": access_token, "token_type": "bearer"}

# --- FRONTEND SUPPORT APIs ---

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    """Fetch the logged-in user's profile and current wallet balance."""
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/me/deposit", response_model=UserProfileResponse)
async def deposit_funds(
    deposit: DepositRequest,
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    """Deposit virtual money into the logged-in user's wallet."""
    if deposit.amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than 0.")

    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Add the money and save to database
    user.balance_cents += deposit.amount_cents
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/me/tickets", response_model=list[MyTicketResponse])
async def get_my_tickets(
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    """View all tickets purchased by the logged-in user."""
    # Query the database for all tickets owned by this specific user
    result = await db.execute(
        select(TicketOwnership).where(TicketOwnership.user_id == current_user_id)
    )
    tickets = result.scalars().all()
    
    return tickets