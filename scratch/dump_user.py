import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

async def main():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    if user:
        for k, v in user.items():
            if k == "cv_text":
                print(f"cv_text: present, len={len(v)}, start={repr(v[:50])}")
            elif k == "hashed_password":
                print(f"hashed_password: [hidden]")
            else:
                print(f"{k}: {repr(v)}")
    else:
        print("USER NOT FOUND")

if __name__ == "__main__":
    asyncio.run(main())
