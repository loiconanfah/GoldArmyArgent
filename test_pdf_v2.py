"""Test all 8 HTML CV templates — generates PDFs via Playwright."""
import sys, asyncio

sys.path.insert(0, '.')
from core.cv_html_templates import TEMPLATES

cv_data = {
    "full_name": "Marie-Claire Dupont",
    "title": "Ingénieure Logiciel Senior",
    "email": "marie@example.com",
    "phone": "+1 514-555-0123",
    "location": "Montréal, QC",
    "linkedin": "linkedin.com/in/marie-dupont",
    "summary": "Ingénieure backend avec 6 ans d'expérience en Python, FastAPI et microservices. "
               "Passionnée par l'architecture propre et les systèmes distribués. "
               "Leadership technique sur des projets à fort impact.",
    "experiences": [
        {
            "title": "Développeuse Backend Senior",
            "company": "TechCorp",
            "location": "Montréal",
            "start_date": "Jan 2021",
            "end_date": "Présent",
            "bullets": [
                "Développé 12 microservices FastAPI, réduisant la latence P99 de 340ms à 180ms",
                "Automatisé le pipeline CI/CD avec GitHub Actions, atteignant 0 downtime",
                "Encadré 3 développeurs juniors et conduit les revues de code hebdomadaires",
            ],
        },
        {
            "title": "Développeuse Backend",
            "company": "StartupAI",
            "location": "Paris",
            "start_date": "Sep 2018",
            "end_date": "Dec 2020",
            "bullets": [
                "Conçu et implémenté l'API REST principale en Django/DRF (~200k req/jour)",
                "Migré la base PostgreSQL vers un cluster haute-disponibilité (zéro perte de données)",
            ],
        },
    ],
    "projects": [
        {
            "name": "GoldArmy Platform",
            "description": "Plateforme IA de recherche d'emploi propulsée par Gemini + FastAPI.",
            "bullets": ["Architecture multi-agents", "Génération de CV PDF avec Playwright"],
        }
    ],
    "education": [
        {"degree": "M.Sc. Génie Informatique", "institution": "Polytechnique Montréal", "year": "2018"},
        {"degree": "B.Sc. Informatique", "institution": "Université de Montréal", "year": "2016"},
    ],
    "skills": {
        "Langages": ["Python", "TypeScript", "Go", "SQL"],
        "Frameworks": ["FastAPI", "Django", "React", "Next.js"],
        "DevOps": ["Docker", "Kubernetes", "GitHub Actions", "Terraform"],
    },
    "languages": ["Français (natif)", "Anglais (courant)", "Espagnol (intermédiaire)"],
    "certifications": ["AWS Solutions Architect Associate (2023)", "Google Cloud Professional Developer (2022)"],
}


async def main():
    from playwright.async_api import async_playwright
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for tid, tdata in TEMPLATES.items():
            try:
                html = tdata["build"](cv_data)
                page = await browser.new_page()
                await page.set_content(html, wait_until="networkidle")
                out_path = f"test_outputs/test_{tid}.pdf"
                import os; os.makedirs("test_outputs", exist_ok=True)
                await page.pdf(
                    path=out_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                )
                size = os.path.getsize(out_path)
                results.append(f"✅ {tid:12s}  →  {out_path}  ({size:,} bytes)")
                await page.close()
            except Exception as e:
                results.append(f"❌ {tid:12s}  ERROR: {e}")
        await browser.close()

    print("\n── CV HTML Template PDF Generation Results ──")
    for r in results:
        print(r)
    print("─────────────────────────────────────────────")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
