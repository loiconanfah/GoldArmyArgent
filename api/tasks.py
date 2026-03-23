import uuid
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel
from loguru import logger
from core.database import get_db
from api.notifications import send_expo_push_notification

class TaskEntry(BaseModel):
    id: str
    user_id: str
    type: str  # 'sniper', 'cv_analysis'
    status: str  # 'pending', 'completed', 'failed'
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

async def create_task(user_id: str, task_type: str) -> str:
    task_id = str(uuid.uuid4())
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    task_data = {
        "id": task_id,
        "user_id": user_id,
        "type": task_type,
        "status": "pending",
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now
    }
    
    await db.tasks.insert_one(task_data)
    return task_id

async def update_task(task_id: str, status: str, result: Any = None, error: str = None):
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    update_data = {
        "status": status,
        "updated_at": now
    }
    if result is not None:
        update_data["result"] = result
    if error is not None:
        update_data["error"] = error
        
    await db.tasks.update_one({"id": task_id}, {"$set": update_data})
    logger.info(f"Task {task_id} updated to {status}")

async def run_background_task(task_id: str, user_id: str, func: Callable, *args, **kwargs):
    """
    Wrapper to run a function in background, update DB and send push notification.
    """
    try:
        logger.info(f"Starting background task {task_id} for user {user_id}")
        # Run the actual work
        result = await func(*args, **kwargs)
        
        # Update DB
        await update_task(task_id, "completed", result=result)
        
        # Send Push Notification
        db = get_db()
        user = await db.users.find_one({"id": user_id})
        if user and user.get("push_tokens"):
            task = await db.tasks.find_one({"id": task_id})
            title = "Scan Sniper Terminé" if task["type"] == "sniper" else "Analyse CV Terminée"
            body = "Tes résultats sont prêts ! Clique pour les voir."
            
            for token in user["push_tokens"]:
                # Fire and forget notification
                asyncio.create_task(
                    send_expo_push_notification(
                        token=token,
                        title=title,
                        body=body,
                        data={"task_id": task_id, "type": task["type"]}
                    )
                )
                
    except Exception as e:
        logger.exception(f"Error in background task {task_id}")
        await update_task(task_id, "failed", error=str(e))
        
        # Optionally notify user of failure
        db = get_db()
        user = await db.users.find_one({"id": user_id})
        if user and user.get("push_tokens"):
            for token in user["push_tokens"]:
                asyncio.create_task(
                    send_expo_push_notification(
                        token=token,
                        title="Oups, une erreur est survenue",
                        body="Le scan a échoué. Relance-le quand tu veux.",
                        data={"task_id": task_id, "error": True}
                    )
                )

async def get_task(task_id: str, user_id: str) -> Optional[Dict]:
    db = get_db()
    task = await db.tasks.find_one({"id": task_id, "user_id": user_id}, {"_id": 0})
    return task

async def get_recent_tasks(user_id: str, limit: int = 10) -> list:
    db = get_db()
    cursor = db.tasks.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
