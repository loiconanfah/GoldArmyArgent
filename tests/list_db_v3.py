import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db_client

async def list_dbs():
    client = get_db_client()
    db_names = await client.list_database_names()
    print(f"DATABASE LIST: {db_names}")
    
    for name in db_names:
        db = client[name]
        collections = await db.list_collection_names()
        print(f"\nDB: {name}")
        for coll in collections:
            count = await db[coll].count_documents({})
            print(f"  - {coll}: {count} docs")
            if coll.lower() == 'users' and count > 0:
                sample = await db[coll].find_one({})
                print(f"    Sample User: {sample.get('email')}")

if __name__ == "__main__":
    asyncio.run(list_dbs())
