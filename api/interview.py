import os
import json
import asyncio
import base64
import re
import uuid as uuid_lib
import edge_tts
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import google.generativeai as genai
from core.database import get_db
from config.settings import settings
from api.auth import get_current_user

# Configure Gemini from central settings
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
else:
    print("WARNING: GEMINI_API_KEY is not set in environment!")

from llm.unified_client import UnifiedLLMClient

INTERVIEW_LLM_MODEL = "gemini-3.1-pro-preview"
llm_client = UnifiedLLMClient()

# Free tier: max complete interviews before paywall
FREE_TIER_INTERVIEW_LIMIT = 2

router = APIRouter(prefix="/api/interview", tags=["Interview Simulator"])


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: count completed interviews for a user
# ─────────────────────────────────────────────────────────────────────────────
async def _count_user_sessions(user_id: str) -> int:
    db = get_db()
    return await db.interview_sessions.count_documents({"user_id": user_id})


# ─────────────────────────────────────────────────────────────────────────────
# GET /usage — check free tier status before starting
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/usage")
async def get_interview_usage(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    tier = current_user.get("subscription_tier", "FREE")
    is_free = tier not in ("PRO", "PREMIUM", "ADMIN")

    count = await _count_user_sessions(user_id)
    can_start = (not is_free) or (count < FREE_TIER_INTERVIEW_LIMIT)

    return {
        "count":     count,
        "limit":     FREE_TIER_INTERVIEW_LIMIT if is_free else None,
        "is_free":   is_free,
        "can_start": can_start,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /history — paginated interview history
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/history")
async def get_interview_history(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    db = get_db()

    cursor = (
        db.interview_sessions
        .find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    sessions = await cursor.to_list(length=limit)

    # Convert datetime to ISO string for JSON serialization
    for s in sessions:
        if isinstance(s.get("created_at"), datetime):
            s["created_at"] = s["created_at"].isoformat()

    total = await _count_user_sessions(user_id)
    return {"total": total, "sessions": sessions}


# ─────────────────────────────────────────────────────────────────────────────
# GET /history/{session_id} — full detail of one session
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/history/{session_id}")
async def get_interview_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    db = get_db()

    session = await db.interview_sessions.find_one(
        {"session_id": session_id, "user_id": user_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")

    if isinstance(session.get("created_at"), datetime):
        session["created_at"] = session["created_at"].isoformat()

    return session


# ─────────────────────────────────────────────────────────────────────────────
# POST /test-voice
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/test-voice")
async def test_voice_hd(data: dict):
    text = data.get("text", "Ceci est un test sonore en Haute Définition.")
    recruiter_id = data.get("recruiterId", "tech")
    
    voice_map = {
        "tech": "fr-FR-DeniseNeural",
        "hr": "fr-FR-HenriNeural", 
        "ceo": "fr-FR-EloiseNeural"
    }
    voice = voice_map.get(recruiter_id, "fr-FR-DeniseNeural")
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if audio_data:
            return {"status": "success", "audio": base64.b64encode(audio_data).decode('utf-8')}
        return {"status": "error", "message": "Failed to generate audio"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# POST /analyze — analyze interview + save to history
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/analyze")
async def analyze_interview(data: dict, current_user: dict = Depends(get_current_user)):
    """
    Analyzes the full interview history and saves result in interview_sessions.
    """
    history     = data.get("history", [])
    job_title   = data.get("jobTitle", "le poste")
    company     = data.get("company", "")
    interview_type = data.get("interviewType", "rh")
    recruiter_id   = data.get("recruiterId", "tech")
    started_at_iso = data.get("startedAt", None)     # ISO string sent from frontend
    ended_at_iso   = data.get("endedAt", None)

    if not history:
        return {"status": "error", "message": "Aucun historique à analyser"}

    formatted_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])

    analysis_prompt = f"""Tu es un évaluateur RH expert. Analyse cet entretien d'embauche pour le poste de {job_title} et produis un bilan structuré pour le candidat.

RÈGLES D'ANALYSE :
- Base-toi UNIQUEMENT sur ce qui a été dit dans l'historique.
- technical (0-10) : compétences techniques, maîtrise du sujet, qualité des exemples.
- communication (0-10) : clarté, fluidité, concision, qualité de l'expression orale.
- soft_skills (0-10) : attitude, écoute, réactivité, gestion des questions, professionnalisme.
- overall (0-10) : note globale (moyenne pondérée cohérente avec les 3 scores).
- points_forts : 2 à 4 points concrets tirés de l'entretien.
- points_amelioration : 2 à 4 axes d'amélioration précis et bienveillants.
- conseils : un paragraphe court (2-4 phrases) de conseils personnalisés.
- decision : exactement une des trois chaînes "Favorable", "Réservé" ou "Défavorable".

Réponds EXCLUSIVEMENT en JSON valide, sans texte avant ou après :
{{
  "scores": {{
    "technical": <nombre 0-10>,
    "communication": <nombre 0-10>,
    "soft_skills": <nombre 0-10>,
    "overall": <nombre 0-10>
  }},
  "feedback": {{
    "points_forts": ["...", "..."],
    "points_amelioration": ["...", "..."],
    "conseils": "..."
  }},
  "decision": "Favorable"
}}

HISTORIQUE DE L'ENTRETIEN :
{formatted_history}
"""
    
    try:
        if not settings.gemini_api_key:
            return {"status": "error", "message": "GEMINI_API_KEY non configurée"}
        model = genai.GenerativeModel(INTERVIEW_LLM_MODEL)
        response = await asyncio.to_thread(model.generate_content, analysis_prompt)
        raw_text = getattr(response, "text", None) or ""
        if not raw_text.strip():
            return {"status": "error", "message": "Réponse vide du modèle d'analyse"}

        clean_json = re.sub(r"^[^{]*", "", raw_text.replace("```json", "").replace("```", "").strip()).strip()
        analysis_result = json.loads(clean_json)

        # ── Save to interview_sessions ───────────────────────────────────────
        now = datetime.now(timezone.utc)
        session_id = str(uuid_lib.uuid4())

        # Compute duration if timestamps provided
        duration_minutes = None
        try:
            if started_at_iso and ended_at_iso:
                from datetime import timedelta
                s = datetime.fromisoformat(started_at_iso.replace("Z", "+00:00"))
                e = datetime.fromisoformat(ended_at_iso.replace("Z", "+00:00"))
                duration_minutes = round((e - s).total_seconds() / 60, 1)
        except Exception:
            pass

        session_doc = {
            "session_id":      session_id,
            "user_id":         current_user["id"],
            "created_at":      now,
            "job_title":       job_title,
            "company":         company,
            "interview_type":  interview_type,
            "recruiter_id":    recruiter_id,
            "scores":          analysis_result.get("scores", {}),
            "feedback":        analysis_result.get("feedback", {}),
            "decision":        analysis_result.get("decision", "Réservé"),
            "duration_minutes":duration_minutes,
        }
        db = get_db()
        await db.interview_sessions.insert_one(session_doc)

        return {
            "status":     "success",
            "session_id": session_id,
            "analysis":   analysis_result,
        }
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Format d'analyse invalide: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket /ws — real-time interview (with free-tier gate)
# ─────────────────────────────────────────────────────────────────────────────
@router.websocket("/ws")
async def websocket_interview(websocket: WebSocket, token: str):
    await websocket.accept()

    from api.auth import ALGORITHM, SECRET_KEY
    import jwt
    from loguru import logger
    
    # 1. Authenticate
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008)
            return
            
        db = get_db()
        user = await db.users.find_one({"id": user_id})
        if not user:
            logger.error(f"WS Auth: User {user_id} not found")
            await websocket.close(code=1008)
            return
            
        logger.success(f"WS Auth Success: {user.get('email')}")
    except Exception as e:
        logger.error(f"WS Auth Error: {e}")
        await websocket.close(code=1008)
        return

    # 2. Free-tier gate — check BEFORE setup to fail fast
    tier = user.get("subscription_tier", "FREE")
    is_free = tier not in ("PRO", "PREMIUM", "ADMIN")
    if is_free:
        session_count = await _count_user_sessions(user_id)
        if session_count >= FREE_TIER_INTERVIEW_LIMIT:
            await websocket.send_json({
                "type": "paywall",
                "message": "Vous avez atteint la limite de 2 entretiens gratuits. Passez à l'abonnement PRO pour continuer.",
                "count": session_count,
                "limit": FREE_TIER_INTERVIEW_LIMIT,
            })
            await websocket.close(code=4003)
            return

    # 3. Setup
    try:
        setup_data = await websocket.receive_text()
        setup_payload = json.loads(setup_data)
        if setup_payload.get("type") != "setup":
             await websocket.close(code=1008)
             return
             
        cfg = setup_payload.get("payload", {})
        cv_content     = cfg.get("cv", "Non renseigné")
        job_title      = cfg.get("jobTitle", "Poste général")
        company        = cfg.get("company", "L'entreprise")
        job_details    = cfg.get("jobDetails", "Pas de détails")
        interview_type = cfg.get("interviewType", "general")
        recruiter_id   = cfg.get("recruiterId", "tech")

        voice_map = {
            "tech": "fr-FR-DeniseNeural",
            "hr":   "fr-FR-HenriNeural",
            "ceo":  "fr-FR-EloiseNeural"
        }
        selected_voice  = voice_map.get(recruiter_id, "fr-FR-DeniseNeural")
        recruiter_names = {"tech": "Sophie", "hr": "Marc", "ceo": "Alice"}
        recruiter_name  = recruiter_names.get(recruiter_id, "Sophie")

    except Exception as e:
        logger.error(f"WS Setup Error: {e}")
        await websocket.close(code=1008)
        return

    # 4. LLM Instructions
    is_technical = interview_type == "technical"
    job_context  = f"\nDétails du poste / offre: {job_details[:800]}" if job_details.strip() not in ("", "Pas de détails") else ""

    if is_technical:
        role_desc = "le CTO ou Lead Tech qui évalue les compétences techniques et la façon de raisonner."
        type_instructions = """
TYPE D'ENTRETIEN: TECHNIQUE.
Tu dois poser des questions typiques d'un entretien technique / CTO :
- Projets récents, stack technique, choix d'architecture ou de technologies.
- Problèmes complexes résolus, débogage, performance, évolutivité.
- Méthodologie (tests, revue de code, CI/CD), travail en équipe technique.
- Une ou deux questions comportementales courtes (gestion du désaccord, priorisation) sont possibles, mais l'accent reste sur la technique.
Adapte le niveau et les sujets au poste et au CV du candidat. Reste concis à l'oral.
"""
    else:
        role_desc = "un recruteur RH expert, bienveillant et professionnel, qui mène un entretien de type RH au complet."
        type_instructions = """
TYPE D'ENTRETIEN: RH / GÉNÉRAL (comportemental, motivation, fit).
Tu dois intégrer les questions que la plupart des recruteurs posent vraiment, par exemple :
- Parlez-moi de vous / Présentez-vous.
- Pourquoi notre entreprise ? Pourquoi ce poste ?
- Vos points forts et une zone d'amélioration ?
- Où vous voyez-vous dans 3 ou 5 ans ?
- Décrivez une situation de conflit ou de désaccord et comment vous l'avez géré.
- Quelle est votre plus grande réussite professionnelle ?
- Pourquoi quittez-vous (ou avez-vous quitté) votre poste actuel ?
- Comment travaillez-vous sous pression ou en équipe ?
Enchaîne naturellement, sans tout poser d'un coup. Rebondis sur les réponses et le CV.
"""

    system_prompt = f"""Tu es {recruiter_name}, {role_desc} chez {company}. Tu mènes un entretien pour le poste de {job_title}.

CV candidat (extrait): {cv_content[:1000]}
{job_context}
{type_instructions}

CONSIGNES COMMUNES (RH et Technique):
1. Pose UNE SEULE question à la fois.
2. Réponses COURTES (1 à 2 phrases max). Synthèse vocale — rythme naturel, pas de longs paragraphes.
3. Rebondis sur ce que dit le candidat. Personnalise en fonction du CV et des réponses.
4. Détecte l'ironie et le second degré : si le candidat est clairement ironique ou sarcastique, relève-le avec légèreté (ex. "Je sens une pointe d'ironie — c'est noté !") et enchaîne sans moraliser.
5. Pas de Markdown, pas de listes. Uniquement du texte brut, naturel à l'oral.

ENTRETIEN COMPLET : Mène l'entretien de bout en bout. Après avoir couvert les thèmes essentiels (présentation, motivation, expérience/compétences, situation), conclus clairement : remercie le candidat, fais un très bref résumé si pertinent, indique les prochaines étapes (ex. "Nous vous recontacterons sous peu.") puis salue. Ainsi l'entretien est complet et le candidat sait qu'il est terminé.
"""

    # 5. Starting greeting
    enchanter = "Ravie de vous rencontrer" if recruiter_name in ("Sophie", "Alice") else "Ravi de vous rencontrer"
    greeting  = f"Bonjour ! Je suis {recruiter_name} pour le poste de {job_title} chez {company}. {enchanter}. Pouvez-vous vous présenter ?"
    
    await websocket.send_json({
        "type": "recruiter_response",
        "text": greeting,
        "recruiter_name": recruiter_name
    })

    async def _speak(text):
        try:
            communicate = edge_tts.Communicate(text, selected_voice)
            chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunks.append(chunk["data"])
            if chunks:
                full_audio_b64 = base64.b64encode(b"".join(chunks)).decode("utf-8")
                await websocket.send_json({"type": "voice", "audio": full_audio_b64})
        except Exception as ve:
            logger.error(f"TTS Error: {ve}")

    asyncio.create_task(_speak(greeting))
    
    conversation_history = [
        {"role": "system",    "content": system_prompt},
        {"role": "assistant", "content": greeting}
    ]

    # 6. Main loop
    try:
        while True:
            data = await websocket.receive_text()
            payload_msg = json.loads(data)
            user_msg = payload_msg.get("text", "")
            if not user_msg:
                continue
            
            await websocket.send_json({"type": "thinking"})
            conversation_history.append({"role": "user", "content": user_msg})
            
            full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history])
            
            try:
                response_text = await llm_client.generate(full_prompt, model=INTERVIEW_LLM_MODEL)
                if not response_text:
                    response_text = "Je vous prie de m'excuser, pouvez-vous reformuler ?"
            except Exception as llm_err:
                logger.error(f"LLM Error in interview: {llm_err}")
                response_text = "⚠️ Désolé, j'ai rencontré un problème technique pour générer ma réponse. Pouvons-nous reprendre ?"
                await websocket.send_json({
                    "type": "error",
                    "message": "Erreur technique LLM. L'entretien peut être instable.",
                    "recruiter_name": recruiter_name
                })

            conversation_history.append({"role": "assistant", "content": response_text})
            
            await websocket.send_json({
                "type": "recruiter_response",
                "text": response_text,
                "recruiter_name": recruiter_name
            })
            asyncio.create_task(_speak(response_text))
            
    except WebSocketDisconnect:
        logger.info("WS Interview Disconnected")
    except Exception as e:
        logger.error(f"WS Loop Error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": f"Erreur critique: {str(e)}"})
            await websocket.close()
        except:
            pass
