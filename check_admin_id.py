import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db

async def check_id():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    if user:
        has_id = "id" in user
        print(f"USER yayzoy@gmail.com | HAS 'id' FIELD: {has_id}")
        if has_id:
            print(f"ID VALUE: {user['id']}")
        else:
            print(f"AVAILABLE KEYS: {list(user.keys())}")
    else:
        print("USER NOT FOUND")

if __name__ == "__main__":
    asyncio.run(check_id())
