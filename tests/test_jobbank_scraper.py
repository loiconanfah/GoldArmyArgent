import asyncio
import sys
from pathlib import Path

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from tools.web_searcher import web_searcher

async def test_jobbank():
    print("🚀 Test Scraping Guichet Emplois (Job Bank)")
    jobs = await web_searcher._search_jobbank("developpeur logiciel", "Montréal", 5)
    
    print(f"\n✅ {len(jobs)} emplois trouvés:")
    for i, job in enumerate(jobs):
        print(f"\n--- Offre {i+1} ---")
        print(f"Titre: {job.get('title')}")
        print(f"Location: {job.get('location')}")
        print(f"Entreprise: {job.get('company')}")
        print(f"URL: {job.get('url')}")
        print(f"Description brève: {job.get('description')}")

if __name__ == "__main__":
    asyncio.run(test_jobbank())
