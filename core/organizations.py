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

# Forfaits Organisation par palier — le palier dépend du nombre de MEMBRES ACTIFS.
# max_active = plafond de membres actifs inclus ; None = sur devis (Enterprise).
# member_gold = Gold mensuel offert à chaque membre SPONSORISÉ de ce palier.
ORG_PLANS = [
    {"key": "free", "name": "Découverte", "max_active": 5, "monthly": 0, "annual": 0,
     "member_gold": 100, "tagline": "tagline_free",
     "features": ["f_dashboard", "f_community", "f_cv_ats", "f_network_manual"]},
    {"key": "starter", "name": "Starter", "max_active": 25, "monthly": 149, "annual": 1490,
     "member_gold": 300, "tagline": "tagline_starter",
     "features": ["f_dashboard", "f_community", "f_cv_ats", "f_network_manual", "f_member_tracking"]},
    {"key": "growth", "name": "Growth", "max_active": 75, "monthly": 399, "annual": 3990,
     "member_gold": 300, "tagline": "tagline_growth",
     "features": ["f_all_starter", "f_mentors_events", "f_network_import", "f_analytics_adv", "f_advisors"]},
    {"key": "scale", "name": "Scale", "max_active": 200, "monthly": 899, "annual": 8990,
     "member_gold": 600, "tagline": "tagline_scale",
     "features": ["f_all_growth", "f_reports_export", "f_priority_support", "f_onboarding"]},
    {"key": "enterprise", "name": "Enterprise", "max_active": None, "monthly": None, "annual": None,
     "member_gold": 1000, "tagline": "tagline_enterprise",
     "features": ["f_all_scale", "f_unlimited", "f_sso_api", "f_white_label", "f_dedicated"]},
]
PLAN_BY_KEY = {p["key"]: p for p in ORG_PLANS}


def get_plan(key: str) -> Optional[Dict[str, Any]]:
    return PLAN_BY_KEY.get(key)


def org_plan_state(org: Dict[str, Any]) -> Dict[str, Any]:
    """Palier effectif d'une organisation : payant si abonnement actif, sinon Découverte.

    Retourne {plan, gold (Gold mensuel par membre sponsorisé), cap (sièges premium)}.
    """
    if org and org.get("billing_status") == "active" and org.get("billing_plan"):
        p = PLAN_BY_KEY.get(org["billing_plan"], PLAN_BY_KEY["free"])
    else:
        p = PLAN_BY_KEY["free"]
    return {"plan": p["key"], "gold": p["member_gold"], "cap": p["max_active"]}


def recommend_plan(active_count: int) -> str:
    """Plus petit forfait dont le plafond couvre le nombre de membres actifs."""
    for p in ORG_PLANS:
        if p["max_active"] is not None and active_count <= p["max_active"]:
            return p["key"]
    return "enterprise"


async def active_member_count(org_id: str) -> int:
    """Nombre de membres ACTIFS : ≥ 1 candidature OU adhésion dans les 30 derniers jours."""
    from datetime import timedelta
    db = get_db()
    member_ids = [u["id"] async for u in db.users.find(
        {"organization_id": org_id, "role": "member"}, {"_id": 0, "id": 1})]
    if not member_ids:
        return 0

    active = set()
    # Actifs par candidature
    async for row in db.applications.aggregate([
        {"$match": {"user_id": {"$in": member_ids}}},
        {"$group": {"_id": "$user_id"}},
    ]):
        active.add(row["_id"])

    # Grâce de 30 jours pour les nouveaux membres
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    async for u in db.users.find(
        {"organization_id": org_id, "role": "member", "org_joined_at": {"$gte": cutoff}},
        {"_id": 0, "id": 1},
    ):
        active.add(u["id"])

    return len(active)


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

    # L'adhésion ne débloque PAS le premium : l'admin sponsorise ensuite (siège premium).
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "organization_id": org["id"],
            "role": "member",
            "account_type": "candidate",
            "subscription_tier": "FREE",
            "sponsored": False,
            "org_joined_at": datetime.now(timezone.utc),
        }},
    )
    return {"status": "success", "organization": org}


