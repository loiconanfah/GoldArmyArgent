import asyncio
from llm.openrouter_client import OpenRouterClient

async def get_free_models():
    client = OpenRouterClient()
    models = await client.list_models()
    free_models = []
    for m in models:
        # Check if pricing is 0 for prompt and completion
        pricing = m.get("pricing", {})
        if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
            free_models.append(m["id"])
    
    print("FREE MODELS FOUND:", len(free_models))
    for m in free_models[:15]:
        print("-", m)

asyncio.run(get_free_models())
