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
        
        # Nettoyage initial de la query (typos)
        query = query.replace("Iogiciel", "logiciel").replace("developper", "développeur").replace("développer", "développeur")
        
        cv_profile = {"skills": [], "target_roles": [], "experience_years": 0, "target_level": "junior"}
        
        if cv_text:
            logger.info("📄 ProfileAgent analyse le CV...")
            # Fusionner les résultats de l'IA avec les valeurs par défaut
            ai_data = await self._analyze_cv(cv_text)
            cv_profile.update(ai_data)
            
        # Détection du niveau par la query si non trouvé dans le CV ou l'IA
        query_lower = query.lower()
        if any(k in query_lower for k in ["alternance", "apprentissage"]):
            cv_profile["target_level"] = "alternance"
        elif any(k in query_lower for k in ["stage", "intern", "stagiaire", "internship"]):
            cv_profile["target_level"] = "stage"
        elif any(k in query_lower for k in ["senior", "lead", "principal", "expert"]) and cv_profile.get("target_level") not in ["stage", "alternance"]:
            cv_profile["target_level"] = "senior"

        # Génération des variations de mots-clés et exclusions
        search_strategy = await self._generate_search_strategy(query, cv_profile)
        
        return {
            "success": True,
            "cv_profile": cv_profile,
            "keywords_list": search_strategy.get("keywords", [query]),
            "exclude_list": search_strategy.get("exclude", []),
            "job_type": cv_profile["target_level"] if cv_profile["target_level"] in ["stage", "alternance"] else "emploi"
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
            resp = await self.generate_response(prompt, json_mode=True, model="gemini-2.0-flash")
            match = re.search(r'\{.*\}', resp.replace('\n', ''), re.S)
            if match: return json.loads(match.group(0))
        except: pass
        return {}


    async def _generate_search_strategy(self, query: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Génère des variations de mots-clés et des termes à exclure."""
        prompt = f"""
        Analyse cette recherche d'emploi et génère une stratégie de recherche optimale.
        RECHERCHE: "{query}"
        PROFIL CIBLE: {profile.get('target_roles')}
        
        CONSIGNES:
        1. NE génère PAS de verbes d'action. Génère des TITRES DE POSTE précis (ex: "Développeur Logiciel", "Ingénieur Etudes et Développement").
        2. Liste 10 termes à EXCLURE pour éviter le bruit (ex: commercial, marketing, hse, dessinateur, projeteur, maintenance, support client, rh, recruteur, comptable).
        3. Assure-toi d'inclure des termes anglais équivalents.
        
        RETOURNE UNIQUEMENT DU JSON:
        {{
          "keywords": ["Titre Poste 1", "Titre Poste 2", "Titre Poste 3"],
          "exclude": ["excl1", "excl2", ...]
        }}
        """
        try:
            resp = await self.generate_response(prompt, json_mode=True, model="gemini-2.0-flash")
            match = re.search(r'\{.*\}', resp.replace('\n', ''), re.S)
            if match:
                data = json.loads(match.group(0))
                return data
        except Exception as e:
            logger.error(f"Error generating search strategy: {e}")
            
        return {"keywords": [query], "exclude": []}

