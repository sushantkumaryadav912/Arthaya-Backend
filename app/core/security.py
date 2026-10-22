import os
import json
import jwt
import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

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
            print(f"✅ Firebase Admin SDK initialized with custom credentials for project {settings.FIREBASE_PROJECT_ID}.")
            return True
        elif settings.FIREBASE_PROJECT_ID:
            firebase_admin.initialize_app(options={"projectId": settings.FIREBASE_PROJECT_ID})
            _firebase_initialized = True
            print(f"✅ Firebase Admin SDK initialized for project: {settings.FIREBASE_PROJECT_ID}")
            return True
        else:
            firebase_admin.initialize_app()
            _firebase_initialized = True
            print("✅ Firebase Admin SDK initialized with default credentials.")
            return True
    except Exception as e:
        print(f"⚠️ Firebase Admin initialization notice: {e}")
        return False

# Initialize on module import
init_firebase()


def verify_firebase_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID token sent from the client (Google, Email, GitHub via Firebase).
    Returns decoded token claims (uid, email, name, picture).
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
        raise RuntimeError(f"Firebase Admin SDK could not initialize for project: {settings.FIREBASE_PROJECT_ID}.")

    try:
        decoded_claims = firebase_auth.verify_id_token(id_token, check_revoked=True)
        return decoded_claims
    except Exception as e:
        raise ValueError(f"Invalid or expired Firebase ID token: {str(e)}")


def verify_google_id_token(token: str) -> Dict[str, Any]:
    """
    Verifies a Google OAuth ID token directly (from Google Sign-In on Web or Android).
    Validates token audience against settings.GOOGLE_WEB_CLIENT_ID and settings.GOOGLE_ANDROID_CLIENT_ID.
    """
    if not token:
        raise ValueError("Google ID token must not be empty.")

    if settings.FIREBASE_AUTH_DISABLED or token.startswith("dev-token-") or token == "mock-google-token":
        return {
            "sub": "google_dev_1001",
            "email": "google.trader@arthaya.ai",
            "name": "Google Demo Trader",
            "picture": "https://api.dicebear.com/7.x/bottts/svg?seed=GoogleTrader",
        }

    valid_audiences: List[str] = [
        c for c in [settings.GOOGLE_WEB_CLIENT_ID, settings.GOOGLE_ANDROID_CLIENT_ID] if c
    ]

    try:
        req = google_requests.Request()
        id_info = google_id_token.verify_oauth2_token(token, req)

        # Validate audience if client IDs are configured
        if valid_audiences and id_info.get("aud") not in valid_audiences:
            raise ValueError(f"Google token audience {id_info.get('aud')} does not match configured client IDs.")

        return {
            "sub": id_info["sub"],
            "email": id_info.get("email"),
            "name": id_info.get("name") or id_info.get("email", "").split("@")[0],
            "picture": id_info.get("picture"),
        }
    except Exception as e:
        raise ValueError(f"Invalid Google ID token: {str(e)}")


async def exchange_github_code(code: str) -> Dict[str, Any]:
    """
    Exchanges a GitHub OAuth authorization code for an access token,
    then retrieves user profile information and primary verified email.
    """
    if not code:
        raise ValueError("GitHub authorization code must not be empty.")

    if settings.FIREBASE_AUTH_DISABLED or code.startswith("dev-code-") or code == "mock-github-code":
        return {
            "github_id": "github_dev_2001",
            "email": "github.developer@arthaya.ai",
            "name": "GitHub Demo Trader",
            "picture": "https://api.dicebear.com/7.x/bottts/svg?seed=GitHubTrader",
        }

    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Exchange code for GitHub access token
        resp = await client.post(token_url, json=payload, headers=headers)
        if resp.status_code != 200:
            raise ValueError(f"Failed to exchange GitHub authorization code: {resp.text}")

        token_data = resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            err = token_data.get("error_description") or token_data.get("error") or "No access token returned"
            raise ValueError(f"GitHub OAuth error: {err}")

        auth_header = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github.v3+json"}

        # 2. Fetch user profile
        user_resp = await client.get("https://api.github.com/user", headers=auth_header)
        if user_resp.status_code != 200:
            raise ValueError(f"Failed to fetch GitHub user details: {user_resp.text}")
        user_data = user_resp.json()

        # 3. Fetch user email (if public email is None)
        email = user_data.get("email")
        if not email:
            email_resp = await client.get("https://api.github.com/user/emails", headers=auth_header)
            if email_resp.status_code == 200:
                emails = email_resp.json()
                for item in emails:
                    if item.get("primary") and item.get("verified"):
                        email = item.get("email")
                        break
                if not email and emails:
                    email = emails[0].get("email")

        if not email:
            email = f"{user_data.get('login')}@users.noreply.github.com"

        return {
            "github_id": str(user_data["id"]),
            "email": email,
            "name": user_data.get("name") or user_data.get("login"),
            "picture": user_data.get("avatar_url"),
        }


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
