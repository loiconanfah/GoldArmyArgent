import asyncio
import os
import sys
import json

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db

async def check_admin():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    
    if user:
        user['_id'] = str(user['_id'])
        print(f"ADMIN USER FOUND:")
        print(json.dumps(user, indent=2, default=str))
    else:
        print("ADMIN USER NOT FOUND BY EMAIL")

if __name__ == "__main__":
    asyncio.run(check_admin())
