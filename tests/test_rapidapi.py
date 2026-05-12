import asyncio
import httpx
import json

async def test_rapidapi():
    base_url = "https://fresh-linkedin-profile-data-api.p.rapidapi.com/api/search"
    headers = {
        "x-rapidapi-key": "c30011fc96mshf54e01fc16d71a0p190dbbjsna557b0fa3efc",
        "x-rapidapi-host": "fresh-linkedin-profile-data-api.p.rapidapi.com"
    }
    
    # On va tester /companies (celui du user) et /people (celui qu'on veut)
    endpoints = {
        "Companies": f"{base_url}/companies?q=CGI&count=2",
        "Employees/People": f"{base_url}/employees?q=CGI%20HR&count=2",
        "People": f"{base_url}/people?q=CGI%20HR&count=2"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for name, url in endpoints.items():
            print(f"\n--- TEST: {name} ---")
            print(f"URL: {url}")
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            try:
                data = resp.json()
                print(json.dumps(data, indent=2, ensure_ascii=False)[:800])
            except Exception:
                print(resp.text[:500])

if __name__ == "__main__":
    asyncio.run(test_rapidapi())
