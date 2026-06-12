import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

async def main():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    if user:
        print("EMAIL:", user.get("email"))
        print("TIER:", user.get("subscription_tier"))
        print("GOOGLE_ID:", user.get("google_id"))
        print("APPLE_ID:", user.get("apple_id"))
        print("HASHED_PWD:", user.get("hashed_password"))
        print("VERIFIED:", user.get("is_verified"))
    else:
        print("USER NOT FOUND")

if __name__ == "__main__":
    asyncio.run(main())
