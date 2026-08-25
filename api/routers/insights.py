"""Insights & Newsletter — cartes du dashboard.

- Articles d'actualité emploi : générés par l'IA (contenu ORIGINAL, jamais de faux
  lien externe inventé), rafraîchis paresseusement tous les 2 jours (pas de cron).
- Newsletter : capture d'e-mails.
"""
import json
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from loguru import logger

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

from api.auth import get_current_user
from core.database import get_db

router = APIRouter(prefix="/api/insights", tags=["Insights"])

REFRESH_DAYS = 2
BATCH_SIZE = 4


async def _generate_articles() -> List[Dict[str, Any]]:
    """Demande à l'IA quelques brèves d'actualité/tendances sur le marché de l'emploi.
    Contenu ORIGINAL et générique (pas de fausse source, pas d'URL inventée)."""
    prompt = (
        "Rédige 4 brèves d'actualité sur le marché de l'emploi et la recherche d'emploi "
        "(tendances IA & recrutement, compétences recherchées, marché caché, ATS, télétravail, "
        "négociation salariale…). Chaque brève : un titre court et accrocheur, un résumé de 2 phrases "
        "actionnable, et une catégorie. Contenu original et factuel au niveau général — n'invente NI "
        "chiffre précis NI source ni URL. Réponds UNIQUEMENT en JSON : "
        '{"articles":[{"title":"…","summary":"…","category":"…"}]}'
    )
    try:
        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()
        raw = await llm.chat(
            [{"role": "user", "content": prompt}],
            json_mode=True, model="gemini-2.0-flash", max_tokens=1200,
        )
        raw = (raw or "").replace("```json", "").replace("```", "").strip()
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(m.group(0)) if m else json.loads(raw)
        out = []
        for a in (data.get("articles") or [])[:BATCH_SIZE]:
            if isinstance(a, dict) and a.get("title") and a.get("summary"):
                out.append({
                    "title": str(a["title"]).strip(),
                    "summary": str(a["summary"]).strip(),
                    "category": str(a.get("category") or "Emploi").strip(),
                })
        return out
    except Exception as e:
        logger.warning(f"[insights] génération articles échouée: {e}")
        return []


@router.get("/articles")
async def get_articles(current_user: dict = Depends(get_current_user)):
    """Retourne les dernières brèves. Régénère si le dernier lot a plus de 2 jours."""
    db = get_db()
    now = datetime.now(timezone.utc)
    try:
        last = await db.insights_articles.find_one(sort=[("created_at", -1)])
        due = True
        if last and last.get("created_at"):
            ts = last["created_at"]
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            due = (now - ts) >= timedelta(days=REFRESH_DAYS)

        if due:
            fresh = await _generate_articles()
            if fresh:
                docs = [{**a, "created_at": now, "batch": now.isoformat()} for a in fresh]
                await db.insights_articles.insert_many(docs)

        cursor = db.insights_articles.find({}, {"_id": 0}).sort("created_at", -1).limit(6)
        articles = await cursor.to_list(length=6)
        for a in articles:
            if isinstance(a.get("created_at"), datetime):
                a["created_at"] = a["created_at"].isoformat()
        return {"status": "success", "data": {"articles": articles}}
    except Exception as e:
        logger.error(f"[insights] get_articles: {e}")
        return {"status": "success", "data": {"articles": []}}


class NewsletterRequest(BaseModel):
    email: str


@router.post("/newsletter")
async def subscribe_newsletter(req: NewsletterRequest, current_user: dict = Depends(get_current_user)):
    """Inscrit un e-mail à la newsletter (idempotent)."""
    if not _EMAIL_RE.match((req.email or "").strip()):
        raise HTTPException(status_code=400, detail="Adresse e-mail invalide.")
    db = get_db()
    user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
    try:
        await db.newsletter_subscribers.update_one(
            {"email": req.email.lower()},
            {"$set": {"email": req.email.lower(), "user_id": user_id, "updated_at": datetime.now(timezone.utc)},
             "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        return {"status": "success", "message": "Inscription confirmée."}
    except Exception as e:
        logger.error(f"[insights] newsletter: {e}")
        raise HTTPException(status_code=500, detail="Inscription impossible pour le moment.")
