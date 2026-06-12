import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db
from api.auth import verify_password

async def main():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    if user:
        hashed = user.get("hashed_password")
        pwd = "GoldArmy2026!"
        ok = verify_password(pwd, hashed)
        print("MATCH:", ok)
        print("HASH IN DB:", hashed)
    else:
        print("User not found")

if __name__ == "__main__":
    asyncio.run(main())
