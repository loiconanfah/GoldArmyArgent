import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db
from api.main import get_profile

async def main():
    db = get_db()
    # Mock current_user
    current_user = {"id": "f039a114-60e2-491d-83c5-c1860010295c", "email": "yayzoy@gmail.com", "subscription_tier": "ADMIN"}
    
    response = await get_profile(current_user=current_user)
    print("Response keys:", list(response.keys()))
    if response.get("status") == "success":
        data = response.get("data", {})
        print("Data keys:", list(data.keys()))
        print("cv_text length:", len(data.get("cv_text")) if data.get("cv_text") else None)
        print("cv_text value:", repr(data.get("cv_text"))[:150])

if __name__ == "__main__":
    asyncio.run(main())
