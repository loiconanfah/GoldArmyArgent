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
            search_prompt = f"""Fais une recherche web approfondie via Google Search pour identifier au moins 5 à 8 vrais profils LinkedIn de décideurs majeurs (RH, Recrutement, CEO, CTO, COO, Directeurs, Talent Acquisition) actuels travaillant chez '{company_name}'.
Tu dois OBLIGATOIREMENT fournir l'URL directe de leur profil LinkedIn (commençant par https://www.linkedin.com/in/). Ne mets pas de liens de recherche.
Retourne ta réponse UNIQUEMENT sous la forme d'un tableau JSON brut, sans wrapper:
[
  {{"name": "Nom Prénom", "role": "Titre exact", "linkedin_url": "https://www.linkedin.com/in/..."}}
]"""
            try:
                json_response, sources = await self.generate_with_sources(
                    search_prompt,
                    model="gemini-2.0-flash",
                    tools=[{"google_search": {}}],
                    system=f"Expert OSINT LinkedIn. Trouve au moins 5 à 8 décideurs réels chez {company_name}. Règle absolue: URL directe du profil."
                )
                raw = re.sub(r"^[^{\[\]]*", "", json_response.strip())
                raw = re.sub(r"[^{\[\]]*$", "", raw)
                logger.debug(f"[_gemini_search] raw JSON extracted: {raw[:300]}")
                try:
                    profiles = json.loads(raw) if raw else []
                except Exception as je:
                    logger.error(f"[_gemini_search] JSON parse error: {je}")
                    profiles = []
                    
                # Unwrap si le JSON est un objet contenant une liste (ex: {"decision_makers": [...]})
                if isinstance(profiles, dict):
                    for v in profiles.values():
                        if isinstance(v, list):
                            profiles = v
                            break
                    if isinstance(profiles, dict):
                        profiles = [profiles]
                elif not isinstance(profiles, list):
                    profiles = []
                    
                seen = set()
                out = []
                used_sources = set()
                import urllib.parse
                
                async def _find_profile_url(person_name: str) -> Optional[str]:
                    try:
                        import urllib.request, urllib.parse, ssl
                        from bs4 import BeautifulSoup
                        ctx = ssl._create_unverified_context()
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                            "Accept-Language": "fr,fr-FR;q=0.8,en;q=0.5,en-US;q=0.3"
                        }
                        q = f'site:linkedin.com/in/ "{person_name}" "{company_name}"'
                        encoded = urllib.parse.quote_plus(q)
                        req = urllib.request.Request(f"https://lite.duckduckgo.com/lite/?q={encoded}", headers=headers)
                        loop = asyncio.get_event_loop()
                        html = await asyncio.wait_for(
                            loop.run_in_executor(None, lambda: urllib.request.urlopen(req, context=ctx, timeout=5).read().decode()),
                            timeout=7
                        )
                        soup = BeautifulSoup(html, "html.parser")
                        for a in soup.find_all("a", href=True):
                            href = a.get("href", "")
                            if "uddg=" in href:
                                try: href = urllib.parse.unquote(href.split("uddg=")[-1].split("&")[0])
                                except: pass
                            if "linkedin.com/in/" in href and "search" not in href and "dir/" not in href:
                                clean = href.split("?")[0].rstrip("/")
                                if not clean.startswith("http"):
                                    clean = "https://www.linkedin.com/in/" + clean.split("/in/")[-1]
                                return clean
                    except Exception as le:
                        logger.debug(f"[_find_profile_url] Failed for {person_name}: {le}")
                    return None
                    
                valid_candidates = []
                for p in profiles:
                    if not isinstance(p, dict): continue
                    name = (p.get("name") or "").strip()
                    if not name or name.lower() in ["nom prénom", "inconnu", "non spécifié"]: continue
                    url = (p.get("linkedin_url") or p.get("url") or "").strip()
                    valid_candidates.append((name, p.get("role"), url))
                    
                async def _resolve_candidate(name: str, role: str, url: str) -> Dict[str, Any]:
                    is_direct = url and "linkedin.com/in/" in url and "search" not in url
                    
                    # 1. Correspondance sur les sources de Grounding
                    if sources and not is_direct:
                        name_slugs = [part.lower() for part in name.split() if len(part) > 2]
                        for s in sources:
                            if "/in/" in s and "search" not in s and s not in used_sources:
                                s_clean = s.split("?")[0].rstrip("/")
                                if any(slug in s_clean.lower() for slug in name_slugs):
                                    url = s_clean
                                    used_sources.add(s)
                                    is_direct = True
                                    break
                                    
                    # 2. Recherche web instantanée du lien direct si toujours manquant
                    if not is_direct:
                        direct_url = await _find_profile_url(name)
                        if direct_url:
                            url = direct_url
                            is_direct = True
                            
                    # 3. Validation de l'URL directe ou fallback sur lien ciblé
                    if is_direct:
                        if not url.startswith("http"):
                            url = "https://www.linkedin.com/in/" + url.split("/in/")[-1]
                        url = url.split("?")[0].strip("',\"<>")
                    else:
                        safe_query = urllib.parse.quote_plus(f"{name} {company_name}")
                        url = f"https://www.linkedin.com/search/results/people/?keywords={safe_query}"
                        
                    return {
                        "name": name,
                        "role": role or "Décideur / RH",
                        "linkedin_url": url,
                        "snippet": f"Identifié pour {company_name}"
                    }
                    
                resolved = await asyncio.gather(*[_resolve_candidate(n, r, u) for n, r, u in valid_candidates])
                
                for res in resolved:
                    u = res["linkedin_url"]
                    if u not in seen:
                        seen.add(u)
                        out.append(res)
                        
                return out[:8]
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
            
        # Priorité absolue d'affichage : les liens directs LinkedIn en tête de liste
        final_profiles.sort(key=lambda x: 0 if "linkedin.com/in/" in x.get("linkedin_url", "") and "search" not in x.get("linkedin_url", "") else 1)
            
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
                model="gemini-2.0-flash",
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
                model="gemini-2.0-flash",
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
