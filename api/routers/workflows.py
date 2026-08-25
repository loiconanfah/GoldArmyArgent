"""Routes workflows : smart-cover, ghostbuster, network-ninja, pre-interview, rejection-pivot,
daily-hunt, social-sniper, post-interview, gold-profile, sniper-apply, radar."""
import io
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.auth import get_current_user
from core.database import get_db

router = APIRouter()


# ─── Smart Cover ───
class SmartCoverRequest(BaseModel):
    company_name: str
    job_title: Optional[str] = "Poste ouvert"
    job_description: Optional[str] = ""   # description collée depuis un lien externe (optionnel)
    job_url: Optional[str] = None         # lien de l'offre (référence, optionnel)


@router.post("/api/workflows/smart-cover")
async def execute_smart_cover(req: SmartCoverRequest, current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Exécute le Playbook 10 (Smart Cover) et retourne le résultat."""
    from agents.headhunter import headhunter_agent
    from api.subscription import check_subscription_limit, log_usage

    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")

    # Vérifie le solde Gold avant de générer (coût "cover_letter").
    check = await check_subscription_limit(user_id, "cover_letter")
    if not check.get("allowed"):
        raise HTTPException(status_code=403, detail=check.get("message", "Gold insuffisant pour générer une lettre."))

    user_data = await db.users.find_one({"id": user_id})
    cv_text = user_data.get("cv_text", "") if user_data else ""

    logger.info(f"🧪 Test Smart Cover pour {req.company_name} par {current_user['email']}")
    result = await headhunter_agent.generate_smart_cover_letter(
        req.company_name, req.job_title, cv_text=cv_text, job_desc=req.job_description or "")

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Débite le Gold seulement après une génération réussie.
    await log_usage(user_id, "cover_letter")
    from api.notifications import notify
    await notify(user_id, "Lettre de motivation prête",
                 f"Ta lettre Smart Cover pour {req.company_name} est prête à télécharger.",
                 "success")

    return {"status": "success", "data": result}


@router.post("/api/workflows/smart-cover/bulk")
async def execute_smart_cover_bulk(req: List[SmartCoverRequest], current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Exécute le Playbook 10 pour plusieurs entreprises."""
    from agents.headhunter import headhunter_agent
    from api.subscription import log_usage

    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    user_data = await db.users.find_one({"id": user_id})
    cv_text = user_data.get("cv_text", "") if user_data else ""

    results = []
    generated = 0
    for item in req:
        logger.info(f"🧪 Bulk Smart Cover pour {item.company_name}")
        res = await headhunter_agent.generate_smart_cover_letter(item.company_name, item.job_title, cv_text=cv_text)
        if isinstance(res, dict) and res.get("letter"):
            generated += 1
        results.append({"company": item.company_name, "result": res})

    # Débite le Gold pour chaque lettre réellement générée.
    if generated:
        await log_usage(user_id, "cover_letter", generated)

    return {"status": "success", "data": results}


@router.post("/api/workflows/smart-cover/download")
async def download_cover_letter(data: dict, current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Génère et retourne un PDF de la lettre avec gestion Premium/Standard."""
    from core.pdf_service import generate_cover_letter_pdf

    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    user_data = await db.users.find_one({"id": user_id})

    user_tier = (user_data.get("subscription_tier") or user_data.get("tier") or user_data.get("plan") or "FREE").upper()
    is_premium_user = user_tier == "ADMIN" or user_tier not in ["FREE", "BASIC", ""]
    force_standard = data.get("force_standard", False)
    is_premium = is_premium_user and not force_standard

    pdf_data = {
        "letter": data.get("letter", ""),
        "full_name": user_data.get("full_name") if user_data else "Candidat",
        "email": user_data.get("email") if user_data else "",
        "phone": user_data.get("phone", "") if user_data else ""
    }

    pdf_bytes = generate_cover_letter_pdf(pdf_data, is_premium=is_premium)

    filename = f"lettre_motivation_{data.get('company','box')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ─── Ghostbuster (#2) ───
class GhostbusterToggleRequest(BaseModel):
    enabled: bool


class GhostbusterSendRequest(BaseModel):
    app_id: str
    via: str = "manual"


class GhostbusterScanRequest(BaseModel):
    force_regenerate: bool = False
    chain_to: Optional[str] = None


@router.post("/api/workflows/ghostbuster/scan")
async def ghostbuster_scan(
    req: GhostbusterScanRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Scanne les candidatures APPLIED sans réponse > 15 jours ouvrables et génère les relances."""
    try:
        from agents.ghostbuster_agent import ghostbuster_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        result = await ghostbuster_agent.scan_and_generate(
            user_id=user_id,
            chain_to=req.chain_to,
            force_regenerate=req.force_regenerate,
        )

        eligible_count = len(result.get("eligible", []))
        await db.ghostbuster_config.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_run_at": datetime.now(timezone.utc),
                    "last_result_count": eligible_count,
                }
            },
            upsert=True,
        )

        if eligible_count:
            from api.notifications import notify
            await notify(user_id, "Relances prêtes",
                         f"{eligible_count} relance(s) anti-fantôme prête(s) à envoyer.",
                         "info", "/crm")

        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[API] Ghostbuster scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/workflows/ghostbuster/status")
