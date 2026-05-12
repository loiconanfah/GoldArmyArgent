
import asyncio
import os
import json
import httpx
from dotenv import load_dotenv

async def manual_check():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ Error: No API Key found in .env")
        return

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501", 
        "X-Title": "GoldArmyArgent",
    }
    data = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": "What is the meaning of life? Answer in 5 words."
            }
        ]
    }
    
    print(f"[INFO] Testing Model: {data['model']} ...")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                print("[SUCCESS] Connected!")
                print(f"Response: {resp.json()['choices'][0]['message']['content']}")
            else:
                print(f"[ERROR] Failed: {resp.status_code}")
                print(resp.text)
        except Exception as e:
            print(f"[EXCEPTION] {e}")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(manual_check())
