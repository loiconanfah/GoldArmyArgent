import os
import httpx
import asyncio

async def test_key():
    key = "AIzaSyBVRksYtbv_ubxW-9P-YFmJxGdC99MZxUU"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            print("Status Code:", response.status_code)
            print("Response:", response.text[:1000])
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test_key())
