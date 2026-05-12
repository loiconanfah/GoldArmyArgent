import asyncio
from agents.hunter_agent import HunterAgent

async def test_filter():
    print("Testing HunterAgent...")
    agent = HunterAgent()
    
    plan = {
        "keywords": ["développeur logiciel", "software engineer"],
        "location": "Quebec",
        "apis": ["jsearch", "google_jobs", "linkedin", "jooble", "findwork"],
        "limit": 10,
        "job_type": "emploi"
    }
    
    # We will temporarily override the _filter_strict_precision to print rejection reasons
    original_filter = agent._filter_strict_precision
    
    def debug_filter(jobs, expected_location, expected_job_type):
        result = []
        loc_lower = expected_location.lower()
        type_lower = expected_job_type.lower()
        
        internship_keywords = ["stage", "intern", "internship", "apprenti", "alternance", "student", "étudiant"]
        is_internship_search = any(w in type_lower for w in internship_keywords)
        
        reasons = {"loc": 0, "type_intern": 0, "type_emploi": 0}
        log_entries = []

        for job in jobs:
            text = f"{job.get('title', '')} {job.get('description', '')} {job.get('raw_contract_type', '')}".lower()
            job_loc = job.get('location', '').lower()
            
            loc_is_valid = False
            search_terms = loc_lower.replace(",", " ").split()
            for term in search_terms:
                if len(term) > 3 and (term in job_loc or job_loc == "remote" or job_loc == "télétravail" or not job_loc or job_loc == "confidentiel"):
                    loc_is_valid = True
                    break
            
            if not loc_is_valid and len(job_loc) > 3 and "remote" not in job_loc:
                log_entries.append({"reason": "loc", "loc": job_loc, "expected": loc_lower, "title": job.get("title")})
                reasons["loc"] += 1
                continue
                
            if is_internship_search:
                if not any(k in text for k in internship_keywords):
                    log_entries.append({"reason": "not_internship", "title": job.get("title"), "expected": "internship"})
                    reasons["type_intern"] += 1
                    continue
            else:
                if any(k in text for k in ["internship", "stage étudiant"]):
                    log_entries.append({"reason": "student_in_emploi", "title": job.get("title")})
                    reasons["type_emploi"] += 1
                    continue
                    
            result.append(job)
            
        with open("filter_debug.json", "w", encoding="utf-8") as f:
            import json
            json.dump({"stats": reasons, "log": log_entries}, f, indent=4, ensure_ascii=False)
        return result

    agent._filter_strict_precision = debug_filter
    
    res = await agent.act(plan)
    print(f"Final jobs: {len(res['jobs'])}")

if __name__ == "__main__":
    asyncio.run(test_filter())
