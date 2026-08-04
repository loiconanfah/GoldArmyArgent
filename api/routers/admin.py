"""Routes d'administration : stats, utilisateurs, broadcast, analytics, monitoring d'erreurs."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from loguru import logger

from api.auth import get_current_user
from core.database import get_db
from core.error_monitor import monitor

router = APIRouter()


class PromoteUserRequest(BaseModel):
    email: str
    tier: str = "PRO"


class BroadcastRequest(BaseModel):
    title: str
    message: str
    type: str = "info"
    action_url: Optional[str] = None


class EmailAdminRequest(BaseModel):
    to_email: Optional[str] = None  # If None, it's a broadcast
    subject: str
    content: str


class TrackEventRequest(BaseModel):
    event_name: str
    page_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def _require_admin(current_user: dict):
    """Vérifie que l'utilisateur connecté est ADMIN."""
    if current_user.get("subscription_tier") != "ADMIN":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs GoldArmy.")


@router.get("/api/admin/stats")
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


@router.get("/api/admin/users")
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


@router.get("/api/admin/user/{user_id}")
async def admin_user_detail(user_id: str, current_user: dict = Depends(get_current_user)):
    """Détail d'un utilisateur (profil + candidatures) pour l'inspection admin."""
    _require_admin(current_user)
    db = get_db()
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    apps = await db.applications.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1).limit(100).to_list(length=100)
    return {"status": "success", "data": {"profile": user, "applications": apps}}


@router.post("/api/admin/promote-user")
async def admin_promote_user(req: PromoteUserRequest, current_user: dict = Depends(get_current_user)):
    """Permet à un administrateur de promouvoir un utilisateur au rang Premium."""
    _require_admin(current_user)
    db = get_db()
    target = await db.users.find_one({"email": req.email})
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable avec cet email.")

    await db.users.update_one(
        {"email": req.email},
        {"$set": {"subscription_tier": req.tier}}
    )

    logger.info(f"👑 Admin {current_user['email']} a promu {req.email} au tier {req.tier}")
    return {"status": "success", "message": f"Utilisateur {req.email} promu au tier {req.tier} avec succès."}


@router.get("/api/admin/system-info")
async def admin_system_info(current_user: dict = Depends(get_current_user)):
    """Récupère les informations techniques du serveur."""
    _require_admin(current_user)
    import platform
    import psutil
    import time

    uptime = time.time() - psutil.boot_time()

    return {
        "status": "success",
        "data": {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "uptime_seconds": uptime,
            "server_time": datetime.now(timezone.utc).isoformat()
        }
    }


@router.post("/api/admin/broadcast")
async def admin_broadcast(req: BroadcastRequest, current_user: dict = Depends(get_current_user)):
    """Envoie une notification à toute la flotte."""
    _require_admin(current_user)
    from api.notifications import broadcast_notification

    count = await broadcast_notification(
        title=req.title,
        message=req.message,
        type=req.type,
        action_url=req.action_url
    )

    logger.info(f"📢 BROADCAST: {req.title} envoyé à {count} agents par {current_user['email']}")
    return {"status": "success", "count": count}


@router.get("/api/admin/analytics")
async def admin_get_analytics(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques de vues et de clics."""
    _require_admin(current_user)
    db = get_db()

    pipeline_pages = [
        {"$match": {"event_name": "page_view"}},
        {"$group": {"_id": "$page_url", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_pages = await db.analytics.aggregate(pipeline_pages).to_list(length=10)

    pipeline_clicks = [
        {"$match": {"event_name": "click"}},
        {"$group": {"_id": "$metadata.target", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_clicks = await db.analytics.aggregate(pipeline_clicks).to_list(length=10)

    total_views = await db.analytics.count_documents({"event_name": "page_view"})
    total_clicks = await db.analytics.count_documents({"event_name": "click"})

    return {
        "status": "success",
        "data": {
            "total_views": total_views,
            "total_clicks": total_clicks,
            "top_pages": top_pages,
            "top_clicks": top_clicks
        }
    }


@router.post("/api/admin/send-email")
async def admin_send_email(req: EmailAdminRequest, current_user: dict = Depends(get_current_user)):
    """Envoie un email à un utilisateur ou à tous."""
    _require_admin(current_user)
    from core.email_service import email_service

    if req.to_email:
        ok = await email_service.send_email(req.to_email, req.subject, req.content)
        return {"status": "success" if ok else "error"}
    else:
        db = get_db()
        users = await db.users.find({}, {"email": 1}).to_list(length=None)
        emails = [u["email"] for u in users if u.get("email")]
        count = await email_service.broadcast_email(emails, req.subject, req.content)
        return {"status": "success", "count": count}


@router.post("/api/analytics/track")
async def track_event(req: TrackEventRequest, request: Request):
    """Enregistre un événement analytique (public)."""
    db = get_db()
    event_data = req.dict()
    event_data["timestamp"] = datetime.now(timezone.utc)
    event_data["ip"] = request.client.host
    event_data["user_agent"] = request.headers.get("user-agent")

    await db.analytics.insert_one(event_data)
    return {"status": "success"}


@router.get("/api/admin/errors")
async def admin_get_errors(
    limit: int = 50,
    level: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Liste les erreurs capturées (admin only)."""
    if current_user.get("tier") not in ["ADMIN", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    errors = await monitor.get_recent(limit=limit, level=level)
    return {"status": "success", "count": len(errors), "data": errors}


@router.patch("/api/admin/errors/{error_id}/resolve")
async def admin_resolve_error(
    error_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Marque une erreur comme résolue."""
    if current_user.get("tier") not in ["ADMIN", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    ok = await monitor.resolve(error_id)
    return {"status": "success" if ok else "error"}
