import os
# Fix for Render Playwright: Force browser installation in the persistent project directory
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "pw-browsers")
 
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import io
import json
import subprocess
import os
import sys
import socket
import time
import zipfile
import datetime

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

# --- MONITORING (MongoDB natif, 100% gratuit) ---
from core.error_monitor import monitor
logger.info("Monitoring actif: MongoDB error_logs collection")

from api.auth import get_current_user, router as auth_router
from api.interview import router as interview_router
from api.notifications import router as notifications_router
from api.subscription import check_subscription_limit, log_usage
from api.stripe_service import create_checkout_session, handle_webhook_payload
from core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from api.tasks import create_task, run_background_task, get_task, get_recent_tasks

app.include_router(auth_router)
app.include_router(interview_router)
app.include_router(notifications_router)

# Enable CORS
_cors_origins = [
    # Dev local
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Production GoldArmy
    "https://goldarmyai.com",
    "https://www.goldarmyai.com",
    "https://app.goldarmyai.com",
    "https://goldarmyai.onrender.com",
    "https://goldarmy.onrender.com",
]
# Origines supplementaires via CORS_ORIGIN env var (virgule-separees)
cors_env = os.getenv("CORS_ORIGIN", "")
if cors_env:
    _cors_origins.extend([o.strip() for o in cors_env.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Security Headers to prevent Clickjacking and other attacks
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Content Security Policy (Basic)
    # Allows frames only from same origin to prevent Clickjacking
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    
    # Fix for Google Auth COOP issues in console
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
    return response

# --- GLOBAL EXCEPTION HANDLER (capture les vraies erreurs 500 uniquement) ---
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

# NOTE: On ne surcharge PAS StarletteHTTPException pour ne pas interférer
# avec la gestion CORS du middleware (les OPTIONS 400 seraient cassés).
# On laisse FastAPI gérer les HTTPException normalement.

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Capture les VRAIES exceptions non gérées (RuntimeError, AttributeError, etc.) dans MongoDB."""
    # CRITIQUE : ne jamais intercepter les HTTPException — elles sont intentionnelles (auth, 404, etc.)
    if isinstance(exc, (FastAPIHTTPException, StarletteHTTPException)):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    user_id = None
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            import jwt as pyjwt
            from config.settings import settings as _cfg
            token = auth_header[7:]
            payload = pyjwt.decode(token, _cfg.jwt_secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id") or payload.get("sub")
    except Exception:
        pass

    await monitor.capture(exc, context={
        "route": str(request.url.path),
        "method": request.method,
        "user_id": user_id,
    })
    logger.error(f"Erreur non geree [{request.method} {request.url.path}]: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "Une erreur interne est survenue. L'equipe a ete notifiee."}
    )

orchestrator = OrchestratorAgent()

@app.on_event("startup")
async def startup_event():
    from core.database import init_db
    logger.info("🚀 Démarrage de l'initialisation du backend...")
    
    try:
        logger.info("📡 Étape 1: Initialisation de la base de données...")
        await init_db()
        
        logger.info("🤖 Étape 2: Initialisation de l'orchestrateur d'agents...")
        await orchestrator.initialize()
        
        # --- Auto-Check Playwright ---
        logger.info("🌐 Étape 3: Vérification des navigateurs Playwright...")
        try:
            import os
            import subprocess
            # Force local install (to prevent Render from discarding cache between build and run)
            # The path is now set at the top of the file

            # Render path normally: /opt/render/.cache/ms-playwright/
            # We try to launch a browser in a separate thread to check if it exists
            def _check_pw():
                from playwright.sync_api import sync_playwright
                try:
                    with sync_playwright() as pw:
                        # Just test if chromium is launchable
                        browser = pw.chromium.launch(args=["--no-sandbox"])
                        browser.close()
                    return True
                except Exception as pw_err:
                    logger.warning(f"Playwright browser missing/error: {pw_err}")
                    return False
            
            pw_ok = await asyncio.to_thread(_check_pw)
            if not pw_ok:
                logger.info("Installing Playwright Chromium automatically...")
                # Try install
                result = subprocess.run(
                    [sys.executable, "-m", "playwright", "install", "chromium"],
                    capture_output=True, text=True, env=os.environ
                )
                if result.returncode == 0:
                    logger.success("Playwright Chromium installed successfully!")
                else:
                    logger.error(f"Playwright installation failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Non-critical Playwright check error: {e}")

        # --- Ghostbuster Scheduler (48h auto mode) ---
        logger.info("👻 Étape 4: Démarrage du Ghostbuster Scheduler (48h)...")
        try:
            from core.ghostbuster_scheduler import start_ghostbuster_scheduler
            start_ghostbuster_scheduler()
            
            from core.pre_interview_scheduler import pre_interview_scheduler
            await pre_interview_scheduler.start()

            from core.daily_hunt_scheduler import daily_hunt_scheduler
            await daily_hunt_scheduler.start()
        except Exception as e:
            logger.warning(f"Non-critical Ghostbuster scheduler start error: {e}")

        logger.success("✨ Initialisation du backend terminée avec succès!")
    except Exception as e:
        logger.error(f"💥 Erreur critique lors de l'initialisation: {e}")
        # On ne Raise pas forcément pour laisser Uvicorn binder le port et permettre le debug via API si possible
    
    # --- Démarrage Automatique du Frontend (Désactivé en Production) ---
    logger.info("ℹ️ Skip frontend auto-start (Production Mode)")

class ChatRequest(BaseModel):
    message: str
    cv_text: Optional[str] = None
    cv_filename: Optional[str] = None
    nb_results: Optional[int] = None
    location: Optional[str] = None
    session_id: Optional[str] = "default"
    image_data: Optional[str] = None # Base64 image for vision tasks
    background: Optional[bool] = False
    task_type: Optional[str] = "sniper" # 'sniper', 'mentor', 'cv_analysis'

class CVAdaptRequest(BaseModel):
    job_title: str
    job_description: str
    cv_text: str

class CompanyEnrichRequest(BaseModel):
    company_name: str

class HeadhunterRequest(BaseModel):
    company_name: str
    target_roles: Optional[str] = "HR OR Recruiter OR \"Talent Acquisition\" OR CTO OR CEO OR Director"

class EmailDraftRequest(BaseModel):
    company_name: str
    company_description: Optional[str] = ""
    hr_name: Optional[str] = ""
    request_type: str = "emploi"
    target_domain: Optional[str] = ""
    cv_text: str

class CRMApplicationRequest(BaseModel):
    job_title: str
    company_name: str
    url: Optional[str] = None
    reference: Optional[str] = None
    status: str = "TO_APPLY"
    notes: Optional[str] = None

class CRMStatusUpdateRequest(BaseModel):
    status: str

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    cv_text: Optional[str] = None
    portfolio_url: Optional[str] = None
    avatar_url: Optional[str] = None
    last_portfolio: Optional[dict] = None

class PromoteUserRequest(BaseModel):
    email: str
    tier: str = "PRO"

class PushTokenRequest(BaseModel):
    token: str

class SupportMessageRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class BroadcastRequest(BaseModel):
    title: str
    message: str
    type: str = "info"
    action_url: Optional[str] = None

class EmailAdminRequest(BaseModel):
    to_email: Optional[str] = None # If None, it's a broadcast
    subject: str
    content: str

class TrackEventRequest(BaseModel):
    event_name: str
    page_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class RejectionPivotRequest(BaseModel):
    app_id: str

@app.post("/api/users/push-token")
async def register_push_token(
    request: PushTokenRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
        await db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"push_tokens": request.token}}
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "ok", "message": "GoldArmy Agent V2 API is running"}

@app.post("/api/support/message")
async def send_support_message(
    request: SupportMessageRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Enregistre un message de support dans la base de données."""
    try:
        from datetime import datetime
        message_data = request.dict()
        message_data["created_at"] = datetime.utcnow()
        
        await db.support_messages.insert_one(message_data)
        
        logger.info(f"📩 Nouveau message de support de {request.email}: {request.subject}")
        
        return {"status": "success", "message": "Message envoyé avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message de support: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-pdf")
async def parse_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Receives a PDF CV from the frontend, extracts text using PyMuPDF (fitz), 
    and returns the raw text. Wait for PyMuPDF to be installed.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")
    
    try:
        import fitz # PyMuPDF
        
        content = await file.read()
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
            
        return {"status": "success", "text": text.strip()}
    except ImportError:
         raise HTTPException(status_code=500, detail="PyMuPDF (fitz) n'est pas installé sur le serveur.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du PDF: {str(e)}")


class CvRewriteRequest(BaseModel):
    cv_json: str  # JSON string du CV structuré
    filename: Optional[str] = "CV_ATS_Optimise"
    theme_id: Optional[str] = "midnight"  # midnight, emerald, modern, minimal, bold, banker, tech, classic, vibrant, luxury


@app.post("/api/generate-cv-pdf")
async def generate_cv_pdf_endpoint(raw_request: Request):
    """
    Reçoit cv_json + filename + template_id dans le body JSON.
    Templates : goldarmy, minimaliste, executive, creatif, classique, neon_tech, scandinave, timeline
    """
    try:
        import logging
        body = await raw_request.json()
        cv_data_input = body.get("cv_json")
        filename = (body.get("filename") or "CV_ATS_Optimise").replace(" ", "_").strip()
        template_id = (body.get("template_id") or body.get("templateId") or "goldarmy").strip().lower()

        if cv_data_input is None:
            raise HTTPException(status_code=400, detail="cv_json manquant")

        if isinstance(cv_data_input, str):
            cv_data_input = cv_data_input.strip()
            # Clean up markdown code blocks if present
            if cv_data_input.startswith("```json"):
                cv_data_input = cv_data_input[7:].strip()
            if cv_data_input.endswith("```"):
                cv_data_input = cv_data_input[:-3].strip()
                
            try:
                cv_data = json.loads(cv_data_input)
            except json.JSONDecodeError as e:
                import re
                import logging
                logging.warning(f"Initial JSON decode failed: {e}. Attempting regex extraction.")
                match = re.search(r'\{.*\}', cv_data_input, re.DOTALL)
                if match:
                    try:
                        cv_data = json.loads(match.group(0))
                    except json.JSONDecodeError as e2:
                        logging.error(f"Regex JSON decode failed: {e2}")
                        raise e2
                else:
                    raise e
        elif isinstance(cv_data_input, dict):
            cv_data = cv_data_input
        else:
            cv_data = {}

        from core.cv_generator import normalize_cv_json
        cv_data = normalize_cv_json(cv_data)

        from core.cv_html_templates import build_html, TEMPLATES as HTML_TEMPLATES
        if template_id not in HTML_TEMPLATES:
            template_id = "goldarmy"
        logging.info(f"[PDF] Generating '{template_id}' via Playwright")
        html_content = build_html(template_id, cv_data)

        try:
            def _generate_pdf_sync(html: str) -> bytes:
                from playwright.sync_api import sync_playwright
                try:
                    with sync_playwright() as pw:
                        # Add sandbox flags for better compatibility in various environments
                        browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
                        page = browser.new_page()
                        # Use 'load' instead of 'networkidle' to avoid hanging on slow external assets
                        # and set a reasonable timeout.
                        page.set_content(html, wait_until="load", timeout=20000)
                        p_bytes = page.pdf(
                            format="A4", print_background=True,
                            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
                        )
                        browser.close()
                        return p_bytes
                except Exception as e:
                    import logging
                    logging.error(f"[Playwright] Critical PDF generation error: {str(e)}")
                    raise e

            import asyncio
            # Run playwright isolated in its own synchronous thread avoiding asyncio Windows NotImplementedError
            pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, html_content)
        except Exception as pw_err:
            logging.error(f"Playwright PDF error: {pw_err}")
            raise HTTPException(status_code=500, detail=f"Erreur Playwright: {pw_err}")

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-CV-Template": template_id,
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON CV invalide: {str(e)}")
    except Exception as e:
        import logging
        logging.exception("Erreur generation PDF")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")


@app.post("/api/generate-cv-pdf-html")
async def generate_cv_pdf_from_html(raw_request: Request):
    """
    Accepts a pre-rendered HTML string from the frontend (built using the JS/TS CV templates)
    and converts it to a PDF via Playwright. This allows the frontend templates to be the
    single source of truth for CV design, in sync with the mobile app.
    Body: { html: string, filename?: string }
    """
    import logging
    try:
        body = await raw_request.json()
        html_content = body.get("html", "")
        filename = (body.get("filename") or "CV_ATS_Optimise").replace(" ", "_").strip()
        if not html_content:
            raise HTTPException(status_code=400, detail="html manquant dans la requête")

        def _generate_pdf_sync(html: str) -> bytes:
            from playwright.sync_api import sync_playwright
            try:
                with sync_playwright() as pw:
                    # Add sandbox flags for better compatibility
                    browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
                    page = browser.new_page()
                    # Use 'load' + timeout to prevent hanging on external fonts/assets
                    page.set_content(html, wait_until="load", timeout=20000)
                    p_bytes = page.pdf(
                        format="A4", print_background=True,
                        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
                    )
                    browser.close()
                    return p_bytes
            except Exception as e:
                import logging
                logging.error(f"[Playwright-HTML] Critical PDF generation error: {str(e)}")
                raise e

        pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, html_content)

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
    except Exception as e:
        logging.exception("Erreur generation PDF depuis HTML")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")

