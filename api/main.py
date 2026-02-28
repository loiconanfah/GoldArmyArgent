from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

from api.auth import get_current_user, router as auth_router
from api.interview import router as interview_router
from api.subscription import check_subscription_limit, log_usage
from api.stripe_service import create_checkout_session, handle_webhook_payload
from core.database import get_db

app.include_router(auth_router)
app.include_router(interview_router)

# Enable CORS for Vue.js frontend (Usually runs on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in dev mode; should be restricted in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = OrchestratorAgent()

@app.on_event("startup")
async def startup_event():
    from core.database import init_db
    await init_db()
    await orchestrator.initialize()
    
    # --- Démarrage Automatique du Frontend ---
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    frontend_port = 5173 # Port par défaut de Vite
    
    if not is_port_in_use(frontend_port):
        logger.info(f"🚀 Tentative de démarrage du frontend sur le port {frontend_port}...")
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
        
        if os.path.exists(frontend_path):
            try:
                # Commande simplifiée pour Windows/Unix avec shell=True
                cmd = "npm run dev"
                log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_startup.log")
                
                with open(log_file, "w") as f:
                    f.write(f"--- Démarrage du frontend le {time.ctime()} ---\n")
                    f.flush()
                    
                    # On lance en arrière-plan
                    subprocess.Popen(
                        cmd,
                        shell=True,
                        cwd=frontend_path,
                        stdout=f,
                        stderr=f,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                    )
                logger.success(f"✅ Commande de démarrage lancée. Log: {log_file}")
            except Exception as e:
                logger.error(f"❌ Erreur lors du lancement du frontend: {e}")
        else:
            logger.warning(f"⚠️ Dossier frontend introuvable à: {frontend_path}")
    else:
        logger.info(f"ℹ️ Le frontend est déjà actif sur le port {frontend_port}")

class ChatRequest(BaseModel):
    message: str
    cv_text: Optional[str] = None
    cv_filename: Optional[str] = None
    nb_results: Optional[int] = None
    location: Optional[str] = None
    session_id: Optional[str] = "default"

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


@app.post("/api/generate-cv-pdf")
async def generate_cv_pdf_endpoint(request: CvRewriteRequest):
    """
    Reçoit les données structurées du CV (JSON) générées par le Mentor IA
    et retourne un fichier .pdf ATS-optimisé en téléchargement.
    """
    try:
        from core.cv_pdf_generator import generate_cv_pdf
        
        cv_data_input = request.cv_json
        
        # Le frontend peut envoyer une string JSON ou un objet direct, on gère les deux
        if isinstance(cv_data_input, str):
            try:
                cv_data = json.loads(cv_data_input)
            except json.JSONDecodeError as e:
                # Si le JSON est corrompu par le LLM
                import re
                match = re.search(r'\{.*\}', cv_data_input, re.DOTALL)
                if match:
                    cv_data = json.loads(match.group(0))
                else:
                    raise e
        elif isinstance(cv_data_input, dict):
            cv_data = cv_data_input
        else:
            cv_data = {}
            
        pdf_bytes = generate_cv_pdf(cv_data)

        filename = (request.filename or "CV_ATS_Optimise").replace(" ", "_").strip()
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
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
async def upload_avatar_endpoint(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
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
        
        avatar_url = f"http://localhost:8000/static/uploads/avatars/{filename}"
        
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

        # Increment follow-up counter
        updated = await db.applications.find_one_and_update(
            {"id": app_id},
            {"$inc": {"follow_up_count": 1}},
            return_document=True
        )
        follow_up_count = updated.get("follow_up_count", 1) if updated else 1

        # Generate email with GoldArmy unified LLM client
        from llm.unified_client import LLMClient
        llm = LLMClient()

        
        prompt = f"""
        Tu es l'assistant de recrutement GoldArmy.
        Rédige un email de relance professionnel, chaleureux et concis (5-7 lignes max) en français.
        Candidature pour : {job_title} chez {company}.
        Notes sur le poste : {notes if notes else 'Aucune note particulière.'}
        C'est la relance numéro {follow_up_count}. Si >1, rends le ton plus direct.
        Format attendu : 
        Objet: [Sujet du mail]
        
        Corps de l'email...
        Cordialement,
        [Prénom de l'utilisateur]
        """
        
        messages = [{"role": "user", "content": prompt}]
        email_text = await llm.chat(messages)

        await log_usage(current_user["id"], "follow_up")

        return {
            "status": "success",
            "email": email_text,
            "followUpCount": follow_up_count
        }
    except Exception as e:
        import logging
        logging.error(f"Followup generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Dashboard Endpoints
# ==========================================

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
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m", "date": "$created_at"}
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


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Main endpoint for interacting with the Orchestrator.
    Handles general chat, search requests, and CV context.
    """
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
        
        task = {
            "query": request.message,
            "cv_text": request.cv_text,
            "cv_filename": request.cv_filename,
            "nb_results": request.nb_results,
            "location": request.location,
            "session_id": request.session_id or "default"
        }
        
        response = await orchestrator.think(task)
        
        # Log usage if it was a search
        if response.get("type") == "job_search_results":
             await log_usage(current_user["id"], "sniper_search")
        
        return {"status": "success", "data": response}
    except Exception as e:
        import logging
        logging.exception("Erreur /api/chat")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/adapt-cv")
async def adapt_cv_endpoint(request: CVAdaptRequest):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
