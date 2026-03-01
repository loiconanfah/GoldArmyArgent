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
        """Évalue les offres en lots avec Gemini 2.0 Flash (Mode Hyper-Vitesse)."""
        jobs = plan.get("jobs", [])
        cv_profile = plan.get("cv_profile", {})
        
        # Gemini 2.0 Flash est 5x plus rapide, on peut augmenter le lot
        chunk_size = 25 
        
        if not jobs:
            return {"success": True, "evaluated_jobs": []}
            
        logger.info(f"⚖️ Judge analyse {len(jobs)} offres (Gemini 2.0 Flash Swarm)...")
        
        chunks = [jobs[i:i + chunk_size] for i in range(0, len(jobs), chunk_size)]
        
        # Sémaphore pour parallélisme contrôlé sur Render (évite les 429)
        semaphore = asyncio.Semaphore(5)

        async def _evaluate_with_semaphore(chunk, profile):
            async with semaphore:
                try:
                    # On force l'usage de flash pour la vitesse
                    return await self._evaluate_batch(chunk, profile, model="gemini-2.0-flash")
                except Exception as e:
                    logger.error(f"🔴 Erreur Judge lot: {e}")
                    return chunk

        tasks = [_evaluate_with_semaphore(chunk, cv_profile) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        evaluated_jobs = []
        for res in results:
            if isinstance(res, list):
                evaluated_jobs.extend(res)
            
        # Tri par score décroissant
        evaluated_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        # Filtre souple (Score >= 30)
        filtered_jobs = [j for j in evaluated_jobs if j.get("match_score", 0) >= 30]
        
        logger.info(f"⚖️ Judge a validé {len(filtered_jobs)} offres en mode Flash.")
        
        return {"success": True, "evaluated_jobs": filtered_jobs}



    async def _evaluate_batch(self, jobs: List[Dict[str, Any]], profile: Dict[str, Any], model: str = None) -> List[Dict[str, Any]]:
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
        
        RÈGLES DE SCORING STRICTES (SUR 100) :
        Tu es le dernier rempart avant l'affichage à l'utilisateur. Ton but est d'éliminer le "bruit".

        1. TYPE DE CONTRAT (CRITÈRE ÉLIMINATOIRE) : 
           - Si l'utilisateur cherche explicitement un "Stage" (Intern) ou une "Alternance" et que l'offre est un emploi permanent (CDI, Permanent, Senior, Staff, etc.), la note DOIT ÊTRE 0. Aucune exception.
           - Si l'utilisateur cherche un emploi et que l'offre est un "Stage étudiant", la note DOIT ÊTRE 0.
        2. PERTINENCE DU RÔLE (CRITÈRE ÉLIMINATOIRE) :
           - L'offre DOIT correspondre au domaine et au métier exact visé par le candidat. Analyse les "Rôles visés" et les "Compétences". Si l'offre concerne un tout autre domaine d'expertise (ex: l'offre est en Vente alors que le profil cible la Finance, ou l'offre est en Ressources Humaines alors que le profil cible l'Informatique), la note DOIT ÊTRE 0. Fais preuve d'analyse et sois intransigeant sur les hors-sujets.
        3. NIVEAU D'EXPÉRIENCE (CRITÈRE ÉLIMINATOIRE) :
           - Un candidat Junior/Stagiaire postulant à une offre "Senior", "Staff", "Principal" ou demandant 5+ ans d'expérience DOIT recevoir une note de 0.
        4. PERTINENCE GLOBALE ET LOCALISATION :
           - Ajuste le score (de 40 à 100) selon la proximité des compétences et de la localisation visées. Sanctionne fortement (score < 40) si l'offre s'éloigne techniquement des compétences du profil.
        5. Descriptions Courtes : Si la description est vide, base-toi sur le "TITRE" et "L'ENTREPRISE". Ne donne pas 0 pour manque de texte si le titre correspond parfaitement au rôle recherché.

        Raisonnement : Décris ta décision de manière claire et concise.
        
        FORMAT DE RÉPONSE (JSON UNIQUEMENT) :
        [
          {{"id": 0, "score": 85, "reason": "Explication courte"}},
          ...
        ]
        """
        
        try:
            resp = await self.generate_response(prompt, json_mode=True, model=model)

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
