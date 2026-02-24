"""Agent Judge spécialisé dans l'évaluation de la pertinence des offres."""
import asyncio
import json
import re
from typing import List, Dict, Any
from loguru import logger
from core.agent_base import BaseAgent

class JudgeAgent(BaseAgent):
    """Agent chargé de noter les offres d'emploi par rapport au profil."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "judge")
        kwargs.setdefault("name", "Judge")
        super().__init__(**kwargs)

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les données pour l'évaluation."""
        return {
            "jobs": task.get("jobs", []),
            "cv_profile": task.get("cv_profile", {}),
            "chunk_size": 10
        }

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue les offres en lots (batches) pour optimiser les appels LLM."""
        jobs = plan.get("jobs", [])
        cv_profile = plan.get("cv_profile", {})
        chunk_size = plan.get("chunk_size", 10)
        
        if not jobs:
            return {"success": True, "evaluated_jobs": []}
            
        logger.info(f"⚖️ Judge analyse {len(jobs)} offres par rapport au CV...")
        
        # Découpage en lots
        chunks = [jobs[i:i + chunk_size] for i in range(0, len(jobs), chunk_size)]
        evaluated_jobs = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"🧠 Judge: Traitement lot {i+1}/{len(chunks)}...")
            batch_results = await self._evaluate_batch(chunk, cv_profile)
            evaluated_jobs.extend(batch_results)
            
        # Tri par score décroissant
        evaluated_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return {"success": True, "evaluated_jobs": evaluated_jobs}

    async def _evaluate_batch(self, jobs: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Appelle le LLM pour noter un lot d'offres."""
        job_list_text = ""
        for i, job in enumerate(jobs):
            job_list_text += f"ID: {i}\nTITRE: {job.get('title')}\nENTREPRISE: {job.get('company')}\nLOC: {job.get('location')}\nDESC: {job.get('description')[:500]}...\n---\n"

        prompt = f"""
        En tant qu'expert en recrutement (Agent Judge), note la pertinence de ces offres pour ce candidat.
        
        PROFIL CANDIDAT:
        - Rôles visés: {profile.get('target_roles')}
        - Compétences: {profile.get('skills')}
        - Expérience: {profile.get('experience_years')} ans
        - Niveau: {profile.get('target_level')}
        
        OFFRES A EVALUER:
        {job_list_text}
        
        RÈGLES DE SCORING (SOIS TRÈS STRICT MAIS NUANCÉ):
        1. Domaine IT/Technique: Si ce n'est PAS du tout technique (ex: Pur Marketing, Vente sans aspect technique, RH) -> SCORE = 0.
        2. Rôle matching: 
           - Si l'utilisateur cherche un "développeur" et que l'offre est "Community Manager" ou "Account Executive" (Vente pure) -> SCORE = 0.
           - Si l'offre est "Solution Engineer", "R&D Engineer", "Integration Specialist" ou "Technical Support" et que le contenu mentionne de la programmation ou des outils techniques -> SCORE POSSIBLE (entre 40 et 75 selon le contenu).
           - "Ingénieur" ou "Engineer" dans un domaine autre que l'informatique (Génie Civil, Maintenance mecanique) -> SCORE = 0.
        3. Alternance/Stage: Si l'utilisateur cherche une "Alternance" et que l'offre est un "CDI" (Full-time) -> SCORE < 10 (Sauf si l'offre mentionne explicitement être ouverte aux alternants).
        4. Niveau: Si le candidat est Junior et l'offre est Senior (5+ ans requis) -> SCORE < 15.
        5. Localisation: L'offre doit être dans la ville demandée ({profile.get('target_location', 'Paris, France')}).
        
        FORMAT DE RÉPONSE (JSON UNIQUEMENT, pas de blabla autour):
        [
          {{"id": 0, "score": 85, "reason": "Explication courte"}},
          ...
        ]
        """
        
        try:
            resp = await self.generate_response(prompt)
            # Nettoyage JSON
            match = re.search(r'\[.*\]', resp.replace('\n', ''), re.S)
            if not match: return jobs # Fail safe

            scores = json.loads(match.group(0))
            
            # Mise à jour des jobs originaux
            for s in scores:
                idx = s.get("id")
                if idx is not None and idx < len(jobs):
                    jobs[idx]["match_score"] = s.get("score", 0)
                    jobs[idx]["match_justification"] = s.get("reason", "")
                    
        except Exception as e:
            logger.error(f"🔴 Judge AI Error: {e}")
            
        return jobs
