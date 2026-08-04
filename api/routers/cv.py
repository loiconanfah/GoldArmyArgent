"""Routes CV : extraction PDF, génération PDF/Word ATS, adaptation à une offre, audits publics."""
import io
import json
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from api.auth import get_current_user
from api.subscription import check_subscription_limit, log_usage

router = APIRouter()


class CVAdaptRequest(BaseModel):
    job_title: str
    job_description: str
    cv_text: str


class CvRewriteRequest(BaseModel):
    cv_json: str
    filename: Optional[str] = "CV_ATS_Optimise"
    theme_id: Optional[str] = "midnight"


class PublicInterviewRequest(BaseModel):
    job_title: str
    user_response: Optional[str] = None
    context: Optional[str] = None


@router.post("/api/parse-pdf")
async def parse_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Reçoit un CV PDF, extrait le texte via PyMuPDF (fitz) et le retourne."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    try:
        import fitz  # PyMuPDF

        content = await file.read()
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()

        return {"status": "success", "text": text.strip()}
    except ImportError:
        raise HTTPException(status_code=500, detail="PyMuPDF (fitz) n'est pas installé sur le serveur.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du PDF: {str(e)}")


@router.post("/api/generate-cv-pdf")
async def generate_cv_pdf_endpoint(raw_request: Request):
    """Reçoit cv_json + filename + template_id et génère un PDF via Playwright."""
    try:
        import logging
        body = await raw_request.json()
        cv_data_input = body.get("cv_json")
        filename = (body.get("filename") or "CV_ATS_Optimise").replace(" ", "_").strip()
        template_id = (body.get("template_id") or body.get("templateId") or "goldarmy").strip().lower()

        if cv_data_input is None:
            raise HTTPException(status_code=400, detail="cv_json manquant")

        if isinstance(cv_data_input, str):
            cv_data_input = cv_data_input.strip()
            if cv_data_input.startswith("```json"):
                cv_data_input = cv_data_input[7:].strip()
            if cv_data_input.endswith("```"):
                cv_data_input = cv_data_input[:-3].strip()

            try:
                cv_data = json.loads(cv_data_input)
            except json.JSONDecodeError as e:
                import re
                logging.warning(f"Initial JSON decode failed: {e}. Attempting regex extraction.")
                match = re.search(r'\{.*\}', cv_data_input, re.DOTALL)
                if match:
                    try:
                        cv_data = json.loads(match.group(0))
                    except json.JSONDecodeError as e2:
                        logging.error(f"Regex JSON decode failed: {e2}")
                        raise e2
                else:
                    raise e
        elif isinstance(cv_data_input, dict):
            cv_data = cv_data_input
        else:
            cv_data = {}

        from core.cv_generator import normalize_cv_json
        cv_data = normalize_cv_json(cv_data)

        from core.cv_html_templates import build_html, TEMPLATES as HTML_TEMPLATES
        if template_id not in HTML_TEMPLATES:
            template_id = "goldarmy"
        logging.info(f"[PDF] Generating '{template_id}' via Playwright")
        html_content = build_html(template_id, cv_data)

        try:
            def _generate_pdf_sync(html: str) -> bytes:
                import logging
                from playwright.sync_api import sync_playwright
                try:
                    with sync_playwright() as pw:
                        browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
                        page = browser.new_page()
                        page.set_viewport_size({"width": 794, "height": 1123})
                        page.set_content(html, wait_until="load", timeout=20000)
                        content_height = page.evaluate("document.documentElement.scrollHeight")
                        A4_HEIGHT_PX = 1123
                        MAX_PAGES = 2
                        max_height = A4_HEIGHT_PX * MAX_PAGES
                        if content_height > max_height:
                            scale = max(0.1, min(1.0, max_height / content_height))
                        else:
                            scale = 1.0
                        logging.info(f"[PDF] content_height={content_height}px, scale={scale:.3f}")
                        p_bytes = page.pdf(
                            format="A4", print_background=True,
                            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                            scale=scale
                        )
                        browser.close()
                        return p_bytes
                except Exception as e:
                    logging.error(f"[Playwright] Critical PDF generation error: {str(e)}")
                    raise e

            pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, html_content)
        except Exception as pw_err:
            logging.error(f"Playwright PDF error: {pw_err}")
            raise HTTPException(status_code=500, detail=f"Erreur Playwright: {pw_err}")

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-CV-Template": template_id,
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON CV invalide: {str(e)}")
    except Exception as e:
        import logging
        logging.exception("Erreur generation PDF")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")