@app.post("/api/generate-cv-word")
async def generate_cv_word_endpoint(raw_request: Request):
    """
    Accepte le cv_json et génère un document Word (.docx) ATS-friendly.
    Body: { cv_json: dict, filename?: string }
    """
    import logging
    try:
        body = await raw_request.json()
        cv_data = body.get("cv_json")
        filename = (body.get("filename") or "CV_Optimise").replace(" ", "_").strip()
        theme_id = body.get("theme_id", "goldarmy")
        
        if not cv_data:
            raise HTTPException(status_code=400, detail="cv_json manquant dans la requête")
            
        from core.cv_word_generator import generate_cv_word
        
        # Génération du Word de manière asynchrone pour ne pas bloquer
        docx_bytes = await asyncio.to_thread(generate_cv_word, cv_data, theme_id)
        
        if not filename.endswith(".docx"):
            filename += ".docx"
            
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
        
        from fastapi.responses import StreamingResponse
        import io
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except Exception as e:
        logging.exception("Erreur generation Word")
        raise HTTPException(status_code=500, detail=f"Erreur génération Word: {str(e)}")

@app.post("/api/network/enrich")
async def enrich_company(request: CompanyEnrichRequest, current_user: dict = Depends(get_current_user)):
    """Cherche les profils RH LinkedIn pour une entreprise."""
    check = await check_subscription_limit(current_user["id"], "network_access")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="L'enrichissement des profils et l'accès direct au réseau sont réservés aux abonnés ESSENTIAL et PRO.")
    try:
        from tools.linkedin_scraper import linkedin_scraper
        profiles = await linkedin_scraper.find_hr_profiles(request.company_name)
        return {"status": "success", "data": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network/headhunter")
async def find_decision_makers_api(req: HeadhunterRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Trouve les décideurs clés via l'Agent Headhunter."""
    # Check limit
    check = await check_subscription_limit(current_user["id"], "headhunter")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail=check["message"])

    try:
        from agents.headhunter import headhunter_agent
        await headhunter_agent.initialize()
        
        profiles = await headhunter_agent.find_decision_makers({
            "company_name": req.company_name,
            "target_roles": req.target_roles
        })
        
        if profiles:
            from agents.network_ninja_agent import network_ninja_agent
            background_tasks.add_task(network_ninja_agent.add_manual_search, current_user["id"], req.company_name, profiles)
        
        await log_usage(current_user["id"], "headhunter")
        return {"status": "success", "data": profiles}
    except Exception as e:
        import logging
        logging.error(f"Erreur API Headhunter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network/draft-email")
async def draft_network_email(request: EmailDraftRequest, current_user: dict = Depends(get_current_user)):
    """Rédige un courriel d'approche via Gemini."""
    check = await check_subscription_limit(current_user["id"], "network_access")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="La rédaction de courriels d'approche réseau est réservée aux forfaits ESSENTIAL et PRO.")
    try:
        from agents.network_agent import NetworkAgent
        agent = NetworkAgent()
        await agent.initialize()
        email_data = await agent.draft_email(request.dict())
        return {"status": "success", "data": email_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GoldProfileTopicRequest(BaseModel):
    topic: str

@app.post("/api/network/gold-profile/audit")
async def gold_profile_audit(current_user: dict = Depends(get_current_user)):
    check = await check_subscription_limit(current_user["id"], "portfolio")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="L'audit de branding LinkedIn et le Portfolio IA sont réservés aux abonnés ESSENTIAL et PRO.")
    from agents.mentor import MentorAgent
    from core.database import get_db
    
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    cv_text = user.get("cv_text", "")
    
    if not cv_text:
        raise HTTPException(status_code=400, detail="Veuillez d'abord uploader un CV dans votre profil pour utiliser Gold Profile.")
        
    mentor = MentorAgent()
    await mentor.initialize()
    result = await mentor.think({"action": "gold_profile_audit", "cv_text": cv_text})
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("content", "Erreur lors de l'audit."))
        
    return {"status": "success", "data": result.get("data")}

@app.post("/api/network/gold-profile/plan")
async def gold_profile_plan(current_user: dict = Depends(get_current_user)):
    check = await check_subscription_limit(current_user["id"], "portfolio")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="La planification de contenu réseau et le Portfolio IA sont inaccessibles en compte gratuit.")
    from agents.mentor import MentorAgent
    from core.database import get_db
    
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    cv_text = user.get("cv_text", "")
    
    mentor = MentorAgent()
    await mentor.initialize()
    result = await mentor.think({"action": "gold_profile_plan", "cv_text": cv_text})
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("content", "Erreur lors de la planification."))
        
    return {"status": "success", "data": result.get("data")}

@app.post("/api/network/gold-profile/post")
async def gold_profile_post(req: GoldProfileTopicRequest, current_user: dict = Depends(get_current_user)):
    check = await check_subscription_limit(current_user["id"], "portfolio")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="La génération de posts viraux et le Portfolio IA nécessitent le déblocage du forfait ESSENTIAL ou PRO.")
    from agents.mentor import MentorAgent
    from core.database import get_db
    
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    cv_text = user.get("cv_text", "")
    
    mentor = MentorAgent()
    await mentor.initialize()
    result = await mentor.think({"action": "gold_profile_post", "cv_text": cv_text, "topic": req.topic})
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("content", "Erreur lors de la génération du post."))
        
    return {"status": "success", "data": result.get("data")}


