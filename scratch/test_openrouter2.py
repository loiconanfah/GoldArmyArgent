import asyncio
from llm.openrouter_client import OpenRouterClient

OPENROUTER_FALLBACK_MODELS = [
    "openrouter/auto",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.3-70b-instruct",
    "anthropic/claude-3.5-haiku",
]

async def test_or():
    client = OpenRouterClient()
    for model in OPENROUTER_FALLBACK_MODELS:
        print(f"Testing {model}...")
        try:
            res = await client.generate("Dis bonjour", model=model)
            print(f"[{model}] Success:", res[:50])
        except Exception as e:
            print(f"[{model}] Error:", e)

asyncio.run(test_or())
