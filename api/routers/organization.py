"""Routes de l'espace Organisation (B2B2C) : gestion de cohorte, invitations, stats.

Toutes les routes d'administration exigent le rôle org_admin.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from api.auth import get_current_user
from core.database import get_db
from core import organizations as orgs

router = APIRouter(prefix="/api/org", tags=["Organization"])


class InviteEmailRequest(BaseModel):
    email: str


class JoinRequest(BaseModel):
    code: str


class OrgSettingsRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    member_tier: Optional[str] = None
    seats_limit: Optional[int] = None
    contact_email: Optional[str] = None


async def get_current_org_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dépendance : recharge l'utilisateur complet et vérifie le rôle org_admin."""
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    if not user or user.get("role") != "org_admin" or not user.get("organization_id"):
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs d'organisation.")
    return user


@router.get("/me")
async def get_my_organization(admin: dict = Depends(get_current_org_admin)):
    """Retourne l'organisation de l'admin connecté."""
    org = await orgs.get_organization(admin["organization_id"])
    if not org:
        raise HTTPException(status_code=404, detail="Organisation introuvable.")
    return {"status": "success", "data": org}


@router.get("/stats")
async def get_cohort_stats(admin: dict = Depends(get_current_org_admin)):
    """KPIs agrégés de la cohorte."""
    stats = await orgs.cohort_stats(admin["organization_id"])
    return {"status": "success", "data": stats}


@router.get("/members")
async def get_members(admin: dict = Depends(get_current_org_admin)):
    """Liste des membres avec leur progression individuelle."""
    members = await orgs.list_members_with_progress(admin["organization_id"])
    return {"status": "success", "data": members}


@router.delete("/members/{user_id}")
async def delete_member(user_id: str, admin: dict = Depends(get_current_org_admin)):
    """Retire un membre de la cohorte (sans supprimer son compte)."""
    ok = await orgs.remove_member(admin["organization_id"], user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Membre introuvable dans cette organisation.")
    return {"status": "success"}


@router.post("/invite")
async def invite_by_email(req: InviteEmailRequest, admin: dict = Depends(get_current_org_admin)):
    """Envoie un email d'invitation contenant le code et le lien d'inscription."""
    org = await orgs.get_organization(admin["organization_id"])
    if not org:
        raise HTTPException(status_code=404, detail="Organisation introuvable.")

    code = org["invite_code"]
    join_url = f"https://goldarmyai.com/register?org={code}"
    subject = f"Invitation à rejoindre {org['name']} sur GoldArmy AI"
    content = (
        f"Bonjour,\n\n"
        f"Vous êtes invité(e) à rejoindre la cohorte « {org['name'] }» sur GoldArmy AI.\n\n"
        f"Inscrivez-vous ici : {join_url}\n"
        f"Ou utilisez le code d'invitation : {code}\n\n"
        f"À bientôt,\nL'équipe GoldArmy AI"
    )
    try:
        from core.email_service import email_service
        await email_service.send_email(req.email, subject, content)
    except Exception as e:
        logger.warning(f"[ORG] Envoi invitation échoué ({req.email}): {e}")
        raise HTTPException(status_code=502, detail="L'email d'invitation n'a pas pu être envoyé.")

    return {"status": "success", "code": code, "join_url": join_url}


@router.put("/settings")
async def update_settings(req: OrgSettingsRequest, admin: dict = Depends(get_current_org_admin)):
    """Met à jour les paramètres de l'organisation."""
    db = get_db()
    fields = {}
    if req.name is not None:
        fields["name"] = req.name.strip()
    if req.type is not None and req.type in orgs.ORG_TYPES:
        fields["type"] = req.type
    if req.member_tier is not None and req.member_tier in ("ESSENTIAL", "PRO", "FREE"):
        fields["member_tier"] = req.member_tier
    if req.seats_limit is not None and req.seats_limit > 0:
        fields["seats_limit"] = int(req.seats_limit)
    if req.contact_email is not None:
        fields["contact_email"] = req.contact_email.strip()

    if not fields:
        return {"status": "success", "message": "Aucun changement."}

    await db.organizations.update_one({"id": admin["organization_id"]}, {"$set": fields})
    org = await orgs.get_organization(admin["organization_id"])
    return {"status": "success", "data": org}


# ─── Public / membre ───

@router.get("/invite/{code}")
async def validate_invite(code: str):
    """Valide un code d'invitation (public) — utilisé par le formulaire d'inscription."""
    org = await orgs.get_org_by_code(code)
    if not org:
        return {"valid": False}
    return {
        "valid": True,
        "organization_name": org["name"],
        "organization_type": org.get("type", "other"),
    }


@router.post("/join")
async def join_org(req: JoinRequest, current_user: dict = Depends(get_current_user)):
    """Rattache l'utilisateur connecté à une organisation via son code d'invitation."""
    result = await orgs.join_organization(current_user["id"], req.code)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return {"status": "success", "data": result.get("organization")}
