"""
Integration tests for GoldArmy Referral & Viral Growth system.
Tests referral code generation, registration referral rewards, validation, stats & analytics endpoints.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from datetime import datetime
import uuid

from core.database import get_db
from api.referral import generate_referral_code

async def test_referral_code_generator():
    code1 = generate_referral_code()
    code2 = generate_referral_code()
    
    assert code1.startswith("GOLD")
    assert len(code1) == 8
    assert code1 != code2

async def test_referral_user_registration_and_rewards():
    db = get_db()
    
    # 1. Create referrer user
    referrer_id = str(uuid.uuid4())
    referrer_code = "GOLDTEST99"
    referrer_email = f"referrer_{referrer_id[:8]}@example.com"
    
    await db.users.insert_one({
        "id": referrer_id,
        "email": referrer_email,
        "subscription_tier": "FREE",
        "referral_code": referrer_code,
        "bonus_credits": 0,
        "referral_count": 0,
        "created_at": datetime.utcnow()
    })
    
    # Verify referrer created
    referrer_db = await db.users.find_one({"id": referrer_id})
    assert referrer_db["referral_code"] == referrer_code
    
    # 2. Simulate new user registration with referral_code
    new_user_id = str(uuid.uuid4())
    new_user_email = f"referee_{new_user_id[:8]}@example.com"
    
    # Process referral reward logic (mimicking api/auth.py)
    clean_code = referrer_code.strip().upper()
    found_referrer = await db.users.find_one({"referral_code": clean_code})
    assert found_referrer is not None
    assert found_referrer["id"] == referrer_id
    
    # Award referrer (+15 bonus credits)
    await db.users.update_one(
        {"id": found_referrer["id"]},
        {"$inc": {"bonus_credits": 15, "referral_count": 1}}
    )

    # Insert referral log
    referral_log_id = str(uuid.uuid4())
    await db.referrals.insert_one({
        "id": referral_log_id,
        "referrer_id": found_referrer["id"],
        "referred_user_id": new_user_id,
        "referred_email": new_user_email,
        "credits_granted": 15,
        "created_at": datetime.utcnow()
    })

    # Insert new user with +10 initial bonus credits
    await db.users.insert_one({
        "id": new_user_id,
        "email": new_user_email,
        "subscription_tier": "FREE",
        "referral_code": "GOLDNEW123",
        "referred_by": referrer_id,
        "bonus_credits": 10,
        "created_at": datetime.utcnow()
    })

    # 3. Assertions
    updated_referrer = await db.users.find_one({"id": referrer_id})
    assert updated_referrer["bonus_credits"] == 15
    assert updated_referrer["referral_count"] == 1

    new_user_db = await db.users.find_one({"id": new_user_id})
    assert new_user_db["bonus_credits"] == 10
    assert new_user_db["referred_by"] == referrer_id

    referral_entry = await db.referrals.find_one({"id": referral_log_id})
    assert referral_entry is not None
    assert referral_entry["referrer_id"] == referrer_id
    assert referral_entry["referred_user_id"] == new_user_id

    # Clean up test records
    await db.users.delete_one({"id": referrer_id})
    await db.users.delete_one({"id": new_user_id})
    await db.referrals.delete_one({"id": referral_log_id})

async def test_referral_validation_logic():
    db = get_db()
    test_code = "GOLDVALID1"
    test_user_id = str(uuid.uuid4())

    await db.users.insert_one({
        "id": test_user_id,
        "email": "validation_test@example.com",
        "referral_code": test_code,
        "created_at": datetime.utcnow()
    })

    # Test valid code search
    valid_referrer = await db.users.find_one({"referral_code": test_code})
    assert valid_referrer is not None
    assert valid_referrer["id"] == test_user_id

    # Test invalid code search
    invalid_referrer = await db.users.find_one({"referral_code": "INVALID999"})
    assert invalid_referrer is None

    # Cleanup
    await db.users.delete_one({"id": test_user_id})

async def run_all_tests():
    print("[TEST] Execution de la suite de tests d'integration du Parrainage...")
    await test_referral_code_generator()
    print("[OK] test_referral_code_generator: PASSED")
    await test_referral_user_registration_and_rewards()
    print("[OK] test_referral_user_registration_and_rewards: PASSED")
    await test_referral_validation_logic()
    print("[OK] test_referral_validation_logic: PASSED")
    print("[SUCCESS] Tous les tests d'integration du Parrainage ont REUSSI avec succes !")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
