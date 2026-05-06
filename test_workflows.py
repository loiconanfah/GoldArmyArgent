import asyncio
import os
from loguru import logger

async def test_workflows():
    from core.orchestrator import orchestrator
    logger.info("Test du dispatcher de Workflows...")
    
    payload = {
        "companyName": "Google",
        "jobTitle": "Ingénieur IA",
        "app_id": "test_app_123",
        "user_id": "system"
    }
    
    logger.info("Testing sniper_to_apply")
    await orchestrator.dispatch_event("sniper_to_apply", payload)
    
    logger.info("Testing card_rejected")
    await orchestrator.dispatch_event("card_rejected", payload)
    
    # Wait for background tasks
    await asyncio.sleep(5)
    
if __name__ == "__main__":
    asyncio.run(test_workflows())
