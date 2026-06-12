import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

async def main():
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"}, {"_id": 0})
    if user:
        # Test JSON serialization
        try:
            user_str = json.dumps(user, default=str, ensure_ascii=False)
            data = json.loads(user_str)
            cv = data.get("cv_text", "")
            print("JSON OK - cv_text longueur:", len(cv))
            print("Champs retournés:", list(data.keys()))
        except Exception as e:
            print("ERREUR JSON:", e)
    else:
        print("USER NOT FOUND")

if __name__ == "__main__":
    asyncio.run(main())
