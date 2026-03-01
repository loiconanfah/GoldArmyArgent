import asyncio
import os
import sys

# Ajouter le répertoire actuel au path pour les imports
sys.path.append(os.getcwd())

from core.database import get_db

async def check_user():
    try:
        db = get_db()
        email = "yayzoy@gmail.com"
        user = await db.users.find_one({"email": email})
        if user:
            print(f"SUCCESS: User found!")
            print(f"ID field: {user.get('id')}")
            print(f"Email field: {user.get('email')}")
            print(f"Full dict: {user}")
        else:
            print(f"FAILURE: User {email} not found in database.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check_user())
