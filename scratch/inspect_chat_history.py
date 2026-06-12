import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db

async def main():
    db = get_db()
    # Find active conversations or tasks or recent messages
    print("Database collections:", await db.list_collection_names())
    
    # Try searching for chat messages or tasks
    # Let's inspect conversations collection if it exists
    collections = await db.list_collection_names()
    for col in ["conversations", "messages", "chats", "tasks", "user_conversations"]:
        if col in collections:
            count = await db[col].count_documents({})
            print(f"Collection '{col}' count:", count)
            if count > 0:
                print(f"--- Sample from '{col}' ---")
                cursor = db[col].find({}).sort("_id", -1).limit(5)
                docs = await cursor.to_list(length=5)
                for d in docs:
                    # print keys
                    print("Keys:", list(d.keys()))
                    if "user_id" in d or "email" in d:
                        print(f"User/Email: {d.get('user_id') or d.get('email')}")
                    if "messages" in d:
                        print("Messages count:", len(d["messages"]))
                        for m in d["messages"][-2:]:
                            print(f"  Role: {m.get('role')}, Type: {m.get('type')}")
                            content = m.get('content', '')
                            print(f"  Content length: {len(content)}")
                            print(f"  Content start: {repr(content[:100])}")
                    elif "content" in d:
                        print(f"  Content length: {len(d['content'])}")
                        print(f"  Content start: {repr(d['content'][:100])}")

if __name__ == "__main__":
    asyncio.run(main())
