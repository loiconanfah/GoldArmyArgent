"""Marketplace de mentorat à la demande (« Uber des mentors »).

Registre ouvert : n'importe quel utilisateur peut devenir mentor.
Mise en relation gratuite (pas de paiement) : un user demande un service à un
mentor, le mentor accepte / refuse / marque terminé, puis le demandeur laisse un avis.
Inclut aussi des événements (ateliers) hébergés par les mentors, avec RSVP.

Collections MongoDB :
- mentor_profiles  : un profil mentor par utilisateur (clé: user_id)
- mentor_requests  : demandes de session
- mentor_reviews   : avis laissés après une session
- mentor_events    : ateliers / événements (RSVP)
"""
import uuid
from datetime import datetime, timezone

from core.database import get_db

# Types de service qu'un mentor peut rendre (libellés traduits côté frontend)
SERVICE_TYPES = [
    "cv_review",        # Revue de CV
    "interview_sim",    # Simulation d'entretien
    "career_advice",    # Conseil carrière
    "salary_nego",      # Négociation salariale
    "reconversion",     # Reconversion
    "networking",       # Mise en réseau
    "other",            # Autre
]

AVAILABILITY = {"available", "busy", "offline"}
REQUEST_STATUSES = {"pending", "accepted", "declined", "completed", "cancelled"}
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
LINK_KEYS = ["linkedin", "website", "portfolio", "calendar", "twitter", "github"]


def _now():
    return datetime.now(timezone.utc).isoformat()


async def _notify(db, user_id, title, message, action_url="/hub-mentors"):
    """Crée une notification in-app (best-effort)."""
    try:
        await db.notifications.insert_one({
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": "info",
            "action_url": action_url,
            "is_read": False,
            "created_at": _now(),
        })
    except Exception:
        pass


# ── Profils mentors ─────────────────────────────────────────────────────────

def _clean_profile(p):
    if not p:
        return None
    p.pop("_id", None)
    p.setdefault("rating_avg", 0)
    p.setdefault("rating_count", 0)
    p.setdefault("sessions_count", 0)
    return p


async def get_mentor_profile(user_id):
    db = get_db()
    return _clean_profile(await db.mentor_profiles.find_one({"user_id": user_id}))


def _clean_links(raw):
    """Ne garde que les liens connus, nettoyés (http(s) forcé)."""
    links = {}
    if not isinstance(raw, dict):
        return links
    for k in LINK_KEYS:
        v = (raw.get(k) or "").strip()[:300]
        if not v:
            continue
        if not v.startswith("http://") and not v.startswith("https://"):
            v = "https://" + v
        links[k] = v
    return links


async def upsert_mentor_profile(user, data):
    """Crée ou met à jour le profil mentor de l'utilisateur courant."""
    db = get_db()
    user_id = user["id"]
    existing = await db.mentor_profiles.find_one({"user_id": user_id})

    availability = data.get("availability") or "available"
    if availability not in AVAILABILITY:
        availability = "available"

    specialties = [s.strip() for s in (data.get("specialties") or []) if s and s.strip()][:8]
    languages = [l.strip() for l in (data.get("languages") or []) if l and l.strip()][:6]
    availability_days = [d for d in (data.get("availability_days") or []) if d in DAYS]

    try:
        experience_years = int(data.get("experience_years") or 0)
    except (TypeError, ValueError):
        experience_years = 0
    experience_years = max(0, min(60, experience_years))

    # Photo : priorité à la valeur fournie, sinon on conserve l'existante, sinon l'avatar du compte
    avatar_url = (data.get("avatar_url") or "").strip()
    if not avatar_url:
        avatar_url = (existing or {}).get("avatar_url") or user.get("avatar_url") or ""

    doc = {
        "user_id": user_id,
        "full_name": user.get("full_name") or (user.get("email", "").split("@")[0]),
        "avatar_url": avatar_url,
        "headline": (data.get("headline") or "").strip()[:120],
        "role": (data.get("role") or "").strip()[:120],
        "company": (data.get("company") or "").strip()[:120],
        "experience_years": experience_years,
        "location": (data.get("location") or "").strip()[:120],
        "timezone": (data.get("timezone") or "").strip()[:60],
        "bio": (data.get("bio") or "").strip()[:1500],
        "specialties": specialties,
        "languages": languages,
        "availability": availability,
        "availability_days": availability_days,
        "availability_note": (data.get("availability_note") or "").strip()[:200],
        "links": _clean_links(data.get("links")),
        "is_active": bool(data.get("is_active", True)),
        "updated_at": _now(),
    }

    if existing:
        await db.mentor_profiles.update_one({"user_id": user_id}, {"$set": doc})
    else:
        doc["id"] = user_id
        doc["rating_avg"] = 0
        doc["rating_count"] = 0
        doc["sessions_count"] = 0
        doc["created_at"] = _now()
        await db.mentor_profiles.insert_one(doc)

    return await get_mentor_profile(user_id)


# ── Photo de profil (GridFS, persistant) ─────────────────────────────────────

