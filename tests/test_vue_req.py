import asyncio
import json
import httpx

async def test_frontend_request():
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": "développer logiciel",
        "cv_text": "",
        "cv_filename": "",
        "nb_results": 10
    }
    
    print("Envoi requête au backend...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        print("Status:", response.status_code)
        
        try:
            data = response.json()
            print("Response Type:", data.get("data", {}).get("type"))
            jobs = data.get("data", {}).get("content", {}).get("matched_jobs", [])
            print(f"Jobs reçus: {len(jobs)}")
            if len(jobs) > 0:
                 print(f"Premier job: {jobs[0].get('title')} ({jobs[0].get('company')})")
        except Exception as e:
            print("Error parsing response:", e)
            print("Raw text:", response.text)

if __name__ == "__main__":
    if __import__('sys').platform == 'win32':
         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_frontend_request())
