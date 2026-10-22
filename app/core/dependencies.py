from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy import select

from app.config import settings
from app.core.security import decode_access_token
from app.database import AsyncSessionLocal
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

class AuthenticatedUser(BaseModel):
    id: str
    email: str
    role: str = "user"
    name: Optional[str] = None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> AuthenticatedUser:
    """
    FastAPI dependency to extract and validate application JWT from Authorization header.
    Raises HTTP 401 Unauthorized if token is missing, invalid, or expired.
    """
    if not credentials or not credentials.credentials:
        if settings.FIREBASE_AUTH_DISABLED:
            return AuthenticatedUser(
                id="dev_trader_001",
                email="trader@arthaya.ai",
                role="admin",
                name="Arthaya Dev Trader"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid. Format must be: Bearer <jwt_token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed JWT payload: missing subject or email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedUser(
        id=user_id,
        email=email,
        role=payload.get("role", "user"),
        name=payload.get("name")
    )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[AuthenticatedUser]:
    """Optional authentication dependency. Returns None if unauthenticated instead of raising 401."""
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id and email:
            return AuthenticatedUser(
                id=user_id,
                email=email,
                role=payload.get("role", "user"),
                name=payload.get("name")
            )
    except Exception:
        pass
    return None
