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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    subscription_tier: str
    
class Token(BaseModel):
    access_token: str
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
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
        
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "subscription_tier": "FREE",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        
        # Create token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "email": user_data.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {"id": user_id, "email": user_data.email, "subscription_tier": "FREE"}
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
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": user["id"], 
                "email": user["email"],
                "subscription_tier": user.get("subscription_tier", "FREE")
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Erreur login")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la connexion")

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
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            g_requests.Request(),
            settings.google_client_id,
            clock_skew_in_seconds=10
        )
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
                "created_at": datetime.utcnow()
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
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user_id, "email": email, "subscription_tier": tier}
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Erreur oauth google")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de l'authentification Google")
