
import asyncio
import os
from dotenv import load_dotenv
from llm.openrouter_client import OpenRouterClient

async def list_models():
    load_dotenv()
    client = OpenRouterClient()
    print("Fetching OpenRouter models...")
    models = await client.list_models()
    if models:
        print(f"Success! Found {len(models)} models.")
        print("Example models:")
        for m in models[:10]:
            print(f"- {m['id']}")
    else:
        print("Failed to fetch models or no models found.")
    await client.close()

if __name__ == "__main__":
    asyncio.run(list_models())
