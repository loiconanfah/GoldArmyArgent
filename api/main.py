import os
# Fix for Render Playwright: Force browser installation in the persistent project directory
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "pw-browsers")

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import sys

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

# --- MONITORING (MongoDB natif, 100% gratuit) ---
from core.error_monitor import monitor
logger.info("Monitoring actif: MongoDB error_logs collection")

from api.auth import get_current_user, router as auth_router
from api.interview import router as interview_router
from api.notifications import router as notifications_router
from api.referral import router as referral_router
from api.subscription import check_subscription_limit, log_usage
from core.database import get_db
from api.tasks import create_task, run_background_task

# --- Routers par domaine (découpage de l'ancien monolithe) ---
from api.routers.cv import router as cv_router
from api.routers.crm import router as crm_router
from api.routers.network import router as network_router
from api.routers.profile import router as profile_router
from api.routers.workflows import router as workflows_router
from api.routers.dashboard import router as dashboard_router
from api.routers.admin import router as admin_router
from api.routers.stripe import router as stripe_router
from api.routers.organization import router as organization_router
from api.routers.shop import router as shop_router
from api.routers.mentors import router as mentors_router

# Routers existants
app.include_router(auth_router)
app.include_router(interview_router)
app.include_router(notifications_router)
app.include_router(referral_router)

# Routers extraits de main.py
app.include_router(cv_router)
app.include_router(crm_router)
app.include_router(network_router)
app.include_router(profile_router)
app.include_router(workflows_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(stripe_router)
app.include_router(organization_router)
app.include_router(shop_router)
app.include_router(mentors_router)

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
    # Content Security Policy (Basic) — allow frames only from same origin
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    # Fix for Google Auth COOP issues in console
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
    return response


# --- GLOBAL EXCEPTION HANDLER (capture les vraies erreurs 500 uniquement) ---
# NOTE: On ne surcharge PAS StarletteHTTPException pour ne pas interférer
# avec la gestion CORS du middleware (les OPTIONS 400 seraient cassés).
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
            import subprocess

            def _check_pw():
                from playwright.sync_api import sync_playwright
                try:
                    with sync_playwright() as pw:
                        browser = pw.chromium.launch(args=["--no-sandbox"])
                        browser.close()
                    return True
                except Exception as pw_err:
                    logger.warning(f"Playwright browser missing/error: {pw_err}")
                    return False

            pw_ok = await asyncio.to_thread(_check_pw)
            if not pw_ok:
                logger.info("Installing Playwright Chromium automatically...")
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

        # --- Schedulers (48h auto modes) ---
        logger.info("👻 Étape 4: Démarrage des schedulers (Ghostbuster, Pre-Interview, Daily Hunt)...")
        try:
            from core.ghostbuster_scheduler import start_ghostbuster_scheduler
            start_ghostbuster_scheduler()

            from core.pre_interview_scheduler import pre_interview_scheduler
            await pre_interview_scheduler.start()

            from core.daily_hunt_scheduler import daily_hunt_scheduler
            await daily_hunt_scheduler.start()
        except Exception as e:
            logger.warning(f"Non-critical scheduler start error: {e}")

        logger.success("✨ Initialisation du backend terminée avec succès!")
    except Exception as e:
        logger.error(f"💥 Erreur critique lors de l'initialisation: {e}")
        # On ne raise pas pour laisser Uvicorn binder le port et permettre le debug via API.

    logger.info("ℹ️ Skip frontend auto-start (Production Mode)")


class ChatRequest(BaseModel):
    message: str
    cv_text: Optional[str] = None
    cv_filename: Optional[str] = None
    nb_results: Optional[int] = None
    location: Optional[str] = None
    session_id: Optional[str] = "default"
    image_data: Optional[str] = None  # Base64 image for vision tasks
    background: Optional[bool] = False
    task_type: Optional[str] = "sniper"  # 'sniper', 'mentor', 'cv_analysis'
    job_text: Optional[str] = None
    job_url: Optional[str] = None
    # Raffinage conversationnel du CV : CV déjà généré + son audit, à modifier
    previous_cv: Optional[dict] = None
    previous_audit: Optional[dict] = None
    # Filtres de source Sniper (ex: ["linkedin"], ["direct"], ["indeed","direct"])
    sources: Optional[list] = None


@app.get("/")
def read_root():
    return {"status": "ok", "message": "GoldArmy Agent V2 API is running"}


# Servir les fichiers statiques (Uploads)
os.makedirs("static/uploads/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


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
            "image_data": request.image_data,
            "job_text": request.job_text,
            "job_url": request.job_url,
            "previous_cv": request.previous_cv,
            "previous_audit": request.previous_audit,
            "sources": request.sources or [],
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
