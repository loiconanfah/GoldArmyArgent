"""
Agent Sniper 7.1 — Ultra-Précision Gemini 3.1 Pro.
Architecture "Direct Vision" (Single-Pass) : Gemini cherche et structure en une seule opération.
"""
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
        Sniper 7.1 Engine (Direct Vision) :
        1. Single-Pass Execution : Gemini 3.1 Pro reçoit l'outil Google Search.
        2. Direct Structuring : Gemini traite les résultats bruts et renvoie DIRECTEMENT le JSON.
        """
        company_name = params.get("company_name", "").strip()
        if not company_name: return []

        logger.info(f"🎯 Sniper 7.1 Direct Vision pour: {company_name}")

        # PROMPT DE VISION DIRECTE (Single-Pass Grounding + JSON)
        search_prompt = f"""
        Utilise Google Search pour trouver 5 profils personnels LinkedIn de décideurs (RH, Recrutement, Direction, CEO, CTO) travaillant ACTUELLEMENT chez '{company_name}'.
        
        RÈGLES CRITIQUES :
        1. Tu dois extraire l'URL LinkedIn EXACTE et COMPLÈTE (ex: https://www.linkedin.com/in/nom-prenom-123456).
        2. Ne jamais inventer ou tronquer les IDs numériques à la fin des URLs.
        3. Retourne UNIQUEMENT un tableau JSON d'objets.
        
        FORMAT JSON :
        [
          {{
            "name": "Nom complet",
            "role": "Poste précis chez {company_name}",
            "linkedin_url": "URL /in/ complète"
          }}
        ]
        """
        
        try:
            # Sniper 7.1 Vision : Gemini 3.1 Pro fait Tout en une fois
            json_response, sources = await self.generate_with_sources(
                search_prompt,
                model="gemini-3.1-pro-preview",
                tools=[{"google_search": {}}],
                json_mode=True,
                system=f"Tu es un expert OSINT LinkedIn. Trouve des profils réels chez {company_name}. Règle d'or: Copie l'URL complète avec ses ID numériques."
            )
            
            profiles = json.loads(json_response)
            final_profiles = []
            seen_urls = set()

            for p in profiles:
                if not isinstance(p, dict): continue
                url = (p.get("linkedin_url") or "").strip()
                name = (p.get("name") or "").strip()
                
                # RECOVERY LOGIC : Substitution si l'URL est courte et qu'on a une meilleure URL dans les sources
                if sources and (not "linkedin.com/in/" in url or len(url.split("/in/")[-1]) < 3):
                    name_parts = [part.lower() for part in name.split() if len(part) >= 2]
                    for s_url in sources:
                        if "/in/" in s_url:
                            s_url_clean = s_url.split("?")[0].rstrip("/")
                            if all(part in s_url_clean.lower() for part in name_parts):
                                url = s_url
                                break
                
                # Final Sanitization
                if url and "linkedin.com/in/" in url:
                    if not url.startswith("http"):
                        url = "https://www.linkedin.com/in/" + url.split("/in/")[-1]
                    url = url.split("?")[0].strip("',\"<>")
                    
                    if len(name) > 2 and url not in seen_urls:
                        seen_urls.add(url)
                        final_profiles.append({
                            "name": name,
                            "role": p.get("role") or "Decision Maker",
                            "linkedin_url": url,
                            "snippet": f"Identifié via Sniper Direct-Vision pour {company_name}"
                        })

            logger.success(f"💎 Sniper Direct-Vision : {len(final_profiles)} profils validés.")
            return final_profiles[:5]

        except Exception as e:
            logger.error(f"❌ Erreur Fatale Sniper : {e}")
            return []

# Instance globale unique
headhunter_agent = HeadhunterAgent()
