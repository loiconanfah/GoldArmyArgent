import asyncio
from llm.openrouter_client import OpenRouterClient

async def test_or():
    client = OpenRouterClient(model="google/gemini-2.0-flash-exp:free")
    try:
        res = await client.generate("Dis bonjour", json_mode=True)
        print("Success JSON mode:", res)
    except Exception as e:
        print("Error JSON mode:", e)

    try:
        res2 = await client.generate("Dis bonjour", json_mode=False)
        print("Success NO JSON:", res2)
    except Exception as e:
        print("Error NO JSON:", e)

asyncio.run(test_or())
