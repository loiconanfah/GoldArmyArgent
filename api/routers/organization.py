"""Routes de l'espace Organisation (B2B2C) : gestion de cohorte, invitations, stats.

Toutes les routes d'administration exigent le rôle org_admin.
"""
import io
import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict
from loguru import logger

from api.auth import get_current_user
from core.database import get_db
from core import organizations as orgs

router = APIRouter(prefix="/api/org", tags=["Organization"])


async def get_current_org_member(current_user: dict = Depends(get_current_user)) -> dict:
    """Dépendance : tout utilisateur rattaché à une organisation (membre OU admin)."""
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    if not user or not user.get("organization_id"):
        raise HTTPException(status_code=403, detail="Vous n'appartenez à aucune organisation.")
    return user


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


# ─── Facturation par siège (1 $/mois par membre, admin exclu) ───

@router.get("/billing")
async def get_billing(admin: dict = Depends(get_current_org_admin)):
    """État de facturation par palier : membres actifs, forfait recommandé, plan courant, grille."""
    org = await orgs.get_organization(admin["organization_id"])
    active = await orgs.active_member_count(admin["organization_id"])
    recommended = orgs.recommend_plan(active)
    current_plan = (org or {}).get("billing_plan")
    state = orgs.org_plan_state(org or {})
    seats_used = await orgs.sponsored_count(admin["organization_id"])

    # Alerte de dépassement : le plan courant ne couvre plus les membres actifs
    over_cap = False
    if current_plan:
        cur = orgs.get_plan(current_plan)
        if cur and cur.get("max_active") is not None and active > cur["max_active"]:
            over_cap = True

    return {
        "status": "success",
        "data": {
            "active_members": active,
            "recommended_plan": recommended,
            "current_plan": current_plan,
            "billing_interval": (org or {}).get("billing_interval"),
            "billing_status": (org or {}).get("billing_status", "inactive"),
            "has_subscription": bool((org or {}).get("stripe_subscription_id")),
            "over_cap": over_cap,
            "member_gold": state["gold"],
            "sponsored_seats_used": seats_used,
            "sponsored_seats_cap": state["cap"],
            "currency": "CAD",
            "plans": [
                {"key": p["key"], "name": p["name"], "max_active": p["max_active"],
                 "monthly": p["monthly"], "annual": p["annual"], "member_gold": p.get("member_gold"),
                 "tagline": p.get("tagline"), "features": p.get("features", [])}
                for p in orgs.ORG_PLANS
            ],
        },
    }


class BillingCheckoutRequest(BaseModel):
    plan: str
    interval: str = "monthly"


@router.post("/billing/checkout")
async def billing_checkout(req: BillingCheckoutRequest, admin: dict = Depends(get_current_org_admin)):
    """Crée une session Stripe Checkout pour le forfait choisi (mensuel ou annuel)."""
    from api.stripe_service import create_org_plan_checkout
    plan = orgs.get_plan(req.plan)
    if not plan or plan["key"] in ("free", "enterprise"):
        raise HTTPException(status_code=400, detail="Ce forfait n'est pas facturable via Checkout.")
    interval = "annual" if req.interval == "annual" else "monthly"
    amount = plan["annual"] if interval == "annual" else plan["monthly"]
    url = create_org_plan_checkout(
        org_id=admin["organization_id"],
        admin_user_id=admin["id"],
        email=admin.get("email", ""),
        plan=req.plan,
        plan_name=plan["name"],
        amount=amount,
        interval=interval,
        currency="cad",
    )
    if not url:
        raise HTTPException(status_code=500, detail="Facturation indisponible (Stripe non configuré).")
    return {"status": "success", "url": url}


@router.post("/billing/refill")
async def billing_refill(admin: dict = Depends(get_current_org_admin)):
    """Recharge en Gold les membres sponsorisés dont la mensualité est due (idempotent 30 j)."""
    n = await orgs.monthly_org_refill(admin["organization_id"])
    return {"status": "success", "refilled": n}


