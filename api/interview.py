import os
import json
import asyncio
import base64
import re
import edge_tts
from dotenv import load_dotenv
load_dotenv() # Load from .env file

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import google.generativeai as genai
from core.database import get_db
from config.settings import settings

# Configure Gemini from central settings
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
else:
    print("WARNING: GEMINI_API_KEY is not set in environment!")

from llm.unified_client import UnifiedLLMClient
llm_client = UnifiedLLMClient() # Auto-selects Gemini if available

router = APIRouter(prefix="/api/interview", tags=["Interview Simulator"])

@router.post("/test-voice")
async def test_voice_hd(data: dict):
    """
    Generates a high-quality test audio sample using edge-tts.
    """
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
            return {
                "status": "success",
                "audio": base64.b64encode(audio_data).decode('utf-8')
            }
        return {"status": "error", "message": "Failed to generate audio"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/analyze")
async def analyze_interview(data: dict):
    """
    Analyzes the full interview history and returns a structured scorecard.
    """
    history = data.get("history", [])
    job_title = data.get("jobTitle", "le poste")
    
    if not history:
        return {"status": "error", "message": "Aucun historique à analyser"}

    # Format history for Gemini
    formatted_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])
    
    analysis_prompt = f"""
    Analyse cet entretien pour le poste de {job_title}. 
    Donne un score sur 10 pour chaque catégorie et un avis global.
    Réponds EXCLUSIVEMENT en JSON avec cette structure :
    {{
      "scores": {{
        "technical": 8,
        "communication": 7,
        "soft_skills": 9,
        "overall": 8
      }},
      "feedback": {{
        "points_forts": ["point 1", "point 2"],
        "points_amelioration": ["point 1", "point 2"],
        "conseils": "Un paragraphe court de conseils personnalisés."
      }},
      "decision": "Favorable / Réservé / Défavorable"
    }}
    
    HISTORIQUE :
    {formatted_history}
    """
    
    try:
        if not settings.gemini_api_key:
            return {"status": "error", "message": "GEMINI_API_KEY non configurée"}
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = await asyncio.to_thread(model.generate_content, analysis_prompt)
        raw_text = getattr(response, "text", None) or ""
        if not raw_text or not raw_text.strip():
            return {"status": "error", "message": "Réponse vide du modèle d'analyse"}
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        clean_json = re.sub(r"^[^{]*", "", clean_json).strip()  # drop leading non-JSON
        analysis_result = json.loads(clean_json)
        return {
            "status": "success",
            "analysis": analysis_result
        }
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Format d'analyse invalide: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.websocket("/ws")
async def websocket_interview(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time Siri-like voice interview.
    """
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

    # 2. Setup
    try:
        setup_data = await websocket.receive_text()
        setup_payload = json.loads(setup_data)
        if setup_payload.get("type") != "setup":
             await websocket.close(code=1008)
             return
             
        cfg = setup_payload.get("payload", {})
        cv_content = cfg.get("cv", "Non renseigné")
        job_title = cfg.get("jobTitle", "Poste général")
        company = cfg.get("company", "L'entreprise")
        job_details = cfg.get("jobDetails", "Pas de détails")
        interview_type = cfg.get("interviewType", "general")
        recruiter_id = cfg.get("recruiterId", "tech")

        voice_map = {
            "tech": "fr-FR-DeniseNeural",
            "hr": "fr-FR-HenriNeural", 
            "ceo": "fr-FR-EloiseNeural"
        }
        selected_voice = voice_map.get(recruiter_id, "fr-FR-DeniseNeural")
        
        recruiter_names = {"tech": "Denise", "hr": "Henri", "ceo": "Eloise"}
        recruiter_name = recruiter_names.get(recruiter_id, "Denise")

    except Exception as e:
        logger.error(f"WS Setup Error: {e}")
        await websocket.close(code=1008)
        return

    # 3. LLM Instructions
    role_desc = "un recruteur expert" if interview_type != "technical" else "le CTO/Lead Tech"
    
    system_prompt = f"""
    Tu es {recruiter_name}, {role_desc} chez {company}. 
    Tu mènes un entretien pour le poste de {job_title}.
    
    CV candidat: {cv_content[:1000]}
    
    CONSIGNES:
    1. Pose UNE SEULE question à la fois.
    2. Sois concis (max 2-3 phrases). C'est pour de la synthèse vocale.
    3. Rebondis sur ce que dit le candidat.
    4. Pas de Markdown, pas de listes. Uniquement du texte brut.
    """

    # 4. Starting greeting
    greeting = f"Bonjour ! Je suis {recruiter_name} pour le poste de {job_title} chez {company}. Ravi de vous rencontrer. Pouvez-vous vous présenter ?"
    
    await websocket.send_json({
        "type": "recruiter_response",
        "text": greeting,
        "recruiter_name": recruiter_name
    })

    # Async voice greeting
    async def _speak(text):
        try:
            communicate = edge_tts.Communicate(text, selected_voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": base64.b64encode(chunk["data"]).decode('utf-8')
                    })
        except Exception as ve:
            logger.error(f"TTS Error: {ve}")

    asyncio.create_task(_speak(greeting))
    
    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": greeting}
    ]

    # 5. Loop
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("text", "")
            if not user_msg: continue
            
            conversation_history.append({"role": "user", "content": user_msg})
            
            # Generate response
            # Format prompt for UnifiedLLMClient
            full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history])
            
            try:
                response_text = await llm_client.generate(full_prompt)
                if not response_text:
                    response_text = "Je vous prie de m'excuser, pouvez-vous reformuler ?"
            except Exception as llm_err:
                logger.error(f"LLM Error in interview: {llm_err}")
                response_text = "⚠️ Désolé, j'ai rencontré un problème technique pour générer ma réponse. Pouvons-nous reprendre ?"
                
                # Send error notice to frontend so it doesn't just hang
                await websocket.send_json({
                    "type": "error",
                    "message": "Erreur technique LLM. L'entretien peut être instable.",
                    "recruiter_name": recruiter_name
                })

            conversation_history.append({"role": "assistant", "content": response_text})
            
            # Send text
            await websocket.send_json({
                "type": "recruiter_response",
                "text": response_text,
                "recruiter_name": recruiter_name
            })
            
            # Send voice
            asyncio.create_task(_speak(response_text))
            
    except WebSocketDisconnect:
        logger.info("WS Interview Disconnected")
    except Exception as e:
        logger.error(f"WS Loop Error: {e}")
        try:
            # Try to notify the user before final crash
            await websocket.send_json({"type": "error", "message": f"Erreur critique: {str(e)}"})
            await websocket.close()
        except:
            pass


