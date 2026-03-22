from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
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
            "created_at": datetime.utcnow().isoformat()
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
