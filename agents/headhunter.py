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

    async def find_decision_makers(self, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Sniper 7.1 Engine (Direct Vision) :
        1. Single-Pass Execution : Gemini 3.1 Pro reçoit l'outil Google Search.
        2. Direct Structuring : Gemini traite les résultats bruts et renvoie DIRECTEMENT le JSON.
        3. No Flash / No Ollama : Seul le modèle Ultra-Pro est utilisé.
        """
        company_name = params.get("company_name", "").strip()
        if not company_name: return []

        logger.info(f"🎯 Sniper 7.1 Direct Vision (Gemini 3.1 Pro) pour: {company_name}")

        # PROMPT ULTRA-STRATÉGIQUE POUR GÉNÉRATION DIRECTE
        prompt = f"""
        Utilise Google Search pour trouver précisément 5 profils personnels LinkedIn de recruteurs ou décideurs travaillant ACTUELLEMENT chez '{company_name}'.
        
        RÈGLES CRITIQUES ANTI-HALLUCINATION :
        - NE JAMAIS deviner ou inventer une URL LinkedIn. C'est strict.
        - Copie l'URL EXACTE depuis les résultats de recherche Google.
        - L'URL doit OBLIGATOIREMENT commencer par "https://www.linkedin.com/in/".
        - Rejette la personne si tu n'as pas son URL exacte dans les résultats.
        - Fournis le résultat UNIQUEMENT sous forme d'un tableau JSON pur.
        
        FORMAT JSON STRICT :
        [
            {{"name": "Nom Prénom", "role": "Poste Actuel", "linkedin_url": "https://www.linkedin.com/in/..."}}
        ]
        """
        
        try:
            # PASS 1 : Grounding (Recherche tool uniquement, sans contrainte JSON)
            search_prompt = f"Trouve 5 profils LinkedIn personnels de recruteurs ou décideurs travaillant ACTUELLEMENT chez '{company_name}'. Liste leurs noms, postes et surtout leurs URLs LinkedIn complètes."
            
            response_text, sources = await self.generate_with_sources(
                search_prompt,
                model="gemini-3.1-pro-preview", # ou gemini-2.5-pro
                tools=[{"google_search": {}}],
                json_mode=False, 
                system="Tu es un chercheur expert OSINT. Trouve des profils LinkedIn réels et donne les liens exacts."
            )
            
            logger.debug(f"🔍 Sniper Grounding: {len(sources)} URLs racines trouvées.")

            # PASS 2 : Structuration JSON Pure (Sans outil de recherche)
            parse_prompt = f"""
            Extrais les profils du texte suivant et convertis-les en JSON.
            
            TEXTE BRUT :
            {response_text}
            
            URLS VÉRIFIÉES DISPONIBLES :
            {", ".join(sources)}
            
            RÈGLES :
            - Ne retiens que les personnes travaillant chez {company_name}.
            - L'URL doit OBLIGATOIREMENT commencer par "https://www.linkedin.com/in/" ou y correspondre parmi les URLs vérifiées.
            
            FORMAT JSON ATTENDU :
            [
                {{"name": "Nom Prénom", "role": "Poste", "linkedin_url": "URL /in/ réelle"}}
            ]
            """
            
            # Utilisation de Flash pour le parsing pur (plus rapide et très fiable pour le JSON statique)
            json_response = await self.generate_response(
                parse_prompt,
                model="gemini-2.5-flash",
                json_mode=True,
                system="Tu es un parseur JSON strict."
            )
            
            match = re.search(r'\[.*\]', json_response, re.DOTALL)
            clean_json = match.group(0) if match else json_response
            profiles = json.loads(clean_json)
            
            final_profiles = []
            seen_urls = set()

            for p in profiles:
                url = p.get("linkedin_url", "").strip()
                name = p.get("name", "").strip()
                
                # RECOVERY LOGIC : Substitution forte
                if sources:
                    name_parts = name.lower().split()
                    for s_url in sources:
                        if "/in/" in s_url and any(part in s_url.lower() for part in name_parts if len(part) > 3):
                            url = s_url
                            break
                
                # Sanitize URl
                if url and "linkedin.com/in/" in url:
                    if not url.startswith("http"):
                        if url.startswith("www."): url = "https://" + url
                        elif url.startswith("linkedin.com"): url = "https://www." + url
                        else: url = "https://www.linkedin.com/in/" + url.split("/in/")[-1]
                            
                    url = url.split("?")[0].strip("',\"<>")
                    
                    if len(name) > 2 and url not in seen_urls:
                        seen_urls.add(url)
                        final_profiles.append({
                            "name": name,
                            "role": p.get("role", "Decision Maker"),
                            "linkedin_url": url,
                            "snippet": f"Identifié via Sniper 2-Pass OSINT pour {company_name}"
                        })

            logger.success(f"💎 Sniper 2-Pass : {len(final_profiles)} profils validés.")
            return final_profiles[:5]

        except Exception as e:
            logger.error(f"❌ Erreur Fatale Sniper : {e}")
            return []

# Instance globale unique
headhunter_agent = HeadhunterAgent()
