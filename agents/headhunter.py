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
                    model="gemini-3.1-pro-preview",
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
                    if url and "linkedin.com/in/" in url and "search" not in url:
                        if not url.startswith("http"):
                            url = "https://www.linkedin.com/in/" + url.split("/in/")[-1]
                        url = url.split("?")[0].strip("',\"<>")
                        if url not in seen:
                            seen.add(url)
                            out.append({"name": name or "Profil LinkedIn", "role": p.get("role") or "Décideur / RH", "linkedin_url": url, "snippet": f"Identifié pour {company_name}"})
                return out[:5]
            except Exception as e:
                logger.warning(f"[_gemini_search] Error: {e}")
                return []

        async def _ddg_search() -> List[Dict[str, Any]]:
            try:
                from tools.linkedin_scraper import linkedin_scraper
                scraped = await linkedin_scraper.find_hr_profiles(company_name, limit=5)
                out = []
                for p in scraped:
                    url = p.get("url", "")
                    if url:
                        # Allow both direct profile URLs and fallback search URLs
                        out.append({"name": p.get("name", "Profil LinkedIn"), "role": "RH / Recrutement", "linkedin_url": url.split("?")[0].rstrip("/") if "linkedin.com/in/" in url else url, "snippet": p.get("snippet", f"Profil pour {company_name}")})
                return out[:5]
            except Exception as e:
                logger.warning(f"[_ddg_search] Error: {e}")
                return []

        gemini_task = asyncio.create_task(_gemini_search())
        ddg_task = asyncio.create_task(_ddg_search())
        
        # Attendre les deux sources (Gemini 3.1 Pro avec Grounding peut prendre 20-60s)
        done, pending = await asyncio.wait([gemini_task, ddg_task], timeout=80)
        
        gemini_results = []
        ddg_results = []
        
        if gemini_task in done:
            try: 
                gemini_results = gemini_task.result()
                logger.info(f"Gemini a trouvé {len(gemini_results)} profils")
            except Exception as e: 
                logger.error(f"Erreur Gemini task: {e}")
        else:
            logger.warning("Gemini task a timeout (>45s)!")

        if ddg_task in done:
            try: ddg_results = ddg_task.result()
            except: pass
            
        # Fusionner les résultats en privilégiant les vrais profils
        final_profiles = []
        seen_urls = set()
        
        # Priorité 1 : Résultats Gemini (Grounding OSINT)
        for p in gemini_results:
            url = p.get("linkedin_url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                final_profiles.append(p)
                
        # Priorité 2 : Résultats DDG (Scraping) — seulement si ce ne sont pas des liens de recherche
        for p in ddg_results:
            url = p.get("linkedin_url", "")
            is_search_link = "linkedin.com/search" in url or "keywords=" in url
            if url and url not in seen_urls and not is_search_link:
                seen_urls.add(url)
                final_profiles.append(p)
                
        # Priorité 3 : Si toujours vide, mettre le lien de recherche en dernier recours
        if not final_profiles:
            for p in ddg_results:
                if "linkedin.com/search" in p.get("linkedin_url", "") or "Chercher" in p.get("name", ""):
                    final_profiles.append(p)
                    break
                    
        # Nettoyage des tâches en cours
        for t in [gemini_task, ddg_task]:
            if not t.done(): t.cancel()
            
        logger.success(f"💎 Sniper : {len(final_profiles)} profils identifiés.")
        return final_profiles[:8]
    
    async def generate_smart_cover_letter(self, company_name: str, job_title: str = "Poste ouvert", cv_text: str = "") -> Dict[str, Any]:
        """
        Génère une lettre de motivation 'Smart' en scrapant les dernières actus de la boîte.
        """
        logger.info(f"🗞️ Génération Smart Cover pour {company_name}")
        
        # 1. Rechercher les actualités récentes
        search_prompt = f"Trouve les 3 dernières actualités majeures (levée de fonds, nouveaux produits, recrutements, partenariats) concernant l'entreprise '{company_name}'."
        try:
            news_text, _ = await self.generate_with_sources(
                search_prompt,
                model="gemini-3.1-pro-preview",
                tools=[{"google_search": {}}],
                system="Journaliste d'affaires. Trouve des faits réels et récents."
            )
        except Exception as e:
            logger.error(f"Erreur scraping news: {e}")
            news_text = "Pas d'actualités récentes trouvées."

        # 2. Rédiger la lettre avec contexte candidat
        candidate_context = f"\nVoici mon profil (CV) pour orienter la rédaction :\n{cv_text}" if cv_text else ""
        
        writing_prompt = f"""
        Rédige une lettre de motivation COMPLÈTE et UNIQUE pour le poste de '{job_title}' chez '{company_name}'.
        {candidate_context}
        
        STRUCTURE DE LA LETTRE :
        1. EN-TÊTE : [Votre Nom] à [Lieu/Date].
        2. OBJET : Candidature au poste de {job_title}.
        3. ACCROCHE : Mentionne impérativement une de ces actualités de '{company_name}' pour montrer ton intérêt : {news_text}.
        4. CORPS (VOUS/MOI/NOUS) : 
           - Pourquoi l'entreprise m'attire (basé sur l'actu).
           - Ce que j'apporte (basé sur mon CV).
           - Ce que nous ferons ensemble.
        5. CONCLUSION : Appel à l'action pour un entretien.
        6. SIGNATURE : Cordialement, [Votre Nom].

        CONSIGNES :
        - Ne sois pas générique. Sois spécifique à {company_name}.
        - Ne retourne QUE le texte de la lettre, sans introduction ni blabla d'IA.
        - Pas de Markdown (# ou **).
        """
        try:
            letter, _ = await self.generate_with_sources(
                writing_prompt,
                model="gemini-3.1-pro-preview",
                system="Tu es un expert en copywriting A-List. Tu rédiges des lettres de motivation percutantes, uniques et structurées qui captent l'attention en 5 secondes. Tu fournis uniquement le texte final, prêt à l'emploi."
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
