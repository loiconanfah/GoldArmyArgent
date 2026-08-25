from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from core.database import get_db
from api.auth import get_current_user
import httpx
import asyncio

async def send_expo_push_notification(token: str, title: str, body: str, data: dict = None):
    message = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body,
        "badge": 1,
        "data": data or {},
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://exp.host/--/api/v2/push/send",
                json=message,
                headers={
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                    "Content-Type": "application/json",
                },
                timeout=5.0
            )
    except Exception as e:
        print(f"Erreur d'envoi Push Expo: {e}")

async def notify(user_id: str, title: str, message: str, type: str = "success", action_url: Optional[str] = None):
    """Crée une notification in-app pour un utilisateur (best-effort, ne casse jamais
    l'action en cours). À appeler à la fin de chaque workflow important : CV prêt,
    lettre générée, Sniper terminé, relance Ghostbuster, etc."""
    if not user_id:
        return
    try:
        db = get_db()
        await db.notifications.insert_one({
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "action_url": action_url,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        from loguru import logger
        logger.warning(f"[notify] échec création notification: {e}")


router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "info"  # success, warning, info, error
    action_url: Optional[str] = None

class NotificationModel(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    action_url: Optional[str]
    is_read: bool
    created_at: str

@router.get("", response_model=List[NotificationModel])
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
        
        cursor = db.notifications.find({"user_id": user_id}).sort("created_at", -1).limit(50)
        notifs = await cursor.to_list(length=50)
        
        results = []
        for n in notifs:
            results.append({
                "id": str(n["_id"]),
                "user_id": n["user_id"],
                "title": n["title"],
                "message": n["message"],
                "type": n.get("type", "info"),
                "action_url": n.get("action_url"),
                "is_read": n.get("is_read", False),
                "created_at": n["created_at"]
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des notifications: {e}")

@router.post("", response_model=NotificationModel)
async def create_notification(
    data: NotificationCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
        
        new_notif = {
            "user_id": user_id,
            "title": data.title,
            "message": data.message,
            "type": data.type,
            "action_url": data.action_url,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.notifications.insert_one(new_notif)
        
        # Envoi asynchrone de la Push Notification
        try:
            user = await db.users.find_one({"id": user_id})
            if user and "push_tokens" in user:
                for token in user["push_tokens"]:
                    asyncio.create_task(
                        send_expo_push_notification(
                            token=token,
                            title=data.title,
                            body=data.message,
                            data={"url": data.action_url}
                        )
                    )
        except Exception as e:
            print(f"Erreur lors du déclenchement Push: {e}")
        
        return {
            "id": str(result.inserted_id),
            "user_id": user_id,
            "title": data.title,
            "message": data.message,
            "type": data.type,
            "action_url": data.action_url,
            "is_read": False,
            "created_at": new_notif["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la notification: {e}")

@router.put("/read-all")
async def mark_all_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
        await db.notifications.update_many(
            {"user_id": user_id, "is_read": False},
            {"$set": {"is_read": True}}
        )
        return {"status": "success", "message": "Toutes les notifications ont été marquées comme lues."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {e}")

@router.put("/{notif_id}/read")
async def mark_read(
    notif_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
        await db.notifications.update_one(
            {"_id": ObjectId(notif_id), "user_id": user_id},
            {"$set": {"is_read": True}}
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {e}")
async def broadcast_notification(title: str, message: str, type: str = "info", action_url: Optional[str] = None):
    """Envoie une notification à tous les utilisateurs enregistrés."""
    from core.database import get_db
    db = get_db()
    
    # 1. Récupérer tous les IDs d'utilisateurs
    cursor = db.users.find({}, {"id": 1, "push_tokens": 1})
    users = await cursor.to_list(length=None)
    
    if not users:
        return 0
        
    created_at = datetime.now(timezone.utc).isoformat()
    
    # 2. Créer les notifications en DB (bulk insert)
    notifications = []
    for user in users:
        notifications.append({
            "user_id": user["id"],
            "title": title,
            "message": message,
            "type": type,
            "action_url": action_url,
            "is_read": False,
            "created_at": created_at
        })
    
    if notifications:
        await db.notifications.insert_many(notifications)
    
    # 3. Envoyer les Push Notifications en arrière-plan
    push_tasks = []
    for user in users:
        if "push_tokens" in user:
            for token in user["push_tokens"]:
                push_tasks.append(
                    send_expo_push_notification(
                        token=token,
                        title=title,
                        body=message,
                        data={"url": action_url}
                    )
                )
    
    if push_tasks:
        # On limite le nombre de tâches simultanées pour ne pas saturer l'event loop
        # ou on laisse asyncio gérer. Pour un broadcast massif, on pourrait utiliser des chunks.
        asyncio.gather(*push_tasks, return_exceptions=True)
        
    return len(users)
