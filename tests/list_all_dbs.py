import asyncio
import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.getcwd())

from core.database import get_db_client

async def list_dbs():
    client = get_db_client()
    dbs = await client.list_database_names()
    print(f"Bases de données disponibles : {dbs}")
    for db_name in dbs:
        db = client[db_name]
        try:
            colls = await db.list_collection_names()
            print(f"Base '{db_name}': {colls}")
            if 'users' in colls:
                count = await db.users.count_documents({})
                print(f"  -> Collection 'users' a {count} documents")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(list_dbs())
