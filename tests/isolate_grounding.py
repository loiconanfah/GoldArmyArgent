
import asyncio
import os
import json
from loguru import logger
from llm.gemini_client import GeminiClient

async def test_grounding():
    client = GeminiClient()
    prompt = "Find 5 LinkedIn profiles of recruiters at Microsoft."
    print("Testing Grounding...")
    
    try:
        text, sources = await client.generate_with_sources(prompt)
        print(f"Success! Found {len(sources)} sources.")
        print(f"Text length: {len(text)}")
        for s in sources[:3]:
            print(f" - {s}")
    except Exception as e:
        print(f"FAILED: {e}")
        if os.path.exists("gemini_error_dump.json"):
            print("Dump file found. Checking first 100 bytes...")
            with open("gemini_error_dump.json", "r", encoding="utf-8") as f:
                content = f.read()
                print(content[:100] + "...")
                print(f"Total length: {len(content)}")

if __name__ == "__main__":
    asyncio.run(test_grounding())
