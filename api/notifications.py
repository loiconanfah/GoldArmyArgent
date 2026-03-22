from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from core.database import get_db
from api.auth import get_current_user

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
