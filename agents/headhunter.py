"""
Agent Sniper 7.1 — Ultra-Précision Gemini 3.1 Pro.
Architecture "Direct Vision" + parallélisation pour vitesse maximale.
"""
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
import json
import re

from core.agent_base import BaseAgent

class HeadhunterAgent(BaseAgent):
    """Agent IA Sniper 7.1 : L'élite du recrutement via Gemini 3.1 Pro."""

    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "headhunter")
        kwargs.setdefault("name", "Sniper 7.1 (Gemini 3.1 Pro)")
        kwargs.setdefault("temperature", 0.0)
        super().__init__(**kwargs)

    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse des critères."""
        return {"company_name": user_input.get("company_name", "").strip()}

    async def act(self, command: Dict[str, Any]) -> str:
        """Exécute la recherche."""
        company = command.get("company_name")
        if not company: return "Entreprise non spécifiée."
        
        results = await self.find_decision_makers({"company_name": company})
        return json.dumps(results, ensure_ascii=False)

    async def find_decision_makers(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sniper 7.1 Engine (vitesse optimale) :
        Gemini + DDG lancés en parallèle → le premier à retourner des résultats gagne.
        """
        company_name = params.get("company_name", "").strip()
        target_roles = params.get("target_roles", [])
        roles_str = ", ".join(target_roles) if target_roles else "RH, Recrutement, CEO, CTO"
        if not company_name:
            return []

        logger.info(f"🎯 Sniper 7.1 (parallèle) pour: {company_name}")

        async def _gemini_search() -> List[Dict[str, Any]]:
            search_prompt = f"""Utilise Google Search pour trouver 5 profils LinkedIn de décideurs ({roles_str}) chez '{company_name}'. Retourne UNIQUEMENT un tableau JSON: [{{"name":"","role":"","linkedin_url":"https://linkedin.com/in/..."}}]"""
            try:
                json_response, sources = await self.generate_with_sources(
                    search_prompt,
                    model="gemini-2.0-flash",
                    tools=[{"google_search": {}}],
                    json_mode=True,
                    system=f"Expert OSINT LinkedIn. Trouve des profils réels chez {company_name}. Règle: URL complète."
                )
                raw = re.sub(r"^[^{\[\]]*", "", json_response.strip())
                raw = re.sub(r"[^{\[\]]*$", "", raw)
                profiles = json.loads(raw) if raw else []
                if not isinstance(profiles, list):
                    profiles = [profiles] if isinstance(profiles, dict) else []
                seen = set()
                out = []
                for p in profiles:
                    if not isinstance(p, dict):
                        continue
                    url = (p.get("linkedin_url") or p.get("url") or "").strip()
                    name = (p.get("name") or "").strip()
                    if sources and (not url or "linkedin.com/in/" not in url):
                        for s in sources:
                            if "/in/" in s:
                                url = s.split("?")[0].rstrip("/")
                                break
                    if url and "linkedin.com/in/" in url:
                        if not url.startswith("http"):
                            url = "https://www.linkedin.com/in/" + url.split("/in/")[-1]
                        url = url.split("?")[0].strip("',\"<>")
                        if url not in seen:
                            seen.add(url)
                            out.append({"name": name or "Profil LinkedIn", "role": p.get("role") or "Décideur / RH", "linkedin_url": url, "snippet": f"Identifié pour {company_name}"})
                return out[:5]
            except Exception:
                return []

        async def _ddg_search() -> List[Dict[str, Any]]:
            try:
                from tools.linkedin_scraper import linkedin_scraper
                scraped = await linkedin_scraper.find_hr_profiles(company_name, limit=5)
                out = []
                for p in scraped:
                    url = p.get("url", "")
                    if url and "linkedin.com/in/" in url:
                        out.append({"name": p.get("name", "Profil LinkedIn"), "role": "RH / Recrutement", "linkedin_url": url.split("?")[0].rstrip("/"), "snippet": p.get("snippet", f"Profil pour {company_name}")})
                    elif "linkedin.com/search" in url:
                        out.append({"name": p.get("name", f"Recherche - {company_name}"), "role": "Lien de recherche", "linkedin_url": url, "snippet": "Cliquez pour voir sur LinkedIn."})
                return out[:5]
            except Exception:
                return []

        gemini_task = asyncio.create_task(_gemini_search())
        ddg_task = asyncio.create_task(_ddg_search())
        done, pending = await asyncio.wait([gemini_task, ddg_task], return_when=asyncio.FIRST_COMPLETED, timeout=15)
        for t in done:
            try:
                r = t.result()
                if r:
                    for p in pending:
                        p.cancel()
                    logger.success(f"💎 Sniper : {len(r)} profils (résultat rapide)")
                    return r
            except Exception:
                pass
        if pending:
            done2, _ = await asyncio.wait(pending, timeout=20)
            for t in done2:
                try:
                    r = t.result()
                    if r:
                        return r
                except Exception:
                    pass
        return []
    
    async def generate_smart_cover_letter(self, company_name: str, job_title: str = "Poste ouvert") -> Dict[str, Any]:
        """
        Génère une lettre de motivation 'Smart' en scrapant les dernières actus de la boîte.
        """
        logger.info(f"🗞️ Génération Smart Cover pour {company_name}")
        
        # 1. Rechercher les actualités récentes
        search_prompt = f"Trouve les 3 dernières actualités majeures (levée de fonds, nouveaux produits, partenariats) concernant l'entreprise '{company_name}'."
        try:
            news_text, _ = await self.generate_with_sources(
                search_prompt,
                model="gemini-2.0-flash",
                tools=[{"google_search": {}}],
                system="Journaliste d'affaires. Trouve des faits réels et récents."
            )
        except Exception as e:
            logger.error(f"Erreur scraping news: {e}")
            news_text = "Pas d'actualités récentes trouvées."

        # 2. Rédiger la lettre
        writing_prompt = f"""
        Rédige une lettre de motivation percutante pour le poste de '{job_title}' chez '{company_name}'.
        UTILISE les actualités suivantes pour montrer que je suis l'entreprise de près:
        {news_text}
        
        Ton: Professionnel, enthousiaste, tourné vers l'avenir.
        Format: Markdown.
        """
        try:
            letter, _ = await self.generate_with_sources(
                writing_prompt,
                model="gemini-2.0-flash",
                system="Expert en recrutement et copywriting. Ta mission est de rendre le candidat irrésistible."
            )
            return {
                "news": news_text,
                "letter": letter
            }
        except Exception as e:
            logger.error(f"Erreur génération lettre: {e}")
            return {"error": str(e)}

# Instance globale unique
headhunter_agent = HeadhunterAgent()
