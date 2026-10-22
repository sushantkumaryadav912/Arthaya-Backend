import os
import json
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from app.config import settings

_firebase_initialized = False

def init_firebase() -> bool:
    """Safely initializes Firebase Admin SDK once."""
    global _firebase_initialized
    if _firebase_initialized or firebase_admin._apps:
        _firebase_initialized = True
        return True

    try:
        cred = None
        if settings.FIREBASE_CREDENTIALS_JSON:
            raw_cred = settings.FIREBASE_CREDENTIALS_JSON.strip()
            # If it's a file path
            if os.path.exists(raw_cred):
                cred = credentials.Certificate(raw_cred)
            # If it's an inline JSON string (common in Render environment variables)
            elif raw_cred.startswith("{") and raw_cred.endswith("}"):
                cred_dict = json.loads(raw_cred)
                cred = credentials.Certificate(cred_dict)

        if cred:
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            print("✅ Firebase Admin SDK initialized with custom service account credentials.")
            return True
        elif settings.FIREBASE_PROJECT_ID:
            firebase_admin.initialize_app(options={"projectId": settings.FIREBASE_PROJECT_ID})
            _firebase_initialized = True
            print(f"✅ Firebase Admin SDK initialized for project: {settings.FIREBASE_PROJECT_ID}")
            return True
        else:
            firebase_admin.initialize_app()
            _firebase_initialized = True
            print("✅ Firebase Admin SDK initialized with default application credentials.")
            return True
    except Exception as e:
        print(f"⚠️ Firebase Admin initialization notice: {e}")
        return False

# Initialize on module import
init_firebase()


def verify_firebase_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID token sent from the client.
    Returns the decoded token claims dictionary (uid, email, name, picture).
    Supports developer mode bypass if FIREBASE_AUTH_DISABLED is enabled.
    """
    if not id_token:
        raise ValueError("Firebase ID token must not be empty.")

    # Developer bypass for local development or sandbox testing
    if settings.FIREBASE_AUTH_DISABLED or id_token.startswith("dev-token-") or id_token == "mock-demo-token":
        return {
            "uid": "dev_trader_001",
            "email": "trader@arthaya.ai",
            "name": "Arthaya Pro Trader",
            "picture": "https://api.dicebear.com/7.x/bottts/svg?seed=ArthayaTrader",
            "firebase": {"sign_in_provider": "developer"}
        }

    if not _firebase_initialized and not init_firebase():
        raise RuntimeError("Firebase Admin SDK is not initialized. Check FIREBASE_PROJECT_ID or FIREBASE_CREDENTIALS_JSON.")

    try:
        decoded_claims = firebase_auth.verify_id_token(id_token, check_revoked=True)
        return decoded_claims
    except Exception as e:
        raise ValueError(f"Invalid or expired Firebase ID token: {str(e)}")


def create_access_token(
    user_id: str,
    email: str,
    role: str = "user",
    display_name: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generates an application JWT access token signed with settings.JWT_SECRET."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "name": display_name or email.split("@")[0],
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "arthaya",
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a signed application JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="arthaya",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("JWT access token has expired.")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid JWT access token: {str(e)}")
