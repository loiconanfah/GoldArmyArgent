import asyncio
import sys
from pathlib import Path

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Ensure path is correct
sys.path.insert(0, str(Path(__file__).parent))

from tools.web_searcher import web_searcher

async def test_ddg():
    print("🚀 Test Scraping DuckDuckGo")
    jobs = await web_searcher._search_general_web("developpeur mobile", "Montréal", 5)
    
    print(f"\n✅ {len(jobs)} emplois trouvés:")
    for i, job in enumerate(jobs):
        print(f"\n--- Offre {i+1} ---")
        print(f"Titre: {job.get('title')}")
        print(f"Location: {job.get('location')}")
        print(f"Entreprise: {job.get('company')}")
        print(f"URL: {job.get('url')}")
        print(f"Description: {job.get('description')}")

if __name__ == "__main__":
    asyncio.run(test_ddg())
