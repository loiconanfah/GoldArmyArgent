"""
Agent Headhunter — Extraction Deep OSINT de Profils LinkedIn.
Architecture 3 étapes:
  1. Gemini 2.0 Flash + Google Search Grounding → Identifier les noms des décideurs
  2. Gemini generate_with_sources (métadonnées) → Extraire les vraies URLs /in/ des sources grounding
  3. Gemini → Enrichir chaque profil (rôle, snippet) à partir des URLs réelles
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import urllib.parse
import json
import re
import asyncio

from core.agent_base import BaseAgent
from config.settings import settings


class HeadhunterAgent(BaseAgent):
    """Agent IA pour identifier et extraire des profils de décideurs."""

    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "headhunter")
        kwargs.setdefault("name", "HeadhunterAgent")
        kwargs.setdefault("temperature", 0.1)
        super().__init__(**kwargs)

    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}

    async def act(self, command: Dict[str, Any]) -> str:
        return "Action completed"

    # ─────────────────────────────────────────────────────────────────────────
    async def find_decision_makers(self, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Stratégie en 3 étapes pour obtenir de vraies URLs LinkedIn /in/ :
        1. Identifier les noms via Gemini Grounding
        2. Extraire les URLs source directes des métadonnées de Grounding 
        3. Enrichir les profils avec ces URLs réelles
        """
        company_name = params.get("company_name", "").strip()
        if not company_name:
            return []

        logger.info(f"🕵️ OSINT Headhunter pour: {company_name}")

        # ── ÉTAPE 1 + 2 : Grounding avec extraction des URLs sources ─────────
        # On utilise plusieurs requêtes ciblées pour maximiser les profils trouvés
        search_queries = [
            f'site:linkedin.com/in/ "{company_name}" recruiter OR "talent acquisition" OR "responsable RH" OR "HR manager"',
            f'site:linkedin.com/in/ "{company_name}" "directeur ressources humaines" OR "VP RH" OR "Chief Human Resources"',
        ]

        linkedin_profiles: List[Dict] = []  # {url, title, snippet}
        seen_urls: set = set()

        for search_q in search_queries:
            if len(linkedin_profiles) >= 6:
                break

            prompt = f"""
                Effectue une recherche Google pour exactement cette requête et retourne les résultats:
                {search_q}
                
                Retourne UNIQUEMENT un JSON tableau, chaque élément contient l'URL EXACTE du résultat Google, le titre et le snippet.
                Format: [{{"url":"URL EXACTE", "title":"Titre", "snippet":"Extrait"}}]
                N'invente pas d'URLs. Utilise UNIQUEMENT les URLs réelles des résultats de recherche Google.
            """

            try:
                # On bypasse UnifiedClient pour accéder directement à GeminiClient avec generate_with_sources
                from llm.gemini_client import GeminiClient
                gemini = GeminiClient()
                text_resp, source_urls = await gemini.generate_with_sources(
                    prompt,
                    model="gemini-2.0-flash",
                    temperature=0.0,
                    tools=[{"googleSearch": {}}]
                )
                logger.debug(f"Sources Grounding ({len(source_urls)} URLs): {source_urls[:5]}")

                # Filtrer uniquement les URLs LinkedIn /in/
                for url in source_urls:
                    match = re.search(r'https?://(?:\w+\.)?linkedin\.com/in/([\w\-]+)', url)
                    if match:
                        clean_url = f"https://www.linkedin.com/in/{match.group(1)}"
                        if clean_url not in seen_urls:
                            seen_urls.add(clean_url)
                            linkedin_profiles.append({
                                "linkedin_url": clean_url,
                                "title_raw": "",
                                "snippet_raw": ""
                            })

                # Si les URLs sources n'ont pas fourni de /in/ links, essayer le texte JSON retourné
                if not linkedin_profiles:
                    clean = text_resp.strip()
                    if "```json" in clean:
                        clean = clean.split("```json")[1].split("```")[0].strip()
                    elif "```" in clean:
                        clean = clean.split("```")[1].split("```")[0].strip()
                    try:
                        raw_list = json.loads(clean)
                        for item in raw_list:
                            url = item.get("url", "")
                            match = re.search(r'https?://(?:\w+\.)?linkedin\.com/in/([\w\-]+)', url)
                            if match:
                                clean_url = f"https://www.linkedin.com/in/{match.group(1)}"
                                if clean_url not in seen_urls:
                                    seen_urls.add(clean_url)
                                    linkedin_profiles.append({
                                        "linkedin_url": clean_url,
                                        "title_raw": item.get("title", ""),
                                        "snippet_raw": item.get("snippet", "")
                                    })
                    except Exception:
                        pass

            except Exception as e:
                logger.warning(f"Grounding avec sources: {e}")

        logger.info(f"🔗 {len(linkedin_profiles)} profils /in/ extraits des sources Google pour {company_name}")

        # ── ÉTAPE 3 : Enrichissement des profils trouvés ─────────────────────
        if linkedin_profiles:
            urls_text = "\n".join(f"- {p['linkedin_url']}" for p in linkedin_profiles[:5])
            enrich_prompt = f"""
            Tu es un expert OSINT RH.
            Voici une liste d'URLs de profils LinkedIn de personnes chez '{company_name}':
            {urls_text}
            
            Pour chaque URL, déduis le nom probable (depuis le slug URL), le rôle, et génère un snippet stratégique (15 mots max).
            Conserve les URLs EXACTEMENT comme fournies.
            
            Réponds UNIQUEMENT avec un tableau JSON (sans markdown):
            [{{"name":"Prénom Nom", "role":"Titre", "linkedin_url":"URL EXACTE", "snippet":"Résumé..."}}]
            """
            try:
                resp = await self.generate_response(enrich_prompt, model="gemini-2.0-flash", temperature=0.1)
                clean = resp.strip()
                if "```json" in clean:
                    clean = clean.split("```json")[1].split("```")[0].strip()
                elif "```" in clean:
                    clean = clean.split("```")[1].split("```")[0].strip()
                enriched = json.loads(clean)
                
                # Garantie finale: url doit contenir /in/
                final = []
                for e in enriched:
                    url = e.get("linkedin_url", "")
                    if "/in/" in url:
                        final.append(e)
                    else:
                        # chercher l'url original dans linkedin_profiles
                        if linkedin_profiles:
                            e["linkedin_url"] = linkedin_profiles[len(final)]["linkedin_url"]
                            final.append(e)

                logger.success(f"✅ {len(final)} profils enrichis avec URLs directes pour {company_name}")
                return final
            except Exception as ex:
                logger.warning(f"Enrichissement Gemini échoué ({ex}). Fallback profils bruts.")
                # Renvoie les URLs brutes avec nom déduit du slug
                return [{
                    "name": p["linkedin_url"].split("/in/")[-1].replace("-", " ").title(),
                    "role": "Décideur / Recruteur",
                    "linkedin_url": p["linkedin_url"],
                    "snippet": f"Profil LinkedIn identifié chez {company_name}"
                } for p in linkedin_profiles[:5]]

        # ── FALLBACK TOTAL : Gemini Grounding direct avec consigne ultra-stricte ─
        logger.warning(f"⚠️ Aucune URL /in/ extraite. Tentative Grounding final pour {company_name}...")
        fallback_prompt = f"""
        Recherche Google: site:linkedin.com/in/ "{company_name}" recruiter OR "talent acquisition"
        
        LISTE les résultats EXACTS trouvés sur Google (pas inventés).
        Retourne UNIQUEMENT un tableau JSON:
        [{{"name":"...", "role":"...", "linkedin_url":"https://www.linkedin.com/in/...", "snippet":"..."}}]
        
        RÈGLE ABSOLUE: linkedin_url doit contenir /in/. JAMAIS de lien générique.
        """
        try:
            resp = await self.generate_response(
                fallback_prompt,
                model="gemini-2.0-flash",
                temperature=0.0,
                tools=[{"googleSearch": {}}]
            )
            clean = resp.strip()
            if "```json" in clean: clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean: clean = clean.split("```")[1].split("```")[0].strip()
            profiles = json.loads(clean)
            
            validated = []
            for p in profiles:
                url = p.get("linkedin_url", "")
                if "/in/" in url:
                    validated.append(p)
            
            logger.success(f"✅ Fallback Grounding: {len(validated)} profils pour {company_name}")
            return validated
        except Exception as e:
            logger.error(f"❌ Headhunter totalement échoué: {e}")
            return []


# Instance globale
headhunter_agent = HeadhunterAgent()
