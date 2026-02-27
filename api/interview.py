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
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = await asyncio.to_thread(model.generate_content, analysis_prompt)
        
        # Clean JSON
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        analysis_result = json.loads(clean_json)
        
        return {
            "status": "success",
            "analysis": analysis_result
        }
    except Exception as e:
        print(f"Analysis Error: {e}")
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
            
        # Get user
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (user_email,)).fetchone()
        if not user:
            await websocket.close(code=1008)
            return

        # 1b. Check Subscription Limit
        from api.subscription import check_subscription_limit, log_usage
        check = await check_subscription_limit(user["id"], "hr_interview")
        if not check["allowed"]:
            await websocket.send_json({"type": "error", "message": check["message"]})
            await websocket.close(code=1008)
            return

        # Get user's latest CV text context if any
        cv_text = user.get("cv_text") or "Candidat avec une expérience en développement logiciel."
        
        # Log usage
        await log_usage(user["id"], "hr_interview")
        
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
        tech_rule = """
        Pose des questions techniques extrêmement pointues. 
        Cherche à piéger poliment le candidat sur la complexité (Big O), les designs patterns, et les choix d'architecture.
        Si la réponse est vague, demande des précisions techniques concrètes.
        Donne ton feedback technique brièvement après chaque réponse avant d'enchaîner.
        """

    recruiter_instruction = f"""
    Tu es {role_desc} chez {company}, un recruteur professionnel et expérimenté.
    Tu mènes un entretien de visioconférence avec un candidat qui postule pour le poste de : {job_title}.
    
    CV du candidat (extrait) :
    ---
    {cv_content[:1500] if cv_content and cv_content != 'Non renseigné' else 'Non fourni — adapte-toi en posant des questions ouvertes.'}
    ---
    Description de l'offre :
    ---
    {job_details[:800] if job_details and job_details != 'Pas de détails' else 'Poste standard.'}
    ---

    STRUCTURE DE L'ENTRETIEN (tu dois couvrir TOUTES ces phases, dans l'ordre) :
    
    PHASE 1 — BRISE-GLACE ET PRÉSENTATION (1-2 échanges)
    - "Pouvez-vous vous présenter en 2-3 minutes ?"
    - Commentaire bref et passage à la suite.
    
    PHASE 2 — MOTIVATION & CONNAISSANCE DE L'ENTREPRISE (2-3 échanges, OBLIGATOIRE)
    - "Qu'est-ce qui vous attire vers {company} spécifiquement ? Que savez-vous de nous ?"
    - "Pourquoi ce poste de {job_title} vous intéresse-t-il à ce stade de votre carrière ?"
    - Si la réponse est vague : "Vous n'avez pas mentionné [aspect spécifique de l'entreprise]. Qu'en pensez-vous ?"
    
    PHASE 3 — EXPÉRIENCES & COMPÉTENCES CLÉS (2-3 échanges)
    - "Parlez-moi d'une réalisation dont vous êtes particulièrement fier dans votre parcours."
    - Rebondir sur des éléments du CV pour creuser : "Vous mentionnez [X] sur votre CV, pouvez-vous m'en dire plus ?"
    
    PHASE 4 — QUESTIONS COMPORTEMENTALES/SITUATIONNELLES (2-3 échanges)
    - "Décrivez une situation difficile au travail et comment vous l'avez gérée." (Méthode STAR attendue)
    - "Parlez-moi d'un conflit avec un collègue ou manager. Comment l'avez-vous résolu ?"
    
    PHASE 5 — DÉFAUTS ET AUTO-ÉVALUATION (1-2 échanges, OBLIGATOIRE)
    - "Quels sont vos 2 ou 3 principaux défauts professionnels ?" (Surveille si le candidat donne de faux défauts "déguisés en qualités")
    - "Comment travaillez-vous sur ces axes d'amélioration ?"
    
    PHASE 6 — LA QUESTION CLÉE : POURQUOI VOUS ? (1-2 échanges, OBLIGATOIRE)
    - "Si je devais choisir entre vous et un autre candidat au profil similaire, pourquoi devrais-je vous choisir vous ?"
    - "Qu'est-ce qui vous rend unique pour ce poste ?"
    
    PHASE 7 — AMBITION & VISION (1 échange)
    - "Où vous voyez-vous dans 3-5 ans ?"
    - "Comment ce poste s'inscrit-il dans vos objectifs de carrière ?"
    
    PHASE 8 — QUESTIONS DU CANDIDAT & CLÔTURE (1-2 échanges)
    - "Avez-vous des questions sur le poste, l'équipe, ou {company} ?"
    - Conclude avec une formule de fin professionnelle et souhaite bonne chance.
    
    RÈGLES IMPÉRATIVES :
    1. Pose UNE SEULE question à la fois.
    2. Écoute la réponse et REBONDIS dessus avant de passer à la phase suivante (sois naturel).
    3. Si une réponse est trop vague, relance : "Pouvez-vous me donner un exemple concret ?"
    4. Sois exigeant mais bienveillant. Tu veux faire ressortir le meilleur du candidat.
    5. Parle en FRANÇAIS naturel et conversationnel. JAMAIS de listes, jamais de markdown.
    6. Sois concis (synthèse vocale). Maximum 2-3 phrases par réplique.
    7. {tech_rule}
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
        recruiter_model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=recruiter_instruction)
        recruiter_chat = recruiter_model.start_chat()
        
        # Shadow Analyst (Nano is great for fast tips)
        analyst_model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=analyst_instruction)
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
