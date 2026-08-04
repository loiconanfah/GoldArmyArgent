"""Routes profil utilisateur : infos, usage, CV, avatar, tâches, support, export RGPD."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.auth import get_current_user
from api.tasks import create_task, run_background_task, get_task, get_recent_tasks
from core.database import get_db

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    cv_text: Optional[str] = None
    portfolio_url: Optional[str] = None
    avatar_url: Optional[str] = None
    last_portfolio: Optional[dict] = None


class PushTokenRequest(BaseModel):
    token: str


class SupportMessageRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str


@router.post("/api/users/push-token")
async def register_push_token(
    request: PushTokenRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
        await db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"push_tokens": request.token}}
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/support/message")
async def send_support_message(
    request: SupportMessageRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Enregistre un message de support dans la base de données."""
    try:
        message_data = request.dict()
        message_data["created_at"] = datetime.utcnow()

        await db.support_messages.insert_one(message_data)

        logger.info(f"📩 Nouveau message de support de {request.email}: {request.subject}")

        return {"status": "success", "message": "Message envoyé avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message de support: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Récupère les informations complètes du profil utilisateur."""
    db = get_db()
    try:
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return {"status": "success", "data": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/profile/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    """Retourne l'utilisation actuelle de chaque feature pour l'utilisateur."""
    from api.subscription import SUBSCRIPTION_LIMITS, check_subscription_limit
    user_id = current_user["id"]
    db = get_db()
    user = await db.users.find_one({"id": user_id})
    tier = user.get("subscription_tier", "FREE") if user else "FREE"
    limits_config = SUBSCRIPTION_LIMITS.get(tier, SUBSCRIPTION_LIMITS["FREE"])

    usage = {}
    for feature, config in limits_config.items():
        result = await check_subscription_limit(user_id, feature)
        usage[feature] = {
            "current": result.get("current", 0),
            "limit": config["limit"],
            "period": config["period"],
            "allowed": result.get("allowed", True)
        }

    return {"status": "success", "data": {"tier": tier, "usage": usage}}


@router.post("/api/profile")
async def update_profile(request: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Met à jour les informations du profil utilisateur."""
    db = get_db()
    try:
        fields = request.dict(exclude_unset=True)
        if not fields:
            return {"status": "success", "message": "Aucun champ à mettre à jour"}

        if "cv_text" in fields:
            old_user = await db.users.find_one({"id": current_user["id"]}, {"cv_text": 1})
            if old_user and old_user.get("cv_text") and old_user.get("cv_text") != fields["cv_text"]:
                history_entry = {
                    "cv_text": old_user["cv_text"],
                    "updated_at": datetime.utcnow().isoformat(),
                    "name": f"Version du {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
                }
                await db.users.update_one(
                    {"id": current_user["id"]},
                    {"$push": {"cv_history": {"$each": [history_entry], "$position": 0, "$slice": 10}}}
                )

        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": fields}
        )
        return {"status": "success", "message": "Profil mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _analyze_cv_background(user_id: str, content: bytes):
    """Extraction de texte en tâche de fond avec notification."""
    import fitz
    try:
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()

        extracted_text = text.strip()
        db = get_db()
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"cv_text": extracted_text}}
        )
        return {"text": extracted_text}
    except Exception as e:
        logger.error(f"Background CV analysis error: {e}")
        raise e


@router.post("/api/profile/upload-cv")
async def upload_cv_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    background: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Upload un CV PDF, extrait le texte et le sauvegarde dans le profil."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les PDF sont acceptés")

    try:
        content = await file.read()

        if background:
            task_id = await create_task(current_user["id"], "cv_analysis")
            background_tasks.add_task(
                run_background_task,
                task_id,
                current_user["id"],
                _analyze_cv_background,
                current_user["id"],
                content
            )
            return {"status": "pending", "task_id": task_id, "message": "Analyse du CV lancée en arrière-plan."}

        import fitz
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()

        extracted_text = text.strip()

        db = get_db()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"cv_text": extracted_text}}
        )

        return {"status": "success", "text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tasks")
async def list_tasks(current_user: dict = Depends(get_current_user)):
    """Liste les tâches récentes de l'utilisateur."""
    tasks = await get_recent_tasks(current_user["id"])
    return {"status": "success", "data": tasks}


@router.get("/api/tasks/{task_id}")
async def fetch_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Récupère l'état et le résultat d'une tâche spécifique."""
    task = await get_task(task_id, current_user["id"])
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    return {"status": "success", "data": task}


@router.post("/api/profile/upload-avatar")
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

        base_url = os.getenv("BASE_URL", "").rstrip("/")
        if not base_url:
            base_url = str(request.base_url).rstrip("/")
        avatar_url = f"{base_url}/static/uploads/avatars/{filename}"

        db = get_db()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"avatar_url": avatar_url}}
        )

        return {"status": "success", "avatar_url": avatar_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/profile/export")
async def export_profile_data(current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Exportation conforme RGPD des données personnelles et historiques au format JSON."""
    user_id = current_user.get("id")
    user_data = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0}) or {}
    candidatures = await db.applications.find({"user_id": user_id}, {"_id": 0}).to_list(length=1000)
    contacts = await db.contacts.find({"user_id": user_id}, {"_id": 0}).to_list(length=1000)

    export_payload = {
        "user_profile": user_data,
        "candidatures": candidatures,
        "contacts": contacts,
        "exported_at": datetime.now(timezone.utc).isoformat()
    }
    return {"status": "success", "data": export_payload}
