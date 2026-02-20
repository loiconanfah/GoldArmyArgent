
try:
    from googlesearch import search
    print("Testing googlesearch-python...")
    query = "python jobs quebec site:indeed.com"
    
    count = 0
    for url in search(query, num_results=5, sleep_interval=2):
        print(f"Found: {url}")
        count += 1
        if count >= 5: break
        
    print(f"Total found: {count}")

except ImportError:
    print("googlesearch not found")
except Exception as e:
    print(f"Error: {e}")
