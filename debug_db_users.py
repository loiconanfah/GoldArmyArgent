import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db
from config.settings import settings

async def check_users():
    db = get_db()
    count = await db.users.count_documents({})
    print(f"Nombre d'utilisateurs en base : {count}")
    
    users_cursor = db.users.find({}, {"password": 0}).limit(10)
    users = await users_cursor.to_list(length=10)
    
    for u in users:
        print(f"- {u.get('email')} | Tier: {u.get('subscription_tier')} | _id: {u.get('_id')}")

if __name__ == "__main__":
    asyncio.run(check_users())
