import asyncio
import sys
from pathlib import Path
import bcrypt

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

def get_password_hash(password: str) -> str:
    truncated_password = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated_password, salt)
    return hashed.decode('utf-8')

async def main():
    db = get_db()
    new_password = "GoldArmy2026!"
    hashed_pwd = get_password_hash(new_password)
    
    result = await db.users.update_one(
        {"email": "yayzoy@gmail.com"},
        {"$set": {"hashed_password": hashed_pwd}}
    )
    if result.modified_count > 0:
        print("SUCCESS: Password updated to 'GoldArmy2026!'")
    else:
        print("FAILED: User not found or not modified")

if __name__ == "__main__":
    asyncio.run(main())
