from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import io
import json

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

from api.auth import router as auth_router, get_current_user
from api.interview import router as interview_router

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
    init_db()
    await orchestrator.initialize()

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
        cv_data = json.loads(request.cv_json)
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
async def find_decision_makers_api(req: HeadhunterRequest):
    """Trouve les décideurs clés via l'Agent Headhunter."""
    try:
        from agents.headhunter import headhunter_agent
        await headhunter_agent.initialize()
        
        profiles = await headhunter_agent.find_decision_makers({
            "company_name": req.company_name,
            "target_roles": req.target_roles
        })
        return {"status": "success", "data": profiles}
    except Exception as e:
        import logging
        logging.error(f"Erreur API Headhunter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network/draft-email")
async def draft_network_email(request: EmailDraftRequest):
    """Rédige un courriel d'approche via Gemini."""
    try:
        if not request.cv_text or len(request.cv_text) < 50:
            raise HTTPException(status_code=400, detail="Veuillez d'abord télécharger un CV dans l'onglet Opportunités.")
            
        from agents.network_agent import NetworkAgent
        agent = NetworkAgent()
        
        email_data = await agent.draft_email(request.dict())
        return {"status": "success", "data": email_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/network/contacts")
def get_network_contacts(current_user: dict = Depends(get_current_user)):
    """Récupère tout le carnet d'adresses réseau."""
    import json as _json
    try:
        from core.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE user_id = ? OR user_id = 'system_user' 
            ORDER BY last_updated DESC
        """, (current_user["id"],))
        rows = cursor.fetchall()
        conn.close()
        contacts = []
        for row in rows:
            contact = dict(row)
            # Parse le champ emails stocké en JSON string vers une liste Python
            if contact.get("emails"):
                try:
                    contact["emails"] = _json.loads(contact["emails"])
                except Exception:
                    contact["emails"] = contact["emails"].split(",")
            else:
                contact["emails"] = []
            contacts.append(contact)
        return {"status": "success", "data": contacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# CRM Endpoints (Kanban)
# ==========================================

@app.post("/api/crm/applications")
def add_crm_application(request: CRMApplicationRequest, current_user: dict = Depends(get_current_user)):
    """Ajoute une candidature au CRM."""
    try:
        from core.database import get_db_connection
        import uuid
        from datetime import datetime
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        app_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO applications (id, user_id, job_title, company_name, url, reference, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            app_id, current_user["id"], request.job_title, request.company_name, request.url, 
            request.reference, request.status, request.notes, datetime.now().isoformat()
        ))
        
        conn.commit()
        return {"status": "success", "data": {"id": app_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@app.get("/api/crm/applications")
def get_crm_applications(current_user: dict = Depends(get_current_user)):
    """Récupère toutes les candidatures pour le Kanban."""
    try:
        from core.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
        rows = cursor.fetchall()
        
        apps = [dict(r) for r in rows]
        return {"status": "success", "data": apps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@app.put("/api/crm/applications/{app_id}/status")
def update_crm_status(app_id: str, request: CRMStatusUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Met à jour le statut (Drag and Drop) et horodate."""
    try:
        from core.database import get_db_connection
        from datetime import datetime
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Si on passe en APPLIED, on note la date d'application par exemple
        applied_at_clause = ""
        params = [request.status]
        
        if request.status == "APPLIED":
            applied_at_clause = ", applied_at = ?"
            params.append(datetime.now().isoformat())
            
        params.append(app_id)
        
        query = f"UPDATE applications SET status = ? {applied_at_clause} WHERE id = ? AND user_id = ?"
        params.append(current_user["id"])
        cursor.execute(query, tuple(params))
        
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# ==========================================
# Dashboard Endpoints
# ==========================================

@app.get("/api/dashboard/stats")
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques réelles pour le Dashboard depuis SQLite."""
    try:
        from core.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Candidatures envoyées (tout sauf TO_APPLY)
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status != 'TO_APPLY' AND user_id = ?", (current_user["id"],))
        applied_count = cursor.fetchone()[0] or 0
        
        # 2. Entretiens (status = INTERVIEW)
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'INTERVIEW' AND user_id = ?", (current_user["id"],))
        interview_count = cursor.fetchone()[0] or 0
        
        # 3. Réseau (Contacts totaux — user direct + contacts auto-extraits par les agents)
        cursor.execute(
            "SELECT COUNT(*) FROM contacts WHERE user_id = ? OR user_id = 'system_user'",
            (current_user["id"],)
        )
        network_count = cursor.fetchone()[0] or 0
        
        # 4. CV Analysés (Correspond au nombre réel de candidatures traitées par l'agent)
        cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ?", (current_user["id"],))
        total_apps = cursor.fetchone()[0] or 0
        cv_analyzed = total_apps
        
        # 5. Croissance Mensuelle (Pour le graphique)
        cursor.execute('''
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count 
            FROM applications 
            WHERE user_id = ?
            GROUP BY month 
            ORDER BY month ASC
        ''', (current_user["id"],))
        monthly_raw = cursor.fetchall()
        
        import datetime
        from dateutil.relativedelta import relativedelta
        
        now = datetime.datetime.now()
        chart_data = []
        months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        
        monthly_dict = {row['month']: row['count'] for row in monthly_raw if row['month']}
        
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
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# CRM Mock Data endpoint
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main endpoint for interacting with the Orchestrator.
    Handles general chat, search requests, and CV context.
    """
    try:
        task = {
            "query": request.message,
            "cv_text": request.cv_text,
            "cv_filename": request.cv_filename,
            "nb_results": request.nb_results,
            "location": request.location,
            "session_id": request.session_id or "default"
        }
        
        response = await orchestrator.think(task)
        
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
            
        from agents.cv_adapter import CVAdapterAgent
        adapter = CVAdapterAgent()
        
        result = await adapter.adapt(
            job_title=request.job_title,
            job_desc=request.job_description,
            cv_text=request.cv_text
        )
        
        return {"status": "success", "data": result}
    except Exception as e:
        from loguru import logger
        logger.error(f"Error in adapt_cv_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- CRM Endpoints (Sniper Pillar) ---
from api.crm_db import get_crm_data, add_crm_item, update_crm_item, delete_crm_item, CRMItem

@app.get("/api/crm")
def fetch_crm(current_user: dict = Depends(get_current_user)):
    return {"status": "success", "data": get_crm_data(current_user["id"])}

@app.post("/api/crm")
def create_crm_entry(item: CRMItem, current_user: dict = Depends(get_current_user)):
    new_item = add_crm_item(current_user["id"], item)
    return {"status": "success", "data": new_item}

class CRMUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

@app.put("/api/crm/{item_id}")
def update_crm_entry(item_id: str, updates: CRMUpdate, current_user: dict = Depends(get_current_user)):
    updated = update_crm_item(current_user["id"], item_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "data": updated}

@app.delete("/api/crm/{item_id}")
def delete_crm_entry(item_id: str, current_user: dict = Depends(get_current_user)):
    delete_crm_item(current_user["id"], item_id)
    return {"status": "success", "message": "Deleted"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
