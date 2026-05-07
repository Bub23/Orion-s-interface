"""
API dependencies (shared across routes)
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token


def get_token_from_header(request: Request) -> str:
    """Extract bearer token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    return auth_header[7:]  # Remove "Bearer " prefix


async def get_current_user_id(
    token: str = Depends(get_token_from_header)
) -> str:
    """Extract and validate JWT token"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload.get("sub")
