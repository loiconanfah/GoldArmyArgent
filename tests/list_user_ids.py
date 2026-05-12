import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db

async def list_ids():
    db = get_db()
    users_cursor = db.users.find({})
    users = await users_cursor.to_list(length=100)
    
    print(f"{'EMAIL':<35} | {'ID (UUID)':<40} | {'TIER':<10}")
    print("-" * 90)
    for u in users:
        email = u.get('email', 'N/A')
        uuid_id = u.get('id', 'MISSING')
        tier = u.get('subscription_tier', 'N/A')
        print(f"{email:<35} | {uuid_id:<40} | {tier:<10}")

if __name__ == "__main__":
    asyncio.run(list_ids())
