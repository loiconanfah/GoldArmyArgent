import os
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import google.generativeai as genai
from core.database import get_db_connection
from api.auth import get_current_user

# Ensure API key is set
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

router = APIRouter(prefix="/api/interview", tags=["Interview Simulator"])

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
        
    except Exception as e:
        print(f"Failed to receive setup: {e}")
        await websocket.close(code=1008)
        return

    # 3. Initialize Gemini configuration
    role_desc = "un recruteur expert (DRH ou Manager)"
    tech_rule = ""
    if interview_type == "technical":
        role_desc = "le CTO ou Lead Tech"
        tech_rule = "Pose des questions techniques sous forme de QCM ou de mise en situation concrète. Attends la réponse, donne ton feedback technique, puis enchaîne."

    system_instruction = f"""
    Tu es {role_desc} chez {company}. Tu mènes un entretien d'embauche de vive voix.
    Le candidat s'appelle {user_email.split('@')[0] if 'user_email' in locals() else 'le candidat'}.
    Il postule pour le poste de : {job_title}.
    
    Contexte de l'offre d'emploi : {job_details}
    Contexte du CV du candidat : {cv_content}
    
    Règles absolues :
    1. Sois professionnel, concis et interactif (comme dans un vrai entretien oral).
    2. Pose UNE SEULE question à la fois. N'enchaîne surtout pas plusieurs questions.
    3. Attends la réponse de l'utilisateur. Rebondis sur ce qu'il dit avant de passer à la suite.
    4. {tech_rule}
    5. Parle en français naturel, adapté à la synthèse vocale (pas de tirets, pas de listes à puces complexes, pas de markdown).
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
        chat = model.start_chat()
        
        # Initial greeting
        initial_greeting = f"Bonjour, je suis ravi de vous recevoir pour ce poste de {job_title} chez {company}. Pourrions-nous commencer par une brève présentation de votre parcours par rapport à votre CV ?"
        await websocket.send_json({"type": "message", "role": "assistant", "content": initial_greeting})
        
        while True:
            # Receive data from frontend. We expect JSON with user message.
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            user_msg = payload.get("text", "")
            if not user_msg:
                continue

            # Send to Gemini securely in a background thread to prevent blocking the WebSocket loop,
            # while avoiding pure 'async for' which is unstable in some versions of the SDK.
            def _get_response():
                return chat.send_message(user_msg, stream=True)
                
            response = await asyncio.to_thread(_get_response)
            
            # Stream response back
            full_reply = ""
            for chunk in response:
                if chunk.text:
                    full_reply += chunk.text
                    await websocket.send_json({
                        "type": "chunk", 
                        "content": chunk.text
                    })
                    
            # Notify frontend that the stream for this message is done so it can trigger TTS
            await websocket.send_json({
                "type": "done"
            })

    except WebSocketDisconnect:
        print("Interview WebSocket disconnected")
    except Exception as e:
        print(f"Error in interview WS: {e}")
        try:
            await websocket.send_json({"type": "error", "message": "Erreur de connexion au serveur IA."})
            await websocket.close()
        except:
            pass
