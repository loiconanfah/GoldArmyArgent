import asyncio
from llm.openrouter_client import OpenRouterClient

async def list_models():
    client = OpenRouterClient()
    models = await client.list_models()
    gemini_models = [m["id"] for m in models if "gemini" in m["id"]]
    print("Gemini models on OpenRouter:", gemini_models)

asyncio.run(list_models())