async def set_mentor_photo(user, content, filename, content_type):
    """Stocke la photo dans GridFS et met à jour l'avatar du profil mentor."""
    from motor.motor_asyncio import AsyncIOMotorGridFSBucket
    db = get_db()
    user_id = user["id"]
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="mentor_photos")

    # Supprime l'ancienne photo si présente
    existing = await db.mentor_profiles.find_one({"user_id": user_id}, {"photo_grid_id": 1})
    if existing and existing.get("photo_grid_id"):
        try:
            from bson import ObjectId
            await bucket.delete(ObjectId(existing["photo_grid_id"]))
        except Exception:
            pass

    grid_id = await bucket.upload_from_stream(
        filename or "photo", content,
        metadata={"user_id": user_id, "content_type": content_type},
    )
    avatar_url = f"/api/mentors/photo/{user_id}?v={str(grid_id)[-8:]}"

    await db.mentor_profiles.update_one(
        {"user_id": user_id},
        {"$set": {
            "photo_grid_id": str(grid_id),
            "avatar_url": avatar_url,
            "full_name": user.get("full_name") or user.get("email", "").split("@")[0],
            "updated_at": _now(),
        }},
        upsert=True,
    )
    return avatar_url


async def get_mentor_photo(user_id):
    """Retourne (bytes, content_type) de la photo du mentor, ou None."""
    from motor.motor_asyncio import AsyncIOMotorGridFSBucket
    from bson import ObjectId
    db = get_db()
    profile = await db.mentor_profiles.find_one({"user_id": user_id}, {"photo_grid_id": 1})
    if not profile or not profile.get("photo_grid_id"):
        return None
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="mentor_photos")
    try:
        stream = await bucket.open_download_stream(ObjectId(profile["photo_grid_id"]))
        data = await stream.read()
        ctype = (stream.metadata or {}).get("content_type", "image/jpeg")
        return data, ctype
    except Exception:
        return None


async def list_mentors(q=None, specialty=None, exclude_user_id=None):
    """Liste des mentors actifs, triés par note puis nombre de sessions."""
    db = get_db()
    query = {"is_active": True}
    if exclude_user_id:
        query["user_id"] = {"$ne": exclude_user_id}
    if specialty:
        query["specialties"] = specialty
    if q:
        rx = {"$regex": q, "$options": "i"}
        query["$or"] = [{"full_name": rx}, {"headline": rx}, {"bio": rx}, {"specialties": rx}]

    cursor = db.mentor_profiles.find(query, {"_id": 0, "bio": 0})
    mentors = await cursor.to_list(length=200)
    mentors.sort(key=lambda m: (m.get("rating_avg", 0), m.get("sessions_count", 0)), reverse=True)
    return mentors


async def mentor_public(mentor_id):
    """Profil public d'un mentor + ses derniers avis."""
    db = get_db()
    profile = _clean_profile(await db.mentor_profiles.find_one({"user_id": mentor_id}))
    if not profile:
        return None
    reviews = await db.mentor_reviews.find(
        {"mentor_id": mentor_id}, {"_id": 0}
    ).sort("created_at", -1).limit(30).to_list(length=30)
    profile["reviews"] = reviews
    return profile


# ── Demandes de session ─────────────────────────────────────────────────────

async def create_request(requester, mentor_id, data):
    db = get_db()
    if requester["id"] == mentor_id:
        raise ValueError("self_request")
    mentor = await db.mentor_profiles.find_one({"user_id": mentor_id, "is_active": True})
    if not mentor:
        raise ValueError("mentor_not_found")

    service_type = data.get("service_type") or "other"
    if service_type not in SERVICE_TYPES:
        service_type = "other"

    req = {
        "id": str(uuid.uuid4()),
        "mentor_id": mentor_id,
        "mentor_name": mentor.get("full_name", ""),
        "requester_id": requester["id"],
        "requester_name": requester.get("full_name") or requester.get("email", "").split("@")[0],
        "requester_avatar": requester.get("avatar_url") or "",
        "service_type": service_type,
        "message": (data.get("message") or "").strip()[:1500],
        "preferred_slot": (data.get("preferred_slot") or "").strip()[:120],
        "status": "pending",
        "response_message": "",
        "reviewed": False,
        "created_at": _now(),
        "updated_at": _now(),
    }
    await db.mentor_requests.insert_one(req)
    req.pop("_id", None)

    await _notify(
        db, mentor_id,
        "Nouvelle demande de mentorat",
        f"{req['requester_name']} souhaite une session avec vous.",
    )
    return req