@router.post("/billing/portal")
async def billing_portal(admin: dict = Depends(get_current_org_admin)):
    """Ouvre le portail Stripe pour gérer l'abonnement de l'organisation."""
    from api.stripe_service import create_customer_portal_session
    org = await orgs.get_organization(admin["organization_id"])
    url = create_customer_portal_session(
        customer_id=(org or {}).get("stripe_customer_id"),
        email=admin.get("email"),
    )
    if not url:
        raise HTTPException(status_code=400, detail="Aucun abonnement à gérer.")
    return {"status": "success", "url": url}


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


# ─── Analytics & suivi individuel ───

@router.get("/analytics")
async def get_analytics(admin: dict = Depends(get_current_org_admin)):
    """Analytics riches pour le dashboard : KPIs, série mensuelle, funnel, top membres."""
    data = await orgs.analytics(admin["organization_id"])
    return {"status": "success", "data": data}


@router.get("/members/{user_id}/detail")
async def get_member_detail(user_id: str, admin: dict = Depends(get_current_org_admin)):
    """Détail complet d'un membre pour le suivi individuel."""
    detail = await orgs.member_detail(admin["organization_id"], user_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Membre introuvable.")
    return {"status": "success", "data": detail}


class MemberRoleRequest(BaseModel):
    member_role: str  # 'member' | 'mentor' | 'advisor'


@router.put("/members/{user_id}/role")
async def set_member_role(user_id: str, req: MemberRoleRequest, admin: dict = Depends(get_current_org_admin)):
    """Promeut un membre en mentor ou conseiller (ou le rétrograde en simple membre)."""
    ok = await orgs.set_member_role(admin["organization_id"], user_id, req.member_role)
    if not ok:
        raise HTTPException(status_code=404, detail="Membre introuvable.")
    return {"status": "success"}


class SponsorRequest(BaseModel):
    sponsored: bool


@router.put("/members/{user_id}/sponsor")
async def sponsor_member(user_id: str, req: SponsorRequest, admin: dict = Depends(get_current_org_admin)):
    """Attribue (ou retire) un siège premium à un membre : débloque son accès complet."""
    result = await orgs.set_sponsorship(admin["organization_id"], user_id, req.sponsored)
    if result["status"] == "error":
        if result.get("message") == "cap_reached":
            raise HTTPException(status_code=403, detail=f"Plafond de sièges premium atteint ({result.get('cap')}). Passez au forfait supérieur.")
        raise HTTPException(status_code=404, detail=result["message"])
    return {"status": "success", "data": result}


@router.get("/mentors")
async def get_mentors(member: dict = Depends(get_current_org_member)):
    """Liste les mentors et conseillers de l'organisation (visible par tous les membres)."""
    db = get_db()
    org_id = member["organization_id"]
    cursor = db.users.find(
        {"organization_id": org_id, "org_member_role": {"$in": ["mentor", "advisor"]}},
        {"_id": 0, "id": 1, "full_name": 1, "email": 1, "org_member_role": 1, "bio": 1, "avatar_url": 1},
    )
    people = await cursor.to_list(length=None)
    mentors = [p for p in people if p.get("org_member_role") == "mentor"]
    advisors = [p for p in people if p.get("org_member_role") == "advisor"]
    return {"status": "success", "data": {"mentors": mentors, "advisors": advisors}}


# ─── Événements ───
class EventRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    date: str  # ISO
    location: Optional[str] = ""
    link: Optional[str] = ""


@router.get("/events")
async def list_events(member: dict = Depends(get_current_org_member)):
    """Événements de l'organisation (ateliers, webinaires…), visibles par tous les membres."""
    db = get_db()
    cursor = db.org_events.find(
        {"organization_id": member["organization_id"]}, {"_id": 0}
    ).sort("date", 1)
    events = await cursor.to_list(length=200)
    # Enrichit chaque événement avec le nombre de participants et l'état du membre courant
    for ev in events:
        attendees = ev.get("attendees", []) or []
        ev["attendees_count"] = len(attendees)
        ev["is_attending"] = member["id"] in attendees
        ev.pop("attendees", None)
    return {"status": "success", "data": events}


@router.post("/events/{event_id}/rsvp")
async def rsvp_event(event_id: str, member: dict = Depends(get_current_org_member)):
    """Le membre s'inscrit / se désinscrit d'un événement (toggle)."""
    db = get_db()
    ev = await db.org_events.find_one({"id": event_id, "organization_id": member["organization_id"]})
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable.")
    attendees = ev.get("attendees", []) or []
    if member["id"] in attendees:
        await db.org_events.update_one({"id": event_id}, {"$pull": {"attendees": member["id"]}})
        attending = False
        count = len(attendees) - 1
    else:
        await db.org_events.update_one({"id": event_id}, {"$addToSet": {"attendees": member["id"]}})
        attending = True
        count = len(attendees) + 1
    return {"status": "success", "is_attending": attending, "attendees_count": max(0, count)}


@router.post("/events")
async def create_event(req: EventRequest, member: dict = Depends(get_current_org_member)):
    """Crée un événement. Réservé aux admins, mentors et conseillers."""
    if member.get("role") != "org_admin" and member.get("org_member_role") not in ("mentor", "advisor"):
        raise HTTPException(status_code=403, detail="Seuls les admins, mentors et conseillers peuvent créer des événements.")
    db = get_db()
    event = {
        "id": str(uuid.uuid4()),
        "organization_id": member["organization_id"],
        "title": req.title.strip(),
        "description": req.description,
        "date": req.date,
        "location": req.location,
        "link": req.link,
        "created_by": member["id"],
        "created_by_name": member.get("full_name") or member.get("email", "").split("@")[0],
        "created_at": datetime.now(timezone.utc),
    }
    await db.org_events.insert_one(event)
    event.pop("_id", None)
    return {"status": "success", "data": event}


@router.delete("/events/{event_id}")
async def delete_event(event_id: str, member: dict = Depends(get_current_org_member)):
    db = get_db()
    q = {"id": event_id, "organization_id": member["organization_id"]}
    if member.get("role") != "org_admin":
        q["created_by"] = member["id"]  # un non-admin ne supprime que ses propres événements
    res = await db.org_events.delete_one(q)
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Événement introuvable ou non autorisé.")
    return {"status": "success"}


# ─── Réseau de l'organisation ───
class NetworkContactRequest(BaseModel):
    name: str
    company: Optional[str] = ""
    role: Optional[str] = ""
    email: Optional[str] = ""
    linkedin: Optional[str] = ""
    notes: Optional[str] = ""
    category: Optional[str] = "partner"  # partner | recruiter | company | mentor | other


@router.get("/network")
async def list_org_network(member: dict = Depends(get_current_org_member)):
    """Carnet de réseau partagé de l'organisation (partenaires, recruteurs, contacts)."""
    db = get_db()
    cursor = db.org_network.find(
        {"organization_id": member["organization_id"]}, {"_id": 0}
    ).sort("created_at", -1)
    contacts = await cursor.to_list(length=500)
    return {"status": "success", "data": contacts}


@router.post("/network")
async def add_org_network(req: NetworkContactRequest, admin: dict = Depends(get_current_org_admin)):
    """Ajoute un contact au réseau de l'organisation."""
    db = get_db()
    valid_cats = {"partner", "recruiter", "company", "mentor", "other"}
    contact = {
        "id": str(uuid.uuid4()),
        "organization_id": admin["organization_id"],
        "name": req.name.strip(),
        "company": req.company,
        "role": req.role,
        "email": req.email,
        "linkedin": req.linkedin,
        "notes": req.notes,
        "category": req.category if req.category in valid_cats else "other",
        "status": "to_contact",
        "last_contact": None,
        "created_at": datetime.now(timezone.utc),
    }
    await db.org_network.insert_one(contact)
    contact.pop("_id", None)
    return {"status": "success", "data": contact}


class NetworkStatusRequest(BaseModel):
    status: str  # to_contact | contacted | responded


@router.put("/network/{contact_id}/status")
async def update_network_status(contact_id: str, req: NetworkStatusRequest, admin: dict = Depends(get_current_org_admin)):
    """Met à jour le statut de relance d'un contact (suivi)."""
    valid = {"to_contact", "contacted", "responded"}
    st = req.status if req.status in valid else "to_contact"
    db = get_db()
    res = await db.org_network.update_one(
        {"id": contact_id, "organization_id": admin["organization_id"]},
        {"$set": {"status": st, "last_contact": datetime.now(timezone.utc) if st != "to_contact" else None}},
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact introuvable.")
    return {"status": "success"}


class NetworkImportRequest(BaseModel):
    contacts: list  # liste d'objets {name, company, role, email, linkedin, notes, category}


@router.post("/network/import")
async def import_network(req: NetworkImportRequest, admin: dict = Depends(get_current_org_admin)):
    """Import en masse de contacts (ex: depuis un CSV). Ignore les doublons nom+email."""
    org_id = admin["organization_id"]
    db = get_db()
    valid_cats = {"partner", "recruiter", "company", "mentor", "other"}

    # Index des contacts existants pour la déduplication
    existing = await db.org_network.find({"organization_id": org_id}, {"_id": 0, "name": 1, "email": 1}).to_list(length=None)
    seen = {((e.get("name") or "").strip().lower(), (e.get("email") or "").strip().lower()) for e in existing}

    docs = []
    for row in req.contacts:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        if not name:
            continue
        email = str(row.get("email", "")).strip()
        key = (name.lower(), email.lower())
        if key in seen:
            continue
        seen.add(key)
        cat = str(row.get("category", "other")).strip().lower()
        docs.append({
            "id": str(uuid.uuid4()),
            "organization_id": org_id,
            "name": name,
            "company": str(row.get("company", "")).strip(),
            "role": str(row.get("role", "")).strip(),
            "email": email,
            "linkedin": str(row.get("linkedin", "")).strip(),
            "notes": str(row.get("notes", "")).strip(),
            "category": cat if cat in valid_cats else "other",
            "status": "to_contact",
            "last_contact": None,
            "created_at": datetime.now(timezone.utc),
        })

    if docs:
        await db.org_network.insert_many(docs)
    return {"status": "success", "imported": len(docs), "skipped": len(req.contacts) - len(docs)}


@router.get("/network/suggestions")
async def network_suggestions(admin: dict = Depends(get_current_org_admin)):
    """Suggère des entreprises à ajouter au réseau, tirées des candidatures des membres."""
    org_id = admin["organization_id"]
    db = get_db()

    member_ids = [u["id"] async for u in db.users.find(
        {"organization_id": org_id, "role": "member"}, {"_id": 0, "id": 1})]
    if not member_ids:
        return {"status": "success", "data": []}

    # Entreprises déjà présentes dans le réseau (pour les exclure)
    existing = await db.org_network.find({"organization_id": org_id}, {"_id": 0, "company": 1}).to_list(length=None)
    known = {(e.get("company") or "").strip().lower() for e in existing if e.get("company")}

    # Agrège les entreprises depuis les candidatures des membres
    pipeline = [
        {"$match": {"user_id": {"$in": member_ids}, "company_name": {"$exists": True, "$ne": ""}}},
        {"$group": {"_id": "$company_name", "applicants": {"$addToSet": "$user_id"}}},
    ]
    rows = await db.applications.aggregate(pipeline).to_list(length=None)
    suggestions = []
    for r in rows:
        company = (r["_id"] or "").strip()
        if not company or company.lower() in known:
            continue
        if company.lower() in ("confidentiel", "anonyme", "entreprise non identifiée"):
            continue
        suggestions.append({"company": company, "applicants": len(r.get("applicants", []))})

    suggestions.sort(key=lambda x: x["applicants"], reverse=True)
    return {"status": "success", "data": suggestions[:12]}


@router.delete("/network/{contact_id}")
async def delete_org_network(contact_id: str, admin: dict = Depends(get_current_org_admin)):
    db = get_db()
    res = await db.org_network.delete_one({"id": contact_id, "organization_id": admin["organization_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact introuvable.")
    return {"status": "success"}


# ─── Communauté (feed de partage entre membres) ───
class CommunityPostRequest(BaseModel):
    type: str = "message"  # 'message' | 'cv' | 'portfolio' | 'offer' | 'interview_result'
    content: str
    title: Optional[str] = ""
    link: Optional[str] = ""


@router.get("/community/members")
async def community_members(member: dict = Depends(get_current_org_member)):
    """Roster des membres de l'organisation pour le panneau latéral (façon Discord)."""
    db = get_db()
    users = await db.users.find(
        {"organization_id": member["organization_id"]},
        {"_id": 0, "id": 1, "full_name": 1, "email": 1, "role": 1, "org_member_role": 1},
    ).to_list(length=None)
    roster = []
    for u in users:
        roster.append({
            "id": u["id"],
            "name": u.get("full_name") or (u.get("email", "").split("@")[0]),
            "role": "org_admin" if u.get("role") == "org_admin" else (u.get("org_member_role") or "member"),
        })
    return {"status": "success", "data": roster}


@router.get("/community/posts")
async def list_community_posts(member: dict = Depends(get_current_org_member)):
    """Fil communautaire : messages et ressources partagées (CV, portfolios, offres, résultats)."""
    db = get_db()
    cursor = db.org_posts.find(
        {"organization_id": member["organization_id"]}, {"_id": 0}
    ).sort("created_at", -1)
    posts = await cursor.to_list(length=200)
    return {"status": "success", "data": posts}


@router.post("/community/posts")
async def create_community_post(req: CommunityPostRequest, member: dict = Depends(get_current_org_member)):
    """Publie un message ou partage une ressource dans la communauté."""
    valid = {"message", "cv", "portfolio", "offer", "interview_result"}
    ptype = req.type if req.type in valid else "message"
    db = get_db()
    post = {
        "id": str(uuid.uuid4()),
        "organization_id": member["organization_id"],
        "type": ptype,
        "title": (req.title or "").strip(),
        "content": req.content.strip(),
        "link": req.link,
        "author_id": member["id"],
        "author_name": member.get("full_name") or member.get("email", "").split("@")[0],
        "author_role": member.get("org_member_role") or ("org_admin" if member.get("role") == "org_admin" else "member"),
        "likes": 0,
        "created_at": datetime.now(timezone.utc),
    }
    await db.org_posts.insert_one(post)
    post.pop("_id", None)
    return {"status": "success", "data": post}


async def _score_cv_ats(text: str) -> int:
    """Score ATS 0-100 : règles objectives + affinage LLM (avec repli sur les règles)."""
    from api.routers.cv import _ats_rule_score
    snippet = (text or "")[:2500]
    rule = _ats_rule_score(snippet)
    try:
        import re as _re, json as _json
        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()
        prompt = (
            "Tu es un expert ATS. Évalue la compatibilité ATS de ce CV (0-100, sévérité réaliste). "
            "Réponds UNIQUEMENT en JSON: {\"score\": <entier>}\n\n---\n" + snippet
        )
        raw = await llm.chat([{"role": "user", "content": prompt}], json_mode=True, model="gemini-2.0-flash", max_tokens=200)
        cleaned = _re.sub(r"```json\s*|```", "", raw or "").strip()
        m = _re.search(r"\{.*\}", cleaned, _re.DOTALL)
        llm_score = int(_json.loads(m.group(0)).get("score", rule)) if m else rule
        llm_score = max(0, min(100, llm_score))
        return max(0, min(100, int(0.45 * rule + 0.55 * llm_score)))
    except Exception as e:
        logger.warning(f"[ORG CV] LLM scoring fallback (rule only): {e}")
        return rule


@router.post("/community/cv")
async def upload_community_cv(
    file: UploadFile = File(...),
    member: dict = Depends(get_current_org_member),
):
    """Upload d'un modèle de CV (PDF) : extrait le texte, calcule le score ATS,
    stocke le fichier dans MongoDB (GridFS, persistant) et publie un post
    consultable/téléchargeable par tous les membres."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 8 Mo).")

    # Extraction du texte
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        logger.warning(f"[ORG CV] Extraction PDF échouée: {e}")
        text = ""

    ats_score = await _score_cv_ats(text)

    # Stockage persistant dans MongoDB via GridFS
    post_id = str(uuid.uuid4())
    db = get_db()
    from motor.motor_asyncio import AsyncIOMotorGridFSBucket
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="org_cv")
    grid_id = await bucket.upload_from_stream(
        file.filename, content,
        metadata={"post_id": post_id, "organization_id": member["organization_id"], "content_type": "application/pdf"},
    )

    post = {
        "id": post_id,
        "organization_id": member["organization_id"],
        "type": "cv",
        "title": file.filename.rsplit(".", 1)[0][:120],
        "content": "",
        "link": "",
        "file_url": f"/api/org/community/cv/{post_id}/file",
        "file_name": file.filename,
        "grid_id": str(grid_id),
        "ats_score": ats_score,
        "author_id": member["id"],
        "author_name": member.get("full_name") or member.get("email", "").split("@")[0],
        "author_role": member.get("org_member_role") or ("org_admin" if member.get("role") == "org_admin" else "member"),
        "likes": 0,
        "comments": [],
        "created_at": datetime.now(timezone.utc),
    }
    await db.org_posts.insert_one(post)
    post.pop("_id", None)
    return {"status": "success", "data": post}


@router.get("/community/cv/{post_id}/file")
async def download_community_cv(post_id: str):
    """Streame le PDF depuis GridFS (URL à UUID indevinable, sert l'aperçu et le téléchargement)."""
    db = get_db()
    post = await db.org_posts.find_one({"id": post_id, "type": "cv"}, {"_id": 0, "grid_id": 1, "file_name": 1})
    if not post or not post.get("grid_id"):
        raise HTTPException(status_code=404, detail="Fichier introuvable.")
    from motor.motor_asyncio import AsyncIOMotorGridFSBucket
    from bson import ObjectId
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="org_cv")
    try:
        stream = await bucket.open_download_stream(ObjectId(post["grid_id"]))
        data = await stream.read()
    except Exception:
        raise HTTPException(status_code=404, detail="Fichier introuvable.")
    safe_name = (post.get("file_name") or "cv.pdf").replace('"', "")
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_name}"', "Cache-Control": "private, max-age=3600"},
    )


@router.post("/community/posts/{post_id}/like")
async def like_community_post(post_id: str, member: dict = Depends(get_current_org_member)):
    db = get_db()
    await db.org_posts.update_one(
        {"id": post_id, "organization_id": member["organization_id"]},
        {"$inc": {"likes": 1}},
    )
    return {"status": "success"}


class CommentRequest(BaseModel):
    content: str


@router.post("/community/posts/{post_id}/comment")
async def comment_community_post(post_id: str, req: CommentRequest, member: dict = Depends(get_current_org_member)):
    """Ajoute un commentaire à une publication."""
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Commentaire vide.")
    db = get_db()
    comment = {
        "id": str(uuid.uuid4()),
        "author_id": member["id"],
        "author_name": member.get("full_name") or member.get("email", "").split("@")[0],
        "content": req.content.strip(),
        "created_at": datetime.now(timezone.utc),
    }
    res = await db.org_posts.update_one(
        {"id": post_id, "organization_id": member["organization_id"]},
        {"$push": {"comments": comment}},
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Publication introuvable.")
    return {"status": "success", "data": comment}


@router.delete("/community/posts/{post_id}")
async def delete_community_post(post_id: str, member: dict = Depends(get_current_org_member)):
    db = get_db()
    q = {"id": post_id, "organization_id": member["organization_id"]}
    if member.get("role") != "org_admin":
        q["author_id"] = member["id"]  # un membre ne supprime que ses propres posts
    post = await db.org_posts.find_one(q, {"_id": 0, "grid_id": 1})
    res = await db.org_posts.delete_one(q)
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Publication introuvable ou non autorisée.")
    # Supprime le fichier GridFS associé (le cas échéant)
    if post and post.get("grid_id"):
        try:
            from motor.motor_asyncio import AsyncIOMotorGridFSBucket
            from bson import ObjectId
            bucket = AsyncIOMotorGridFSBucket(db, bucket_name="org_cv")
            await bucket.delete(ObjectId(post["grid_id"]))
        except Exception as e:
            logger.warning(f"[ORG CV] Suppression fichier GridFS échouée: {e}")
    return {"status": "success"}


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
    return {"status": "success", "data": result.get("organization") or {}}
