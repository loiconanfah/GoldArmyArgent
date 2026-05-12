import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Ajouter le chemin racine pour importer les modules
sys.path.append(os.getcwd())

from llm.gemini_client import GeminiClient

async def test_gemini():
    load_dotenv()
    print(f"API Key found: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
    
    try:
        client = GeminiClient()
        print(f"Client init... OK")
        
        prompt = "Hello"
        models_to_test = ["gemini-3.0-pro-preview", "gemini-3.1-pro-preview"]
        
        for model in models_to_test:
            print(f"\n--- Testing model: {model} ---")
            try:
                response = await client.generate(prompt, model=model)
                print(f"Response: {response}")
                print(f"SUCCESS: {model} is working.")
            except Exception as api_err:
                print(f"ERROR with {model}: {api_err}")
            
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_gemini())

