"""
OrchestratorAgent — Point d'entrée principal du système.
Analyse l'intention de l'utilisateur, maintient l'historique de conversation,
et délègue aux agents spécialisés.
"""
from typing import Dict, Any, List
from loguru import logger
from collections import deque
import time

from agents.job_searcher import JobSearchAgent
from agents.mentor import MentorAgent
from agents.headhunter import HeadhunterAgent


# Mémoire de conversation (par session_id), max 20 échanges, TTL 30 minutes
_CONVERSATION_STORE: Dict[str, Dict] = {}
MAX_HISTORY = 20  # nb de messages (user + assistant)
SESSION_TTL = 1800  # 30 minutes


def _get_history(session_id: str) -> List[Dict[str, str]]:
    """Retourne l'historique d'une session, crée la session si inexistante."""
    now = time.time()
    # Nettoyage des sessions expirées
    expired = [sid for sid, s in _CONVERSATION_STORE.items() if now - s["last_access"] > SESSION_TTL]
    for sid in expired:
        del _CONVERSATION_STORE[sid]

    if session_id not in _CONVERSATION_STORE:
        _CONVERSATION_STORE[session_id] = {
            "history": [],
            "last_access": now
        }
    _CONVERSATION_STORE[session_id]["last_access"] = now
    return _CONVERSATION_STORE[session_id]["history"]


def _add_to_history(session_id: str, role: str, content: str):
    """Ajoute un message à l'historique, taille limitée."""
    history = _get_history(session_id)
    history.append({"role": role, "content": content})
    # Trim: garder les MAX_HISTORY derniers messages
    if len(history) > MAX_HISTORY:
        # Toujours garder le system prompt s'il existe
        system_msgs = [m for m in history if m["role"] == "system"]
        other_msgs = [m for m in history if m["role"] != "system"]
        trimmed = other_msgs[-(MAX_HISTORY - len(system_msgs)):]
        _CONVERSATION_STORE[session_id]["history"] = system_msgs + trimmed


