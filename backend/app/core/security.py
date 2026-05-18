from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from app.core.config import get_settings, Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain: str, hashed_or_plain: str) -> bool:
    if hashed_or_plain.startswith("$2"):
        return pwd_context.verify(plain, hashed_or_plain)
    return plain == hashed_or_plain


def create_access_token(subject: str, expires_minutes: int = 720) -> str:
    settings = get_settings()
    payload = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.app_secret_key, algorithm="HS256")


def verify_google_credential(credential: str, settings: Settings) -> str:
    if not settings.google_oauth_client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google login is not configured")
    try:
        payload = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_oauth_client_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential") from exc
    email = str(payload.get("email") or "").lower()
    if not email or not payload.get("email_verified"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google email is not verified")
    if email != settings.dashboard_admin_email.lower():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google account is not allowed")
    return email


def get_current_user(token: str = Depends(oauth2_scheme), settings: Settings = Depends(get_settings)) -> str:
    try:
        payload = jwt.decode(token, settings.app_secret_key, algorithms=["HS256"])
        user = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if user.lower() != settings.dashboard_admin_email.lower():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return user