@router.post("/api/generate-cv-pdf-html")
async def generate_cv_pdf_from_html(raw_request: Request):
    """Convertit un HTML pré-rendu par le frontend en PDF via Playwright."""
    import logging
    try:
        body = await raw_request.json()
        html_content = body.get("html", "")
        filename = (body.get("filename") or "CV_ATS_Optimise").replace(" ", "_").strip()
        if not html_content:
            raise HTTPException(status_code=400, detail="html manquant dans la requête")

        def _generate_pdf_sync(html: str) -> bytes:
            import logging
            from playwright.sync_api import sync_playwright
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
                    page = browser.new_page()
                    page.set_viewport_size({"width": 794, "height": 1123})
                    page.set_content(html, wait_until="load", timeout=20000)
                    content_height = page.evaluate("document.documentElement.scrollHeight")
                    A4_HEIGHT_PX = 1123
                    MAX_PAGES = 2
                    max_height = A4_HEIGHT_PX * MAX_PAGES
                    if content_height > max_height:
                        scale = max(0.1, min(1.0, max_height / content_height))
                    else:
                        scale = 1.0
                    logging.info(f"[PDF-HTML] content_height={content_height}px, scale={scale:.3f}")
                    p_bytes = page.pdf(
                        format="A4", print_background=True,
                        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                        scale=scale
                    )
                    browser.close()
                    return p_bytes
            except Exception as e:
                logging.error(f"[Playwright-HTML] Critical PDF generation error: {str(e)}")
                raise e

        pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, html_content)

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
    except Exception as e:
        logging.exception("Erreur generation PDF depuis HTML")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")


@router.post("/api/generate-cv-word")
async def generate_cv_word_endpoint(raw_request: Request):
    """Accepte le cv_json et génère un document Word (.docx) ATS-friendly."""
    import logging
    try:
        body = await raw_request.json()
        cv_data = body.get("cv_json")
        filename = (body.get("filename") or "CV_Optimise").replace(" ", "_").strip()
        theme_id = body.get("theme_id", "goldarmy")

        if not cv_data:
            raise HTTPException(status_code=400, detail="cv_json manquant dans la requête")

        from core.cv_word_generator import generate_cv_word

        docx_bytes = await asyncio.to_thread(generate_cv_word, cv_data, theme_id)

        if not filename.endswith(".docx"):
            filename += ".docx"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }

        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except Exception as e:
        logging.exception("Erreur generation Word")
        raise HTTPException(status_code=500, detail=f"Erreur génération Word: {str(e)}")


@router.post("/api/adapt-cv")
async def adapt_cv_endpoint(request: CVAdaptRequest, current_user: dict = Depends(get_current_user)):
    """Adapter un CV spécifiquement pour une offre d'emploi via Gemini."""
    try:
        if not request.cv_text or len(request.cv_text) < 50:
            raise HTTPException(status_code=400, detail="Le texte du CV est introuvable ou trop court. Veuillez uploader un CV d'abord.")

        check = await check_subscription_limit(current_user["id"], "cv_adaptation")
        if not check["allowed"]:
            raise HTTPException(status_code=403, detail=check["message"])

        from agents.cv_adapter import CVAdapterAgent
        adapter = CVAdapterAgent()
        await adapter.initialize()

        result = await adapter.adapt(
            job_title=request.job_title,
            job_desc=request.job_description,
            cv_text=request.cv_text
        )

        await log_usage(current_user["id"], "cv_adaptation")
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in adapt_cv_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _ats_rule_score(text: str) -> int:
    """Score ATS basé sur des règles (0-100) : sections reconnues, bullets, longueur, contact."""
    if not text or len(text.strip()) < 50:
        return 25
    t = text.lower().strip()
    score = 0
    sections = [
        "expérience", "experience", "formation", "education", "études",
        "compétences", "competences", "skills", "compétence",
        "résumé", "resume", "summary", "profil", "objectif"
    ]
    found = sum(1 for s in sections if s in t)
    score += min(35, found * 8)
    bullet_count = t.count("\n•") + t.count("\n-") + t.count("\n*") + t.count("•")
    score += min(25, bullet_count * 3)
    if 200 <= len(text) <= 2500:
        score += 20
    elif 100 <= len(text) < 200 or 2500 < len(text) <= 4000:
        score += 12
    elif len(text) > 4000:
        score += 8
    if "@" in text or "email" in t:
        score += 10
    if any(c.isdigit() for c in text) and ("tél" in t or "phone" in t or "06" in text or "07" in text):
        score += 10
    return min(100, score)


