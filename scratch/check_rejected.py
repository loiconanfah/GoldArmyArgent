import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from core.database import get_db

async def check():
    db = get_db()
    count = await db.applications.count_documents({"status": "REJECTED"})
    print(f"Rejected apps: {count}")
    apps = await db.applications.find({"status": "REJECTED"}, {"_id": 0, "id": 1, "job_title": 1, "company_name": 1}).to_list(length=5)
    for app in apps:
        print(f"- {app.get('job_title')} at {app.get('company_name')} (ID: {app.get('id')})")

if __name__ == "__main__":
    asyncio.run(check())
