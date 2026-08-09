"""Routes du marketplace de mentorat à la demande (« Uber des mentors »).

Ouvert à tout utilisateur authentifié :
- Découvrir des mentors et demander une session (mise en relation gratuite)
- Devenir mentor et gérer ses demandes reçues
- Événements / ateliers avec RSVP
- Avis après session
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from api.auth import get_current_user
from core.database import get_db
from core import mentors as m

router = APIRouter(prefix="/api/mentors", tags=["Mentors"])


async def _full_user(current_user: dict) -> dict:
    """Recharge le document utilisateur complet (id, full_name, avatar_url, email)."""
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return user


# ── Schémas ──────────────────────────────────────────────────────────────────

class MentorProfileRequest(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    availability: Optional[str] = None
    is_active: Optional[bool] = True


class SessionRequest(BaseModel):
    service_type: str
    message: Optional[str] = None
    preferred_slot: Optional[str] = None


class RespondRequest(BaseModel):
    action: str  # accept | decline | complete
    message: Optional[str] = None


class ReviewRequest(BaseModel):
    rating: int
    comment: Optional[str] = None


class EventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    date: str
    location: Optional[str] = None
    link: Optional[str] = None


# ── Découverte ───────────────────────────────────────────────────────────────

@router.get("")
async def list_mentors(q: Optional[str] = None, specialty: Optional[str] = None,
                       current_user: dict = Depends(get_current_user)):
    data = await m.list_mentors(q=q, specialty=specialty, exclude_user_id=current_user["id"])
    return {"status": "success", "data": data}


@router.get("/meta")
async def mentors_meta():
    """Constantes utiles au frontend (types de service)."""
    return {"status": "success", "data": {"service_types": m.SERVICE_TYPES}}


@router.get("/me")
async def get_my_mentor_profile(current_user: dict = Depends(get_current_user)):
    profile = await m.get_mentor_profile(current_user["id"])
    return {"status": "success", "data": profile}


@router.put("/me")
async def update_my_mentor_profile(req: MentorProfileRequest, current_user: dict = Depends(get_current_user)):
    user = await _full_user(current_user)
    profile = await m.upsert_mentor_profile(user, req.dict())
    return {"status": "success", "data": profile}


@router.get("/{mentor_id}")
async def get_mentor(mentor_id: str, current_user: dict = Depends(get_current_user)):
    profile = await m.mentor_public(mentor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Mentor introuvable.")
    return {"status": "success", "data": profile}


# ── Demandes (côté demandeur) ────────────────────────────────────────────────

@router.post("/{mentor_id}/request")
async def request_session(mentor_id: str, req: SessionRequest, current_user: dict = Depends(get_current_user)):
    user = await _full_user(current_user)
    try:
        created = await m.create_request(user, mentor_id, req.dict())
    except ValueError as e:
        msgs = {"self_request": "Vous ne pouvez pas vous demander à vous-même.",
                "mentor_not_found": "Mentor indisponible."}
        raise HTTPException(status_code=400, detail=msgs.get(str(e), "Demande impossible."))
    return {"status": "success", "data": created}


@router.get("/requests/sent")
async def sent_requests(current_user: dict = Depends(get_current_user)):
    return {"status": "success", "data": await m.list_sent(current_user["id"])}


@router.get("/requests/received")
async def received_requests(current_user: dict = Depends(get_current_user)):
    return {"status": "success", "data": await m.list_received(current_user["id"])}


@router.post("/requests/{request_id}/respond")
async def respond(request_id: str, req: RespondRequest, current_user: dict = Depends(get_current_user)):
    try:
        updated = await m.respond_request(current_user["id"], request_id, req.action, req.message or "")
    except ValueError as e:
        msgs = {"not_found": "Demande introuvable.", "bad_action": "Action invalide."}
        raise HTTPException(status_code=400, detail=msgs.get(str(e), "Action impossible."))
    return {"status": "success", "data": updated}


@router.post("/requests/{request_id}/cancel")
async def cancel(request_id: str, current_user: dict = Depends(get_current_user)):
    try:
        updated = await m.cancel_request(current_user["id"], request_id)
    except ValueError as e:
        msgs = {"not_found": "Demande introuvable.", "bad_state": "Cette demande ne peut plus être annulée."}
        raise HTTPException(status_code=400, detail=msgs.get(str(e), "Annulation impossible."))
    return {"status": "success", "data": updated}


@router.post("/requests/{request_id}/review")
async def review(request_id: str, req: ReviewRequest, current_user: dict = Depends(get_current_user)):
    user = await _full_user(current_user)
    try:
        created = await m.add_review(user, request_id, req.rating, req.comment or "")
    except ValueError as e:
        msgs = {"not_found": "Demande introuvable.", "not_completed": "La session n'est pas terminée.",
                "already_reviewed": "Vous avez déjà laissé un avis.", "bad_rating": "Note invalide."}
        raise HTTPException(status_code=400, detail=msgs.get(str(e), "Avis impossible."))
    return {"status": "success", "data": created}


# ── Événements ───────────────────────────────────────────────────────────────

@router.get("/events/list")
async def events(current_user: dict = Depends(get_current_user)):
    return {"status": "success", "data": await m.list_events(current_user["id"])}


@router.post("/events")
async def new_event(req: EventRequest, current_user: dict = Depends(get_current_user)):
    user = await _full_user(current_user)
    try:
        created = await m.create_event(user, req.dict())
    except ValueError as e:
        msgs = {"not_a_mentor": "Seuls les mentors peuvent créer un atelier.",
                "missing_fields": "Titre et date requis."}
        raise HTTPException(status_code=400, detail=msgs.get(str(e), "Création impossible."))
    return {"status": "success", "data": created}


@router.post("/events/{event_id}/rsvp")
async def rsvp(event_id: str, current_user: dict = Depends(get_current_user)):
    try:
        view = await m.rsvp_event(current_user["id"], event_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Événement introuvable.")
    return {"status": "success", "data": view, "is_attending": view["is_attending"],
            "attendees_count": view["attendees_count"]}


@router.delete("/events/{event_id}")
async def remove_event(event_id: str, current_user: dict = Depends(get_current_user)):
    ok = await m.delete_event(current_user["id"], event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Événement introuvable.")
    return {"status": "success"}