@router.post("/api/public/mini-audit")
async def public_mini_audit(file: UploadFile = File(...)):
    """Scanne la 1ère page du CV, calcule un score ATS (règles + LLM) et renvoie score + défauts."""
    try:
        import fitz  # PyMuPDF
        import re

        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            raise HTTPException(status_code=400, detail="PDF vide.")
        first_page_text = doc[0].get_text()
        doc.close()

        text_snippet = first_page_text[:2500]
        rule_score = _ats_rule_score(text_snippet)

        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()

        prompt = f"""Tu es un expert ATS (Applicant Tracking System). Évalue la compatibilité ATS de ce CV (1ère page).
Texte extrait :
---
{text_snippet}
---

Réponds UNIQUEMENT en JSON valide avec 2 clés (pas de markdown) :
- "score": entier 0-100 (sévérité réaliste : 50-70 = moyen, >80 = très bon pour ATS).
- "flaws": tableau de 5 à 7 objets avec "flaw" (critique courte) et "correction" (action courte). Points bloquants ATS : structure, mots-clés, chiffres, bullet points.
"""
        result = await llm.chat(
            [{"role": "user", "content": prompt}],
            json_mode=True,
            model="gemini-2.0-flash",
            max_tokens=1024,
        )

        cleaned = re.sub(r"```json\s*", "", result, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        raw = json.loads(match.group(0)) if match else json.loads(cleaned)
        llm_score = max(0, min(100, int(raw.get("score", 50))))
        flaws = raw.get("flaws") or []

        final_score = int(0.45 * rule_score + 0.55 * llm_score)
        final_score = max(0, min(100, final_score))

        return {
            "status": "success",
            "score": final_score,
            "flaws": flaws[:7] if isinstance(flaws, list) else [
                {"flaw": "Structure difficile à lire pour un ATS.", "correction": "Simplifiez le design et utilisez des sections claires."},
                {"flaw": "Manque de mots-clés.", "correction": "Ajoutez une section Compétences avec termes métier."},
            ],
        }
    except Exception as e:
        logger.error(f"[Public API] Erreur Mini-Audit: {e}")
        return {
            "status": "success",
            "score": 42,
            "flaws": [
                {"flaw": "Le format du fichier empêche l'analyse.", "correction": "Uploadez un PDF avec texte sélectionnable (Word, Canva)."},
                {"flaw": "Texte potentiellement en image.", "correction": "Assurez-vous que le texte du PDF peut être copié."},
            ],
        }


@router.post("/api/public/interview")
async def public_interview(req: PublicInterviewRequest):
    """Simulation d'entretien vocal express de la landing page."""
    try:
        from llm.unified_client import UnifiedLLMClient
        llm = UnifiedLLMClient()

        if not req.user_response:
            prompt = f"""Tu es un recruteur expert. Tu fais passer un entretien express (1 seule question) pour le poste de : {req.job_title}.
Pose UNE question piège, difficile ou très technique, que ce candidat rencontrerait dans la vraie vie.
Ne dis pas bonjour la réponse doit être juste la question elle-même pour qu'elle soit lue par une synthèse vocale (ton sec et professionnel)."""
        else:
            prompt = f"""Tu es un recruteur expert. Tu as posé cette question pour un poste de {req.job_title} :
Question : {req.context}

Le candidat a répondu (transcription orale) :
{req.user_response}

Fais-lui un feedback cash en 2 phrases MAXIMUM ! (soit positif, soit indique pourquoi c'est mauvais).
Ne sois pas poli, sois un coach stricte. Cette réponse sera lue par synthèse vocale."""

        response_text = await llm.chat([{"role": "user", "content": prompt}], max_tokens=200)

        return {
            "status": "success",
            "text": response_text.replace("*", "").replace("\"", "").strip()
        }

    except Exception as e:
        logger.error(f"[Public API] Erreur Interview: {e}")
        raise HTTPException(status_code=500, detail="Erreur génération.")
