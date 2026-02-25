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
        kwargs.setdefault("max_tokens", 8192)
        super().__init__(**kwargs)

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les données pour l'évaluation."""
        return {
            "jobs": task.get("jobs", []),
            "cv_profile": task.get("cv_profile", {}),
            "chunk_size": 25
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
        
        # Exécution parallèle
        tasks = [self._evaluate_batch(chunk, cv_profile) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        evaluated_jobs = []
        for i, res in enumerate(results):
            if isinstance(res, list):
                evaluated_jobs.extend(res)
            else:
                logger.error(f"🔴 Erreur Judge lot {i+1}: {res}")
            
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
        
        RÈGLES DE SCORING (SOIS INTELLIGENT, PRÉCIS, ET NUANCÉ SUR 100) :
        Tu dois évaluer si l'offre est une bonne opportunité pour ce candidat précis. Ne mets pas un score de 0 brut si l'offre n'est pas parfaite, mais pénalise intelligemment :

        1. Pertinence globale (Rôle & Compétences) : Évalue dans quelle mesure le titre et le contenu correspondent aux compétences du profil.
        2. Distinction Stage / Emploi : 
           - Si l'offre est un "Stage" ou "Internship" et que l'utilisateur cherche un "Emploi" classique (CDI/CDD), baisse fortement la note (ex: 20-40) car ce n'est pas le bon type d'engagement, mais ne mets pas 0 systématiquement si la boîte est top.
           - Si l'utilisateur cherche un "Stage" et l'offre est un CDI, baisse fortement la note (ex: 10-30).
           - Cependant, si l'offre correspond PARFAITEMENT au type de contrat recherché, donne un bonus significatif.
        3. Niveau d'expérience : Un candidat Junior postulant à une offre "Sénior" (5+ ans) doit voir le score de cette offre diminuer (ex: 30-50).
        4. Localisation : Si c'est hors de la zone voulue ({profile.get('target_location', 'Paris, France')}), déduis des points.
        5. L'importance du titre vs description vide : Si la description (DESC) dit "Aucune description fournie" ou est très courte, n'écrase pas le score ! Base-toi sur le "TITRE" et "ENTREPRISE" et deduis la pertinence. Si un CV cherche un stage developpeur et le TITRE est "Stagiaire Développeur Logiciel", donne-lui un très bon score (70-90) malgré le manque de texte !

        Raisonnement : Décris toujours ta décision de manière claire et concise.
        
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
            if not match: 
                return jobs # Fail safe

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
