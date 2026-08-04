"""Routes CRM : gestion des candidatures (Kanban), ajout par lien, statut, relance."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from api.auth import get_current_user
from api.subscription import check_subscription_limit, log_usage
from core.database import get_db

router = APIRouter()


class CRMApplicationRequest(BaseModel):
    job_title: str
    company_name: str
    url: Optional[str] = None
    reference: Optional[str] = None
    status: str = "TO_APPLY"
    notes: Optional[str] = None


class CRMStatusUpdateRequest(BaseModel):
    status: str


class CRMLinkRequest(BaseModel):
    url: str


@router.put("/api/crm/applications/{app_id}/status")
async def update_crm_status(app_id: str, request: CRMStatusUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Met à jour le statut (Drag and Drop) et horodate MongoDB."""
    try:
        db = get_db()
        update_fields = {"status": request.status}

        if request.status == "APPLIED":
            update_fields["applied_at"] = datetime.utcnow()

        await db.applications.update_one(
            {"id": app_id, "user_id": current_user["id"]},
            {"$set": update_fields}
        )

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/crm/applications/{app_id}/followup")
async def generate_followup_email(app_id: str, current_user: dict = Depends(get_current_user)):
    """Génère un email de relance personnalisé et incrémente le compteur MongoDB."""
    try:
        db = get_db()

        app_data = await db.applications.find_one({"id": app_id, "user_id": current_user["id"]})
        if not app_data:
            raise HTTPException(status_code=404, detail="Application not found")

        job_title = app_data.get("job_title", "le poste")
        company = app_data.get("company_name", "l'entreprise")
        notes = app_data.get("notes", "")

        check = await check_subscription_limit(current_user["id"], "follow_up")
        if not check["allowed"]:
            raise HTTPException(status_code=403, detail=check["message"])

        updated = await db.applications.find_one_and_update(
            {"id": app_id, "user_id": current_user["id"]},
            {"$inc": {"follow_up_count": 1}},
            return_document=True
        )
        follow_up_count = updated.get("follow_up_count", 1) if updated else 1

        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()

        prompt = (
            "Tu rédiges un email de relance professionnel COMPLET en français. "
            "Le mail doit OBLIGATOIREMENT contenir les 4 parties suivantes, dans l'ordre :\n"
            "1) Objet: [un sujet clair]\n"
            "2) Formule d'appel (ex: Bonjour, ou Bonjour M. Dupont,)\n"
            "3) Corps du mail : 3 à 5 phrases complètes. Rappeler la candidature (poste et entreprise), "
            "réaffirmer ton intérêt, demander poliment où en est le processus de recrutement.\n"
            "4) Formule de politesse (Cordialement, ou Bien à vous,) puis une ligne type [Prénom].\n\n"
            f"Contexte : candidature pour {job_title} chez {company}. "
            f"Notes : {notes if notes else 'Aucune.'} "
            f"Relance n°{follow_up_count}. Si >1, ton un peu plus direct.\n\n"
            "Réponds UNIQUEMENT par le texte de l'email complet, rien d'autre."
        )
        messages = [{"role": "user", "content": prompt}]
        email_text = await llm.chat(
            messages,
            model="gemini-2.0-flash",
            max_tokens=2048,
            temperature=0.7,
            timeout=120,
        )
        if not email_text or not email_text.strip():
            raise HTTPException(status_code=503, detail="Réponse vide du modèle. Réessayez.")

        await log_usage(current_user["id"], "follow_up")

        return {
            "status": "success",
            "email": email_text,
            "followUpCount": follow_up_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Followup generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/crm/link")
async def add_crm_from_link(request: CRMLinkRequest, current_user: dict = Depends(get_current_user)):
    """Scrape une URL d'offre, extrait poste/entreprise via Gemini et l'ajoute au CRM."""
    import uuid
    import httpx
    try:
        logger.info(f"[CRM] Scraping de l'URL: {request.url}")

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            resp = await client.get(request.url, headers=headers)
            resp.raise_for_status()
            html_content = resp.text

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        page_title = soup.title.string if soup.title else ""
        og_title_tag = soup.find("meta", attrs={"property": "og:title"})
        og_title = og_title_tag["content"] if og_title_tag else ""
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"] if meta_desc_tag else ""

        for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            script.decompose()
        text_content = soup.get_text(separator=" ", strip=True)
        text_snippet = text_content[:15000]

        from llm.unified_client import UnifiedLLMClient
        import json
        llm = UnifiedLLMClient()
        prompt = f"""Tu es un assistant expert en recrutement.
Voici les métadonnées et le texte extrait d'une page web d'offre d'emploi :

[METADONNEES SEO]
Titre de la page : {page_title}
OG Title : {og_title}
Description : {meta_desc}

[CONTENU DU CORPS]
{text_snippet}

Renvoie UNIQUEMENT un JSON avec les clés :
- "job_title" (le titre explicite du poste, ex: "Développeur Full Stack")
- "company_name" (le nom de l'entreprise qui recrute)
- "job_summary" (un résumé concis de l'offre en 2-3 phrases max, incluant les technos/mots-clés principaux ou les missions clés)
Ne rajoute PAS de balises markdown comme ```json, renvoie uniquement l'objet JSON brut."""

        logger.info("[CRM] Appel LLM pour extraction d'offre...")
        result_text = await llm.chat([{"role": "user", "content": prompt}], json_mode=True)

        extracted = {}
        try:
            import re
            cleaned_result = re.sub(r'```json\s*', '', result_text, flags=re.IGNORECASE)
            cleaned_result = re.sub(r'```\s*', '', cleaned_result).strip()

            json_match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group(0))
            else:
                extracted = json.loads(cleaned_result)
        except Exception as parse_error:
            logger.error(f"[CRM] Erreur parsing JSON: {parse_error} - Raw: {result_text}")
            extracted = {}

        job_title = str(extracted.get("job_title", "")).strip()
        company_name = str(extracted.get("company_name", "")).strip()
        job_summary = str(extracted.get("job_summary", "")).strip()

        if not job_title or job_title.lower() == "none" or job_title.lower() == "inconnu":
            job_title = "Poste non identifié"
        if not company_name or company_name.lower() == "none" or company_name.lower() == "inconnu":
            company_name = "Entreprise non identifiée"
        if not job_summary:
            job_summary = "Ajouté via le lien externe (aucune description extraite)."

        logger.info(f"[CRM] Link Extrait: '{job_title}' chez '{company_name}'")

        db = get_db()
        app_id = str(uuid.uuid4())

        new_app = {
            "id": app_id,
            "user_id": current_user["id"],
            "job_title": job_title,
            "company_name": company_name,
            "url": request.url,
            "reference": "",
            "status": "APPLIED",
            "notes": job_summary,
            "created_at": datetime.utcnow()
        }

        await db.applications.insert_one(new_app)
        new_app["_id"] = str(new_app["_id"])

        return {"status": "success", "data": new_app}

    except httpx.HTTPError as e:
        logger.error(f"[CRM] Erreur HTTP lors du scraping : {e}")
        raise HTTPException(status_code=400, detail="Impossible d'accéder à ce lien. Le site bloque l'accès aux requêtes externes.")
    except Exception as e:
        logger.error(f"[CRM] Erreur traitement lien CRM: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du lien: {str(e)}")


