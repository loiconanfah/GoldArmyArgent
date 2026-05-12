import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db

async def check_tiers():
    db = get_db()
    users_cursor = db.users.find({}, {"email": 1, "subscription_tier": 1, "full_name": 1})
    users = await users_cursor.to_list(length=100)
    
    print("USER TIERS IN 'goldarmy' DB:")
    for u in users:
        print(f"- {u.get('email')} | Tier: {u.get('subscription_tier')} | Name: {u.get('full_name')}")

if __name__ == "__main__":
    asyncio.run(check_tiers())
