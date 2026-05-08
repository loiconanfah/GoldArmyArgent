import os

filepath = r'c:\Users\Utilisateur\PycharmProjects\GoldArmyArgent\api\main.py'
with open(filepath, 'a', encoding='utf-8') as f:
    f.write('''

# ==========================================
# Sniper To Apply Endpoints
# ==========================================

class SniperApplySearchRequest(BaseModel):
    job_title: str
    location: str
    nb_results: Optional[int] = 10

class SniperApplyExecuteRequest(BaseModel):
    selected_offers: List[Dict[str, Any]]

@app.post("/api/workflows/sniper-apply/search")
async def sniper_apply_search(
    req: SniperApplySearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        
        from agents.job_searcher import JobSearchAgent
        searcher = JobSearchAgent()
        await searcher.initialize()
        
        task = {
            "query": req.job_title,
            "location": req.location,
            "nb_results": req.nb_results,
            "cv_text": cv_text
        }
        plan = await searcher.think(task)
        result = await searcher.act(plan)
        
        return {"status": "success", "data": result.get("matched_jobs", [])}
    except Exception as e:
        import logging
        logging.error(f"Sniper Apply Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/sniper-apply/execute")
async def sniper_apply_execute(
    req: SniperApplyExecuteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        import uuid
        import httpx
        from datetime import datetime
        from agents.cv_adapter import CVAdapterAgent
        
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        is_premium = user.get("subscription_tier") in ["PRO", "PREMIUM", "GOLD"] if user else False
        
        max_allowed = 10 if is_premium else 3
        if len(req.selected_offers) > max_allowed:
            raise HTTPException(status_code=403, detail=f"Limite d'abonnement dépassée. Max: {max_allowed}")
            
        adapter = CVAdapterAgent()
        await adapter.initialize()
        
        # Clé API Skyvern fournie par l'utilisateur
        skyvern_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQ5MjMwNTQ5NzIsInN1YiI6Im9fNTI1NzU0NTQ1NTE4ODc2MjA4In0.pplBLwI9niInf3yTWzLGwVuGoiggQgLKB8r4FzePbIY"
        skyvern_api_url = "https://api.skyvern.com/api/v1/tasks"
        
        results = []
        
        for offer in req.selected_offers:
            title = offer.get("title", "")
            company = offer.get("company", "")
            desc = offer.get("description", "")
            url = offer.get("url", "")
            
            # 1. Adapter le CV
            adapt_result = await adapter.adapt(title, desc, cv_text)
            cv_json = adapt_result.get("cv_json", {})
            
            # 2. Lancer la tâche Skyvern
            skyvern_task_id = None
            if url and skyvern_api_key:
                try:
                    prompt = f"Apply to this job. My name is {cv_json.get('full_name', 'Candidat')}. My skills are {cv_json.get('skills', {})}. Please fill the form and attach my resume or paste my details."
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        resp = await client.post(
                            skyvern_api_url,
                            headers={"x-api-key": skyvern_api_key, "Content-Type": "application/json"},
                            json={
                                "url": url,
                                "webhook_callback_url": "",
                                "navigation_goal": prompt,
                                "data_extraction_goal": "",
                                "proxy_location": "US"
                            }
                        )
                        if resp.status_code in [200, 201]:
                            skyvern_task_id = resp.json().get("task_id")
                except Exception as ex:
                    import logging
                    logging.warning(f"Skyvern API call failed for {company}: {ex}")
            
            # 3. Sauvegarder dans CRM
            app_id = str(uuid.uuid4())
            new_app = {
                "id": app_id,
                "user_id": user_id,
                "job_title": title,
                "company_name": company,
                "url": url,
                "status": "APPLIED",
                "notes": "Appliqué via Sniper To Apply (Skyvern)\\n" + (f"Skyvern Task: {skyvern_task_id}" if skyvern_task_id else ""),
                "cv_json": cv_json,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.applications.insert_one(new_app)
            
            results.append({
                "id": app_id,
                "company": company,
                "title": title,
                "skyvern_task_id": skyvern_task_id,
                "status": "success"
            })
            
        return {"status": "success", "data": results}
    except Exception as e:
        import logging
        logging.error(f"Sniper Apply Execute Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
''')
print('Endpoints appended.')
