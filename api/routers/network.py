"""Routes réseau : enrichissement entreprise, headhunter, emails d'approche, Gold Profile, contacts, Network Ninja."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from loguru import logger

from api.auth import get_current_user
from api.subscription import check_subscription_limit, log_usage
from core.database import get_db

router = APIRouter()


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


class GoldProfileAuditRequest(BaseModel):
    linkedin_profile: Optional[str] = None
    start_day: Optional[int] = 1
    days_count: Optional[int] = 15


class GoldProfileTopicRequest(BaseModel):
    topic: str
    format: Optional[str] = "Text"
    linkedin_profile: Optional[str] = None
    day: Optional[int] = None


@router.post("/api/network/enrich")
async def enrich_company(request: CompanyEnrichRequest, current_user: dict = Depends(get_current_user)):
    """Cherche les profils RH LinkedIn pour une entreprise."""
    check = await check_subscription_limit(current_user["id"], "network_access")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="L'enrichissement des profils et l'accès direct au réseau sont réservés aux abonnés ESSENTIAL et PRO.")
    try:
        from tools.linkedin_scraper import linkedin_scraper
        profiles = await linkedin_scraper.find_hr_profiles(request.company_name)
        return {"status": "success", "data": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/network/headhunter")
async def find_decision_makers_api(req: HeadhunterRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Trouve les décideurs clés via l'Agent Headhunter."""
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

        if profiles:
            from agents.network_ninja_agent import network_ninja_agent
            background_tasks.add_task(network_ninja_agent.add_manual_search, current_user["id"], req.company_name, profiles)

        await log_usage(current_user["id"], "headhunter")
        return {"status": "success", "data": profiles}
    except Exception as e:
        logger.error(f"Erreur API Headhunter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/network/draft-email")
async def draft_network_email(request: EmailDraftRequest, current_user: dict = Depends(get_current_user)):
    """Rédige un courriel d'approche via Gemini."""
    check = await check_subscription_limit(current_user["id"], "network_access")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="La rédaction de courriels d'approche réseau est réservée aux forfaits ESSENTIAL et PRO.")
    try:
        from agents.network_agent import NetworkAgent
        agent = NetworkAgent()
        await agent.initialize()
        email_data = await agent.draft_email(request.dict())
        return {"status": "success", "data": email_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/network/gold-profile/results")
async def get_gold_profile_results(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=44, detail="Utilisateur non trouvé.")
    return {
        "status": "success",
        "data": {
            "audit": user.get("gold_profile_audit"),
            "plan": user.get("gold_profile_plan"),
            "posts": user.get("gold_profile_posts", {}),
            "updated_at": user.get("gold_profile_updated_at")
        }
    }


@router.post("/api/network/gold-profile/audit")
async def gold_profile_audit(req: Optional[GoldProfileAuditRequest] = None, current_user: dict = Depends(get_current_user)):
    check = await check_subscription_limit(current_user["id"], "portfolio")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="L'audit de branding LinkedIn et le Portfolio IA sont réservés aux abonnés ESSENTIAL et PRO.")
    from agents.mentor import MentorAgent

    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    cv_text = user.get("cv_text", "") if user else ""
    linkedin_text = (req.linkedin_profile if req and req.linkedin_profile else "") or (user.get("linkedin_profile", "") if user else "")

    if not cv_text and not linkedin_text:
        raise HTTPException(status_code=400, detail="Veuillez d'abord uploader un CV ou coller votre profil LinkedIn pour utiliser Gold Profile.")

    if req and req.linkedin_profile and user:
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"linkedin_profile": req.linkedin_profile}})

    mentor = MentorAgent()
    await mentor.initialize()
    result = await mentor.think({"action": "gold_profile_audit", "cv_text": cv_text, "linkedin_text": linkedin_text})

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("content", "Erreur lors de l'audit."))

    audit_data = result.get("data")
    now_iso = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"gold_profile_audit": audit_data, "gold_profile_updated_at": now_iso}}
    )

    # Débit Gold une seule fois pour le Portfolio / Gold Profile (sur l'audit, pas le plan).
    await log_usage(current_user["id"], "portfolio")

    return {"status": "success", "data": audit_data}


