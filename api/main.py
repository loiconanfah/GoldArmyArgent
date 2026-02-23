from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import io

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

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
    await orchestrator.initialize()

class ChatRequest(BaseModel):
    message: str
    cv_text: Optional[str] = None
    cv_filename: Optional[str] = None
    nb_results: Optional[int] = None

class CVAdaptRequest(BaseModel):
    job_title: str
    job_description: str
    cv_text: str

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
            "nb_results": request.nb_results
        }
        print(f"DEBUG API: request.message={request.message}, request.nb_results={request.nb_results}")
        print(f"DEBUG API task: {task}")
        
        response = await orchestrator.think(task)
        
        return {"status": "success", "data": response}
    except Exception as e:
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
def fetch_crm():
    return {"status": "success", "data": get_crm_data()}

@app.post("/api/crm")
def create_crm_entry(item: CRMItem):
    new_item = add_crm_item(item)
    return {"status": "success", "data": new_item}

class CRMUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

@app.put("/api/crm/{item_id}")
def update_crm_entry(item_id: str, updates: CRMUpdate):
    updated = update_crm_item(item_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "data": updated}

@app.delete("/api/crm/{item_id}")
def delete_crm_entry(item_id: str):
    delete_crm_item(item_id)
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
