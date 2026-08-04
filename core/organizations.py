"""
Logique métier des Organisations (espace B2B2C).

Une organisation (école, organisme d'employabilité, bootcamp, agence, coach)
regroupe une cohorte de candidats. Le propriétaire est un utilisateur avec
role="org_admin"; les membres ont role="member" et organization_id renseigné.

Ce module ne dépend PAS de FastAPI/auth pour éviter les imports circulaires.
"""
import uuid
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.database import get_db

# Types d'organisation reconnus (libellés côté frontend)
ORG_TYPES = {"school", "employability", "bootcamp", "agency", "coach", "other"}

# Palier accordé par défaut aux membres d'une cohorte
DEFAULT_MEMBER_TIER = "ESSENTIAL"
DEFAULT_SEATS_LIMIT = 50


def generate_invite_code(length: int = 8) -> str:
    """Code d'invitation court, lisible, sans caractères ambigus."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sans I, O, 0, 1
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def create_organization(
    owner_id: str,
    name: str,
    org_type: str = "other",
    member_tier: str = DEFAULT_MEMBER_TIER,
    seats_limit: int = DEFAULT_SEATS_LIMIT,
    contact_email: str = "",
) -> Dict[str, Any]:
    """Crée une organisation et promeut le propriétaire au rang org_admin."""
    db = get_db()
    org_id = str(uuid.uuid4())
    if org_type not in ORG_TYPES:
        org_type = "other"

    # Génère un code d'invitation unique
    code = generate_invite_code()
    while await db.organizations.find_one({"invite_code": code}):
        code = generate_invite_code()

    org = {
        "id": org_id,
        "name": name.strip() or "Mon organisation",
        "type": org_type,
        "owner_id": owner_id,
        "invite_code": code,
        "member_tier": member_tier,
        "seats_limit": int(seats_limit),
        "contact_email": contact_email.strip(),
        "created_at": datetime.now(timezone.utc),
    }
    await db.organizations.insert_one(org)

    # Le propriétaire devient administrateur de l'organisation
    await db.users.update_one(
        {"id": owner_id},
        {"$set": {
            "account_type": "organization",
            "role": "org_admin",
            "organization_id": org_id,
        }},
    )
    org.pop("_id", None)
    return org


async def get_organization(org_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    return await db.organizations.find_one({"id": org_id}, {"_id": 0})


async def get_org_by_code(code: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    return await db.organizations.find_one(
        {"invite_code": (code or "").strip().upper()}, {"_id": 0}
    )


async def count_members(org_id: str) -> int:
    db = get_db()
    return await db.users.count_documents({"organization_id": org_id, "role": "member"})


async def join_organization(user_id: str, code: str) -> Dict[str, Any]:
    """Rattache un utilisateur connecté à une organisation via son code d'invitation.

    Retourne {"status": "success"|"error", ...}.
    """
    db = get_db()
    org = await get_org_by_code(code)
    if not org:
        return {"status": "error", "message": "Code d'invitation invalide."}

    # Empêche de rejoindre si déjà membre d'une organisation
    user = await db.users.find_one({"id": user_id})
    if user and user.get("organization_id"):
        if user.get("organization_id") == org["id"]:
            return {"status": "success", "organization": org, "message": "Déjà membre."}
        return {"status": "error", "message": "Vous appartenez déjà à une organisation."}

    # Vérifie les sièges disponibles
    current = await count_members(org["id"])
    if current >= org.get("seats_limit", DEFAULT_SEATS_LIMIT):
        return {"status": "error", "message": "Cette organisation a atteint sa limite de places."}

    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "organization_id": org["id"],
            "role": "member",
            "account_type": "candidate",
            "subscription_tier": org.get("member_tier", DEFAULT_MEMBER_TIER),
            "org_joined_at": datetime.now(timezone.utc),
        }},
    )
    return {"status": "success", "organization": org}


async def remove_member(org_id: str, user_id: str) -> bool:
    """Détache un membre de l'organisation (sans supprimer son compte)."""
    db = get_db()
    res = await db.users.update_one(
        {"id": user_id, "organization_id": org_id, "role": "member"},
        {"$set": {"organization_id": None, "role": None, "subscription_tier": "FREE"}},
    )
    return res.modified_count > 0


async def list_members_with_progress(org_id: str) -> List[Dict[str, Any]]:
    """Liste les membres de la cohorte avec leur progression individuelle."""
    db = get_db()
    members = await db.users.find(
        {"organization_id": org_id, "role": "member"},
        {"_id": 0, "id": 1, "email": 1, "full_name": 1, "cv_text": 1,
         "created_at": 1, "org_joined_at": 1},
    ).to_list(length=None)

    if not members:
        return []

    member_ids = [m["id"] for m in members]

    # Agrège les candidatures par membre en une seule requête
    pipeline = [
        {"$match": {"user_id": {"$in": member_ids}}},
        {"$group": {
            "_id": "$user_id",
            "total": {"$sum": 1},
            "applied": {"$sum": {"$cond": [{"$ne": ["$status", "TO_APPLY"]}, 1, 0]}},
            "interviews": {"$sum": {"$cond": [{"$eq": ["$status", "INTERVIEW"]}, 1, 0]}},
            "last_activity": {"$max": "$created_at"},
        }},
    ]
    agg = {row["_id"]: row async for row in db.applications.aggregate(pipeline)}

    result = []
    for m in members:
        stats = agg.get(m["id"], {})
        result.append({
            "id": m["id"],
            "email": m.get("email", ""),
            "full_name": m.get("full_name", ""),
            "has_cv": bool(m.get("cv_text")),
            "applications": stats.get("total", 0),
            "applied": stats.get("applied", 0),
            "interviews": stats.get("interviews", 0),
            "last_activity": stats.get("last_activity"),
            "joined_at": m.get("org_joined_at") or m.get("created_at"),
        })
    # Trie par activité décroissante (plus actifs d'abord)
    result.sort(key=lambda x: x["applications"], reverse=True)
    return result


async def cohort_stats(org_id: str) -> Dict[str, Any]:
    """KPIs agrégés de la cohorte pour le tableau de bord organisme."""
    db = get_db()
    member_ids = [
        u["id"] async for u in db.users.find(
            {"organization_id": org_id, "role": "member"}, {"_id": 0, "id": 1}
        )
    ]
    total_members = len(member_ids)

    if not member_ids:
        return {
            "total_members": 0, "active_members": 0, "with_cv": 0,
            "total_applications": 0, "total_interviews": 0,
            "avg_applications": 0, "placement_rate": 0,
        }

    with_cv = await db.users.count_documents(
        {"organization_id": org_id, "role": "member", "cv_text": {"$exists": True, "$ne": ""}}
    )

    pipeline = [
        {"$match": {"user_id": {"$in": member_ids}}},
        {"$group": {
            "_id": None,
            "total_applications": {"$sum": 1},
            "total_interviews": {"$sum": {"$cond": [{"$eq": ["$status", "INTERVIEW"]}, 1, 0]}},
            "active_members": {"$addToSet": "$user_id"},
        }},
    ]
    rows = await db.applications.aggregate(pipeline).to_list(length=1)
    if rows:
        r = rows[0]
        total_applications = r.get("total_applications", 0)
        total_interviews = r.get("total_interviews", 0)
        active_members = len(r.get("active_members", []))
    else:
        total_applications = total_interviews = active_members = 0

    return {
        "total_members": total_members,
        "active_members": active_members,
        "with_cv": with_cv,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
        "avg_applications": round(total_applications / total_members, 1) if total_members else 0,
        "placement_rate": round((total_interviews / total_members) * 100) if total_members else 0,
    }