@router.get("/api/crm")
async def fetch_crm(current_user: dict = Depends(get_current_user)):
    """Alias pour les candidatures existantes via MongoDB."""
    try:
        db = get_db()
        cursor = db.applications.find({"user_id": current_user["id"]}).sort("created_at", -1)
        apps = await cursor.to_list(length=None)

        for app in apps:
            app["_id"] = str(app["_id"])

        return {"status": "success", "data": apps}
    except Exception as e:
        logger.error(f"Error fetching CRM: {e}")
        return {"status": "error", "message": "Failed to fetch CRM data"}


@router.post("/api/crm")
async def create_crm_entry(request: CRMApplicationRequest, current_user: dict = Depends(get_current_user)):
    """Crée une entrée dans le CRM MongoDB."""
    import uuid
    try:
        db = get_db()
        app_id = str(uuid.uuid4())

        new_app = {
            "id": app_id,
            "user_id": current_user["id"],
            "job_title": request.job_title,
            "company_name": request.company_name,
            "url": request.url,
            "reference": getattr(request, 'reference', ''),
            "status": request.status,
            "notes": getattr(request, 'notes', ''),
            "created_at": datetime.utcnow()
        }

        await db.applications.insert_one(new_app)

        if request.status == "TO_APPLY":
            from core.orchestrator import orchestrator
            await orchestrator.dispatch_event("sniper_to_apply", {
                "companyName": request.company_name,
                "jobTitle": request.job_title,
                "app_id": app_id,
                "user_id": current_user["id"]
            })

        return {"status": "success", "data": {"id": app_id}}
    except Exception as e:
        logger.error(f"Error creating CRM entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create CRM entry")


@router.put("/api/crm/{item_id}")
async def update_crm_entry(item_id: str, updates: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Met à jour une entrée CRM MongoDB."""
    try:
        db = get_db()

        allowed_fields = ["status", "notes", "job_title", "company_name"]
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_fields:
            return {"status": "success", "message": "No changes"}

        await db.applications.update_one(
            {"id": item_id, "user_id": current_user["id"]},
            {"$set": update_fields}
        )

        if "status" in update_fields:
            new_status = update_fields["status"]
            app_data = await db.applications.find_one({"id": item_id, "user_id": current_user["id"]})
            if app_data:
                from core.orchestrator import orchestrator
                payload = {
                    "companyName": app_data.get("company_name", ""),
                    "jobTitle": app_data.get("job_title", ""),
                    "app_id": item_id,
                    "user_id": current_user["id"]
                }
                if new_status == "TO_APPLY":
                    await orchestrator.dispatch_event("sniper_to_apply", payload)
                elif new_status == "INTERVIEW":
                    await orchestrator.dispatch_event("interview_scheduled", payload)
                elif new_status == "REJECTED":
                    await orchestrator.dispatch_event("card_rejected", payload)

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error updating CRM entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to update CRM entry")


@router.delete("/api/crm/{item_id}")
async def delete_crm_entry(item_id: str, current_user: dict = Depends(get_current_user)):
    """Supprime une entrée CRM MongoDB."""
    try:
        db = get_db()
        await db.applications.delete_one({"id": item_id, "user_id": current_user["id"]})
        return {"status": "success", "message": "Deleted"}
    except Exception as e:
        logger.error(f"Erreur delete CRM: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
