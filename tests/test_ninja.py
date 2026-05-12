import asyncio
import sys
from loguru import logger
from agents.network_ninja_agent import network_ninja_agent

async def test():
    try:
        # User ID for testing, maybe we can fetch the first user from db
        from core.database import get_db
        db = get_db()
        user = await db.users.find_one()
        if not user:
            print("No users found.")
            return
        
        user_id = user.get("id") or user.get("_id")
        user_id = str(user_id)
        
        print(f"Testing for user_id: {user_id}")
        result = await network_ninja_agent.run(user_id)
        print("Success:", result)
    except Exception as e:
        logger.exception("Ninja failed")
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
