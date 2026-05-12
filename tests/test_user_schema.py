import asyncio
import pprint
from core.database import get_db, init_db

async def test():
    await init_db()
    db = get_db()
    user = await db.users.find_one({"email": "yayzoy@gmail.com"})
    pprint.pprint(user)

if __name__ == "__main__":
    asyncio.run(test())
