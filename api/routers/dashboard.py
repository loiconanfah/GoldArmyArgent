"""Routes tableau de bord : statistiques KPI, téléchargement et rendu du portfolio."""
import io
import zipfile
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from loguru import logger

from api.auth import get_current_user
from core.database import get_db

router = APIRouter()


@router.get("/api/portfolio/download-zip")
async def download_portfolio_zip(current_user: dict = Depends(get_current_user)):
    """Convertit le portfolio stocké en base de données en archive ZIP."""
    db = get_db()
    user = await db.users.find_one({"id": current_user["id"]}, {"last_portfolio": 1, "_id": 0})

    if not user or "last_portfolio" not in user:
        raise HTTPException(status_code=404, detail="Aucun portfolio trouvé. Générez-en un d'abord !")

    project = user["last_portfolio"]
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("index.html", project.get("html", ""))
        zip_file.writestr("style.css", project.get("css", "/* Extra CSS */"))
        zip_file.writestr("script.js", project.get("js", "// Extra JS"))

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=goldarmy_portfolio.zip"}
    )


@router.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Récupère les statistiques réelles pour le Dashboard depuis MongoDB Atlas."""
    try:
        db = get_db()

        applied_count = await db.applications.count_documents({
            "status": {"$ne": "TO_APPLY"},
            "user_id": current_user["id"]
        })

        interview_count = await db.applications.count_documents({
            "status": "INTERVIEW",
            "user_id": current_user["id"]
        })

        network_count = await db.contacts.count_documents({
            "$or": [
                {"user_id": current_user["id"]},
                {"user_id": "system_user"}
            ]
        })

        cv_analyzed = await db.applications.count_documents({
            "user_id": current_user["id"]
        })

        pipeline = [
            {"$match": {
                "user_id": current_user["id"],
                "created_at": {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$created_at"}}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]

        monthly_raw = await db.applications.aggregate(pipeline).to_list(length=None)
        monthly_dict = {row["_id"]: row["count"] for row in monthly_raw if row.get("_id")}

        import datetime
        from dateutil.relativedelta import relativedelta

        now = datetime.datetime.now()
        chart_data = []
        months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]

        max_val = max(monthly_dict.values()) if monthly_dict else 10
        if max_val < 10:
            max_val = 10

        for i in range(7, -1, -1):
            d = now - relativedelta(months=i)
            key = d.strftime('%Y-%m')
            count = monthly_dict.get(key, 0)

            pct = int((count / max_val) * 80) + 10
            if count == 0:
                pct = 5

            chart_data.append({
                "label": months_fr[d.month - 1],
                "count": count,
                "heightPct": pct
            })

        return {
            "status": "success",
            "data": {
                "kpis": {
                    "applied": applied_count,
                    "interviews": interview_count,
                    "network": network_count,
                    "cv_analyzed": cv_analyzed
                },
                "chart": chart_data
            }
        }
    except Exception as e:
        logger.error(f"Erreur Dashboard Stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/portfolio/render/{user_id}")
async def render_portfolio(user_id: str):
    """Sert le contenu HTML du portfolio pour une iframe."""
    db = get_db()
    user = await db.users.find_one({"id": user_id})
    if not user or "last_portfolio" not in user:
        return HTMLResponse(content="<html><body><h1>Portfolio non trouvé.</h1></body></html>", status_code=404)

    portfolio = user["last_portfolio"]
    html_content = portfolio.get("html", "")
    css_content = portfolio.get("css", "")
    js_content = portfolio.get("js", "")

    full_html = f"""
    <!DOCTYPE html>
    <html style="scroll-behavior: smooth;">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Portfolio - GoldArmy</title>
            <style>{css_content}</style>
        </head>
        <body>
            {html_content}
            <script>
                (function() {{
                    const self = window;
                    Object.defineProperty(window, 'top', {{ get: () => self }});
                    Object.defineProperty(window, 'parent', {{ get: () => self }});

                    document.addEventListener('click', (e) => {{
                        const link = e.target.closest('a');
                        if (link) {{
                            const href = link.getAttribute('href');
                            if (href && href.startsWith('#')) {{
                                e.preventDefault();
                                const target = document.querySelector(href);
                                if (target) {{
                                    target.scrollIntoView({{ behavior: 'smooth' }});
                                }}
                            }}
                        }}
                    }}, true);
                }})();
                {js_content}
            </script>
        </body>
    </html>
    """

    return HTMLResponse(content=full_html)
