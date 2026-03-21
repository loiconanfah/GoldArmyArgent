import urllib.request
import os
import json

os.makedirs('src/assets/lottie', exist_ok=True)

lotties = [
    ('rocket.json', 'https://lottie.host/81b2a95c-3074-45fb-8db5-05e8105777bd/v8yT7sRjJ7.json'),
    ('scan.json', 'https://lottie.host/762d1ea2-5cb0-40e1-88c9-4a005085e683/C5xM31I8E6.json'),
    ('document.json', 'https://lottie.host/241d3cc2-58e6-42bb-90ad-5a3d0ae8a6a6/y16z02pG9G.json'),
    ('success.json', 'https://lottie.host/b4fbe48e-f6f7-4a09-bb4b-e85fe56b62ff/P2y8vBxXb0.json')
]

for name, url in lotties:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            with open(f'src/assets/lottie/{name}', 'w') as f:
                json.dump(data, f)
        print(f"Success: {name}")
    except Exception as e:
        print(f"Failed {name}: {e}")
