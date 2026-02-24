"""Agent Profile spécialisé dans l'analyse de CV et la définition de critères."""
import json
import re
from typing import Dict, Any
from loguru import logger
from core.agent_base import BaseAgent

class ProfileAgent(BaseAgent):
    """Agent chargé de comprendre le candidat et de préparer les critères de recherche."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "profile")
        kwargs.setdefault("name", "Analyzer")
        super().__init__(**kwargs)

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare l'analyse du CV."""
        return {
            "cv_text": task.get("cv_text"),
            "query": task.get("query", ""),
            "location": task.get("location", "")
        }

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le CV et génère les critères de recherche finaux."""
        cv_text = plan.get("cv_text")
        query = plan.get("query", "")
        
        cv_profile = {"skills": [], "target_roles": [], "experience_years": 0, "target_level": "junior"}
        
        if cv_text:
            logger.info("📄 ProfileAgent analyse le CV...")
            # Fusionner les résultats de l'IA avec les valeurs par défaut
            ai_data = await self._analyze_cv(cv_text)
            cv_profile.update(ai_data)
            
        # Détection du niveau par la query si non trouvé dans le CV ou l'IA
        query_lower = query.lower()
        if "stage" in query_lower or "intern" in query_lower:
            cv_profile["target_level"] = "stage"
        elif any(k in query_lower for k in ["senior", "lead", "principal", "expert"]) and cv_profile.get("target_level") != "stage":
            cv_profile["target_level"] = "senior"

        # Génération des variations de mots-clés
        keywords_list = await self._generate_keywords(query, cv_profile)
        
        return {
            "success": True,
            "cv_profile": cv_profile,
            "keywords_list": keywords_list,
            "job_type": "stage" if cv_profile["target_level"] == "stage" else "emploi"
        }

    async def _analyze_cv(self, text: str) -> Dict[str, Any]:
        """Analyse structurelle du CV via LLM."""
        prompt = f"""
        Analyse ce CV et extrais les informations pour une recherche d'emploi.
        CV: {text[:4000]}
        
        EXTRACTS UNIQUEMENT EN JSON:
        {{
          "target_roles": ["Liste de titres de postes vise"],
          "skills": ["Liste de competences cles"],
          "experience_years": 0,
          "target_level": "junior/senior/stage"
        }}
        """
        try:
            resp = await self.generate_response(prompt)
            match = re.search(r'\{.*\}', resp.replace('\n', ''), re.S)
            if match: return json.loads(match.group(0))
        except: pass
        return {}

    async def _generate_keywords(self, query: str, profile: Dict[str, Any]) -> list:
        """Génère des variations de mots-clés (Anglais/Français)."""
        prompt = f"""
        Génère 3 variations de mots-clés de recherche pour: "{query}"
        PROFIL: {profile.get('target_roles')}
        FORMAT: ["var1", "var2", "var3"]
        JSON UNIQUEMENT.
        """
        try:
            resp = await self.generate_response(prompt)
            match = re.search(r'\[.*\]', resp.replace('\n', ''), re.S)
            if match: return json.loads(match.group(0))
        except: pass
        return [query]
