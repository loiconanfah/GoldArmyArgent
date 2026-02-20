import asyncio
from duckduckgo_search import DDGS
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

async def analyze_filtering():
    keywords = "Développeur React"
    location = "Québec"
    
    print(f"\n--- Analysis for '{keywords}' in '{location}' ---")
    
    # Broader queries to catch more results (MATCHING web_searcher.py)
    sources_queries = [
        ("Indeed", f'{keywords} {location} "Indeed"'), 
        ("LinkedIn", f'{keywords} {location} "LinkedIn"'),
        ("Glassdoor", f'{keywords} {location} "Glassdoor"') 
    ]
    
    for src, q in sources_queries:
        print(f"\n[Source: {src}] Query: {q}")
        try:
            with DDGS() as ddgs:
                # Region wt-wt for broader results
                results = list(ddgs.text(q, region='wt-wt', max_results=20))
                print(f"  Raw Results: {len(results)}")
                
                valid_count = 0
                for i, res in enumerate(results):
                    title = res.get('title', '')
                    href = res.get('href', '')
                    
                    is_valid = False
                    if src == "Indeed" and ("/viewjob" in href or "/rc/clk" in href): is_valid = True
                    elif src == "LinkedIn" and ("/jobs/view" in href): is_valid = True
                    elif src == "Glassdoor" and ("/job-" in href or "/job/" in href): is_valid = True
                    
                    if not is_valid:
                        low_title = title.lower()
                        bad_words = ["emploi", "jobs", "recherche", "search", "offres", "salaires", "avis"]
                        if not any(w in low_title for w in bad_words):
                            is_valid = True
                            
                    if "search?" in href or "jobs?" in href or "=search" in href: 
                        is_valid = False

                    status = "✅ ACCEPTED" if is_valid else "❌ REJECTED"
                    if is_valid: valid_count += 1
                    
                    print(f"    {i}. {status} | {title[:40]}... | {href}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_filtering())
