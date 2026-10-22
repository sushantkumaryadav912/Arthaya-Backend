from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, or_
import uuid

from app.config import settings
from app.core.security import (
    verify_firebase_id_token,
    verify_google_id_token,
    exchange_github_code,
    create_access_token
)
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.database import AsyncSessionLocal
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

class TokenExchangeRequest(BaseModel):
    id_token: str

class GitHubAuthRequest(BaseModel):
    code: str

class DevLoginRequest(BaseModel):
    email: Optional[str] = "trader@arthaya.ai"
    name: Optional[str] = "Arthaya Demo Trader"
    role: Optional[str] = "user"


async def _upsert_user(
    email: str,
    display_name: Optional[str] = None,
    photo_url: Optional[str] = None,
    firebase_uid: Optional[str] = None,
    google_id: Optional[str] = None,
    github_id: Optional[str] = None,
    provider: str = "firebase"
) -> Dict[str, Any]:
    """Helper to persist or update user profile and return user dict."""
    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    user_role = "user"

    try:
        async with AsyncSessionLocal() as db:
            # Match existing user by provider ID or email
            conditions = [User.email == email]
            if firebase_uid:
                conditions.append(User.firebase_uid == firebase_uid)
            if google_id:
                conditions.append(User.google_id == google_id)
            if github_id:
                conditions.append(User.github_id == github_id)

            result = await db.execute(select(User).where(or_(*conditions)))
            user = result.scalars().first()

            if user:
                user_id = user.id
                user_role = user.role
                user.last_login_at = datetime.utcnow()
                if display_name and not user.display_name:
                    user.display_name = display_name
                if photo_url and not user.photo_url:
                    user.photo_url = photo_url
                if firebase_uid and not user.firebase_uid:
                    user.firebase_uid = firebase_uid
                if google_id and not user.google_id:
                    user.google_id = google_id
                if github_id and not user.github_id:
                    user.github_id = github_id
            else:
                user = User(
                    id=user_id,
                    firebase_uid=firebase_uid,
                    google_id=google_id,
                    github_id=github_id,
                    provider=provider,
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

    # Create signed application JWT
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
            "role": user_role,
            "provider": provider
        }
    }


@router.post("/firebase-login")
async def firebase_login(req: TokenExchangeRequest):
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

    return await _upsert_user(
        email=email,
        display_name=display_name,
        photo_url=photo_url,
        firebase_uid=uid,
        provider="firebase"
    )


@router.post("/google")
async def google_login(req: TokenExchangeRequest):
    """
    Direct Google OAuth ID Token verification endpoint.
    Exchanges a Google Web/Android ID token for a signed Arthaya backend JWT.
    """
    try:
        info = verify_google_id_token(req.id_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    google_sub = info.get("sub")
    email = info.get("email") or f"google_{google_sub}@arthaya.oauth"
    name = info.get("name")
    picture = info.get("picture")

    return await _upsert_user(
        email=email,
        display_name=name,
        photo_url=picture,
        google_id=google_sub,
        provider="google"
    )


@router.post("/github")
async def github_login(req: GitHubAuthRequest):
    """
    GitHub OAuth authentication endpoint.
    Exchanges an authorization code from GitHub OAuth redirect for a user session and JWT.
    """
    try:
        gh_user = await exchange_github_code(req.code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub OAuth error: {str(e)}"
        )

    github_id = gh_user.get("github_id")
    email = gh_user.get("email")
    name = gh_user.get("name")
    picture = gh_user.get("picture")

    return await _upsert_user(
        email=email,
        display_name=name,
        photo_url=picture,
        github_id=github_id,
        provider="github"
    )


@router.get("/oauth-config")
async def get_oauth_config():
    """Returns public client IDs and project identifiers for frontend configuration."""
    return {
        "firebase": {
            "projectId": settings.FIREBASE_PROJECT_ID,
            "authDomain": f"{settings.FIREBASE_PROJECT_ID}.firebaseapp.com",
            "storageBucket": f"{settings.FIREBASE_PROJECT_ID}.firebasestorage.app",
        },
        "google": {
            "webClientId": settings.GOOGLE_WEB_CLIENT_ID,
            "androidClientId": settings.GOOGLE_ANDROID_CLIENT_ID,
        },
        "github": {
            "clientId": settings.GITHUB_CLIENT_ID,
            "authorizeUrl": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope=user:email",
        }
    }


@router.post("/dev-login")
async def dev_login(req: DevLoginRequest):
    """Developer login endpoint for local testing and demonstration."""
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
            "provider": "dev",
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
                user_data["provider"] = db_user.provider
                user_data["created_at"] = db_user.created_at.isoformat() if db_user.created_at else None
    except Exception:
        pass

    return {"user": user_data, "authenticated": True}
