
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from tools.web_searcher import web_searcher

async def main():
    print("Testing WebSearcher Location & Enrichment...")
    
    # 1. Test Location "Québec" (City)
    print("\n1. Searching for 'Serveur' in 'Québec'...")
    jobs = await web_searcher.search_jobs("Serveur", "Québec", max_results=5)
    
    print(f"Found {len(jobs)} jobs.")
    
    qc_count = 0
    toronto_count = 0
    
    for j in jobs:
        loc = j['location'].lower()
        print(f"- {j['title']} | {j['location']}")
        if "québec" in loc or "quebec" in loc or "qc" in loc:
            qc_count += 1
        if "toronto" in loc:
            toronto_count += 1
            
    print(f"Stats: QC={qc_count}, Toronto={toronto_count}")
    
    if toronto_count > qc_count:
        print("❌ FAIL: Too many Toronto results for 'Québec' search.")
    else:
        print("✅ PASS: Location filtering seems better.")
    # 3. Test Multi-Source
    print("\n3. Verifying Multi-Source Results...")
    sources = set(j['source'] for j in jobs)
    print(f"Sources found: {sources}")
    
    if "Indeed" in sources or "LinkedIn" in sources:
        print("✅ PASS: Multi-source search working.")
    else:
        print("⚠️ WARNING: Only Job Bank results found (or DDG blocked).")

    # 2. Test Enrich Details
    if jobs:
        # Prefer enriching a Job Bank job for this test as it has the robust scraper
        jb_jobs = [j for j in jobs if j.get("source") == "Guichet Emplois"]
        job_to_enrich = jb_jobs[0] if jb_jobs else jobs[0]
        
        print(f"\n2. Enriching job: {job_to_enrich['title']} ({job_to_enrich['source']})...")
        
        enriched = await web_searcher.enrich_job_details(job_to_enrich)
        
        desc = enriched.get("full_description", "")
        print(f"Full Description Length: {len(desc)}")
        
        if len(desc) > 100:
            print("✅ PASS: Enrichment successful.")
            print(f"Snippet: {desc[:100]}...")
            
            # Check for skills
            print(f"Skills found: {enriched.get('required_skills')}")
        else:
            print("❌ FAIL: Description empty or too short.")
    else:
        print("⚠️ SKIPPING Enrichment test (No Job Bank result found).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
