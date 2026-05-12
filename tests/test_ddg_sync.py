
from duckduckgo_search import DDGS
import json

print("Testing DDGS (Sync)...")
try:
    with DDGS() as ddgs:
        print("Trying backend='html'...")
        results = ddgs.text("python jobs quebec", max_results=5, backend="html")
        results_list = list(results)
        print(f"Found {len(results_list)} results with html backend")
        
        if not results_list:
            print("Trying backend='lite'...")
            results = ddgs.text("python jobs quebec", max_results=5, backend="lite")
            results_list = list(results)
            print(f"Found {len(results_list)} results with lite backend")
        
        for r in results_list:
            print(json.dumps(r, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