@app.get("/api/network/contacts")
async def get_network_contacts(current_user: dict = Depends(get_current_user)):
    """Récupère tout le carnet d'adresses réseau."""
    check = await check_subscription_limit(current_user["id"], "address_book")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="L'accès au carnet d'adresses réseau enrichi est réservé aux forfaits ESSENTIAL et PRO.")
    import json as _json
    try:
        from core.database import get_db
        db = get_db()
        cursor = db.contacts.find({
            "$or": [
                {"user_id": current_user["id"]},
                {"user_id": 'system_user'}
            ]
        }).sort("last_updated", -1)
        rows = await cursor.to_list(length=None)
        
        contacts = []
        for row in rows:
            contact = dict(row)
            # Clean ObjectID
            if "_id" in contact:
                contact["_id"] = str(contact["_id"])
            
            # Format emails list if needed
            if contact.get("emails") and isinstance(contact["emails"], str):
                try:
                    contact["emails"] = _json.loads(contact["emails"])
                except Exception:
                    contact["emails"] = contact["emails"].split(",")
            elif not contact.get("emails"):
                contact["emails"] = []
            
            contacts.append(contact)
        return {"status": "success", "data": contacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Profile Endpoints
# ==========================================

@app.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Récupère les informations complètes du profil utilisateur."""
    from core.database import get_db
    db = get_db()
    try:
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return {"status": "success", "data": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    """Retourne l'utilisation actuelle de chaque feature pour l'utilisateur."""
    from api.subscription import SUBSCRIPTION_LIMITS, check_subscription_limit
    user_id = current_user["id"]
    db = get_db()
    user = await db.users.find_one({"id": user_id})
    tier = user.get("subscription_tier", "FREE") if user else "FREE"
    limits_config = SUBSCRIPTION_LIMITS.get(tier, SUBSCRIPTION_LIMITS["FREE"])

    usage = {}
    for feature, config in limits_config.items():
        result = await check_subscription_limit(user_id, feature)
        usage[feature] = {
            "current": result.get("current", 0),
            "limit": config["limit"],
            "period": config["period"],
            "allowed": result.get("allowed", True)
        }

    return {"status": "success", "data": {"tier": tier, "usage": usage}}

@app.post("/api/profile")
async def update_profile(request: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Met à jour les informations du profil utilisateur."""
    from core.database import get_db
    from datetime import datetime
    db = get_db()
    try:
        fields = request.dict(exclude_unset=True)
        if not fields:
            return {"status": "success", "message": "Aucun champ à mettre à jour"}
        
        # --- LOGIQUE HISTORIQUE CV ---
        if "cv_text" in fields:
            old_user = await db.users.find_one({"id": current_user["id"]}, {"cv_text": 1})
            if old_user and old_user.get("cv_text") and old_user.get("cv_text") != fields["cv_text"]:
                history_entry = {
                    "cv_text": old_user["cv_text"],
                    "updated_at": datetime.utcnow().isoformat(),
                    "name": f"Version du {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
                }
                await db.users.update_one(
                    {"id": current_user["id"]},
                    {"$push": {"cv_history": {"$each": [history_entry], "$position": 0, "$slice": 10}}}
                )
        # -----------------------------

        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": fields}
        )
        return {"status": "success", "message": "Profil mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _analyze_cv_background(user_id: str, content: bytes):
    """Extraction de texte en tâche de fond avec notification."""
    import fitz
    try:
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        
        extracted_text = text.strip()
        from core.database import get_db
        db = get_db()
        await db.users.update_one(
            {"id": user_id}, 
            {"$set": {"cv_text": extracted_text}}
        )
        return {"text": extracted_text}
    except Exception as e:
        from loguru import logger
        logger.error(f"Background CV analysis error: {e}")
        raise e

@app.post("/api/profile/upload-cv")
async def upload_cv_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    background: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Upload un CV PDF, extrait le texte et le sauvegarde dans le profil."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les PDF sont acceptés")
    
    try:
        content = await file.read()
        
        if background:
            task_id = await create_task(current_user["id"], "cv_analysis")
            background_tasks.add_task(
                run_background_task,
                task_id,
                current_user["id"],
                _analyze_cv_background,
                current_user["id"],
                content
            )
            return {"status": "pending", "task_id": task_id, "message": "Analyse du CV lancée en arrière-plan."}

        # Direct extraction
        import fitz
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        
        extracted_text = text.strip()
        
        from core.database import get_db
        db = get_db()
        await db.users.update_one(
            {"id": current_user["id"]}, 
            {"$set": {"cv_text": extracted_text}}
        )
        
        return {"status": "success", "text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def list_tasks(current_user: dict = Depends(get_current_user)):
    """Liste les tâches récentes de l'utilisateur."""
    tasks = await get_recent_tasks(current_user["id"])
    return {"status": "success", "data": tasks}

@app.get("/api/tasks/{task_id}")
async def fetch_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Récupère l'état et le résultat d'une tâche spécifique."""
    task = await get_task(task_id, current_user["id"])
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    return {"status": "success", "data": task}

@app.post("/api/profile/upload-avatar")
async def upload_avatar_endpoint(request: Request, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload une photo de profil et sauvegarde l'URL."""
    import os
    import uuid
    
    UPLOAD_DIR = "static/uploads/avatars"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user['id']}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Build the public URL using the incoming request base (works in all envs)
        # Falls back to BASE_URL env var, then to the request origin.
        base_url = os.getenv("BASE_URL", "").rstrip("/")
        if not base_url:
            base_url = str(request.base_url).rstrip("/")
        avatar_url = f"{base_url}/static/uploads/avatars/{filename}"
        
        from core.database import get_db
        db = get_db()
        await db.users.update_one(
            {"id": current_user["id"]}, 
            {"$set": {"avatar_url": avatar_url}}
        )
        
        return {"status": "success", "avatar_url": avatar_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Servir les fichiers statiques (Uploads)
from fastapi.staticfiles import StaticFiles
import os
os.makedirs("static/uploads/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CRM Endpoints (Kanban) ---
# Note: Les endpoints /api/crm/applications font doublons avec /api/crm
# Je les supprime et on passe directement au drag and drop status et followup.

@app.put("/api/crm/applications/{app_id}/status")
async def update_crm_status(app_id: str, request: CRMStatusUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Met à jour le statut (Drag and Drop) et horodate MongoDB."""
    try:
        from core.database import get_db
        from datetime import datetime
        
        db = get_db()
        update_fields = {"status": request.status}
        
        if request.status == "APPLIED":
            update_fields["applied_at"] = datetime.utcnow()
            
        await db.applications.update_one(
            {"id": app_id, "user_id": current_user["id"]},
            {"$set": update_fields}
        )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/crm/applications/{app_id}/followup")
async def generate_followup_email(app_id: str, current_user: dict = Depends(get_current_user)):
    """Génère un email de relance personnalisé et incrémente le compteur MongoDB."""
    try:
        from core.database import get_db
        db = get_db()

        # Fetch application details
        app_data = await db.applications.find_one({"id": app_id, "user_id": current_user["id"]})
        if not app_data:
            raise HTTPException(status_code=404, detail="Application not found")

        job_title = app_data.get("job_title", "le poste")
        company = app_data.get("company_name", "l'entreprise")
        notes = app_data.get("notes", "")

        # Check limit
        check = await check_subscription_limit(current_user["id"], "follow_up")
        if not check["allowed"]:
            raise HTTPException(status_code=403, detail=check["message"])

        # Increment follow-up counter (scoped by user_id for security)
        updated = await db.applications.find_one_and_update(
            {"id": app_id, "user_id": current_user["id"]},
            {"$inc": {"follow_up_count": 1}},
            return_document=True
        )
        follow_up_count = updated.get("follow_up_count", 1) if updated else 1

        # Email de relance avec gemini-2.0-flash (même modèle que Sniper / reste de l'app)
        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()

        prompt = (
            "Tu rédiges un email de relance professionnel COMPLET en français. "
            "Le mail doit OBLIGATOIREMENT contenir les 4 parties suivantes, dans l'ordre :\n"
            "1) Objet: [un sujet clair]\n"
            "2) Formule d'appel (ex: Bonjour, ou Bonjour M. Dupont,)\n"
            "3) Corps du mail : 3 à 5 phrases complètes. Rappeler la candidature (poste et entreprise), "
            "réaffirmer ton intérêt, demander poliment où en est le processus de recrutement.\n"
            "4) Formule de politesse (Cordialement, ou Bien à vous,) puis une ligne type [Prénom].\n\n"
            f"Contexte : candidature pour {job_title} chez {company}. "
            f"Notes : {notes if notes else 'Aucune.'} "
            f"Relance n°{follow_up_count}. Si >1, ton un peu plus direct.\n\n"
            "Réponds UNIQUEMENT par le texte de l'email complet, rien d'autre."
        )
        messages = [{"role": "user", "content": prompt}]
        email_text = await llm.chat(
            messages,
            model="gemini-2.0-flash",
            max_tokens=2048,
            temperature=0.7,
            timeout=120,
        )
        if not email_text or not email_text.strip():
            raise HTTPException(status_code=503, detail="Réponse vide du modèle. Réessayez.")

        await log_usage(current_user["id"], "follow_up")

        return {
            "status": "success",
            "email": email_text,
            "followUpCount": follow_up_count
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Followup generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Dashboard Endpoints
# ==========================================
@app.get("/api/portfolio/download-zip")
async def download_portfolio_zip(current_user: dict = Depends(get_current_user)):
    """Convertit le portfolio stocké en base de données en archive ZIP."""
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]}, {"last_portfolio": 1, "_id": 0})
    
    if not user or "last_portfolio" not in user:
        raise HTTPException(status_code=404, detail="Aucun portfolio trouvé. Générez-en un d'abord !")
    
    project = user["last_portfolio"]
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("index.html", project.get("html", ""))
        zip_file.writestr("style.css", project.get("css", "/* Extra CSS */"))
        zip_file.writestr("script.js", project.get("js", "// Extra JS"))
        
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=goldarmy_portfolio.zip"}
    )

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques réelles pour le Dashboard depuis MongoDB Atlas."""
    try:
        from core.database import get_db
        db = get_db()
        
        # 1. Candidatures envoyées (tout sauf TO_APPLY)
        applied_count = await db.applications.count_documents({
            "status": {"$ne": "TO_APPLY"}, 
            "user_id": current_user["id"]
        })
        
        # 2. Entretiens (status = INTERVIEW)
        interview_count = await db.applications.count_documents({
            "status": "INTERVIEW", 
            "user_id": current_user["id"]
        })
        
        # 3. Réseau (Contacts totaux — user direct + système)
        network_count = await db.contacts.count_documents({
            "$or": [
                {"user_id": current_user["id"]},
                {"user_id": "system_user"}
            ]
        })
        
        # 4. CV Analysés (Candidatures totales)
        cv_analyzed = await db.applications.count_documents({
            "user_id": current_user["id"]
        })
        
        # 5. Croissance Mensuelle (Aggregation Pipeline)
        pipeline = [
            {"$match": {
                "user_id": current_user["id"],
                "created_at": {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$created_at"}}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        monthly_raw = await db.applications.aggregate(pipeline).to_list(length=None)
        monthly_dict = {row["_id"]: row["count"] for row in monthly_raw if row.get("_id")}

        import datetime
        from dateutil.relativedelta import relativedelta
        
        now = datetime.datetime.now()
        chart_data = []
        months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        
        max_val = max(monthly_dict.values()) if monthly_dict else 10
        if max_val < 10: max_val = 10
        
        for i in range(7, -1, -1):
            d = now - relativedelta(months=i)
            key = d.strftime('%Y-%m')
            count = monthly_dict.get(key, 0)
            
            pct = int((count / max_val) * 80) + 10
            if count == 0: pct = 5
            
            chart_data.append({
                "label": months_fr[d.month - 1],
                "count": count,
                "heightPct": pct
            })
            
        return {
            "status": "success", 
            "data": {
                "kpis": {
                    "applied": applied_count,
                    "interviews": interview_count,
                    "network": network_count,
                    "cv_analyzed": cv_analyzed
                },
                "chart": chart_data
            }
        }
    except Exception as e:
        import logging
        logging.error(f"Erreur Dashboard Stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _enrich_contacts_from_jobs(content: Any, user_id: str) -> None:
    """Enrichit le carnet avec site officiel + emails RH pour les entreprises des offres trouvées."""
    if not content or not isinstance(content, dict):
        return
    jobs = content.get("matched_jobs") or content.get("jobs") or []
    if not jobs:
        return
    seen = set()
    companies = []
    for j in jobs:
        company = (j.get("company") or "").strip()
        if not company or company.lower() in ("confidentiel", "anonyme", "incognito"):
            continue
        key = company.lower()
        if key not in seen:
            seen.add(key)
            apply_email = (j.get("apply_email") or "").strip().lower()
            if "@" not in apply_email:
                apply_email = ""
            companies.append({
                "company": company,
                "location": j.get("location", ""),
                "source_job": j.get("url", ""),
                "apply_email": apply_email
            })
    companies = companies[:12]
    if not companies:
        return
    try:
        from tools.web_searcher import web_searcher
        from core.contacts import contacts_manager
        for c in companies:
            try:
                data = await web_searcher.find_official_website_and_contact(c["company"], c.get("location", ""))
                emails = list(data.get("emails", []))
                if c.get("apply_email") and c["apply_email"] not in emails:
                    emails.insert(0, c["apply_email"])
                if data.get("site_url") or emails:
                    await contacts_manager.save_contact(
                        company_name=data["company_name"],
                        site_url=data.get("site_url", ""),
                        emails=emails,
                        phone=data.get("phone", ""),
                        source_job=c.get("source_job", ""),
                        category="Sniper Recherche",
                        user_id=user_id
                    )
                    logger.info(f"📇 Carnet enrichi: {data['company_name']} ({len(emails)} emails)")
            except Exception as e:
                logger.debug(f"Enrich contact {c.get('company')}: {e}")
    except Exception as e:
        logger.warning(f"Enrichissement carnet: {e}")


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Main endpoint for interacting with the Orchestrator.
    Handles general chat, search requests, and CV context.
    """
    logger.info(f"📥 REQUEST /api/chat - User: {current_user['email']} | Message: {request.message[:50]}")
    try:
        # Intercept search for limit check
        if request.nb_results or any(k in request.message.lower() for k in ["cherche", "trouve", "stage", "emploi", "job"]):
            check = await check_subscription_limit(current_user["id"], "sniper_search")
            if not check["allowed"]:
                return {
                    "status": "error",
                    "type": "limit_reached",
                    "content": check["message"]
                }
        
        cv_text = request.cv_text
        cv_filename = request.cv_filename

        # Auto-CV Retrieval from MongoDB if missing
        if not cv_text:
            from core.database import get_db
            db = get_db()
            user_profile = await db.users.find_one({"id": current_user["id"]}, {"cv_text": 1, "_id": 0})
            if user_profile and user_profile.get("cv_text"):
                cv_text = user_profile["cv_text"]
                cv_filename = "CV_Profil_Sauvegarde.pdf"
                logger.info(f"Using stored CV for user {current_user['id']}")

        task = {
            "query": request.message,
            "cv_text": cv_text,
            "cv_filename": cv_filename,
            "nb_results": request.nb_results,
            "location": request.location,
            "session_id": request.session_id or "default",
            "image_data": request.image_data
        }
        
        # Background mode handling
        if request.background:
            t_type = request.task_type or "sniper"
            task_id = await create_task(current_user["id"], t_type)
            background_tasks.add_task(
                run_background_task,
                task_id,
                current_user["id"],
                orchestrator.think,
                task
            )
            return {"status": "pending", "task_id": task_id, "message": "Recherche lancée en arrière-plan. Vous recevrez une notification une fois terminée."}

        response = await orchestrator.think(task)

        # Log usage si recherche d'emploi
        if response.get("type") == "job_search_results":
            await log_usage(current_user["id"], "sniper_search")
            # Enrichissement carnet en arrière-plan : site officiel + emails RH pour chaque entreprise
            asyncio.create_task(_enrich_contacts_from_jobs(response.get("content"), current_user["id"]))
        
        # Persistance du Portfolio en MongoDB si généré
        if response.get("type") == "portfolio_project":
            try:
                db = get_db()
                await db.users.update_one(
                    {"id": current_user["id"]},
                    {"$set": {"last_portfolio": response.get("project")}}
                )
                logger.info(f"💾 Portfolio sauvegardé pour l'utilisateur {current_user['id']}")
            except Exception as e:
                logger.error(f"❌ Erreur sauvegarde portfolio: {e}")

        return {"status": "success", "data": response}
    except Exception as e:
        import logging
        logging.exception("Erreur /api/chat")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/adapt-cv")
async def adapt_cv_endpoint(request: CVAdaptRequest, current_user: dict = Depends(get_current_user)):
    """
    Adapter un CV spécifiquement pour une offre d'emploi via Gemini 3.
    """
    try:
        from loguru import logger
        if not request.cv_text or len(request.cv_text) < 50:
            raise HTTPException(status_code=400, detail="Le texte du CV est introuvable ou trop court. Veuillez uploader un CV d'abord.")
            
        # Check limit
        check = await check_subscription_limit(current_user["id"], "cv_adaptation")
        if not check["allowed"]:
            raise HTTPException(status_code=403, detail=check["message"])
            
        from agents.cv_adapter import CVAdapterAgent
        adapter = CVAdapterAgent()
        await adapter.initialize()
        
        result = await adapter.adapt(
            job_title=request.job_title,
            job_desc=request.job_description,
            cv_text=request.cv_text
        )
        
        await log_usage(current_user["id"], "cv_adaptation")
        return {"status": "success", "data": result}
    except Exception as e:
        from loguru import logger
        logger.error(f"Error in adapt_cv_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- CRM Endpoints (Sniper Pillar) ---
# Note: Consolidé pour utiliser core.database au lieu de api.crm_db (JSON)
from core.database import get_db

class CRMLinkRequest(BaseModel):
    url: str

@app.post("/api/crm/link")
async def add_crm_from_link(request: CRMLinkRequest, current_user: dict = Depends(get_current_user)):
    """Scrape une URL d'offre d'emploi, extrait le poste et l'entreprise via Gemini et l'ajoute au CRM."""
    import uuid
    from datetime import datetime
    import httpx
    try:
        from loguru import logger
        logger.info(f"[CRM] Scraping de l'URL: {request.url}")
        
        # 1. Scraper le contenu de la page
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            resp = await client.get(request.url, headers=headers)
            resp.raise_for_status()
            html_content = resp.text

        # 2. Nettoyer basiquement le HTML et extraire les métadonnées pour Gemini (utile pour les sites JS)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extraire le title et les metas OG pour aider l'IA (très utile si le body est vide car rendu en JS)
        page_title = soup.title.string if soup.title else ""
        og_title_tag = soup.find("meta", attrs={"property": "og:title"})
        og_title = og_title_tag["content"] if og_title_tag else ""
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"] if meta_desc_tag else ""
        
        # Nettoyer le script/style
        for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            script.decompose()
        text_content = soup.get_text(separator=" ", strip=True)
        # Tronquer à 15000 caractères pour le LLM
        text_snippet = text_content[:15000]

        # 3. Extraction via LLM
        from llm.unified_client import UnifiedLLMClient
        import json
        llm = UnifiedLLMClient()
        prompt = f"""Tu es un assistant expert en recrutement.
Voici les métadonnées et le texte extrait d'une page web d'offre d'emploi :

[METADONNEES SEO]
Titre de la page : {page_title}
OG Title : {og_title}
Description : {meta_desc}

[CONTENU DU CORPS]
{text_snippet}

Renvoie UNIQUEMENT un JSON avec les clés :
- "job_title" (le titre explicite du poste, ex: "Développeur Full Stack")
- "company_name" (le nom de l'entreprise qui recrute)
- "job_summary" (un résumé concis de l'offre en 2-3 phrases max, incluant les technos/mots-clés principaux ou les missions clés)
Ne rajoute PAS de balises markdown comme ```json, renvoie uniquement l'objet JSON brut."""
        
        logger.info(f"[CRM] Appel LLM pour extraction d'offre...")
        result_text = await llm.chat([{"role": "user", "content": prompt}], json_mode=True)
        
        extracted = {}
        try:
            import re
            cleaned_result = re.sub(r'```json\s*', '', result_text, flags=re.IGNORECASE)
            cleaned_result = re.sub(r'```\s*', '', cleaned_result).strip()
            
            json_match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group(0))
            else:
                extracted = json.loads(cleaned_result)
        except Exception as parse_error:
            logger.error(f"[CRM] Erreur parsing JSON: {parse_error} - Raw: {result_text}")
            extracted = {}
            
        job_title = str(extracted.get("job_title", "")).strip()
        company_name = str(extracted.get("company_name", "")).strip()
        job_summary = str(extracted.get("job_summary", "")).strip()
        
        if not job_title or job_title.lower() == "none" or job_title.lower() == "inconnu": job_title = "Poste non identifié"
        if not company_name or company_name.lower() == "none" or company_name.lower() == "inconnu": company_name = "Entreprise non identifiée"
        if not job_summary: job_summary = "Ajouté via le lien externe (aucune description extraite)."
            
        logger.info(f"[CRM] Link Extrait: '{job_title}' chez '{company_name}'")

        # 4. Insertion dans MongoDB
        db = get_db()
        app_id = str(uuid.uuid4())
        
        new_app = {
            "id": app_id,
            "user_id": current_user["id"],
            "job_title": job_title,
            "company_name": company_name,
            "url": request.url,
            "reference": "",
            "status": "APPLIED",
            "notes": job_summary,
            "created_at": datetime.utcnow()
        }
        
        await db.applications.insert_one(new_app)
        
        # Rend les ObjectId stringifiable
        new_app["_id"] = str(new_app["_id"])
        
        return {"status": "success", "data": new_app}
        
    except httpx.HTTPError as e:
        logger.error(f"[CRM] Erreur HTTP lors du scraping : {e}")
        raise HTTPException(status_code=400, detail="Impossible d'accéder à ce lien. Le site bloque l'accès aux requêtes externes.")
    except Exception as e:
        logger.error(f"[CRM] Erreur traitement lien CRM: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du lien: {str(e)}")

@app.get("/api/crm")
async def fetch_crm(current_user: dict = Depends(get_current_user)):
    """Alias pour les candidatures existantes via MongoDB."""
    try:
        db = get_db()
        cursor = db.applications.find({"user_id": current_user["id"]}).sort("created_at", -1)
        apps = await cursor.to_list(length=None)
        
        # Clean ObjectID for JSON serialization
        for app in apps:
            app["_id"] = str(app["_id"])
            
        return {"status": "success", "data": apps}
    except Exception as e:
        logger.error(f"Error fetching CRM: {e}")
        return {"status": "error", "message": "Failed to fetch CRM data"}

@app.post("/api/crm")
async def create_crm_entry(request: CRMApplicationRequest, current_user: dict = Depends(get_current_user)):
    """Crée une entrée dans le CRM MongoDB."""
    import uuid
    from datetime import datetime
    try:
        db = get_db()
        app_id = str(uuid.uuid4())
        
        new_app = {
            "id": app_id,
            "user_id": current_user["id"],
            "job_title": request.job_title,
            "company_name": request.company_name,
            "url": request.url,
            "reference": getattr(request, 'reference', ''),
            "status": request.status,
            "notes": getattr(request, 'notes', ''),
            "created_at": datetime.utcnow() # Using UTC for safer global timestamping
        }
        
        await db.applications.insert_one(new_app)
        
        # Trigger workflow event
        if request.status == "TO_APPLY":
            from core.orchestrator import orchestrator
            await orchestrator.dispatch_event("sniper_to_apply", {
                "companyName": request.company_name,
                "jobTitle": request.job_title,
                "app_id": app_id,
                "user_id": current_user["id"]
            })
            
        return {"status": "success", "data": {"id": app_id}}
    except Exception as e:
        logger.error(f"Error creating CRM entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create CRM entry")

@app.put("/api/crm/{item_id}")
async def update_crm_entry(item_id: str, updates: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Met à jour une entrée CRM MongoDB."""
    try:
        db = get_db()
        
        # Filtre les champs modifiables
        allowed_fields = ["status", "notes", "job_title", "company_name"]
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not update_fields:
            return {"status": "success", "message": "No changes"}
            
        await db.applications.update_one(
            {"id": item_id, "user_id": current_user["id"]},
            {"$set": update_fields}
        )
        
        # Dispatch workflow events based on status change
        if "status" in update_fields:
            new_status = update_fields["status"]
            app_data = await db.applications.find_one({"id": item_id, "user_id": current_user["id"]})
            if app_data:
                from core.orchestrator import orchestrator
                payload = {
                    "companyName": app_data.get("company_name", ""),
                    "jobTitle": app_data.get("job_title", ""),
                    "app_id": item_id,
                    "user_id": current_user["id"]
                }
                if new_status == "TO_APPLY":
                    await orchestrator.dispatch_event("sniper_to_apply", payload)
                elif new_status == "INTERVIEW":
                    await orchestrator.dispatch_event("interview_scheduled", payload)
                elif new_status == "REJECTED":
                    await orchestrator.dispatch_event("card_rejected", payload)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error updating CRM entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to update CRM entry")

@app.delete("/api/crm/{item_id}")
async def delete_crm_entry(item_id: str, current_user: dict = Depends(get_current_user)):
    """Supprime une entrée CRM MongoDB."""
    try:
        db = get_db()
        await db.applications.delete_one({"id": item_id, "user_id": current_user["id"]})
        return {"status": "success", "message": "Deleted"}
    except Exception as e:
        logger.error(f"Erreur delete CRM: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --- Workflows Endpoints ---
class SmartCoverRequest(BaseModel):
    company_name: str
    job_title: Optional[str] = "Poste ouvert"

@app.post("/api/workflows/smart-cover")
async def execute_smart_cover(req: SmartCoverRequest, current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Exécute le Playbook 10 (Smart Cover) et retourne le résultat."""
    from agents.headhunter import headhunter_agent
    
    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    user_data = await db.users.find_one({"id": user_id})
    cv_text = user_data.get("cv_text", "") if user_data else ""
    
    logger.info(f"🧪 Test Smart Cover pour {req.company_name} par {current_user['email']}")
    result = await headhunter_agent.generate_smart_cover_letter(req.company_name, req.job_title, cv_text=cv_text)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {
        "status": "success",
        "data": result
    }

@app.post("/api/workflows/smart-cover/bulk")
async def execute_smart_cover_bulk(req: List[SmartCoverRequest], current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Exécute le Playbook 10 pour plusieurs entreprises."""
    from agents.headhunter import headhunter_agent
    
    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    user_data = await db.users.find_one({"id": user_id})
    cv_text = user_data.get("cv_text", "") if user_data else ""
    
    results = []
    for item in req:
        logger.info(f"🧪 Bulk Smart Cover pour {item.company_name}")
        res = await headhunter_agent.generate_smart_cover_letter(item.company_name, item.job_title, cv_text=cv_text)
        results.append({"company": item.company_name, "result": res})
    
    return {"status": "success", "data": results}

@app.post("/api/workflows/smart-cover/download")
async def download_cover_letter(data: dict, current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Génère et retourne un PDF de la lettre avec gestion Premium/Standard."""
    from core.pdf_service import generate_cover_letter_pdf
    
    # Vérification Premium
    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    user_data = await db.users.find_one({"id": user_id})
    
    # On vérifie si l'utilisateur a un abonnement payant ou est ADMIN
    user_tier = (user_data.get("subscription_tier") or user_data.get("tier") or user_data.get("plan") or "FREE").upper()
    is_premium_user = user_tier == "ADMIN" or user_tier not in ["FREE", "BASIC", ""]
    force_standard = data.get("force_standard", False)
    is_premium = is_premium_user and not force_standard
    
    # Données pour le PDF
    pdf_data = {
        "letter": data.get("letter", ""),
        "full_name": user_data.get("full_name") if user_data else "Candidat",
        "email": user_data.get("email") if user_data else "",
        "phone": user_data.get("phone", "") if user_data else ""
    }
    
    pdf_bytes = generate_cover_letter_pdf(pdf_data, is_premium=is_premium)
    
    filename = f"lettre_motivation_{data.get('company','box')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==========================================
# Ghostbuster Workflow Endpoints (#2)
# ==========================================

class GhostbusterToggleRequest(BaseModel):
    enabled: bool

class GhostbusterSendRequest(BaseModel):
    app_id: str
    via: str = "manual"  # "email" | "linkedin" | "manual"

class GhostbusterScanRequest(BaseModel):
    force_regenerate: bool = False
    chain_to: Optional[str] = None  # "network_ninja" | "post_interview" | None

@app.post("/api/workflows/ghostbuster/scan")
async def ghostbuster_scan(
    req: GhostbusterScanRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Scanne les candidatures APPLIED sans réponse depuis > 15 jours ouvrables.
    Génère email de relance + message LinkedIn pour chaque candidature éligible.
    Ne re-génère pas si une relance existe déjà (sauf si force_regenerate=True).
    """
    try:
        from agents.ghostbuster_agent import ghostbuster_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        result = await ghostbuster_agent.scan_and_generate(
            user_id=user_id,
            chain_to=req.chain_to,
            force_regenerate=req.force_regenerate,
        )

        # Mettre à jour la config ghostbuster (last_run_at)
        await db.ghostbuster_config.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_run_at": datetime.datetime.utcnow(),
                    "last_result_count": len(result.get("eligible", [])),
                }
            },
            upsert=True,
        )

        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[API] Ghostbuster scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/ghostbuster/status")
async def ghostbuster_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retourne le statut du Ghostbuster pour l'utilisateur :
    - mode auto activé/désactivé
    - dernière exécution
    - prochaine exécution prévue
    - nombre de relances détectées lors du dernier run
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
        config = await db.ghostbuster_config.find_one({"user_id": user_id}, {"_id": 0}) or {}

        return {
            "status": "success",
            "data": {
                "auto_enabled": config.get("auto_enabled", False),
                "last_run_at": config.get("last_run_at"),
                "next_run_at": config.get("next_run_at"),
                "last_result_count": config.get("last_result_count", 0),
                "threshold_days": 15,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/ghostbuster/toggle")
async def ghostbuster_toggle(
    req: GhostbusterToggleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Active ou désactive le mode automatique 48h du Ghostbuster.
    Quand activé, le scheduler global le traitera automatiquement.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
        now = datetime.datetime.utcnow()

        await db.ghostbuster_config.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "auto_enabled": req.enabled,
                    "updated_at": now,
                    # Si on active, programmer le premier run dans 48h
                    "next_run_at": now + datetime.timedelta(hours=48) if req.enabled else None,
                }
            },
            upsert=True,
        )

        action = "activé" if req.enabled else "désactivé"
        logger.info(f"[Ghostbuster] Mode auto {action} pour user {user_id}")
        return {
            "status": "success",
            "message": f"Mode automatique Ghostbuster {action}.",
            "auto_enabled": req.enabled,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/ghostbuster/send")
async def ghostbuster_send(
    req: GhostbusterSendRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Marque une relance Ghostbuster comme envoyée (copie manuelle par l'utilisateur).
    Met à jour relance_sent_at et relance_sent_via dans MongoDB.
    """
    try:
        from agents.ghostbuster_agent import ghostbuster_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        ok = await ghostbuster_agent.mark_sent(
            user_id=user_id,
            app_id=req.app_id,
            via=req.via,
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Candidature introuvable ou aucune modification.")
        return {"status": "success", "message": "Relance marquée comme envoyée."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Network Ninja Workflow Endpoints (#3)
# ==========================================

@app.post("/api/workflows/network-ninja/run")
async def network_ninja_run(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Lance le workflow Network Ninja :
    - Récupère les 15 dernières candidatures APPLIED/FOLLOW_UP
    - Recherche les décideurs LinkedIn pour chaque entreprise unique (max 8)
    - Génère un message d'approche LinkedIn ≤ 180 chars par profil
    - Persiste et retourne les résultats
    """
    try:
        from agents.network_ninja_agent import network_ninja_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        logger.info(f"[API] Network Ninja lancé pour user {user_id}")
        result = await network_ninja_agent.run(user_id=user_id)

        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[API] Network Ninja run error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/network-ninja/results")
async def network_ninja_results(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retourne les résultats Network Ninja persistés pour l'utilisateur.
    Les résultats sont permanents jusqu'au prochain run.
    """
    try:
        from agents.network_ninja_agent import network_ninja_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        result = await network_ninja_agent.get_results(user_id=user_id)
        if not result:
            return {"status": "success", "data": None}

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Radar Endpoints (Market Insights) ---
class RadarRequest(BaseModel):
    company_name: str
    job_title: str

@app.post("/api/radar")
async def fetch_market_radar(req: RadarRequest):
    """Snipe company red flags and fetch salary estimates."""
    from agents.researcher import ResearcherAgent
    researcher = ResearcherAgent()
    await researcher.initialize()
    
    # Analyze reputation
    rep_query = f"{req.company_name} avis employes red flags culture entreprise"
    rep_task = {"action": "research", "query": rep_query}
    rep_result = await researcher.think(rep_task)
    
    # Analyze salary
    sal_query = f"salaire moyen {req.job_title} quebec montreal 2024"
    sal_task = {"action": "research", "query": sal_query}
    sal_result = await researcher.think(sal_task)
    
    return {
        "status": "success",
        "data": {
            "reputation": rep_result.get("content", "Aucune donnée claire sur la réputation."),
            "salary": sal_result.get("content", "Aucune donnée salariale chiffrée trouvée.")
        }
    }

# ─── STRIPE ENDPOINTS ───

class CheckoutRequest(BaseModel):
    tier: str

@app.post("/api/stripe/create-checkout-session")
async def stripe_checkout(req: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Crée une session de paiement Stripe."""
    from api.stripe_service import create_checkout_session
    url = create_checkout_session(
        user_id=current_user["id"],
        email=current_user["email"],
        tier=req.tier
    )
    if not url:
        raise HTTPException(status_code=500, detail="Impossible de créer la session Stripe")
    
    return {"status": "success", "url": url}

@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handler pour les webhooks Stripe."""
    from api.stripe_service import handle_webhook_payload
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    success, message = await handle_webhook_payload(payload, sig_header)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"status": "success"}


def _require_admin(current_user: dict):
    """Vérifie que l'utilisateur connecté est ADMIN."""
    if current_user.get("subscription_tier") != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs GoldArmy.")


@app.get("/api/admin/stats")
async def admin_stats(current_user: dict = Depends(get_current_user)):
    """Statistiques globales pour le tableau de bord admin (effectif, tiers, candidatures)."""
    _require_admin(current_user)
    db = get_db()
    total_users = await db.users.count_documents({})
    pipeline = [
        {"$group": {"_id": "$subscription_tier", "count": {"$sum": 1}}},
    ]
    tiers = {"pro": 0, "essential": 0, "free": 0}
    async for doc in db.users.aggregate(pipeline):
        t = (doc["_id"] or "FREE").upper()
        if t == "PRO":
            tiers["pro"] = doc["count"]
        elif t == "ESSENTIAL":
            tiers["essential"] = doc["count"]
        elif t == "FREE" or t == "ADMIN":
            tiers["free"] = tiers.get("free", 0) + doc["count"]
    total_applications = await db.applications.count_documents({})
    return {"status": "success", "data": {"total_users": total_users, "tiers": tiers, "total_applications": total_applications}}


@app.get("/api/admin/users")
async def admin_users(current_user: dict = Depends(get_current_user)):
    """Liste des utilisateurs pour le radar admin (id, email, full_name, subscription_tier)."""
    _require_admin(current_user)
    db = get_db()
    cursor = db.users.find({}, {"_id": 0, "id": 1, "email": 1, "full_name": 1, "subscription_tier": 1, "created_at": 1})
    users = []
    async for u in cursor:
        u["subscription_tier"] = u.get("subscription_tier") or "FREE"
        users.append(u)
    return {"status": "success", "data": users}


@app.get("/api/admin/user/{user_id}")
async def admin_user_detail(user_id: str, current_user: dict = Depends(get_current_user)):
    """Détail d'un utilisateur (profil + candidatures) pour l'inspection admin."""
    _require_admin(current_user)
    db = get_db()
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    apps = await db.applications.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1).limit(100).to_list(length=100)
    return {"status": "success", "data": {"profile": user, "applications": apps}}


@app.post("/api/admin/promote-user")
async def admin_promote_user(req: PromoteUserRequest, current_user: dict = Depends(get_current_user)):
    """Permet à un administrateur de promouvoir un utilisateur au rang Premium."""
    _require_admin(current_user)
    db = get_db()
    # Trouver l'utilisateur par email
    target = await db.users.find_one({"email": req.email})
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable avec cet email.")
    
    # Mettre à jour le tier
    await db.users.update_one(
        {"email": req.email},
        {"$set": {"subscription_tier": req.tier}}
    )
    
    logger.info(f"👑 Admin {current_user['email']} a promu {req.email} au tier {req.tier}")
    return {"status": "success", "message": f"Utilisateur {req.email} promu au tier {req.tier} avec succès."}

@app.get("/api/admin/system-info")
async def admin_system_info(current_user: dict = Depends(get_current_user)):
    """Récupère les informations techniques du serveur."""
    _require_admin(current_user)
    import platform
    import psutil
    import time
    
    # Calcul simple de l'uptime
    uptime = time.time() - psutil.boot_time()
    
    return {
        "status": "success",
        "data": {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "uptime_seconds": uptime,
            "server_time": datetime.utcnow().isoformat()
        }
    }

@app.post("/api/admin/broadcast")
async def admin_broadcast(req: BroadcastRequest, current_user: dict = Depends(get_current_user)):
    """Envoie une notification à toute la flotte."""
    _require_admin(current_user)
    from api.notifications import broadcast_notification
    
    count = await broadcast_notification(
        title=req.title,
        message=req.message,
        type=req.type,
        action_url=req.action_url
    )
    
    logger.info(f"📢 BROADCAST: {req.title} envoyé à {count} agents par {current_user['email']}")
    return {"status": "success", "count": count}

@app.get("/api/admin/analytics")
async def admin_get_analytics(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques de vues et de clics."""
    _require_admin(current_user)
    db = get_db()
    
    # 1. Top Pages
    pipeline_pages = [
        {"$match": {"event_name": "page_view"}},
        {"$group": {"_id": "$page_url", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_pages = await db.analytics.aggregate(pipeline_pages).to_list(length=10)
    
    # 2. Top Clicks
    pipeline_clicks = [
        {"$match": {"event_name": "click"}},
        {"$group": {"_id": "$metadata.target", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_clicks = await db.analytics.aggregate(pipeline_clicks).to_list(length=10)
    
    # 3. Total Views/Clicks
    total_views = await db.analytics.count_documents({"event_name": "page_view"})
    total_clicks = await db.analytics.count_documents({"event_name": "click"})
    
    return {
        "status": "success",
        "data": {
            "total_views": total_views,
            "total_clicks": total_clicks,
            "top_pages": top_pages,
            "top_clicks": top_clicks
        }
    }

@app.post("/api/admin/send-email")
async def admin_send_email(req: EmailAdminRequest, current_user: dict = Depends(get_current_user)):
    """Envoie un email à un utilisateur ou à tous."""
    _require_admin(current_user)
    from core.email_service import email_service
    
    if req.to_email:
        # Email unique
        ok = await email_service.send_email(req.to_email, req.subject, req.content)
        return {"status": "success" if ok else "error"}
    else:
        # Broadcast email
        db = get_db()
        users = await db.users.find({}, {"email": 1}).to_list(length=None)
        emails = [u["email"] for u in users if u.get("email")]
        count = await email_service.broadcast_email(emails, req.subject, req.content)
        return {"status": "success", "count": count}

@app.post("/api/analytics/track")
async def track_event(req: TrackEventRequest, request: Request):
    """Enregistre un événement analytique (public)."""
    db = get_db()
    event_data = req.dict()
    event_data["timestamp"] = datetime.datetime.utcnow()
    event_data["ip"] = request.client.host
    event_data["user_agent"] = request.headers.get("user-agent")
    
    await db.analytics.insert_one(event_data)
    return {"status": "success"}

@app.get("/api/portfolio/render/{user_id}")
async def render_portfolio(user_id: str):
    """Sert le contenu HTML du portfolio pour une iframe."""
    from core.database import get_db
    from fastapi.responses import HTMLResponse
    
    db = get_db()
    user = await db.users.find_one({"id": user_id})
    if not user or "last_portfolio" not in user:
        return HTMLResponse(content="<html><body><h1>Portfolio non trouvé.</h1></body></html>", status_code=404)
    
    portfolio = user["last_portfolio"]
    html_content = portfolio.get("html", "")
    css_content = portfolio.get("css", "")
    js_content = portfolio.get("js", "")
    
    # Injection sécurisée et isolée
    full_html = f"""
    <!DOCTYPE html>
    <html style="scroll-behavior: smooth;">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Portfolio - GoldArmy</title>
            <style>{css_content}</style>
        </head>
        <body>
            {html_content}
            <script>
                // Isolation Radicale & Sécurité
                (function() {{
                    const self = window;
                    Object.defineProperty(window, 'top', {{ get: () => self }});
                    Object.defineProperty(window, 'parent', {{ get: () => self }});
                    
                    // Intercepteur de navigation interne (Smooth Scroll)
                    document.addEventListener('click', (e) => {{
                        const link = e.target.closest('a');
                        if (link) {{
                            const href = link.getAttribute('href');
                            if (href && href.startsWith('#')) {{
                                e.preventDefault();
                                const target = document.querySelector(href);
                                if (target) {{
                                    target.scrollIntoView({{ behavior: 'smooth' }});
                                }}
                            }}
                        }}
                    }}, true);
                }})();
                {js_content}
            </script>
        </body>
    </html>
    """
    
    return HTMLResponse(content=full_html)


# --- Public Try-Before-You-Buy Endpoints ---

def _ats_rule_score(text: str) -> int:
    """
    Score ATS basé sur des règles (0-100) : sections reconnues, bullets, longueur, contact.
    Utilisé pour ancrer le score et le rendre cohérent avec la réalité ATS.
    """
    if not text or len(text.strip()) < 50:
        return 25
    t = text.lower().strip()
    score = 0
    # Sections typiques ATS (max 35 pts)
    sections = [
        "expérience", "experience", "formation", "education", "études",
        "compétences", "competences", "skills", "compétence",
        "résumé", "resume", "summary", "profil", "objectif"
    ]
    found = sum(1 for s in sections if s in t)
    score += min(35, found * 8)
    # Bullets / listes (max 25 pts) — indicateur de structure parsable
    bullet_count = t.count("\n•") + t.count("\n-") + t.count("\n*") + t.count("•")
    score += min(25, bullet_count * 3)
    # Longueur raisonnable première page (max 20 pts)
    if 200 <= len(text) <= 2500:
        score += 20
    elif 100 <= len(text) < 200 or 2500 < len(text) <= 4000:
        score += 12
    elif len(text) > 4000:
        score += 8
    # Contact présent (max 20 pts)
    if "@" in text or "email" in t:
        score += 10
    if any(c.isdigit() for c in text) and ("tél" in t or "phone" in t or "06" in text or "07" in text):
        score += 10
    return min(100, score)


@app.post("/api/public/mini-audit")
async def public_mini_audit(file: UploadFile = File(...)):
    """
    Scanne la 1ère page du CV (PyMuPDF), calcule un score ATS fiable (règles + LLM rapide)
    et renvoie score /100 + jusqu'à 7 défauts avec corrections. Traitement accéléré.
    """
    try:
        import fitz  # PyMuPDF
        import re

        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            raise HTTPException(status_code=400, detail="PDF vide.")
        first_page_text = doc[0].get_text()
        doc.close()

        text_snippet = first_page_text[:2500]
        rule_score = _ats_rule_score(text_snippet)

        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()

        prompt = f"""Tu es un expert ATS (Applicant Tracking System). Évalue la compatibilité ATS de ce CV (1ère page).
Texte extrait :
---
{text_snippet}
---

Réponds UNIQUEMENT en JSON valide avec 2 clés (pas de markdown) :
- "score": entier 0-100 (sévérité réaliste : 50-70 = moyen, >80 = très bon pour ATS).
- "flaws": tableau de 5 à 7 objets avec "flaw" (critique courte) et "correction" (action courte). Points bloquants ATS : structure, mots-clés, chiffres, bullet points.
"""
        result = await llm.chat(
            [{"role": "user", "content": prompt}],
            json_mode=True,
            model="gemini-2.0-flash",
            max_tokens=1024,
        )

        cleaned = re.sub(r"```json\s*", "", result, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        raw = json.loads(match.group(0)) if match else json.loads(cleaned)
        llm_score = max(0, min(100, int(raw.get("score", 50))))
        flaws = raw.get("flaws") or []

        # Score final : mélange règles (objectif) + LLM (qualité rédactionnelle) pour un score ATS fiable
        final_score = int(0.45 * rule_score + 0.55 * llm_score)
        final_score = max(0, min(100, final_score))

        return {
            "status": "success",
            "score": final_score,
            "flaws": flaws[:7] if isinstance(flaws, list) else [
                {"flaw": "Structure difficile à lire pour un ATS.", "correction": "Simplifiez le design et utilisez des sections claires."},
                {"flaw": "Manque de mots-clés.", "correction": "Ajoutez une section Compétences avec termes métier."},
            ],
        }
    except Exception as e:
        logger.error(f"[Public API] Erreur Mini-Audit: {e}")
        return {
            "status": "success",
            "score": 42,
            "flaws": [
                {"flaw": "Le format du fichier empêche l'analyse.", "correction": "Uploadez un PDF avec texte sélectionnable (Word, Canva)."},
                {"flaw": "Texte potentiellement en image.", "correction": "Assurez-vous que le texte du PDF peut être copié."},
            ],
        }

class PublicInterviewRequest(BaseModel):
    job_title: str
    user_response: Optional[str] = None
    context: Optional[str] = None

@app.post("/api/public/interview")
async def public_interview(req: PublicInterviewRequest):
    """
    Point d'entrée pour la simulation d'entretien vocal de la landing page.
    Si user_response est None -> l'IA donne la question initiale.
    Sinon -> l'IA donne un feedback hyper rapide.
    """
    try:
        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()
        
        if not req.user_response:
            # 1. Générer la question piège
            prompt = f"""Tu es un recruteur expert. Tu fais passer un entretien express (1 seule question) pour le poste de : {req.job_title}.
Pose UNE question piège, difficile ou très technique, que ce candidat rencontrerait dans la vraie vie.
Ne dis pas bonjour la réponse doit être juste la question elle-même pour qu'elle soit lue par une synthèse vocale (ton sec et professionnel)."""
        else:
            # 2. Evaluer la réponse
            prompt = f"""Tu es un recruteur expert. Tu as posé cette question pour un poste de {req.job_title} :
Question : {req.context}

Le candidat a répondu (transcription orale) :
{req.user_response}

Fais-lui un feedback cash en 2 phrases MAXIMUM ! (soit positif, soit indique pourquoi c'est mauvais).
Ne sois pas poli, sois un coach stricte. Cette réponse sera lue par synthèse vocale."""

        response_text = await llm.chat([{"role": "user", "content": prompt}], max_tokens=200)
        
        return {
            "status": "success",
            "text": response_text.replace("*", "").replace("\"", "").strip()  # Clean for TTS
        }
        
    except Exception as e:
        logger.error(f"[Public API] Erreur Interview: {e}")
        raise HTTPException(status_code=500, detail="Erreur génération.")


# ==========================================
# Admin — Error Monitoring Dashboard
# ==========================================

@app.get("/api/admin/errors")
async def admin_get_errors(
    limit: int = 50,
    level: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Liste les erreurs capturées (admin only).
    Requiert que l'utilisateur soit admin (tier=ADMIN).
    """
    if current_user.get("tier") not in ["ADMIN", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    errors = await monitor.get_recent(limit=limit, level=level)
    return {"status": "success", "count": len(errors), "data": errors}

@app.patch("/api/admin/errors/{error_id}/resolve")
async def admin_resolve_error(
    error_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Marque une erreur comme résolue."""
    if current_user.get("tier") not in ["ADMIN", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    ok = await monitor.resolve(error_id)
    return {"status": "success" if ok else "error"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ---------------------------------------------------------------------------
# NETWORK NINJA ROUTES
# ---------------------------------------------------------------------------
from agents.network_ninja_agent import network_ninja_agent

@app.post("/api/network/ninja/run")
async def run_network_ninja(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        result = await network_ninja_agent.run(user_id)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error running network ninja: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/network/ninja/results")
async def get_network_ninja_results(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        db = get_db()
        doc = await db.ninja_results.find_one({"user_id": user_id})
        if not doc:
            return {"status": "success", "data": {"companies": []}}
        
        # Remove mongo _id before returning
        doc.pop("_id", None)
        return {"status": "success", "data": doc}
    except Exception as e:
        logger.error(f"Error getting network ninja results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Pre-Interview Workflow Endpoints (#4)
# ==========================================

class PreInterviewItem(BaseModel):
    application_id: str
    simulation_date: str # ISO Format
    prep_type: str # 'interview', 'star', 'both'

class PreInterviewScheduleRequest(BaseModel):
    items: List[PreInterviewItem]

@app.get("/api/workflows/pre-interview/pending")
async def get_pre_interview_pending(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Récupère les candidatures en cours (INTERVIEW ou APPLIED) pour les planifier."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        # Find applications with status 'INTERVIEW', 'APPLIED', or 'FOLLOW_UP'
        cursor = db.applications.find(
            {"user_id": user_id, "status": {"$in": ["INTERVIEW", "APPLIED", "FOLLOW_UP"]}},
            {"_id": 0}
        ).sort("created_at", -1)
        
        apps = await cursor.to_list(length=100)
        return {"status": "success", "data": apps}
    except Exception as e:
        logger.error(f"Error fetching pending applications for pre-interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/pre-interview/schedule")
async def schedule_pre_interview(
    req: PreInterviewScheduleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Planifie une ou plusieurs simulations d'entretien avec des dates individuelles."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        
        import uuid
        from datetime import datetime
        
        app_ids = [item.application_id for item in req.items]
        
        # Récupérer les détails des candidatures pour enrichir les simulations
        apps_data = await db.applications.find(
            {"user_id": user_id, "id": {"$in": app_ids}},
            {"_id": 0}
        ).to_list(length=None)
        
        app_map = {a["id"]: a for a in apps_data}
            
        simulations = []
        for item in req.items:
            app = app_map.get(item.application_id)
            if not app: continue
            
            sim_date = datetime.fromisoformat(item.simulation_date.replace("Z", "+00:00"))
            sim_id = str(uuid.uuid4())
            
            simulations.append({
                "id": sim_id,
                "user_id": user_id,
                "application_id": item.application_id,
                "company_name": app.get("company_name", ""),
                "job_title": app.get("job_title", ""),
                "simulation_date": sim_date,
                "prep_type": item.prep_type,
                "status": "PENDING",
                "created_at": datetime.utcnow(),
                "prep_data": None
            })
            
        if simulations:
            await db.simulations.insert_many(simulations)
            
        return {"status": "success", "data": {"scheduled_count": len(simulations)}}
    except Exception as e:
        logger.error(f"Error scheduling pre-interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Rejection Pivot Workflow Endpoints (#9)
# ==========================================

@app.get("/api/workflows/rejection-pivot/rejected")
async def get_rejected_applications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Récupère les candidatures avec le statut REJECTED."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        cursor = db.applications.find(
            {"user_id": user_id, "status": "REJECTED"},
            {"_id": 0}
        ).sort("updated_at", -1)
        apps = await cursor.to_list(length=100)
        return {"status": "success", "data": apps}
    except Exception as e:
        logger.error(f"Error fetching rejected applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/rejection-pivot/generate")
async def generate_rejection_pivot(
    req: RejectionPivotRequest,
    current_user: dict = Depends(get_current_user)
):
    """Lance le workflow Rejection Pivot pour une candidature."""
    try:
        from agents.rejection_pivot_agent import rejection_pivot_agent
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        
        await rejection_pivot_agent.initialize()
        result = await rejection_pivot_agent.run_pivot(user_id, req.app_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running rejection pivot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class WorkflowStatusUpdate(BaseModel):
    workflow_id: int
    active: bool

@app.get("/api/workflows/status")
async def get_workflows_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retourne l'état d'activité persisté de tous les workflows pour l'utilisateur."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        active_workflows = user.get("active_workflows", []) if user else []
        
        # Build status map — keys must be STRINGS for JSON serialization compatibility
        status_map = {str(wf_id): True for wf_id in active_workflows}
        
        # Override with specific configs for workflows that have their own toggle
        dh_config = await db.daily_hunt_config.find_one({"user_id": user_id})
        if dh_config:
            status_map["5"] = dh_config.get("enabled", False)
            
        gb_config = await db.ghostbuster_config.find_one({"user_id": user_id})
        if gb_config:
            status_map["2"] = gb_config.get("auto_scan", False)
            
        return {"status": "success", "data": status_map}
    except Exception as e:
        logger.error(f"Error fetching workflows status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/status")
async def set_workflow_status(
    req: WorkflowStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Persiste l'état actif/inactif d'un workflow dans le document utilisateur."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        
        if req.active:
            await db.users.update_one({"id": user_id}, {"$addToSet": {"active_workflows": req.workflow_id}})
        else:
            await db.users.update_one({"id": user_id}, {"$pull": {"active_workflows": req.workflow_id}})
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Daily Hunt Workflow Endpoints (#5)
# ==========================================

class DailyHuntToggleRequest(BaseModel):
    enabled: bool
    query: Optional[str] = "Développeur"
    location: Optional[str] = "Montreal, QC"

@app.get("/api/workflows/daily-hunt/config")
async def get_daily_hunt_config(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        cfg = await db.daily_hunt_config.find_one({"user_id": user_id}, {"_id": 0})
        if not cfg:
            return {"status": "success", "data": {"enabled": False, "query": "Développeur", "location": "Montreal, QC"}}
        return {"status": "success", "data": cfg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/daily-hunt/toggle")
async def toggle_daily_hunt(
    req: DailyHuntToggleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        from datetime import datetime
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        await db.daily_hunt_config.update_one(
            {"user_id": user_id},
            {"$set": {
                "enabled": req.enabled,
                "query": req.query,
                "location": req.location,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        return {"status": "success", "data": {"enabled": req.enabled}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/social-sniper/generate")
async def generate_social_sniper(
    req: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        if not cv_text:
            raise HTTPException(status_code=400, detail="CV requis.")

        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "social_sniper",
            "cv_text": cv_text,
            "company": req.get("company"),
            "job": req.get("job")
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/post-interview/apps")
async def get_interview_apps(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        apps = await db.applications.find(
            {"user_id": user_id, "status": "INTERVIEW"},
            {"_id": 0}
        ).sort("updated_at", -1).to_list(length=20)
        return {"status": "success", "data": apps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/post-interview/generate")
async def generate_post_interview(
    req: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        from datetime import datetime
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        
        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "post_interview_analysis",
            "cv_text": cv_text,
            "company": req.get("company"),
            "job": req.get("job"),
            "debrief": req.get("debrief")
        })
        
        # Optionnel: Mettre à jour le statut dans le CRM
        if req.get("app_id") and result.get("status") == "success":
            await db.applications.update_one(
                {"id": req.get("app_id"), "user_id": user_id},
                {"$set": {"status": "FOLLOW_UP", "updated_at": datetime.utcnow()}}
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/gold-profile/audit")
async def gold_profile_audit(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "")
        
        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "gold_profile_audit",
            "cv_text": cv_text
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/gold-profile/plan")
async def gold_profile_plan(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        # Chercher un plan existant
        existing = await db.gold_profile_plans.find_one({"user_id": user_id})
        if existing:
            return {"status": "success", "data": {"plan": existing["plan"]}}
            
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "")
        
        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "gold_profile_plan",
            "cv_text": cv_text
        })
        
        if result["status"] == "success":
            await db.gold_profile_plans.update_one(
                {"user_id": user_id},
                {"$set": {"plan": result["data"]["plan"], "updated_at": datetime.datetime.utcnow()}},
                upsert=True
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/gold-profile/post")
async def gold_profile_post(
    req: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "")
        
        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "gold_profile_post",
            "cv_text": cv_text,
            "topic": req.get("topic")
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Sniper To Apply Endpoints
# ==========================================

class SniperApplySearchRequest(BaseModel):
    job_title: str
    location: str
    nb_results: Optional[int] = 10

class SniperApplyExecuteRequest(BaseModel):
    selected_offers: List[Dict[str, Any]]

@app.post("/api/workflows/sniper-apply/search")
async def sniper_apply_search(
    req: SniperApplySearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        
        from agents.job_searcher import JobSearchAgent
        searcher = JobSearchAgent()
        await searcher.initialize()
        
        task = {
            "query": req.job_title,
            "location": req.location,
            "nb_results": req.nb_results,
            "cv_text": cv_text
        }
        plan = await searcher.think(task)
        result = await searcher.act(plan)
        
        return {"status": "success", "data": result.get("matched_jobs", [])}
    except Exception as e:
        import logging
        logging.error(f"Sniper Apply Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/sniper-apply/execute")
async def sniper_apply_execute(
    req: SniperApplyExecuteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        import uuid
        import httpx
        from datetime import datetime
        from agents.cv_adapter import CVAdapterAgent
        
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        from api.subscription import check_subscription_limit, log_usage
        check = await check_subscription_limit(user_id, "sniper_apply")
        remaining = check["limit"] - check.get("current", 0)
        
        if len(req.selected_offers) > remaining and check["limit"] < 99999: # Admins can bypass
            raise HTTPException(status_code=403, detail=f"Limite journalière dépassée. Offres restantes aujourd'hui : {remaining}")
            
        adapter = CVAdapterAgent()
        await adapter.initialize()
        
        # Clé API Skyvern depuis l'environnement
        from config.settings import settings
        skyvern_api_key = settings.skyvern_api_key
        if not skyvern_api_key:
            # Fallback en mode développement uniquement, ou lever une exception
            raise HTTPException(status_code=500, detail="La clé d'API Skyvern n'est pas configurée dans l'environnement du serveur.")
            
        skyvern_api_url = "https://api.skyvern.com/v1/run/tasks"
        
        results = []
        
        for offer in req.selected_offers:
            title = offer.get("title", "")
            company = offer.get("company", "")
            desc = offer.get("description", "")
            url = offer.get("url", "")
            
            # 1. Adapter le CV
            adapt_result = await adapter.adapt(title, desc, cv_text)
            cv_json = adapt_result.get("cv_json", {})
            
            # 2. Lancer la tâche Skyvern
            skyvern_task_id = None
            if url and skyvern_api_key:
                try:
                    prompt = f"Apply to this job. My name is {cv_json.get('full_name', 'Candidat')}. My skills are {cv_json.get('skills', {})}. Please fill the form and attach my resume or paste my details."
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        resp = await client.post(
                            skyvern_api_url,
                            headers={"x-api-key": skyvern_api_key, "Content-Type": "application/json"},
                            json={
                                "url": url,
                                "prompt": prompt,
                                "title": f"Auto-Apply to {company} - {title}",
                                "proxy_location": "RESIDENTIAL",
                                "engine": "skyvern-2.0"
                            }
                        )
                        if resp.status_code in [200, 201]:
                            skyvern_task_id = resp.json().get("run_id") or resp.json().get("task_id")
                        else:
                            import logging
                            logging.warning(f"Skyvern API error: {resp.status_code} - {resp.text}")
                except Exception as ex:
                    import logging
                    logging.warning(f"Skyvern API call failed for {company}: {ex}")
            
            # 3. Sauvegarder dans CRM
            app_id = str(uuid.uuid4())
            new_app = {
                "id": app_id,
                "user_id": user_id,
                "job_title": title,
                "company_name": company,
                "url": url,
                "status": "APPLIED",
                "notes": "Appliqué via Sniper To Apply (Skyvern)\n" + (f"Skyvern Task: {skyvern_task_id}" if skyvern_task_id else ""),
                "cv_json": cv_json,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.applications.insert_one(new_app)
            
            results.append({
                "id": app_id,
                "company": company,
                "title": title,
                "skyvern_task_id": skyvern_task_id,
                "status": "success"
            })
            
        await log_usage(user_id, "sniper_apply", len(results))
        return {"status": "success", "data": results}
    except Exception as e:
        import logging
        logging.error(f"Sniper Apply Execute Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
