import asyncio
import os
import sys
import json

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db

async def check_user_struct():
    db = get_db()
    users_cursor = db.users.find({})
    users = await users_cursor.to_list(length=100)
    
    print(f"TOTAL USERS IN 'goldarmy': {len(users)}")
    for u in users:
        # Convert ObjectId to string for printing
        u['_id'] = str(u['_id'])
        if 'last_portfolio' in u: u['last_portfolio'] = "TRUNCATED"
        print(f"\nUser: {u.get('email')}")
        print(json.dumps(u, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(check_user_struct())
