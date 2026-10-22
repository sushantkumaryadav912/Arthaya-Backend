from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
import uuid

from app.core.security import verify_firebase_id_token, create_access_token
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.database import AsyncSessionLocal
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

class FirebaseLoginRequest(BaseModel):
    id_token: str

class DevLoginRequest(BaseModel):
    email: Optional[str] = "trader@arthaya.ai"
    name: Optional[str] = "Arthaya Demo Trader"
    role: Optional[str] = "user"

@router.post("/firebase-login")
async def firebase_login(req: FirebaseLoginRequest):
    """
    Exchanges a Firebase ID token (from client-side Firebase Auth)
    for a signed Arthaya backend JWT access token.
    """
    try:
        claims = verify_firebase_id_token(req.id_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firebase verification error: {str(e)}"
        )

    uid = claims.get("uid")
    email = claims.get("email") or f"{uid}@arthaya.firebase"
    display_name = claims.get("name") or claims.get("displayName") or email.split("@")[0]
    photo_url = claims.get("picture") or claims.get("photoURL")

    # Upsert user record in database
    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    user_role = "user"

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.firebase_uid == uid))
            user = result.scalars().first()

            if user:
                user_id = user.id
                user_role = user.role
                user.last_login_at = datetime.utcnow()
                if display_name:
                    user.display_name = display_name
                if photo_url:
                    user.photo_url = photo_url
            else:
                user = User(
                    id=user_id,
                    firebase_uid=uid,
                    email=email,
                    display_name=display_name,
                    photo_url=photo_url,
                    role="user",
                    created_at=datetime.utcnow(),
                    last_login_at=datetime.utcnow()
                )
                db.add(user)

            await db.commit()
    except Exception as db_err:
        print(f"⚠️ User persistence notice: {db_err}")

    # Generate signed JWT access token using settings.JWT_SECRET
    access_token = create_access_token(
        user_id=user_id,
        email=email,
        role=user_role,
        display_name=display_name
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
            "name": display_name,
            "picture": photo_url,
            "role": user_role
        }
    }

@router.post("/dev-login")
async def dev_login(req: DevLoginRequest):
    """
    Developer login endpoint for local testing and demonstration.
    Mints a valid application JWT without requiring live Firebase client setup.
    """
    user_id = f"dev_{uuid.uuid4().hex[:8]}"
    email = req.email or "trader@arthaya.ai"
    name = req.name or "Arthaya Demo Trader"
    role = req.role or "user"

    access_token = create_access_token(
        user_id=user_id,
        email=email,
        role=role,
        display_name=name
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
            "name": name,
            "picture": "https://api.dicebear.com/7.x/bottts/svg?seed=ArthayaTrader",
            "role": role,
            "is_dev": True
        }
    }

@router.get("/me")
async def get_current_user_profile(user: AuthenticatedUser = Depends(get_current_user)):
    """Returns the authenticated user profile verified by the JWT secret."""
    user_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.name or user.email.split("@")[0],
    }

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user.id))
            db_user = result.scalars().first()
            if db_user:
                user_data["picture"] = db_user.photo_url
                user_data["created_at"] = db_user.created_at.isoformat() if db_user.created_at else None
    except Exception:
        pass

    return {"user": user_data, "authenticated": True}