@router.post("/api/network/gold-profile/plan")
async def gold_profile_plan(req: Optional[GoldProfileAuditRequest] = None, current_user: dict = Depends(get_current_user)):
    check = await check_subscription_limit(current_user["id"], "portfolio")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="La planification de contenu réseau et le Portfolio IA sont inaccessibles en compte gratuit.")
    from agents.mentor import MentorAgent

    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    cv_text = user.get("cv_text", "") if user else ""
    linkedin_text = (req.linkedin_profile if req and req.linkedin_profile else "") or (user.get("linkedin_profile", "") if user else "")

    if not cv_text and not linkedin_text:
        raise HTTPException(status_code=400, detail="Veuillez d'abord uploader un CV ou coller votre profil LinkedIn pour générer le plan.")

    start_day = req.start_day if req and req.start_day else 1
    days_count = req.days_count if req and req.days_count else 15

    mentor = MentorAgent()
    await mentor.initialize()
    result = await mentor.think({
        "action": "gold_profile_plan",
        "cv_text": cv_text,
        "linkedin_text": linkedin_text,
        "start_day": start_day,
        "days_count": days_count
    })

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("content", "Erreur lors de la planification."))

    new_plan_slice = result.get("data", {}).get("plan") or result.get("data") or []
    now_iso = datetime.now(timezone.utc).isoformat()

    if start_day > 1 and user and user.get("gold_profile_plan"):
        existing_plan = user.get("gold_profile_plan")
        if isinstance(existing_plan, list):
            combined_plan = existing_plan + new_plan_slice
        elif isinstance(existing_plan, dict) and "plan" in existing_plan:
            combined_plan = existing_plan["plan"] + new_plan_slice
        else:
            combined_plan = new_plan_slice
    else:
        combined_plan = new_plan_slice

    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"gold_profile_plan": combined_plan, "gold_profile_updated_at": now_iso}}
    )

    return {"status": "success", "data": combined_plan}


@router.post("/api/network/gold-profile/post")
async def gold_profile_post(req: GoldProfileTopicRequest, current_user: dict = Depends(get_current_user)):
    check = await check_subscription_limit(current_user["id"], "portfolio")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="La génération de posts viraux et le Portfolio IA nécessitent le déblocage du forfait ESSENTIAL ou PRO.")
    from agents.mentor import MentorAgent

    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    cv_text = user.get("cv_text", "") if user else ""
    linkedin_text = req.linkedin_profile or (user.get("linkedin_profile", "") if user else "")

    mentor = MentorAgent()
    await mentor.initialize()
    result = await mentor.think({"action": "gold_profile_post", "topic": req.topic, "format": req.format or "Text", "cv_text": cv_text, "linkedin_text": linkedin_text})

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("content", "Erreur lors de la génération du post."))

    post_data = result.get("data")
    key = str(req.day) if req.day is not None else req.topic
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {f"gold_profile_posts.{key}": post_data}}
    )

    return {"status": "success", "data": post_data}


@router.get("/api/network/contacts")
async def get_network_contacts(current_user: dict = Depends(get_current_user)):
    """Récupère tout le carnet d'adresses réseau."""
    check = await check_subscription_limit(current_user["id"], "address_book")
    if not check["allowed"]:
        raise HTTPException(status_code=403, detail="L'accès au carnet d'adresses réseau enrichi est réservé aux forfaits ESSENTIAL et PRO.")
    import json as _json
    try:
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
            if "_id" in contact:
                contact["_id"] = str(contact["_id"])

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


@router.post("/api/network/ninja/run")
async def run_network_ninja(current_user: dict = Depends(get_current_user)):
    from agents.network_ninja_agent import network_ninja_agent
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        result = await network_ninja_agent.run(user_id)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error running network ninja: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/network/ninja/results")
async def get_network_ninja_results(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        db = get_db()
        doc = await db.ninja_results.find_one({"user_id": user_id})
        if not doc:
            return {"status": "success", "data": {"companies": []}}

        doc.pop("_id", None)
        return {"status": "success", "data": doc}
    except Exception as e:
        logger.error(f"Error getting network ninja results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