class OrchestratorAgent:
    """
    Main entry point that analyzes user intent and routes 
    the request to the specialized agents (Searcher, Mentor, etc.).
    """
    def __init__(self):
        self.agent_name = "Sniper 2.0 Reloaded"
        self.job_searcher = JobSearchAgent()
        self.mentor = MentorAgent()
        from agents.headhunter import headhunter_agent
        self.headhunter = headhunter_agent

        # System prompt for general conversation mode
        self.system_prompt = (
            "Tu es GoldArmy, un co-pilote de carrière IA ultra-compétent et motivant. "
            "Tu aides les chercheurs d'emploi québécois à trouver des offres, auditer leur CV, "
            "générer leur portfolio web, et se préparer aux entretiens. "
            "Tu parles français, tu es direct et actionnable. "
            "Tu te souviens de l'historique de conversation ci-dessus."
        )

    async def initialize(self):
        """Initialise tous les sous-agents d'orchestration."""
        await self.job_searcher.initialize()
        await self.mentor.initialize()
        await self.headhunter.initialize()

    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes intention and orchestrates work."""
        query = user_input.get("query", "")
        logger.info(f"[Orchestrator] Received task: {str(query)[:80]}...")

        # Récupérer ou créer un session_id
        session_id = user_input.get("session_id", "default")

        # Charger historique
        history = _get_history(session_id)

        # 1. Analyze intention
        intention = await self._route_request(user_input)

        # 2. Delegate to correct Agent
        if intention["action"] == "headhunter":
            logger.info(f"[Sniper 2.0 Reloaded] Routing to Headhunter for {query}")
            # Extraction des paramètres via IA
            params_prompt = f"""
            Extrait UNIQUEMENT le nom de l'entreprise de cette recherche : '{query}'.
            Si l'utilisateur cherche des gens chez une boite, donne juste le nom de la boite.
            Exemple: "recruteurs chez Google" -> "Google"
            Réponds UNIQUEMENT avec le nom.
            """
            company_name = await self.mentor.generate_response(params_prompt, model="gemini-2.0-flash", temperature=0.0)
            
            results = await self.headhunter.find_decision_makers({"company_name": company_name.strip()})
            return {
                "status": "success",
                "type": "headhunter_results",
                "content": results
            }

        if intention["action"] == "job_search":
            search_result = await self.job_searcher.execute_task(user_input)
            response = {
                "status": "success",
                "type": "job_search_results",
                "content": search_result
            }
            # Mémoriser l'échange
            if query:
                _add_to_history(session_id, "user", query)
            _add_to_history(session_id, "assistant", f"[Recherche d'emploi executée pour: {query}]")
            return response

        elif intention["action"] == "headhunter":
            logger.info(f"[Orchestrator] Routing to HeadhunterAgent")
            result = await self.headhunter.execute_task(user_input)
            response = {
                "status": "success",
                "type": "headhunter_results",
                "content": result
            }
            if query:
                _add_to_history(session_id, "user", query)
            _add_to_history(session_id, "assistant", f"[Recherche de décideurs LinkedIn executée pour: {query}]")
            return response

        elif intention["action"] in ["audit_cv", "generate_portfolio", "rewrite_cv"]:
            logger.info(f"[Orchestrator] Routing to MentorAgent for {intention['action']}")
            user_input["action"] = intention["action"]
            result = await self.mentor.think(user_input)
            # Mémoriser
            if query:
                _add_to_history(session_id, "user", query)
            content = result.get("content", "")
            if content and result.get("type") not in ["cv_rewrite"]:  # ne pas stocker le JSON entier en mémoire
                _add_to_history(session_id, "assistant", str(content)[:500])
            return result

        else:
            # Mode conversation générale — utiliser l'historique comme contexte
            return await self._general_chat(session_id, query, user_input, history)

    async def _general_chat(
        self,
        session_id: str,
        query: str,
        user_input: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Répond à une question générale en utilisant l'historique de conversation."""

        # Construire les messages avec l'historique
        messages = [{"role": "system", "content": self.system_prompt}]

        # Ajouter le contexte CV si disponible (une seule fois en début)
        cv_text = user_input.get("cv_text", "")
        if cv_text:
            cv_snippet = cv_text[:1500]
            messages.append({
                "role": "user",
                "content": f"[Contexte CV chargé par l'utilisateur]\n{cv_snippet}"
            })
            messages.append({
                "role": "assistant",
                "content": "J'ai bien reçu ton CV. Je vais l'utiliser comme contexte pour mes réponses."
            })

        # Ajouter l'historique de conversation
        for msg in history[-16:]:  # max 16 messages d'historique (8 échanges)
            messages.append(msg)

        # Ajouter le message actuel
        if query:
            messages.append({"role": "user", "content": query})

        try:
            # Appel LLM via le client unifié du MentorAgent (déjà initialisé)
            response_text = await self.mentor.llm_client.chat(messages)

            # Mémoriser l'échange
            if query:
                _add_to_history(session_id, "user", query)
            _add_to_history(session_id, "assistant", response_text[:500])

            return {
                "status": "success",
                "type": "chat",
                "content": response_text
            }
        except Exception as e:
            logger.error(f"[Orchestrator] Erreur chat général: {e}")
            return {
                "status": "error",
                "type": "chat",
                "content": f"Désolé, une erreur s'est produite: {str(e)}"
            }

    async def _route_request(self, user_input: Dict[str, Any]) -> Dict[str, str]:
        """Determine which agent handles the query."""
        query = user_input.get("query", "").lower().strip()
        has_cv = bool(user_input.get("cv_text", "").strip())

        if "portfolio" in query or "site web" in query:
            if not has_cv:
                return {"action": "chat", "message": "Tu dois d'abord uploader ton CV (PDF) pour que je génère ton portfolio !"}
            return {"action": "generate_portfolio"}

        # Réécriture / correction ATS (priorité sur audit simple)
        if any(k in query for k in ["réécris", "reecris", "corrige", "correction", "corrige mon cv", "réécriture",
                                     "optimise mon cv", "ats", "refais mon cv", "améliore mon cv", "rewrite"]):
            if not has_cv:
                return {"action": "chat", "message": "J'ai besoin de ton CV. Upload ton PDF via le bouton 'Ajouter CV'."}
            return {"action": "rewrite_cv"}

        if any(k in query for k in ["audit", "critique", "mentor", "failles", "analyse mon cv"]):
            if not has_cv:
                return {"action": "chat", "message": "J'ai besoin de ton CV. Upload ton PDF via le bouton 'Ajouter CV'."}
            return {"action": "audit_cv"}

        # Si le CV est chargé et que le message est vide ou parle du CV → audit automatique
        if has_cv and (not query or "cv" in query):
            return {"action": "audit_cv"}

        if any(k in query for k in ["cherche", "trouve", "stage", "emploi", "job", "offre", "poste"]):
            return {"action": "job_search"}

        if any(k in query for k in ["linkedin", "profil", "recruteur", "décideur", "headhunter", "contact"]):
            return {"action": "headhunter"}

        if user_input.get("nb_results"):
            return {"action": "job_search"}

        return {"action": "chat", "message": ""}
