import os
import json
import asyncio
import base64
import edge_tts
from dotenv import load_dotenv
load_dotenv() # Load from .env file

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import google.generativeai as genai
from core.database import get_db_connection
from api.auth import get_current_user

# Ensure API key is set
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    # Try alternate name if needed
    api_key = os.environ.get("GOOGLE_API_KEY", "")

if not api_key:
    print("WARNING: GEMINI_API_KEY is not set in environment!")
else:
    print(f"INFO: Gemini API Key found (starts with {api_key[:5]}...)")

genai.configure(api_key=api_key)

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

@router.websocket("/ws")
async def websocket_interview(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time Siri-like voice interview using Gemini.
    We expect the frontend to send a token in query params to authenticate.
    """
    await websocket.accept()

    # 1. Authenticate user from token
    # (Simplified for WebSocket, normally use the auth dependency but WS needs token extraction)
    from api.auth import oauth2_scheme, ALGORITHM, SECRET_KEY
    import jwt
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            await websocket.close(code=1008)
            return
            
        # Get user ID
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (user_email,)).fetchone()
        
        # Get user's latest CV text context if any
        # For MVP, we'll just check applications notes or a dedicated CV field if it exists
        cv_text = "Candidat avec une expérience en développement logiciel."
        
    except Exception as e:
        await websocket.close(code=1008)
        return
    finally:
        if 'conn' in locals(): conn.close()
    
    # 2. Wait for Setup Payload from Frontend
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
        interview_type = cfg.get("interviewType", "general") # "general" or "technical"
        recruiter_id = cfg.get("recruiterId", "tech") # tech, hr, ceo

        # Map recruiter to edge-tts voice
        voice_map = {
            "tech": "fr-FR-DeniseNeural",
            "hr": "fr-FR-HenriNeural", 
            "ceo": "fr-FR-EloiseNeural"
        }
        selected_voice = voice_map.get(recruiter_id, "fr-FR-DeniseNeural")
        
    except Exception as e:
        print(f"Failed to receive setup: {e}")
        await websocket.close(code=1008)
        return

    # 3. Initialize Gemini Models (Recruiter + Analyst)
    role_desc = "un recruteur expert (DRH ou Manager)"
    tech_rule = ""
    if interview_type == "technical":
        role_desc = "le CTO ou Lead Tech"
        tech_rule = "Pose des questions techniques pointus. Attends la réponse, donne ton feedback technique, puis enchaîne."

    recruiter_instruction = f"""
    Tu es {role_desc} chez {company}. Tu mènes un entretien de VISIOCONFÉRENCE.
    Le candidat s'appelle {user_email.split('@')[0] if 'user_email' in locals() else 'le candidat'}.
    Il postule pour le poste de : {job_title}.
    
    Règles absolues :
    1. Sois extrêmement concis pour la synthèse vocale.
    2. Pose UNE SEULE question à la fois.
    3. Mène l'entretien de A à Z (Présentation -> Expérience -> Technique -> Clôture).
    4. {tech_rule}
    5. Parle en français naturel. Pas de listes, pas de markdown.
    """

    analyst_instruction = f"""
    Tu es un analyste RH "fantôme" qui observe l'entretien pour le poste de {job_title}.
    Ton rôle est de donner des CONSEILS BREF au candidat en temps réel (metadata).
    Analyse ce qu'il dit et donne des points sur : Posture, Pertinence technique, ou Soft skills.
    Réponds TOUJOURS en JSON format court : {{"tip": "ton conseil court", "sentiment": "neutre|positif|stressé"}}
    Max 10 mots par conseil.
    """

    try:
        # Main Recruiter
        recruiter_model = genai.GenerativeModel("gemini-3-flash-preview", system_instruction=recruiter_instruction)
        recruiter_chat = recruiter_model.start_chat()
        
        # Shadow Analyst
        analyst_model = genai.GenerativeModel("nano-banana-pro-preview", system_instruction=analyst_instruction)
        analyst_chat = analyst_model.start_chat()
        
        # Initial greeting
        initial_greeting = f"Bonjour, je suis ravi de vous recevoir pour ce poste de {job_title} chez {company}. Nous sommes en visioconférence, je vous vois bien. Pourrions-nous commencer par votre présentation ?"
        await websocket.send_json({"type": "message", "role": "assistant", "content": initial_greeting})
        await websocket.send_json({"type": "done"})
        
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("text", "")
            if not user_msg: continue

            # 1. Recruiter Response (Gemini 3)
            def _get_recruiter_resp():
                return recruiter_chat.send_message(user_msg, stream=True)
            
            recruiter_stream = await asyncio.to_thread(_get_recruiter_resp)
            
            full_reply = ""
            for chunk in recruiter_stream:
                if chunk.text:
                    full_reply += chunk.text
                    await websocket.send_json({"type": "chunk", "content": chunk.text})
            
            await websocket.send_json({"type": "done"})

            # 3. Generate HD Voice (edge-tts)
            async def _generate_voice(text, voice):
                try:
                    communicate = edge_tts.Communicate(text, voice)
                    audio_data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]
                    
                    if audio_data:
                        # Encode in base64 to send via JSON
                        b64_audio = base64.b64encode(audio_data).decode('utf-8')
                        await websocket.send_json({
                            "type": "voice",
                            "audio": b64_audio
                        })
                except Exception as e:
                    print(f"TTS Error: {e}")

            # Trigger voice generation after the recruiter finished talking
            asyncio.create_task(_generate_voice(full_reply, selected_voice))

            # 2. Shadow Analysis (Nano Banana) - Runs after the turn to provide a "tip"
            async def _run_analysis():
                try:
                    analysis_resp = await asyncio.to_thread(analyst_chat.send_message, f"Analyse ce message du candidat: {user_msg}")
                    # Extract JSON from Nano Banana response
                    raw_text = analysis_resp.text
                    # Simple cleanup in case it adds markdown ```json
                    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
                    analysis_data = json.loads(clean_text)
                    await websocket.send_json({"type": "analysis", "payload": analysis_data})
                except:
                    pass # Analyst is silent if error

            # Run analyst in background so recruiter stays fast
            asyncio.create_task(_run_analysis())

    except WebSocketDisconnect:
        print("Interview WebSocket disconnected")
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        print(f"CRITICAL Error in interview WS:\n{error_info}")
        
        try:
            # Send a more descriptive error if possible
            msg = f"Erreur de connexion au serveur IA: {str(e)}"
            await websocket.send_json({"type": "error", "message": msg})
            await websocket.close()
        except:
            pass
