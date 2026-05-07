"""
Auth routes
POST /auth/register
POST /auth/login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, create_access_token, verify_password
from app.models.user import User
from app.schemas.content import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.core.exceptions import UserAlreadyExists, InvalidCredentials
from uuid import uuid4
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )
    
    # Create user
    user = User(
        id=str(uuid4()),
        email=request.email,
        password_hash=hash_password(request.password),
        subscription_status="free"
    )
    
    db.add(user)
    await db.commit()
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(hours=24)
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    
    # Get user
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(hours=24)
    )
    
    return TokenResponse(access_token=access_token)
