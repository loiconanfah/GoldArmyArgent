"""
Agent spécialisé dans la rédaction de courriels d'approche (Networking / Cold Email).
Génère des messages sur-mesure basés sur le profil du candidat et les infos de l'entreprise.
"""
from typing import Dict, Any
from loguru import logger
from core.agent_base import BaseAgent

class NetworkAgent(BaseAgent):
    """Agent IA pour rédiger des courriels d'approche RH ciblés."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "networker")
        kwargs.setdefault("name", "NetworkAgent")
        kwargs.setdefault("temperature", 0.7) # Un peu de créativité pour l'écriture
        super().__init__(**kwargs)

    async def draft_email(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère un e-mail d'approche.
        
        Args:
            params: Dict contenant:
                - company_name (str)
                - company_description (str)
                - hr_name (str, optionnel)
                - cv_text (str)
                - request_type (str): "stage" ou "emploi"
                - target_domain (str, optionnel): ex "Développement Front-End"
        """
        company_name = params.get("company_name", "l'entreprise")
        company_description = params.get("company_description", "")
        hr_name = params.get("hr_name", "")
        cv_text = params.get("cv_text", "CV non fourni")
        request_type = params.get("request_type", "emploi").lower()
        target_domain = params.get("target_domain", "")
        
        logger.info(f"📧 Rédaction courriel d'approche pour {company_name} ({request_type})")
        
        greeting = f"Bonjour {hr_name}," if hr_name else "Bonjour,"
        
        context_block = f"""
        CONTEXTE DE L'ENTREPRISE CIBLE:
        Nom: {company_name}
        Description: {company_description}
        
        PROFIL DU CANDIDAT (CV):
        {cv_text[:3000]}
        
        OBJECTIF DE LA DÉMARCHE:
        Type de demande: Recherche de {request_type}
        """
        if target_domain:
            context_block += f"Domaine visé: {target_domain}\n"
            
        prompt = f"""
        Tu es un expert en communication professionnelle et recrutement. 
        Ton but est d'écrire un "cold email" (courriel d'approche à froid) extrêmement convaincant, naturel et percutant.
        Le candidat écrit au recruteur/RH de l'entreprise ciblée.
        
        {context_block}
        
        RÈGLES DE RÉDACTION:
        1. Formule d'appel: Utilise obligatoirement "{greeting}".
        2. Tonalité: Professionnelle, dynamique, audacieuse mais polie. Ni trop formel, ni familier.
        3. Structure: 
           - 1 phrase d'accroche (montrer qu'on connaît l'entreprise).
           - 2 phrases sur l'offre de valeur du candidat (basé sur le CV).
           - 1 phrase claire précisant la demande ({request_type}).
           - Appel à l'action (Call to Action) simple (ex: un appel de 10 min).
        4. Longueur: MAXIMUM 150 mots. Les RH n'ont pas le temps de lire des romans.
        5. Spécificité: Le courriel DOIT mentionner des éléments de la description de l'entreprise si pertinent.
        6. Objet: Tu dois générer un Objet d'email accrocheur (sur la première ligne).
        
        FORMAT DE SORTIE REQUIS:
        Renvoie SEULEMENT le résultat en format JSON strict (sans balises markdown ```json).
        {{
            "subject": "Objet accrocheur du courriel",
            "body": "Le corps du message avec des sauts de ligne \n"
        }}
        """
        
        try:
            resp = await self.generate_response(prompt)
            import json, re
            
            clean_resp = resp.replace("```json", "").replace("```", "").strip()
            
            try:
                parsed = json.loads(clean_resp)
                return parsed
            except json.JSONDecodeError:
                # Fallback Regex
                match = re.search(r'\{.*\}', clean_resp, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                    
            raise Exception("Impossible de parser le JSON retourné par l'IA.")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de l'email: {e}")
            return {
                "subject": f"Candidature spontanée - {target_domain or request_type.capitalize()}",
                "body": f"{greeting}\n\nJe me permets de vous contacter car je suis très intéressé(e) par les activités de {company_name}.\n\nActuellement en recherche de {request_type}, j'aimerais vous soumettre mon profil.\n\nCordialement,"
            }
