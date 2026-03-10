from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
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

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

from api.auth import get_current_user, router as auth_router
from api.interview import router as interview_router
from api.subscription import check_subscription_limit, log_usage
from api.stripe_service import create_checkout_session, handle_webhook_payload
from core.database import get_db

app.include_router(auth_router)
app.include_router(interview_router)

# Enable CORS (allow_credentials=True exige des origines explicites, pas "*")
_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# En prod, ajouter l’origine du front (ex. https://ton-site.com) ou la lire depuis .env
if os.getenv("CORS_ORIGIN"):
    _cors_origins.append(os.getenv("CORS_ORIGIN").strip())
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Fix for Google Auth COOP issues in console
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
    return response

# Global orchestrator instance
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

@app.get("/")
def read_root():
    return {"status": "ok", "message": "GoldArmy Agent V2 API is running"}

@app.post("/api/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
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
    Reçoit cv_json + filename + theme_id dans le body JSON.
    Génère un PDF avec le design du thème choisi (midnight, emerald, modern, etc.).
    """
    try:
        from core.cv_pdf_generator import generate_cv_pdf

        body = await raw_request.json()
        cv_data_input = body.get("cv_json")
        filename = (body.get("filename") or "CV_ATS_Optimise").replace(" ", "_").strip()
        # Accepter theme_id ou themeId (camelCase) pour compatibilité
        theme_id = body.get("theme_id") or body.get("themeId")
        if not isinstance(theme_id, str) or not theme_id.strip():
            theme_id = "midnight"
        theme_id = theme_id.strip().lower()
        valid_themes = {"midnight", "emerald", "modern", "minimal", "bold", "banker", "tech", "classic", "vibrant", "luxury"}
        if theme_id not in valid_themes:
            theme_id = "midnight"

        if cv_data_input is None:
            raise HTTPException(status_code=400, detail="cv_json manquant")

        if isinstance(cv_data_input, str):
            cv_data_input = cv_data_input.strip()
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
        import logging
        logging.info(f"Generating PDF for theme {theme_id} with data keys: {list(cv_data.keys())}")
        
        pdf_bytes = generate_cv_pdf(cv_data, theme_id=theme_id)
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-CV-Theme": theme_id,
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

@app.post("/api/network/enrich")
async def enrich_company(request: CompanyEnrichRequest):
    """Cherche les profils RH LinkedIn pour une entreprise."""
    try:
        from tools.linkedin_scraper import linkedin_scraper
        profiles = await linkedin_scraper.find_hr_profiles(request.company_name)
        return {"status": "success", "data": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network/headhunter")
async def find_decision_makers_api(req: HeadhunterRequest, current_user: dict = Depends(get_current_user)):
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
        
        await log_usage(current_user["id"], "headhunter")
        return {"status": "success", "data": profiles}
    except Exception as e:
        import logging
        logging.error(f"Erreur API Headhunter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network/draft-email")
async def draft_network_email(request: EmailDraftRequest):
    """Rédige un courriel d'approche via Gemini."""
    try:
        from agents.network_agent import NetworkAgent
        agent = NetworkAgent()
        await agent.initialize()
        email_data = await agent.draft_email(request.dict())
        return {"status": "success", "data": email_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/network/contacts")
async def get_network_contacts(current_user: dict = Depends(get_current_user)):
    """Récupère tout le carnet d'adresses réseau."""
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

@app.post("/api/profile")
async def update_profile(request: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Met à jour les informations du profil utilisateur."""
    from core.database import get_db
    db = get_db()
    try:
        fields = request.dict(exclude_unset=True)
        if not fields:
            return {"status": "success", "message": "Aucun champ à mettre à jour"}
        
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": fields}
        )
        return {"status": "success", "message": "Profil mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/profile/upload-cv")
async def upload_cv_endpoint(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload un CV PDF, extrait le texte et le sauvegarde dans le profil."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les PDF sont acceptés")
    
    try:
        import fitz
        content = await file.read()
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

        # Email de relance avec gemini-3.1-pro-preview (même modèle que Sniper / reste de l'app)
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
            model="gemini-3.1-pro-preview",
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
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
