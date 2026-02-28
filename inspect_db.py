
import asyncio
from core.database import get_db

async def inspect():
    db = get_db()
    cursor = db.applications.find().limit(5)
    async for doc in cursor:
        print(f"ID: {doc.get('id')} | Created At: {doc.get('created_at')} | Type: {type(doc.get('created_at'))}")

if __name__ == "__main__":
    asyncio.run(inspect())
