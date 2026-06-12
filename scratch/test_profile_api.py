"""
Simulates exactly what the frontend does:
1. Login with email/password
2. Call /api/profile with the access token
3. Print what cv_text looks like in the JSON response
"""
import asyncio
import sys
from pathlib import Path
import json

import httpx

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "yayzoy@gmail.com"
PASSWORD = "GoldArmy2026!"

async def main():
    async with httpx.AsyncClient() as client:
        # Step 1: Login (same as frontend handleLogin)
        print("=== Step 1: Login ===")
        resp = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Login status: {resp.status_code}")
        if resp.status_code != 200:
            print("Login FAILED:", resp.text[:300])
            return

        login_data = resp.json()
        token = login_data.get("access_token")
        print(f"Token obtained: {token[:30]}...")
        print(f"User from login: {login_data.get('user')}")

        # Step 2: GET /api/profile (same as Profile.vue fetchProfile)
        print("\n=== Step 2: GET /api/profile ===")
        resp2 = await client.get(
            f"{BASE_URL}/api/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Profile status: {resp2.status_code}")
        if resp2.status_code != 200:
            print("Profile FAILED:", resp2.text[:300])
            return

        profile_data = resp2.json()
        print(f"Response status: {profile_data.get('status')}")
        data = profile_data.get("data", {})
        print(f"Data keys: {list(data.keys())}")
        
        cv_text = data.get("cv_text")
        print(f"\ncv_text type: {type(cv_text)}")
        if cv_text is None:
            print("cv_text is NULL in response!")
        elif cv_text == "":
            print("cv_text is EMPTY STRING in response!")
        else:
            print(f"cv_text length: {len(cv_text)}")
            print(f"cv_text start: {repr(cv_text[:100])}")
        
        # Check if json parsing went well
        raw_size = len(resp2.content)
        print(f"\nRaw response size: {raw_size} bytes")
        
        print("\n=== DONE ===")
        print("Profile info:")
        print(f"  full_name: {data.get('full_name')}")
        print(f"  email: {data.get('email')}")
        print(f"  subscription_tier: {data.get('subscription_tier')}")

if __name__ == "__main__":
    asyncio.run(main())