async def ghostbuster_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retourne le statut du Ghostbuster pour l'utilisateur."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
        config = await db.ghostbuster_config.find_one({"user_id": user_id}, {"_id": 0}) or {}

        return {
            "status": "success",
            "data": {
                "auto_enabled": config.get("auto_enabled", False),
                "last_run_at": config.get("last_run_at"),
                "next_run_at": config.get("next_run_at"),
                "last_result_count": config.get("last_result_count", 0),
                "threshold_days": 15,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/ghostbuster/toggle")
async def ghostbuster_toggle(
    req: GhostbusterToggleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Active ou désactive le mode automatique 48h du Ghostbuster."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
        now = datetime.now(timezone.utc)

        await db.ghostbuster_config.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "auto_enabled": req.enabled,
                    "updated_at": now,
                    "next_run_at": now + timedelta(hours=48) if req.enabled else None,
                }
            },
            upsert=True,
        )

        action = "activé" if req.enabled else "désactivé"
        logger.info(f"[Ghostbuster] Mode auto {action} pour user {user_id}")
        return {
            "status": "success",
            "message": f"Mode automatique Ghostbuster {action}.",
            "auto_enabled": req.enabled,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/ghostbuster/send")
async def ghostbuster_send(
    req: GhostbusterSendRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Marque une relance Ghostbuster comme envoyée (copie manuelle par l'utilisateur)."""
    try:
        from agents.ghostbuster_agent import ghostbuster_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        ok = await ghostbuster_agent.mark_sent(
            user_id=user_id,
            app_id=req.app_id,
            via=req.via,
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Candidature introuvable ou aucune modification.")
        return {"status": "success", "message": "Relance marquée comme envoyée."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Network Ninja (#3) ───
@router.post("/api/workflows/network-ninja/run")
async def network_ninja_run(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Lance le workflow Network Ninja."""
    try:
        from agents.network_ninja_agent import network_ninja_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        logger.info(f"[API] Network Ninja lancé pour user {user_id}")
        result = await network_ninja_agent.run(user_id=user_id)

        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[API] Network Ninja run error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/workflows/network-ninja/results")
async def network_ninja_results(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retourne les résultats Network Ninja persistés pour l'utilisateur."""
    try:
        from agents.network_ninja_agent import network_ninja_agent
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")

        result = await network_ninja_agent.get_results(user_id=user_id)
        if not result:
            return {"status": "success", "data": None}

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Radar ───
class RadarRequest(BaseModel):
    company_name: str
    job_title: str


@router.post("/api/radar")
async def fetch_market_radar(req: RadarRequest):
    """Snipe company red flags and fetch salary estimates."""
    from agents.researcher import ResearcherAgent
    researcher = ResearcherAgent()
    await researcher.initialize()

    rep_query = f"{req.company_name} avis employes red flags culture entreprise"
    rep_task = {"action": "research", "query": rep_query}
    rep_result = await researcher.think(rep_task)

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


# ─── Pre-Interview (#4) ───
class PreInterviewItem(BaseModel):
    application_id: str
    simulation_date: str
    prep_type: str


class PreInterviewScheduleRequest(BaseModel):
    items: List[PreInterviewItem]


@router.get("/api/workflows/pre-interview/pending")
async def get_pre_interview_pending(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Récupère les candidatures en cours (INTERVIEW ou APPLIED) pour les planifier."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        cursor = db.applications.find(
            {"user_id": user_id, "status": {"$in": ["INTERVIEW", "APPLIED", "FOLLOW_UP"]}},
            {"_id": 0}
        ).sort("created_at", -1)

        apps = await cursor.to_list(length=100)
        return {"status": "success", "data": apps}
    except Exception as e:
        logger.error(f"Error fetching pending applications for pre-interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/pre-interview/schedule")
async def schedule_pre_interview(
    req: PreInterviewScheduleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Planifie une ou plusieurs simulations d'entretien avec des dates individuelles."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")

        import uuid

        app_ids = [item.application_id for item in req.items]

        apps_data = await db.applications.find(
            {"user_id": user_id, "id": {"$in": app_ids}},
            {"_id": 0}
        ).to_list(length=None)

        app_map = {a["id"]: a for a in apps_data}

        simulations = []
        for item in req.items:
            app = app_map.get(item.application_id)
            if not app:
                continue

            sim_date = datetime.fromisoformat(item.simulation_date.replace("Z", "+00:00"))
            sim_id = str(uuid.uuid4())

            simulations.append({
                "id": sim_id,
                "user_id": user_id,
                "application_id": item.application_id,
                "company_name": app.get("company_name", ""),
                "job_title": app.get("job_title", ""),
                "simulation_date": sim_date,
                "prep_type": item.prep_type,
                "status": "PENDING",
                "created_at": datetime.utcnow(),
                "prep_data": None
            })

        if simulations:
            await db.simulations.insert_many(simulations)

        return {"status": "success", "data": {"scheduled_count": len(simulations)}}
    except Exception as e:
        logger.error(f"Error scheduling pre-interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Rejection Pivot (#9) ───
class RejectionPivotRequest(BaseModel):
    app_id: str


@router.get("/api/workflows/rejection-pivot/rejected")
async def get_rejected_applications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Récupère les candidatures avec le statut REJECTED."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        cursor = db.applications.find(
            {"user_id": user_id, "status": "REJECTED"},
            {"_id": 0}
        ).sort("updated_at", -1)
        apps = await cursor.to_list(length=100)
        return {"status": "success", "data": apps}
    except Exception as e:
        logger.error(f"Error fetching rejected applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/rejection-pivot/generate")
async def generate_rejection_pivot(
    req: RejectionPivotRequest,
    current_user: dict = Depends(get_current_user)
):
    """Lance le workflow Rejection Pivot pour une candidature."""
    try:
        from agents.rejection_pivot_agent import rejection_pivot_agent
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")

        await rejection_pivot_agent.initialize()
        result = await rejection_pivot_agent.run_pivot(user_id, req.app_id)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running rejection pivot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Workflow status ───
class WorkflowStatusUpdate(BaseModel):
    workflow_id: int
    active: bool


@router.get("/api/workflows/status")
async def get_workflows_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retourne l'état d'activité persisté de tous les workflows pour l'utilisateur."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        active_workflows = user.get("active_workflows", []) if user else []

        status_map = {str(wf_id): True for wf_id in active_workflows}

        dh_config = await db.daily_hunt_config.find_one({"user_id": user_id})
        if dh_config:
            status_map["5"] = dh_config.get("enabled", False)

        gb_config = await db.ghostbuster_config.find_one({"user_id": user_id})
        if gb_config:
            status_map["2"] = gb_config.get("auto_scan", False)

        return {"status": "success", "data": status_map}
    except Exception as e:
        logger.error(f"Error fetching workflows status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/status")
async def set_workflow_status(
    req: WorkflowStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Persiste l'état actif/inactif d'un workflow dans le document utilisateur."""
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")

        if req.active:
            await db.users.update_one({"id": user_id}, {"$addToSet": {"active_workflows": req.workflow_id}})
        else:
            await db.users.update_one({"id": user_id}, {"$pull": {"active_workflows": req.workflow_id}})

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Daily Hunt (#5) ───
class DailyHuntToggleRequest(BaseModel):
    enabled: bool
    query: Optional[str] = "Développeur"
    location: Optional[str] = "Montreal, QC"


@router.get("/api/workflows/daily-hunt/config")
async def get_daily_hunt_config(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        cfg = await db.daily_hunt_config.find_one({"user_id": user_id}, {"_id": 0})
        if not cfg:
            return {"status": "success", "data": {"enabled": False, "query": "Développeur", "location": "Montreal, QC"}}
        return {"status": "success", "data": cfg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/daily-hunt/toggle")
async def toggle_daily_hunt(
    req: DailyHuntToggleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        await db.daily_hunt_config.update_one(
            {"user_id": user_id},
            {"$set": {
                "enabled": req.enabled,
                "query": req.query,
                "location": req.location,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        return {"status": "success", "data": {"enabled": req.enabled}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/social-sniper/generate")
async def generate_social_sniper(
    req: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        if not cv_text:
            raise HTTPException(status_code=400, detail="CV requis.")

        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "social_sniper",
            "cv_text": cv_text,
            "company": req.get("company"),
            "job": req.get("job")
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/workflows/post-interview/apps")
async def get_interview_apps(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        apps = await db.applications.find(
            {"user_id": user_id, "status": "INTERVIEW"},
            {"_id": 0}
        ).sort("updated_at", -1).to_list(length=20)
        return {"status": "success", "data": apps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/post-interview/generate")
async def generate_post_interview(
    req: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""

        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "post_interview_analysis",
            "cv_text": cv_text,
            "company": req.get("company"),
            "job": req.get("job"),
            "debrief": req.get("debrief")
        })

        if result.get("status") == "success":
            from api.subscription import log_usage
            await log_usage(user_id, "post_interview")
            if req.get("app_id"):
                await db.applications.update_one(
                    {"id": req.get("app_id"), "user_id": user_id},
                    {"$set": {"status": "FOLLOW_UP", "updated_at": datetime.utcnow()}}
                )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/workflows/gold-profile/audit")
async def gold_profile_audit(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "")

        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "gold_profile_audit",
            "cv_text": cv_text
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/workflows/gold-profile/plan")
async def gold_profile_plan(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        existing = await db.gold_profile_plans.find_one({"user_id": user_id})
        if existing:
            return {"status": "success", "data": {"plan": existing["plan"]}}

        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "")

        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "gold_profile_plan",
            "cv_text": cv_text
        })

        if result["status"] == "success":
            await db.gold_profile_plans.update_one(
                {"user_id": user_id},
                {"$set": {"plan": result["data"]["plan"], "updated_at": datetime.now(timezone.utc)}},
                upsert=True
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/gold-profile/post")
async def gold_profile_post(
    req: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "")

        from agents.mentor import MentorAgent
        mentor = MentorAgent()
        result = await mentor.think({
            "action": "gold_profile_post",
            "cv_text": cv_text,
            "topic": req.get("topic")
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Sniper To Apply ───
class SniperApplySearchRequest(BaseModel):
    job_title: str
    location: str
    nb_results: Optional[int] = 10


class SniperApplyExecuteRequest(BaseModel):
    selected_offers: List[Dict[str, Any]]


@router.post("/api/workflows/sniper-apply/search")
async def sniper_apply_search(
    req: SniperApplySearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""

        from agents.job_searcher import JobSearchAgent
        searcher = JobSearchAgent()
        await searcher.initialize()

        task = {
            "query": req.job_title,
            "location": req.location,
            "nb_results": req.nb_results,
            "cv_text": cv_text
        }
        plan = await searcher.think(task)
        result = await searcher.act(plan)

        return {"status": "success", "data": result.get("matched_jobs", [])}
    except Exception as e:
        logger.error(f"Sniper Apply Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workflows/sniper-apply/execute")
async def sniper_apply_execute(
    req: SniperApplyExecuteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        import uuid
        import httpx
        from agents.cv_adapter import CVAdapterAgent

        user_id = current_user.get("id") or current_user.get("uid") or current_user.get("sub")
        user = await db.users.find_one({"id": user_id})
        cv_text = user.get("cv_text", "") if user else ""
        from api.subscription import check_subscription_limit, log_usage
        check = await check_subscription_limit(user_id, "sniper_apply")
        remaining = check["limit"] - check.get("current", 0)

        if len(req.selected_offers) > remaining and check["limit"] < 99999:
            raise HTTPException(status_code=403, detail=f"Limite journalière dépassée. Offres restantes aujourd'hui : {remaining}")

        adapter = CVAdapterAgent()
        await adapter.initialize()

        from config.settings import settings
        skyvern_api_key = settings.skyvern_api_key
        if not skyvern_api_key:
            raise HTTPException(status_code=500, detail="La clé d'API Skyvern n'est pas configurée dans l'environnement du serveur.")

        skyvern_api_url = "https://api.skyvern.com/v1/run/tasks"

        results = []

        for offer in req.selected_offers:
            title = offer.get("title", "")
            company = offer.get("company", "")
            desc = offer.get("description", "")
            url = offer.get("url", "")

            adapt_result = await adapter.adapt(title, desc, cv_text)
            cv_json = adapt_result.get("cv_json", {})

            skyvern_task_id = None
            if url and skyvern_api_key:
                try:
                    prompt = f"Apply to this job. My name is {cv_json.get('full_name', 'Candidat')}. My skills are {cv_json.get('skills', {})}. Please fill the form and attach my resume or paste my details."
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        resp = await client.post(
                            skyvern_api_url,
                            headers={"x-api-key": skyvern_api_key, "Content-Type": "application/json"},
                            json={
                                "url": url,
                                "prompt": prompt,
                                "title": f"Auto-Apply to {company} - {title}",
                                "proxy_location": "RESIDENTIAL",
                                "engine": "skyvern-2.0"
                            }
                        )
                        if resp.status_code in [200, 201]:
                            skyvern_task_id = resp.json().get("run_id") or resp.json().get("task_id")
                        else:
                            logger.warning(f"Skyvern API error: {resp.status_code} - {resp.text}")
                except Exception as ex:
                    logger.warning(f"Skyvern API call failed for {company}: {ex}")

            app_id = str(uuid.uuid4())
            new_app = {
                "id": app_id,
                "user_id": user_id,
                "job_title": title,
                "company_name": company,
                "url": url,
                "status": "APPLIED",
                "notes": "Appliqué via Sniper To Apply (Skyvern)\n" + (f"Skyvern Task: {skyvern_task_id}" if skyvern_task_id else ""),
                "cv_json": cv_json,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.applications.insert_one(new_app)

            results.append({
                "id": app_id,
                "company": company,
                "title": title,
                "skyvern_task_id": skyvern_task_id,
                "status": "success"
            })

        await log_usage(user_id, "sniper_apply", len(results))
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Sniper Apply Execute Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