async def sponsored_count(org_id: str) -> int:
    db = get_db()
    return await db.users.count_documents(
        {"organization_id": org_id, "role": "member", "sponsored": True})


async def set_sponsorship(org_id: str, user_id: str, sponsored: bool) -> Dict[str, Any]:
    """Sponsorise (ou retire) un membre : règle son subscription_tier en conséquence.

    Respecte le plafond de sièges du palier effectif de l'organisation.
    """
    db = get_db()
    org = await get_organization(org_id)
    state = org_plan_state(org or {})

    member = await db.users.find_one({"id": user_id, "organization_id": org_id, "role": "member"})
    if not member:
        return {"status": "error", "message": "Membre introuvable."}

    if sponsored:
        newly = not member.get("sponsored")
        if newly:
            cap = state["cap"]
            if cap is not None:
                current = await sponsored_count(org_id)
                if current >= cap:
                    return {"status": "error", "message": "cap_reached", "cap": cap}
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"sponsored": True, "last_org_refill": datetime.now(timezone.utc)}},
        )
        if newly:
            # Crédite immédiatement le Gold mensuel du palier
            from core.gold import grant_gold
            await grant_gold(user_id, state["gold"], "org_sponsor", meta={"org_id": org_id})
    else:
        await db.users.update_one({"id": user_id}, {"$set": {"sponsored": False}})
    return {"status": "success", "sponsored": sponsored, "gold": state["gold"] if sponsored else 0}


async def monthly_org_refill(org_id: str) -> int:
    """Recharge mensuelle des membres sponsorisés en Gold (idempotent, > 30 j).

    À déclencher par un cron mensuel (ou l'endpoint dédié). Retourne le nb de membres rechargés.
    """
    from datetime import timedelta
    from core.gold import grant_gold
    db = get_db()
    org = await get_organization(org_id)
    state = org_plan_state(org or {})
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)

    members = await db.users.find(
        {"organization_id": org_id, "role": "member", "sponsored": True},
        {"_id": 0, "id": 1, "last_org_refill": 1},
    ).to_list(length=None)

    n = 0
    for m in members:
        last = m.get("last_org_refill")
        if last and getattr(last, "tzinfo", None) is None:
            last = last.replace(tzinfo=timezone.utc)
        if last is None or last < cutoff:
            await db.users.update_one({"id": m["id"]}, {"$set": {"last_org_refill": now}})
            await grant_gold(m["id"], state["gold"], "org_monthly", meta={"org_id": org_id})
            n += 1
    return n


async def monthly_refill_all() -> int:
    """Recharge toutes les organisations (pour un cron global). Retourne le total rechargé."""
    db = get_db()
    total = 0
    org_ids = [o["id"] async for o in db.organizations.find({}, {"_id": 0, "id": 1})]
    for oid in org_ids:
        total += await monthly_org_refill(oid)
    return total


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
         "created_at": 1, "org_joined_at": 1, "sponsored": 1, "subscription_tier": 1},
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
            "sponsored": bool(m.get("sponsored")),
            "tier": m.get("subscription_tier", "FREE"),
        })
    # Trie par activité décroissante (plus actifs d'abord)
    result.sort(key=lambda x: x["applications"], reverse=True)
    return result


async def set_member_role(org_id: str, user_id: str, member_role: str) -> bool:
    """Définit le rôle interne d'un membre : 'member' | 'mentor' | 'advisor'."""
    db = get_db()
    if member_role not in ("member", "mentor", "advisor"):
        member_role = "member"
    res = await db.users.update_one(
        {"id": user_id, "organization_id": org_id, "role": "member"},
        {"$set": {"org_member_role": member_role}},
    )
    return res.modified_count > 0


