import asyncio
from llm.unified_client import UnifiedLLMClient

async def test_unified():
    client = UnifiedLLMClient()
    try:
        # On simule un appel comme dans l'endpoint mini-audit (CV Roast)
        res = await client.chat(
            [{"role": "user", "content": "Dis bonjour et confirme que tu es sur OpenRouter."}],
            json_mode=False,
            model="gemini-2.0-flash",
            max_tokens=100
        )
        print("Success Unified Chat mapping:", res)
    except Exception as e:
        print("Error Unified Chat mapping:", e)

asyncio.run(test_unified())
