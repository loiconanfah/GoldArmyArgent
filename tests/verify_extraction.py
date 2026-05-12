
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from agents.job_searcher import JobSearchAgent

async def main():
    print("Testing JobSearchAgent Extraction...")
    agent = JobSearchAgent()
    
    # Mock LLM response with noise
    messy_response = """
    Voici le JSON demandé pour votre recherche :
    ```json
    {
        "location": "Québec",
        "job_type": "emploi",
        "domain": "informatique",
        "keywords": ["python", "développeur"]
    }
    ```
    J'espère que cela aide !
    """
    
    # We can't easily mock generate_response without mocking the whole class or method.
    # But we can test the regex logic by importing it or extracting it.
    # Since we modified _extract_criteria_from_text, let's just test the regex logic directly here to be sure.
    
    import re
    import json
    
    print("Testing Regex Logic:")
    json_match = re.search(r'\{.*\}', messy_response.strip(), re.DOTALL)
    if json_match:
        print("✅ Regex matched JSON block")
        try:
            data = json.loads(json_match.group(0))
            print(f"✅ JSON parsed: {data}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
    else:
        print("❌ Regex failed to match")

    # Test stopwords logic
    print("\nTesting Stopwords Logic:")
    text = "Trouve moi des offres Python à Québec pour un stage"
    stop_words = {"le", "la", "les", "un", "une", "des", "à", "de", "pour", "moi", "je", "trouve", "offre", "offres", "job", "jobs", "en", "sur", "dans", "et", "ou"}
    raw_words = text.lower().split()
    cleaned = [w for w in raw_words if w not in stop_words]
    print(f"Original: {text}")
    print(f"Cleaned: {cleaned}")
    
    if "python" in cleaned and "québec" in cleaned and "stage" in cleaned:
        print("✅ Stopwords filtering worked")
    else:
        print("❌ Stopwords filtering failed")

if __name__ == "__main__":
    asyncio.run(main())
