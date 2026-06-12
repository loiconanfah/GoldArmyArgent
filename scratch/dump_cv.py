import asyncio
import sys
import json

sys.path.append(r'c:\Users\Utilisateur\PycharmProjects\GoldArmyArgent')

from config.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]
    
    print("Searching for user yayzoy@gmail.com...")
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    if not user:
        print("User not found in DB.")
        # Try finding any user with a CV
        user = await db.users.find_one({"cv_json": {"$ne": None}})
        if not user:
            print("No user with cv_json found.")
            return
        else:
            print(f"Found alternative user: {user.get('email')}")
            
    cv_json = user.get("cv_json")
    if not cv_json:
        print("User has no cv_json in their profile.")
        # Try cv_text
        cv_text = user.get("cv_text")
        if cv_text:
            print(f"User has cv_text of length {len(cv_text)} but no cv_json.")
        return
        
    print(f"Found CV JSON. Writing to scratch/user_cv.json...")
    with open("scratch/user_cv.json", "w", encoding="utf-8") as f:
        json.dump(cv_json, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
