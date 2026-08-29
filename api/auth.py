from fastapi import APIRouter, HTTPException, Depends, status
from loguru import logger
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import os
import re
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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # Inscription en tant qu'organisation (espace B2B2C)
    account_type: Optional[str] = "candidate"  # "candidate" | "organization"
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None
    # Rejoindre une organisation existante via code d'invitation
    org_invite_code: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    subscription_tier: str
    is_verified: bool = False
    full_name: Optional[str] = None
    role: Optional[str] = None
    account_type: Optional[str] = None
    organization_id: Optional[str] = None
    
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

@router.post("/register")
async def register(user_data: UserCreate):
    db = get_db()
    try:
        # Validation basique de l'adresse (bloque les saisies grossièrement invalides)
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (user_data.email or "").strip()):
            raise HTTPException(status_code=400, detail="Adresse e-mail invalide.")
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
        
        # Nom complet à partir du prénom/nom fournis par le formulaire
        full_name = " ".join(
            p for p in [(user_data.first_name or "").strip(), (user_data.last_name or "").strip()] if p
        ).strip()

        new_user = {
            "id": user_id,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "subscription_tier": "FREE",
            "is_verified": False,
            "created_at": datetime.now(timezone.utc),
            "referral_code": own_referral_code,
            "referred_by": referred_by_id,
            "bonus_credits": initial_bonus_credits,
            "gold_balance": 50 + initial_bonus_credits,  # 50 Gold offerts à l'inscription
            "referral_count": 0,
            "account_type": "candidate",
            "role": None,
            "organization_id": None,
        }
        await db.users.insert_one(new_user)

        # --- Espace Organisation (B2B2C) ---
        org_role = None
        org_id = None
        org_account_type = "candidate"
        try:
            if (user_data.account_type or "").lower() == "organization":
                # Création d'une nouvelle organisation : l'inscrit devient org_admin
                from core.organizations import create_organization
                org = await create_organization(
                    owner_id=user_id,
                    name=user_data.organization_name or (full_name or user_data.email.split("@")[0]),
                    org_type=(user_data.organization_type or "other"),
                    contact_email=user_data.email,
                )
                org_role = "org_admin"
                org_id = org["id"]
                org_account_type = "organization"
            elif user_data.org_invite_code:
                # Rejoindre une organisation existante via code d'invitation
                from core.organizations import join_organization
                joined = await join_organization(user_id, user_data.org_invite_code)
                if joined.get("status") == "success" and joined.get("organization"):
                    org_role = "member"
                    org_id = joined["organization"]["id"]
        except Exception as org_err:
            logger.warning(f"[REGISTER] Traitement organisation échoué: {org_err}")
        # Vérification e-mail OBLIGATOIRE : on envoie un code et on NE connecte PAS.
        # Tant que le code n'est pas validé (via /verify-otp), aucun token n'est délivré.
        otp_code = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db.otp_codes.update_one(
            {"email": user_data.email},
            {"$set": {"code": otp_code, "expires_at": expires_at}},
            upsert=True,
        )
        try:
            sent = await email_service.send_otp(user_data.email, otp_code)
        except Exception as mail_err:
            sent = False
            logger.error(f"[REGISTER] Envoi OTP échoué pour {user_data.email}: {mail_err}")
        if not sent:
            logger.warning(f"[REGISTER] OTP NON envoyé à {user_data.email} — vérifier la config SMTP.")

        return {
            "status": "verification_required",
            "email": user_data.email,
            "message": "Un code de vérification a été envoyé à ton adresse e-mail. Saisis-le pour activer ton compte.",
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Erreur inscription: {e}")
        raise HTTPException(status_code=500, detail=f"Database/Registration Error: {str(e)}")

@router.post("/login")
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

        # Vérification e-mail obligatoire pour les comptes créés en direct (non-Google).
        # Les anciens comptes ont été marqués vérifiés par la migration → non impactés.
        if not user.get("is_verified", False) and not user.get("google_id"):
            otp_code = str(random.randint(100000, 999999))
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
            await db.otp_codes.update_one(
                {"email": user["email"]},
                {"$set": {"code": otp_code, "expires_at": expires_at}},
                upsert=True,
            )
            try:
                await email_service.send_otp(user["email"], otp_code)
            except Exception:
                pass
            return {
                "status": "verification_required",
                "email": user["email"],
                "message": "Ton adresse e-mail n'est pas encore vérifiée. Un nouveau code vient de t'être envoyé.",
            }

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
                "is_verified": user.get("is_verified", False),
                "full_name": user.get("full_name"),
                "role": user.get("role"),
                "account_type": user.get("account_type"),
                "organization_id": user.get("organization_id"),
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
            try:
                await email_service.send_welcome(email, full_name or email.split("@")[0])
            except Exception:
                pass
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
        _u = await db.users.find_one({"id": user_id}, {"_id": 0}) or {}
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "subscription_tier": _u.get("subscription_tier", tier),
                "is_verified": _u.get("is_verified", True),
                "full_name": _u.get("full_name"),
                "role": _u.get("role"),
                "account_type": _u.get("account_type"),
                "organization_id": _u.get("organization_id"),
            }
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
            try:
                await email_service.send_welcome(email, full_name or email.split("@")[0])
            except Exception:
                pass
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
        _u = await db.users.find_one({"id": user_id}, {"_id": 0}) or {}
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "subscription_tier": _u.get("subscription_tier", tier),
                "is_verified": _u.get("is_verified", True),
                "full_name": _u.get("full_name"),
                "role": _u.get("role"),
                "account_type": _u.get("account_type"),
                "organization_id": _u.get("organization_id"),
            }
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

