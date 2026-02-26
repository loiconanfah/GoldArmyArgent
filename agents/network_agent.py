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

    async def think(self, task):
        """Requis par BaseAgent — NetworkAgent utilise draft_email directement."""
        return task

    async def act(self, action_plan):
        """Requis par BaseAgent — NetworkAgent utilise draft_email directement."""
        return action_plan

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
        Tu es un expert en "Cold Approach" et en "Growth Hacking" de carrière, spécialisé dans le marché francophone.
        Ton but est de rédiger un courriel d'approche à froid si percutant, authentique et personnalisé que le recruteur se sent obligé de répondre.

        {context_block}

        STRATÉGIE DE RÉDACTION:
        1. L'ACCROCHE (Le Hook): Ne commence pas par "Je m'appelle...". Commence par un détail sur {company_name} qui montre que tu as fait tes recherches (basé sur la description si disponible, sinon sur la réputation de l'entreprise).
        2. LA VALEUR (Le Why You): Identifie 2 réalisations spécifiques dans le CV qui résonnent avec {company_name} ou le domaine {target_domain}. Parle de résultats, pas juste de compétences.
        3. LA DEMANDE (The Ask): Sois direct mais humble. Tu ne demandes pas un job, tu demandes une conversation de 10 minutes pour explorer comment tes compétences peuvent aider {company_name} à [objectif probable de l'entreprise].
        4. LE TON: "High-Status/High-Value". Tu n'es pas un quémandeur, tu es un expert qui apporte une solution.

        RÈGLES STRICTES:
        - Langue: Français impeccable, ton moderne (évite le "vouvoiement" excessivement lourd si c'est une startup, reste pro).
        - Longueur: Moins de 120 mots.
        - Salutations: Toujours commencer par "{greeting}".
        - Objet: Créatif, court, et incluant soit le nom de l'entreprise, soit un bénéfice immédiat.

        FORMAT DE SORTIE REQUIS:
        Renvoie SEULEMENT le résultat en format JSON strict.
        {{
            "subject": "Sujet percutant",
            "body": "Corps du message avec \\n pour les sauts de ligne"
        }}
        """
        
        try:
            # Upgrade to ultra-high reasoning model for max personalization
            # Using Pro for complex reasoning on CV + Company
            resp = await self.generate_response(prompt, model="gemini-2.0-pro-exp-02-05")
            import json, re
            
            # Robust parsing
            clean_resp = resp.strip()
            if "```json" in clean_resp:
                clean_resp = clean_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_resp:
                clean_resp = clean_resp.split("```")[1].split("```")[0].strip()
            
            try:
                parsed = json.loads(clean_resp)
                # Validation
                if "subject" in parsed and "body" in parsed:
                    return parsed
            except:
                pass

            # Deep extraction fallback
            match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', clean_resp, re.DOTALL)
            if match:
                return json.loads(match.group(0))
                    
            raise Exception("Parsing failed")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de l'email: {e}")
            return {
                "subject": f"Candidature spontanée - {target_domain or request_type.capitalize()}",
                "body": f"{greeting}\n\nJe me permets de vous contacter car je suis très intéressé(e) par les activités de {company_name}.\n\nActuellement en recherche de {request_type}, j'aimerais vous soumettre mon profil.\n\nCordialement,"
            }
