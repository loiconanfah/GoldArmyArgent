import asyncio
from core.database import get_db

async def test():
    try:
        db = get_db()
        # Find one user
        user = await db.users.find_one({})
        print(f"Connection success. Found user: {user.get('email') if user else 'None'}")
    except Exception as e:
        print(f"Exception exactly: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test())
