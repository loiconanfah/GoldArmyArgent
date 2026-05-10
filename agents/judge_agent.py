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
        target_loc = (profile.get("target_location") or "").lower()
        is_quebec = "quebec" in target_loc or "qu\u00e9bec" in target_loc or "montreal" in target_loc or "qc" in target_loc

        # CV profile — used for real skills matching when available
        cv_skills = profile.get("skills") or []
        cv_roles = profile.get("target_roles") or []
        cv_experience = profile.get("experience_years") or 0
        has_cv = bool(cv_skills or cv_roles)

        if has_cv:
            cv_section = f"""\n=== PROFIL CV DE L'UTILISATEUR ===\n- Comp\u00e9tences cl\u00e9s : {cv_skills[:15]}\n- Exp\u00e9rience : {cv_experience} ans\n- R\u00f4les dans le CV : {cv_roles}"""
            skills_rule = f"""2. CORRESPONDANCE CV / OFFRE (0-25 pts) :\n   - Les comp\u00e9tences du CV ({cv_skills[:5]}) correspondent aux exigences de l'offre \u2192 20-25 pts\n   - Correspondance partielle \u2192 10-19 pts\n   - Aucune correspondance \u2192 0-9 pts\n   - Description vide \u2192 12 pts (neutre)"""
        else:
            cv_section = "\n=== PROFIL CV === Non fourni \u2014 noter sans crit\u00e8re comp\u00e9tences."
            skills_rule = "2. CORRESPONDANCE CV (0-25 pts) : CV non fourni \u2192 attribuer 12 pts par d\u00e9faut."

        target_loc_display = profile.get('target_location', 'Non spécifié')
        prompt = f"""Tu es un recruteur expert. Note chaque offre d'emploi sur 100 selon 4 crit\u00e8res.
{cv_section}

=== RECHERCHE DE L'UTILISATEUR ===
- M\u00e9tier recherch\u00e9 (CRI\u00c8RE PRINCIPAL) : \"{search_query}\"
- Localisation cible : \"{target_loc_display}\"
- Type de contrat : {target_job_type.upper()}

=== GRILLE DE NOTATION (total = 100 pts) ===
1. PERTINENCE DU M\u00c9TIER (0-50 pts) \u2014 \u00c9LIMINATOIRE :
   - L'offre correspond directement au m\u00e9tier \"{search_query}\" \u2192 40-50 pts
   - L'offre est proche/similaire \u2192 20-39 pts
   - L'offre n'a AUCUN rapport avec \"{search_query}\" \u2192 0 pts (stop, ignorer les autres crit\u00e8res)

{skills_rule}

3. LOCALISATION (0-15 pts) :
   - Correspond exactement \u2192 15 pts
   - R\u00e9gion proche ou remote \u2192 10 pts
   - {"Offre 'Canada' seule sans province qu\u00e9b\u00e9coise \u2192 0 pts" if is_quebec else "Autre r\u00e9gion \u2192 5 pts"}

4. TYPE DE CONTRAT (0-10 pts) :
   - {"Stage/intern clairement indiqu\u00e9 \u2192 10 pts. Offre permanente \u2192 0 pts" if "stage" in target_job_type.lower() else "Offre permanente/CDI \u2192 10 pts. Stage uniquement \u2192 0 pts"}

=== OFFRES \u00c0 NOTER (ID = index 0 \u00e0 N-1) ===
{job_list_text}

=== R\u00c9PONSE JSON UNIQUEMENT ===
[{{\"id\": 0, \"score\": 82, \"reason\": \"Correspond bien \u00e0 {search_query}. Comp\u00e9tences CV align\u00e9es. Montr\u00e9al \u2713\"}}, ...]
Un objet par offre. Scores 0-100."""
        
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
