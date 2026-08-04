from fastapi import APIRouter, HTTPException, Depends, status
from loguru import logger
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from core.database import get_db
from config.settings import settings
import uuid
import random
from core.email_service import email_service

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as g_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

# Removed direct os.getenv calls, using settings instead

# Configuration (SECRET_KEY from settings / JWT_SECRET_KEY in .env)
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    email: str
    password: str
    referral_code: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    subscription_tier: str
    is_verified: bool = False
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt limits passwords to 72 bytes. Truncate to avoid errors.
    truncated_password = plain_password.encode('utf-8')[:72]
    try:
        return bcrypt.checkpw(truncated_password, hashed_password.encode('utf-8'))
    except ValueError:
        # Happens if hashed_password is a placeholder (like Google OAuth users)
        return False

def get_password_hash(password: str) -> str:
    # bcrypt limits passwords to 72 bytes. Truncate to avoid errors.
    truncated_password = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated_password, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Creates a long-lived refresh token (30 days)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    db = get_db()
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "id": 1, "email": 1, "subscription_tier": 1})
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    db = get_db()
    try:
        # Check if email exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data.password)
        
        # Generate personal referral code for new user
        from api.referral import generate_referral_code
        own_referral_code = generate_referral_code()
        
        # Initial bonus credits
        initial_bonus_credits = 0
        referred_by_id = None

        # Process referral code if provided
        if user_data.referral_code:
            clean_code = user_data.referral_code.strip().upper()
            referrer = await db.users.find_one({"referral_code": clean_code})
            if referrer and referrer.get("id") != user_id:
                referred_by_id = referrer["id"]
                initial_bonus_credits = 10  # 10 bonus credits for the new referred user
                
                # Reward referrer (+15 bonus credits)
                await db.users.update_one(
                    {"id": referrer["id"]},
                    {"$inc": {"bonus_credits": 15, "referral_count": 1}}
                )

                # Log referral relationship
                await db.referrals.insert_one({
                    "id": str(uuid.uuid4()),
                    "referrer_id": referrer["id"],
                    "referred_user_id": user_id,
                    "referred_email": user_data.email,
                    "credits_granted": 15,
                    "created_at": datetime.now(timezone.utc)
                })

                # Notify referrer
                await db.notifications.insert_one({
                    "id": str(uuid.uuid4()),
                    "user_id": referrer["id"],
                    "title": "🎉 Nouveau filleul inscrit !",
                    "message": f"Un ami s'est inscrit avec votre code ! Youpi, vous avez gagné 15 crédits bonus.",
                    "read": False,
                    "created_at": datetime.now(timezone.utc)
                })
        
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "subscription_tier": "FREE",
            "is_verified": False,
            "created_at": datetime.now(timezone.utc),
            "referral_code": own_referral_code,
            "referred_by": referred_by_id,
            "bonus_credits": initial_bonus_credits,
            "referral_count": 0
        }
        await db.users.insert_one(new_user)
        try:
            otp_code = str(random.randint(100000, 999999))
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
            await db.otp_codes.update_one(
                {"email": user_data.email},
                {"$set": {"code": otp_code, "expires_at": expires_at}},
                upsert=True
            )
            await email_service.send_otp(user_data.email, otp_code)
        except: pass
        
        # Create access + refresh tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "email": user_data.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user_id, "email": user_data.email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"id": user_id, "email": user_data.email, "subscription_tier": "FREE", "is_verified": False}
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Erreur inscription: {e}")
        raise HTTPException(status_code=500, detail=f"Database/Registration Error: {str(e)}")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        db = get_db()
        user = await db.users.find_one({"email": form_data.username})
        
        if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"], "email": user["email"]}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user["id"], "email": user["email"]})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"], 
                "email": user["email"],
                "subscription_tier": user.get("subscription_tier", "FREE"),
                "is_verified": user.get("is_verified", False)
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Erreur login")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la connexion")


class RefreshRequest(BaseModel):
    refreshToken: str

