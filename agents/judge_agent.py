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
            "chunk_size": 50
        }

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue les offres en lots avec Gemini 2.0 Flash (Mode Hyper-Vitesse)."""
        jobs = plan.get("jobs", [])
        cv_profile = plan.get("cv_profile", {})
        
        # Lots plus grands + parallélisme massif : 50 offres/lot, jusqu'à 30 lots en parallèle
        chunk_size = 50
        
        if not jobs:
            return {"success": True, "evaluated_jobs": []}
            
        logger.info(f"⚖️ Judge analyse {len(jobs)} offres (Gemini Flash, lots de {chunk_size} en parallèle)...")
        
        chunks = [jobs[i:i + chunk_size] for i in range(0, len(jobs), chunk_size)]
        
        # Semaphore réduit à 3 pour respecter le quota Gemini Flash (évite les 429)
        semaphore = asyncio.Semaphore(3)


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

        target_job_type = profile.get("target_job_type") or profile.get("target_level") or "emploi"
        search_query = (profile.get("search_query") or "").strip()
        search_query_lower = search_query.lower()
        target_loc = (profile.get("target_location") or "").lower()
        is_quebec = "quebec" in target_loc or "québec" in target_loc or "montreal" in target_loc or "qc" in target_loc

        prompt = f"""Tu es un expert en recrutement. Note chaque offre d'emploi sur 100 en fonction de sa pertinence pour la recherche de l'utilisateur.

=== RECHERCHE DE L'UTILISATEUR ===
- Métier recherché (PRIORITÉ ABSOLUE): "{search_query}"
- Localisation cible : "{profile.get('target_location', 'Non spécifié')}"
- Type de contrat : {target_job_type.upper()}
- Rôles du CV (contexte secondaire seulement) : {profile.get('target_roles', [])}

=== RÈGLES DE NOTATION ===
1. PERTINENCE DU MÉTIER (critère principal, 0-60 pts) :
   - L'offre correspond directement au métier "{search_query}" → 50-60 pts
   - L'offre est proche/similaire → 30-49 pts
   - L'offre n'a AUCUN rapport avec "{search_query}" → 0 pts IMMÉDIATEMENT
   
2. LOCALISATION (0-25 pts) :
   - Localisation correspond exactement → 25 pts
   - Région proche / remote → 15 pts
   - Autre pays/région → 5 pts
   - {"Offre marquée 'Canada' sans province québécoise précise → 0 pts" if is_quebec else "Localisation non précisée → 10 pts"}

3. TYPE DE CONTRAT (0-15 pts) :
   - {"Offre = stage/intern/stagiaire → 15 pts. Offre permanente sans 'stage' → 0 pts" if "stage" in target_job_type.lower() else "Offre permanente/CDI → 15 pts. Offre uniquement stage → 0 pts"}

=== OFFRES À NOTER (ID = index 0 à N-1) ===
{job_list_text}

=== RÉPONSE JSON UNIQUEMENT ===
[{{"id": 0, "score": 85, "reason": "Correspond bien à {search_query}..."}}, {{"id": 1, "score": 0, "reason": "Métier sans rapport avec {search_query}"}}, ...]
Exactement un objet par offre. Scores de 0 à 100."""
        
        try:
            resp = await self.generate_response(prompt, json_mode=True, model=model)

            # Guard : si Gemini retourne None ou vide (rate limit épuisé, safety filter...)
            if not resp:
                logger.warning(f"⚠️ Judge: Réponse Gemini vide (None ou ''), lot ignoré. Retour fail-safe.")
                return jobs

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

            # Filet de sécurité universel : règles strictes indépendantes du métier recherché
            target_loc = (profile.get("target_location") or "").lower()
            search_q = (profile.get("search_query") or "").lower()
            job_type = (profile.get("target_job_type") or profile.get("target_level") or "emploi").lower()
            user_wants_stage = job_type == "stage" or any(w in search_q for w in ["stage", "intern", "stagiaire", "internship"])
            is_quebec_target = any(x in target_loc for x in ["quebec", "québec", "montreal", ", qc"])
            stage_intern_keywords = ["stage", "intern", "stagiaire", "internship"]

            for job in jobs:
                loc = (job.get("location") or "").strip().lower()
                title = (job.get("title") or "").lower()
                desc = (job.get("description") or "")[:400].lower()
                job_type_field = (job.get("job_type") or "").lower()
                text = f"{title} {desc} {job_type_field}"

                # Règle 1 : Québec ciblé → forcer 0 si localisation = "Canada" seul sans province québécoise
                if is_quebec_target and loc.strip() == "canada":
                    job["match_score"] = 0
                    job["match_justification"] = "Localisation « Canada » seule sans province québécoise."

                # Règle 2 : Stage ciblé → l'offre DOIT être un stage/intern
                if user_wants_stage and job.get("match_score", 0) > 0:
                    if not any(kw in text for kw in stage_intern_keywords):
                        job["match_score"] = 0
                        job["match_justification"] = "Recherche stage : l'offre n'est pas un stage/intern."

        except Exception as e:
            logger.error(f"🔴 Judge AI Error: {e}")

        return jobs
