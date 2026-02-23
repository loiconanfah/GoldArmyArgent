"""
Agent Headhunter : Spécialiste de la recherche de décideurs.
Utilise l'OSINT (Google Dorking via DDG) pour trouver les profils LinkedIn 
(RH, CEO, Lead Dev, Talent Acquisition) d'une entreprise spécifique.
"""
from typing import Dict, Any, List
from loguru import logger
import urllib.request
import urllib.parse
import json
import re
import ssl

from core.agent_base import BaseAgent
from tools.web_searcher import web_searcher

class HeadhunterAgent(BaseAgent):
    """Agent IA pour identifier et extraire des profils de décideurs."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "headhunter")
        kwargs.setdefault("name", "HeadhunterAgent")
        kwargs.setdefault("temperature", 0.3) # Basse température pour structurer l'OSINT
        super().__init__(**kwargs)

    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode requise par BaseAgent."""
        return {"status": "success", "message": "Headhunter Agent prêt."}

    async def act(self, command: Dict[str, Any]) -> str:
        """Méthode requise par BaseAgent."""
        return "Action completed"

    async def find_decision_makers(self, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Trouve les décideurs d'une entreprise via OSINT et Gemini.
        Returns:
            List[Dict] contenant: name, role, linkedin_url
        """
        company_name = params.get("company_name", "").strip()
        target_roles = params.get("target_roles", "HR OR Recruiter OR \"Talent Acquisition\" OR CTO OR CEO OR Director")
        
        if not company_name:
            logger.warning("Agent Headhunter a reçu une requête sans entreprise.")
            return []

        logger.info(f"🕵️‍♂️ Agent Headhunter: Recherche dynamique native Google Search (Gemini) pour '{company_name}'...")
        
        prompt = f"""
        Tu es un analyste OSINT expert en ressources humaines.
        Ta mission est de trouver 2 ou 3 profils LinkedIn exacts de décideurs (comme {target_roles}) travaillant actuellement chez l'entreprise '{company_name}'.
        
        UTILISE TON OUTIL DE RECHERCHE GOOGLE NATIVEMENT FOURNI (Google Search Grounding) pour exécuter une recherche:
        Exemple de requêtes que tu devrais lancer : 
        "profil linkedin directeur ressources humaines {company_name}"
        "profil linkedin talent acquisition {company_name}"
        
        Analyse les résultats de tes propres requêtes de recherche pour isoler UNIQUEMENT les vraies personnes.
        
        FORMAT DE SORTIE REQUIS STRICT :
        Renvoie UNIQUEMENT un tableau JSON structuré (format texte plat, SANS markdown ```json) :
        [
            {{"name":"Prénom Nom", "role":"Titre Exact", "linkedin_url":"https://ca.linkedin.com/in/..."}}
        ]
        
        Si aucun profil n'est trouvé, renvoie un tableau vide []. NE METS AUCUN TEXTE DE BAVARDAGE, JUSTE LE JSON VALIDE.
        """
        
        try:
            # On force le modèle gemini-2.0-flash qui supporte le Google Search Grounding nativement
            resp = await self.generate_response(
                prompt, 
                model="gemini-2.0-flash", 
                temperature=0.2,
                tools=[{"googleSearch": {}}]
            )
            
            clean_resp = resp.replace("```json", "").replace("```", "").strip()
            logger.debug(f"DEBUG GEMINI GROUNDING RAW:\n{clean_resp}")
            
            parsed_profiles = json.loads(clean_resp)
            logger.success(f"✅ {len(parsed_profiles)} profils décortiqués pour {company_name} par l'IA de Recherche !")
            return parsed_profiles
            
        except json.JSONDecodeError:
            logger.error("❌ Headhunter a renvoyé un JSON invalide. Tentative RegExp.")
            import re
            
            objects = []
            matches = re.finditer(r'\{[^{}]*"name"[^{}]*"role"[^{}]*"linkedin_url"[^{}]*\}', clean_resp, re.IGNORECASE)
            for m in matches:
                try:
                    obj_str = m.group(0)
                    obj_str = re.sub(r',\s*\}', '}', obj_str)
                    parsed_obj = json.loads(obj_str)
                    if parsed_obj.get('name') and parsed_obj.get('linkedin_url'):
                        objects.append(parsed_obj)
                except:
                    pass
            
            if objects:
                logger.success(f"✅ Fallback RegExp réussi : {len(objects)} profils sauvés !")
                return objects
                
            return []
        except Exception as e:
            logger.error(f"❌ Erreur critique Headhunter (Grounding): {e}")
            return []

# Instanciation globale
headhunter_agent = HeadhunterAgent()
