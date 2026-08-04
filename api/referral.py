from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import random
import string
from loguru import logger

from core.database import get_db
from api.auth import get_current_user

router = APIRouter(prefix="/api/referral", tags=["Referral & Viral Growth"])

def generate_referral_code(prefix: str = "GOLD") -> str:
    """Generates a unique 7-character referral code (e.g. GOLD92A)."""
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{random_chars}"

class ShareAction(BaseModel):
    platform: str  # linkedin, whatsapp, email, copy_link

@router.get("/stats")
async def get_referral_stats(current_user: dict = Depends(get_current_user)):
    """Returns referral stats for current user and ensures they have a referral code."""
    db = get_db()
    user_id = current_user["id"]

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    referral_code = user.get("referral_code")
    if not referral_code:
        # Generate unique referral code if missing
        for _ in range(10):
            candidate_code = generate_referral_code()
            exists = await db.users.find_one({"referral_code": candidate_code})
            if not exists:
                referral_code = candidate_code
                break
        if not referral_code:
            referral_code = f"GOLD{uuid.uuid4().hex[:4].upper()}"

        await db.users.update_one(
            {"id": user_id},
            {"$set": {"referral_code": referral_code}}
        )

    # Fetch referral records
    referral_cursor = db.referrals.find({"referrer_id": user_id})
    referrals_list = await referral_cursor.to_list(length=100)

    total_referrals = len(referrals_list)
    credits_earned = sum(r.get("credits_granted", 15) for r in referrals_list)

    # Format list of friends referred (anonymized email)
    referred_friends = []
    for ref in referrals_list:
        email = ref.get("referred_email", "Utilisateur")
        parts = email.split("@")
        masked_email = f"{parts[0][:3]}***@{parts[1]}" if len(parts) == 2 else "Ami GoldArmy"
        referred_friends.append({
            "id": ref.get("id"),
            "masked_email": masked_email,
            "date": ref.get("created_at", datetime.now(timezone.utc)).isoformat() if isinstance(ref.get("created_at"), datetime) else str(ref.get("created_at")),
            "status": "Actif",
            "credits_earned": ref.get("credits_granted", 15)
        })

    # Tier rewards calculation
    next_tier = 3
    if total_referrals >= 10:
        tier_label = "Ambassadeur VIP (Illimité)"
    elif total_referrals >= 5:
        tier_label = "Mentor Gold (1 Mois Pro Offert)"
        next_tier = 10
    elif total_referrals >= 3:
        tier_label = "Initié Gold (50 Crédits Bonus)"
        next_tier = 5
    else:
        tier_label = "Débutant"
        next_tier = 3

    share_url = f"https://goldarmyai.com/register?ref={referral_code}"

    return {
        "status": "success",
        "data": {
            "referral_code": referral_code,
            "share_url": share_url,
            "total_referrals": total_referrals,
            "credits_earned": credits_earned,
            "bonus_credits_balance": user.get("bonus_credits", 0),
            "tier_label": tier_label,
            "next_tier_target": next_tier,
            "referred_friends": referred_friends
        }
    }

@router.get("/validate/{code}")
async def validate_referral_code(code: str):
    """Validates a referral code and returns bonus info for the registration page."""
    db = get_db()
    code_upper = code.strip().upper()
    
    referrer = await db.users.find_one({"referral_code": code_upper})
    if not referrer:
        return {
            "valid": False,
            "message": "Code de parrainage non trouvé ou expiré"
        }

    return {
        "valid": True,
        "referral_code": code_upper,
        "bonus_credits": 10,
        "message": "Code valide ! Vous recevrez 10 crédits bonus lors de votre inscription."
    }

@router.post("/share")
async def track_share_action(body: ShareAction, current_user: dict = Depends(get_current_user)):
    """Logs viral share analytics for optimization."""
    db = get_db()
    await db.viral_shares.insert_one({
        "user_id": current_user["id"],
        "platform": body.platform,
        "created_at": datetime.now(timezone.utc)
    })
    return {"status": "success", "message": f"Partage {body.platform} enregistré"}
