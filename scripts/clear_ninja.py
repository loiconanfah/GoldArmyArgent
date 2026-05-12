import asyncio
from core.database import get_db

async def clear():
    db = get_db()
    await db.ninja_results.delete_many({})
    print('DB Cleared')

if __name__ == '__main__':
    asyncio.run(clear())