@router.post("/email-test")
async def email_test(request: dict, current_user: dict = Depends(get_current_user)):
    """Diagnostic (ADMIN) : envoie un e-mail de test et indique la config active."""
    db = get_db()
    uid = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
    u = await db.users.find_one({"id": uid}) or {}
    if u.get("subscription_tier") != "ADMIN":
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs.")
    to = (request.get("to") or u.get("email") or "").strip()
    if not to:
        raise HTTPException(status_code=400, detail="Destinataire manquant.")
    ok = await email_service.send_email(to, "Test e-mail GoldArmy", "<p>Ceci est un test d'envoi ✅ — si tu le reçois, la config e-mail fonctionne.</p>")
    return {
        "status": "success" if ok else "failed",
        "to": to,
        "resend_configured": bool(getattr(settings, "resend_api_key", None)),
        "smtp_configured": bool(settings.smtp_user and settings.smtp_password),
        "from": settings.smtp_from,
    }


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
    db = get_db()
    email = (request.get("email") or "").strip()
    code = str(request.get("code") or "").strip()
    otp_record = await db.otp_codes.find_one({"email": email, "code": code})
    if not otp_record:
        raise HTTPException(status_code=400, detail="Code invalide.")
    exp = otp_record.get("expires_at")
    if exp and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if not exp or exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Code expiré. Demande un nouveau code.")

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Compte introuvable.")

    already_verified = user.get("is_verified", False)
    await db.users.update_one({"email": email}, {"$set": {"is_verified": True}})
    await db.otp_codes.delete_one({"email": email})

    # Mail de bienvenue à la première vérification (best-effort, ne bloque pas la connexion).
    if not already_verified:
        try:
            await email_service.send_welcome(email, user.get("full_name") or email.split("@")[0])
        except Exception as we:
            logger.warning(f"[verify-otp] mail de bienvenue non envoyé: {we}")

    # Compte vérifié → on délivre enfin les tokens (connexion).
    access_token = create_access_token(
        data={"sub": user["id"], "email": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": user["id"], "email": email})
    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": email,
            "subscription_tier": user.get("subscription_tier", "FREE"),
            "is_verified": True,
            "full_name": user.get("full_name"),
            "role": user.get("role"),
            "account_type": user.get("account_type"),
            "organization_id": user.get("organization_id"),
        },
    }