async def list_sent(user_id):
    db = get_db()
    rows = await db.mentor_requests.find(
        {"requester_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(length=200)
    return rows


async def list_received(mentor_id):
    db = get_db()
    rows = await db.mentor_requests.find(
        {"mentor_id": mentor_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(length=200)
    return rows


async def respond_request(mentor_id, request_id, action, message=""):
    """Le mentor répond : accept / decline / complete."""
    db = get_db()
    req = await db.mentor_requests.find_one({"id": request_id, "mentor_id": mentor_id})
    if not req:
        raise ValueError("not_found")

    mapping = {"accept": "accepted", "decline": "declined", "complete": "completed"}
    if action not in mapping:
        raise ValueError("bad_action")
    new_status = mapping[action]

    await db.mentor_requests.update_one(
        {"id": request_id},
        {"$set": {"status": new_status, "response_message": (message or "").strip()[:800], "updated_at": _now()}},
    )

    # Incrémente le compteur de sessions quand une session est marquée terminée
    if new_status == "completed":
        await db.mentor_profiles.update_one({"user_id": mentor_id}, {"$inc": {"sessions_count": 1}})

    titles = {
        "accepted": "Demande acceptée",
        "declined": "Demande déclinée",
        "completed": "Session terminée",
    }
    await _notify(
        db, req["requester_id"],
        titles[new_status],
        f"{req['mentor_name']} — {titles[new_status].lower()}.",
    )
    updated = await db.mentor_requests.find_one({"id": request_id}, {"_id": 0})
    return updated


async def cancel_request(user_id, request_id):
    db = get_db()
    req = await db.mentor_requests.find_one({"id": request_id, "requester_id": user_id})
    if not req:
        raise ValueError("not_found")
    if req["status"] not in ("pending", "accepted"):
        raise ValueError("bad_state")
    await db.mentor_requests.update_one(
        {"id": request_id}, {"$set": {"status": "cancelled", "updated_at": _now()}}
    )
    return await db.mentor_requests.find_one({"id": request_id}, {"_id": 0})


async def add_review(reviewer, request_id, rating, comment=""):
    """Le demandeur note le mentor après une session terminée."""
    db = get_db()
    req = await db.mentor_requests.find_one({"id": request_id, "requester_id": reviewer["id"]})
    if not req:
        raise ValueError("not_found")
    if req["status"] != "completed":
        raise ValueError("not_completed")
    if req.get("reviewed"):
        raise ValueError("already_reviewed")

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        raise ValueError("bad_rating")
    rating = max(1, min(5, rating))

    review = {
        "id": str(uuid.uuid4()),
        "mentor_id": req["mentor_id"],
        "request_id": request_id,
        "reviewer_id": reviewer["id"],
        "reviewer_name": reviewer.get("full_name") or reviewer.get("email", "").split("@")[0],
        "rating": rating,
        "comment": (comment or "").strip()[:800],
        "created_at": _now(),
    }
    await db.mentor_reviews.insert_one(review)
    review.pop("_id", None)
    await db.mentor_requests.update_one({"id": request_id}, {"$set": {"reviewed": True}})

    # Recalcule la moyenne du mentor
    agg = await db.mentor_reviews.aggregate([
        {"$match": {"mentor_id": req["mentor_id"]}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}},
    ]).to_list(length=1)
    if agg:
        await db.mentor_profiles.update_one(
            {"user_id": req["mentor_id"]},
            {"$set": {"rating_avg": round(agg[0]["avg"], 1), "rating_count": agg[0]["count"]}},
        )
    await _notify(
        db, req["mentor_id"],
        "Nouvel avis reçu",
        f"{review['reviewer_name']} vous a attribué {rating}/5.",
    )
    return review


# ── Événements (ateliers) ───────────────────────────────────────────────────

def _event_view(ev, user_id):
    ev.pop("_id", None)
    attendees = ev.get("attendees", [])
    ev["attendees_count"] = len(attendees)
    ev["is_attending"] = user_id in attendees
    ev["is_host"] = ev.get("host_id") == user_id
    ev.pop("attendees", None)
    return ev


async def list_events(user_id):
    db = get_db()
    rows = await db.mentor_events.find({}).sort("date", 1).to_list(length=200)
    return [_event_view(ev, user_id) for ev in rows]


async def create_event(host, data):
    db = get_db()
    # Seuls les mentors actifs peuvent créer des ateliers
    profile = await db.mentor_profiles.find_one({"user_id": host["id"], "is_active": True})
    if not profile:
        raise ValueError("not_a_mentor")
    if not (data.get("title") or "").strip() or not data.get("date"):
        raise ValueError("missing_fields")
    ev = {
        "id": str(uuid.uuid4()),
        "host_id": host["id"],
        "host_name": host.get("full_name") or host.get("email", "").split("@")[0],
        "title": data["title"].strip()[:160],
        "description": (data.get("description") or "").strip()[:1000],
        "date": data["date"],
        "location": (data.get("location") or "").strip()[:160],
        "link": (data.get("link") or "").strip()[:400],
        "attendees": [],
        "created_at": _now(),
    }
    await db.mentor_events.insert_one(ev)
    return _event_view(dict(ev), host["id"])


async def rsvp_event(user_id, event_id):
    db = get_db()
    ev = await db.mentor_events.find_one({"id": event_id})
    if not ev:
        raise ValueError("not_found")
    attending = user_id in ev.get("attendees", [])
    op = "$pull" if attending else "$addToSet"
    await db.mentor_events.update_one({"id": event_id}, {op: {"attendees": user_id}})
    ev = await db.mentor_events.find_one({"id": event_id})
    view = _event_view(ev, user_id)
    return view


async def delete_event(user_id, event_id):
    db = get_db()
    res = await db.mentor_events.delete_one({"id": event_id, "host_id": user_id})
    return res.deleted_count > 0
