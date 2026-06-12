import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

async def main():
    db = get_db()
    cursor = db.users.find({})
    users = await cursor.to_list(length=100)
    print("Total users in database:", len(users))
    for i, user in enumerate(users):
        print(f"User {i+1}: Email={user.get('email')} ID={user.get('id')} has_cv={'cv_text' in user}")
        if 'cv_text' in user:
            print(f"  CV length: {len(user['cv_text'])}")

if __name__ == "__main__":
    asyncio.run(main())
