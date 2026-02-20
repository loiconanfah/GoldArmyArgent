
import asyncio
from llm.unified_client import UnifiedLLMClient
from config.settings import settings
import sys

async def check():
    print(f"[INFO] Testing OpenRouter Connection...")
    print(f"Key configured: {bool(settings.openrouter_api_key)}")
    print(f"Default Model: {settings.openrouter_default_model}")
    
    client = UnifiedLLMClient()
    
    if not client.openrouter_client:
        print("[ERROR] OpenRouter Client NOT active (Fallback to Local)")
    else:
        print("[SUCCESS] OpenRouter Client ACTIVE")
        
    try:
        print("\nSending prompt: 'Who are you and what model are you running on?'...")
        response = await client.generate(
            "Who are you and what model are you running on? Answer in one short sentence.",
            model=settings.openrouter_default_model
        )
        print(f"\nRESPONSE:\n{response}\n")
        print("[SUCCESS] Test Successful!")
    except Exception as e:
        print(f"\n[ERROR] Test Failed: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    # Fix for Windows loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check())
