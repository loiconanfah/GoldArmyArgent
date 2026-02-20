from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio

from agents.orchestrator import OrchestratorAgent

app = FastAPI(title="GoldArmy Agent V2 API", version="2.0.0")

# Enable CORS for Vue.js frontend (usually runs on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in dev mode; should be restricted in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = OrchestratorAgent()

class ChatRequest(BaseModel):
    message: str
    cv_text: Optional[str] = None
    cv_filename: Optional[str] = None
    nb_results: int = 15

@app.get("/")
def read_root():
    return {"status": "ok", "message": "GoldArmy Agent V2 API is running"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main endpoint for interacting with the Orchestrator.
    Handles general chat, search requests, and CV context.
    """
    try:
        # We pass the payload to the orchestrator acting as the main entry point
        # For V2, the orchestrator needs to process the request and return JSON
        # In this initial migration step, we wrap the existing logic
        
        task = {
            "query": request.message,
            "cv_text": request.cv_text,
            "cv_filename": request.cv_filename,
            "nb_results": request.nb_results
        }
        
        # This will need to be adapted to strictly return JSON instead of Markdown
        response = await orchestrator.think(task)
        
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
