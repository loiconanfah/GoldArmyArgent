from typing import Dict, Any
from loguru import logger

from agents.job_searcher import JobSearchAgent
from agents.mentor import MentorAgent
# from agents.researcher import ResearcherAgent

class OrchestratorAgent:
    """
    Main entry point that analyzes user intent and routes 
    the request to the specialized agents (Searcher, Mentor, etc.).
    """
    def __init__(self):
        self.agent_name = "Orchestrator"
        self.job_searcher = JobSearchAgent()
        self.mentor = MentorAgent()

    async def initialize(self):
        """Initialise tous les sous-agents d'orchestration."""
        await self.job_searcher.initialize()
        await self.mentor.initialize()

    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes intention and orchestrates work."""
        logger.info(f"[Orchestrator] Received task: {user_input.get('query')[:50]}...")
        
        # 1. Analyze intention
        intention = await self._route_request(user_input)
        
        # 2. Delegate to correct Agent
        if intention["action"] == "job_search":
             # Execute the full task pipeline (think -> act -> learn)
             md_response = await self.job_searcher.execute_task(user_input)
             return {
                 "status": "success",
                 "type": "job_search_results",
                 "content": md_response
             }
             
        elif intention["action"] in ["audit_cv", "generate_portfolio"]:
             logger.info(f"[Orchestrator] Routing to MentorAgent for {intention['action']}")
             user_input["action"] = intention["action"]
             return await self.mentor.think(user_input)
             
        else:
             return {
                 "status": "success", 
                 "type": "chat",
                 "content": intention.get("message", "Désolé, je n'ai pas compris ta requête.")
             }

    async def _route_request(self, user_input: Dict[str, Any]) -> Dict[str, str]:
        """Determine which agent handles the query."""
        query = user_input.get("query", "").lower()
        
        if "portfolio" in query or "site web" in query:
             if not user_input.get("cv_text"):
                  return {"action": "chat", "message": "Tu dois me fournir un CV (texte) pour que je puisse générer ton portfolio !"}
             return {"action": "generate_portfolio"}
             
        if "audit" in query or "critique" in query or "mentor" in query or "failles" in query or "cv" in query:
             if not user_input.get("cv_text") and "cv" in query:
                  return {"action": "chat", "message": "J'ai besoin de ton CV pour faire un audit implacable."}
             # Only audit if explicitly requested
             if any(k in query for k in ["audit", "critique", "mentor", "failles"]):
                  return {"action": "audit_cv"}
             
        if "cherche" in query or "trouve" in query or "stage" in query or "emploi" in query or "job" in query:
             return {"action": "job_search"}
             
        if user_input.get("nb_results"):
             return {"action": "job_search"}
             
        return {"action": "chat", "message": "Que puis-je faire pour toi ? Je peux chercher des offres, sculpter ton portfolio Web ou auditer ton CV de manière agressive."}
