import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db
from config.settings import settings

async def check_db():
    db = get_db()
    collections = await db.list_collection_names()
    print(f"Collections dans la base '{settings.mongodb_db_name}': {collections}")
    
    for coll_name in collections:
        count = await db[coll_name].count_documents({})
        print(f"- {coll_name}: {count} documents")
        if count > 0:
            sample = await db[coll_name].find_one({})
            print(f"  Sample {coll_name}: {sample.keys()}")

if __name__ == "__main__":
    asyncio.run(check_db())