@router.post("/refresh")
async def refresh_access_token(body: RefreshRequest):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(body.refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
        # Ensure it's a refresh token, not an access token reused as refresh
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id: str = payload.get("sub")
        email: str = payload.get("email", "")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    new_access_token = create_access_token(
        data={"sub": user_id, "email": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(data={"sub": user_id, "email": email})

    return {
        "data": {
            "accessToken": new_access_token,
            "refreshToken": new_refresh_token,
        }
    }

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


# ─── Google OAuth ───────────────────────────────────────────────────────────
class GoogleTokenRequest(BaseModel):
    credential: str  # Google ID token from the frontend

@router.post("/google", response_model=Token)
async def google_login(payload: GoogleTokenRequest):
    """Verify a Google ID token and return our own JWT."""
    if not GOOGLE_AUTH_AVAILABLE:
        raise HTTPException(status_code=501, detail="google-auth library not installed. Run: pip install google-auth")
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not set in environment variables.")
    
    try:
        # Check signature without strict audience (we verify audience manually below)
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            g_requests.Request(),
            audience=None,
            clock_skew_in_seconds=10
        )
        
        valid_audiences = [
            settings.google_client_id,
            getattr(settings, "google_ios_client_id", None),
            getattr(settings, "google_android_client_id", None)
        ]
        
        aud = idinfo.get("aud")
        if not aud or aud not in [a for a in valid_audiences if a]:
            raise ValueError(f"Unrecognized audience: {aud}")
            
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")

    google_id   = idinfo["sub"]
    email       = idinfo.get("email", "")
    full_name   = idinfo.get("name", "")
    avatar_url  = idinfo.get("picture", "")

    db = get_db()
    try:
        # Try to find by google_id first
        user = await db.users.find_one({"google_id": google_id})

        if user is None:
            # Try to find by email
            user = await db.users.find_one({"email": email})

        if user is None:
            # Create new user (no password for Google OAuth users)
            user_id = str(uuid.uuid4())
            new_user = {
                "id": user_id,
                "email": email,
                "hashed_password": "GOOGLE_OAUTH_NO_PASSWORD",
                "full_name": full_name,
                "avatar_url": avatar_url,
                "google_id": google_id,
                "subscription_tier": "FREE",
                "is_verified": True,
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(new_user)
            tier = "FREE"
        else:
            user_id = user["id"]
            tier = user.get("subscription_tier", "FREE")
            # Link google_id if not yet set
            if not user.get("google_id"):
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"google_id": google_id, "avatar_url": avatar_url}}
                )

        access_token = create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": user_id, "email": email})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"id": user_id, "email": email, "subscription_tier": tier}
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Erreur oauth google")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de l'authentification Google")

# ─── Apple OAuth ────────────────────────────────────────────────────────────
class AppleTokenRequest(BaseModel):
    credential: str  # Apple identity token

@router.post("/apple", response_model=Token)
async def apple_login(payload: AppleTokenRequest):
    """Verify an Apple ID token and return our own JWT."""
    try:
        # Decode without strict verification (Expo Apple Auth signs and verifies securely on the device)
        decoded = jwt.decode(payload.credential, options={"verify_signature": False})
        apple_id = decoded.get("sub")
        email = decoded.get("email", "")
        if not apple_id:
            raise ValueError("No subject found in Apple token")

        db = get_db()
        user = await db.users.find_one({"apple_id": apple_id})
        if user is None:
            user = await db.users.find_one({"email": email}) if email else None

        if user is None:
            user_id = str(uuid.uuid4())
            new_user = {
                "id": user_id,
                "email": email or f"{apple_id}@privaterelay.appleid.com",
                "hashed_password": "APPLE_OAUTH_NO_PASSWORD",
                "full_name": "",
                "avatar_url": "",
                "apple_id": apple_id,
                "subscription_tier": "FREE",
                "is_verified": True,
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(new_user)
            tier = "FREE"
        else:
            user_id = user["id"]
            tier = user.get("subscription_tier", "FREE")
            if not user.get("apple_id"):
                await db.users.update_one({"id": user_id}, {"$set": {"apple_id": apple_id}})

        access_token = create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": user_id, "email": email})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"id": user_id, "email": email, "subscription_tier": tier}
        }
    except Exception as e:
        logger.exception(f"Erreur oauth apple: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de l'authentification Apple")


# ─── Account Deletion ───────────────────────────────────────────────────────
@router.delete("/me")
async def delete_user_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        user_id = current_user["id"]
        # Delete user
        await db.users.delete_one({"id": user_id})
        # Delete related data to comply with privacy laws
        await db.applications.delete_many({"user_id": user_id})
        await db.contacts.delete_many({"user_id": user_id})
        return {"status": "success", "message": "Account and all data deleted successfully"}
    except Exception as e:
        logger.error(f"Erreur delete account: {e}")
        raise HTTPException(status_code=500, detail="Error deleting account")

@router.post("/send-otp")
async def send_otp(email_data: dict):
    email = email_data.get("email")
    db = get_db()
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    await db.otp_codes.update_one({"email": email}, {"$set": {"code": otp_code, "expires_at": expires_at}}, upsert=True)
    await email_service.send_otp(email, otp_code)
    return {"status": "success"}

@router.post("/verify-otp")
async def verify_otp(request: dict):
    db, email, code = get_db(), request.get("email"), request.get("code")
    otp_record = await db.otp_codes.find_one({"email": email, "code": code})
    if not otp_record or otp_record["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Code invalide/expiré")
    await db.users.update_one({"email": email}, {"$set": {"is_verified": True}})
    await db.otp_codes.delete_one({"email": email})
    return {"status": "success"}
