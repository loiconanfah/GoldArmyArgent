import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

async def main():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    if user:
        cv_text = user.get("cv_text", "")
        print("cv_text présent:", bool(cv_text))
        print("cv_text longueur:", len(cv_text) if cv_text else 0)
        if cv_text:
            print("cv_text début (100 chars):", cv_text[:100])
        else:
            print("cv_text: VIDE ou absent")
    else:
        print("USER NOT FOUND")

if __name__ == "__main__":
    asyncio.run(main())
