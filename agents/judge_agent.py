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
        
        # Traitement simultané : jusqu'à 30 appels Gemini en parallèle pour la vitesse
        semaphore = asyncio.Semaphore(30)


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
        search_query = (profile.get("search_query") or "").strip().lower()
        target_loc = (profile.get("target_location") or "").lower()
        is_quebec = "quebec" in target_loc or "québec" in target_loc or "montreal" in target_loc or "qc" in target_loc
        is_dev_search = any(w in search_query for w in ["dev", "developpeur", "developer", "logiciel", "software", "programmation", "programming", "informatique", "web", "frontend", "backend"])

        prompt = f"""Tu es un Judge recrutement. Note chaque offre sur 100. APPLIQUE D'ABORD LES 3 RÈGLES ÉLIMINATOIRES (score 0 obligatoire), puis score le reste.

=== RÈGLES ÉLIMINATOIRES (score 0 SANS EXCEPTION) ===
A) LOCALISATION CIBLE = QUÉBEC/Montreal/QC : Si le champ LOC de l'offre est exactement "Canada" (sans Québec, QC, Montreal, ou ville québécoise) → score 0. L'utilisateur veut le Québec, pas le Canada entier.
B) RÔLE : Si la recherche ou le profil vise DÉVELOPPEMENT LOGICIEL / SOFTWARE (dev, programmation, software) : offres en mécanique, formation/RH, relations industrielles, génie manufacturier, "Controls Engineering" (sans software), maintenance, logistique → score 0.
C) TYPE CONTRAT (PRIORITAIRE) :
   - Si l'utilisateur cherche un STAGE : l'offre DOIT être explicitement un stage/intern (TITRE ou DESC contient stage, intern, stagiaire, internship). Sinon → score 0. Les offres CDI, permanent, full-time sans "stage/intern/stagiaire" = 0.
   - Si l'utilisateur cherche un EMPLOI (CDI) : les offres uniquement "Stage" ou "Intern" sans poste permanent = 0.

=== BON SCORE (70-100) ===
- Offre AU QUÉBEC (LOC contient Québec, QC, Montreal ou ville du Québec) ET métier = développement logiciel / software / programmation → score 70 à 100 selon adéquation.
- Description vide mais TITRE = dev/programmation et LOC = Québec → minimum 70.

=== PROFIL & RECHERCHE ===
- Recherche utilisateur (mots-clés) : "{search_query or 'non fourni'}"
- Localisation cible : "{profile.get('target_location')}"
- Type contrat recherché : {target_job_type.upper()} — Si STAGE : ne garder QUE les offres dont le titre ou la description indique clairement stage/intern/stagiaire/internship.
- Rôles visés : {profile.get('target_roles')}
- Compétences : {profile.get('skills')}

=== OFFRES (ID = index 0 à N-1) ===
{job_list_text}

=== RÉPONSE (JSON uniquement, un objet par offre) ===
[{{"id": 0, "score": 85, "reason": "..."}}, {{"id": 1, "score": 0, "reason": "..."}}, ...]
Exactement un objet par offre. Pas d'oubli."""
        
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

            # Filet de sécurité : forcer 0 si le LLM a laissé passer des offres non conformes
            target_loc = (profile.get("target_location") or "").lower()
            search_q = (profile.get("search_query") or "").lower()
            job_type = (profile.get("target_job_type") or profile.get("target_level") or "emploi").lower()
            user_wants_stage = job_type == "stage" or any(w in search_q for w in ["stage", "intern", "stagiaire", "internship"])
            is_quebec_target = any(x in target_loc for x in ["quebec", "québec", "montreal", ", qc"])
            is_dev_search = any(w in search_q for w in ["dev", "developpeur", "developer", "logiciel", "software", "programmation", "programming"])
            non_dev_keywords = ["mécanique", "mechanic", "formation", "rh", "relations industrielles", "manufacturing engineering", "controls engineering", "ordnance", "maintenance "]
            stage_intern_keywords = ["stage", "intern", "stagiaire", "internship"]

            for job in jobs:
                loc = (job.get("location") or "").strip().lower()
                title = (job.get("title") or "").lower()
                desc = (job.get("description") or "")[:400].lower()
                job_type_field = (job.get("job_type") or "").lower()
                text = f"{title} {desc} {job_type_field}"

                if is_quebec_target and loc == "canada" and "quebec" not in loc and "qc" not in loc and "montreal" not in loc:
                    job["match_score"] = 0
                    job["match_justification"] = "Localisation « Canada » seule : hors Québec."
                if is_dev_search and any(kw in title or kw in desc for kw in non_dev_keywords):
                    job["match_score"] = 0
                    job["match_justification"] = (job.get("match_justification") or "") + " [Hors dev: mécanique/formation/manufacturing.]"
                # Utilisateur veut un STAGE : l'offre doit être clairement un stage/intern, sinon 0
                if user_wants_stage and job.get("match_score", 0) > 0:
                    if not any(kw in text for kw in stage_intern_keywords):
                        job["match_score"] = 0
                        job["match_justification"] = "Recherche stage : l'offre n'est pas un stage/intern."

        except Exception as e:
            logger.error(f"🔴 Judge AI Error: {e}")

        return jobs