async def member_detail(org_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Détail complet d'un membre : profil, candidatures, simulations d'entretien."""
    db = get_db()
    user = await db.users.find_one(
        {"id": user_id, "organization_id": org_id},
        {"_id": 0, "hashed_password": 0},
    )
    if not user:
        return None

    applications = await db.applications.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(length=200)

    simulations = await db.simulations.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(length=50)

    # Répartition par statut (funnel individuel)
    funnel: Dict[str, int] = {}
    for a in applications:
        st = a.get("status", "TO_APPLY")
        funnel[st] = funnel.get(st, 0) + 1

    return {
        "profile": {
            "id": user["id"],
            "email": user.get("email", ""),
            "full_name": user.get("full_name", ""),
            "has_cv": bool(user.get("cv_text")),
            "org_member_role": user.get("org_member_role", "member"),
            "joined_at": user.get("org_joined_at") or user.get("created_at"),
            "subscription_tier": user.get("subscription_tier", "FREE"),
        },
        "funnel": funnel,
        "applications": applications,
        "simulations": simulations,
    }


async def analytics(org_id: str) -> Dict[str, Any]:
    """Analytics riches pour le dashboard : KPIs, série mensuelle, funnel, top membres."""
    db = get_db()
    members = await db.users.find(
        {"organization_id": org_id, "role": "member"},
        {"_id": 0, "id": 1, "full_name": 1, "email": 1, "cv_text": 1},
    ).to_list(length=None)
    member_ids = [m["id"] for m in members]
    total_members = len(member_ids)

    base = await cohort_stats(org_id)

    empty_series = []
    import datetime as _dt
    from dateutil.relativedelta import relativedelta
    months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    now = _dt.datetime.now()

    funnel = {"TO_APPLY": 0, "APPLIED": 0, "FOLLOW_UP": 0, "INTERVIEW": 0, "REJECTED": 0}
    monthly = {}
    per_member = {}

    if member_ids:
        # Funnel global par statut
        async for row in db.applications.aggregate([
            {"$match": {"user_id": {"$in": member_ids}}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]):
            key = row["_id"] or "TO_APPLY"
            funnel[key] = funnel.get(key, 0) + row["count"]

        # Série mensuelle des candidatures
        async for row in db.applications.aggregate([
            {"$match": {"user_id": {"$in": member_ids}, "created_at": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$created_at"}}}, "count": {"$sum": 1}}},
        ]):
            if row["_id"]:
                monthly[row["_id"]] = row["count"]

        # Candidatures + entretiens par membre (pour le top)
        async for row in db.applications.aggregate([
            {"$match": {"user_id": {"$in": member_ids}}},
            {"$group": {
                "_id": "$user_id",
                "apps": {"$sum": 1},
                "interviews": {"$sum": {"$cond": [{"$eq": ["$status", "INTERVIEW"]}, 1, 0]}},
            }},
        ]):
            per_member[row["_id"]] = row

    # Construit la série des 8 derniers mois
    max_val = max(monthly.values()) if monthly else 10
    if max_val < 10:
        max_val = 10
    for i in range(7, -1, -1):
        d = now - relativedelta(months=i)
        key = d.strftime("%Y-%m")
        count = monthly.get(key, 0)
        pct = int((count / max_val) * 100) if max_val else 0
        empty_series.append({"label": months_fr[d.month - 1], "count": count, "pct": max(pct, 3 if count else 0)})

    # Top 5 membres les plus actifs
    name_by_id = {m["id"]: (m.get("full_name") or m.get("email", "").split("@")[0]) for m in members}
    top = sorted(
        [{"id": uid, "name": name_by_id.get(uid, "?"), "apps": v["apps"], "interviews": v["interviews"]}
         for uid, v in per_member.items()],
        key=lambda x: x["apps"], reverse=True,
    )[:5]

    # Compteurs additionnels (mentors, conseillers, événements, réseau, communauté)
    mentors_count = await db.users.count_documents({"organization_id": org_id, "org_member_role": "mentor"})
    advisors_count = await db.users.count_documents({"organization_id": org_id, "org_member_role": "advisor"})
    events_count = await db.org_events.count_documents({"organization_id": org_id})
    network_count = await db.org_network.count_documents({"organization_id": org_id})
    posts_count = await db.org_posts.count_documents({"organization_id": org_id})

    return {
        "kpis": base,
        "funnel": funnel,
        "monthly": empty_series,
        "top_members": top,
        "counts": {
            "mentors": mentors_count,
            "advisors": advisors_count,
            "events": events_count,
            "network": network_count,
            "posts": posts_count,
        },
    }


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
