"""Test du scraper Emploi.cm — affiche les infos complètes des offres récupérées."""
import asyncio
import json
import os
import sys

OUTPUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_emploi_cm_test_result.json")
OUTPUT_REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_emploi_cm_offres.txt")


def format_job(job: dict, index: int, desc_max_len: int = 800) -> str:
    """Formate une offre pour affichage lisible."""
    lines = [
        "",
        "=" * 70,
        f"  OFFRE #{index}",
        "=" * 70,
        f"  Titre      : {job.get('title', '—')}",
        f"  Entreprise : {job.get('company', '—')}",
        f"  Lieu       : {job.get('location', '—')}",
        f"  Contrat    : {job.get('job_type', '—')}",
        f"  Date       : {job.get('posted_date', '—')}",
        f"  URL        : {job.get('url', '—')}",
        "",
        "  Description :",
        "-" * 70,
    ]
    desc = (job.get("description") or "").strip()
    if desc:
        if len(desc) > desc_max_len:
            lines.append(desc[:desc_max_len] + "\n  [...] (tronqué, " + str(len(desc)) + " caractères au total)")
        else:
            lines.append(desc)
    else:
        lines.append("  (aucune)")
    skills = job.get("required_skills") or []
    if skills:
        lines.append("")
        lines.append("  Compétences / mots-clés : " + ", ".join(skills[:15]))
    lines.append("")
    return "\n".join(lines)


async def main():
    try:
        from tools.emploi_cm_searcher import EmploiCmSearcher
    except Exception as e:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump({"error": f"import: {e}", "count": 0}, f, ensure_ascii=False)
        print(f"Erreur import: {e}", file=sys.stderr)
        return 0

    searcher = EmploiCmSearcher()
    try:
        # Récupérer les offres avec détails complets (page de détail si disponible)
        limit = int(os.environ.get("EMPLOI_CM_LIMIT", "5"))
        jobs = await searcher.search_jobs(limit=limit, full_details=True)
        await searcher.close()
    except Exception as e:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump({"error": str(e), "count": 0}, f, ensure_ascii=False)
        print(f"Erreur: {e}", file=sys.stderr)
        return 0

    # Sauvegarder le JSON complet (descriptions tronquées pour lisibilité du JSON)
    out = {
        "count": len(jobs),
        "offres": [
            {
                "title": j.get("title"),
                "company": j.get("company"),
                "location": j.get("location"),
                "job_type": j.get("job_type"),
                "posted_date": j.get("posted_date"),
                "url": j.get("url"),
                "description_length": len(j.get("description") or ""),
                "description": (j.get("description") or "")[:2000],
                "required_skills": j.get("required_skills", []),
            }
            for j in jobs
        ],
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Rapport texte lisible avec infos complètes
    report_lines = [
        "EMPLOI.CM — OFFRES RÉCUPÉRÉES",
        f"Nombre d'offres : {len(jobs)}",
    ]
    for i, job in enumerate(jobs, 1):
        report_lines.append(format_job(job, i, desc_max_len=1200))
    report_lines.append("=" * 70)
    report_lines.append("Fin du rapport")
    report_text = "\n".join(report_lines)

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Affichage console (résumé + premières offres)
    print(f"\n📄 Emploi.cm : {len(jobs)} offres récupérées.\n")
    print(f"  Rapport détaillé écrit dans : {OUTPUT_REPORT}")
    print(f"  JSON écrit dans             : {OUTPUT_JSON}\n")
    for i, job in enumerate(jobs[:3], 1):
        print(format_job(job, i, desc_max_len=400))
    if len(jobs) > 3:
        print(f"  ... et {len(jobs) - 3} autre(s) offre(s) — voir {OUTPUT_REPORT}\n")

    return len(jobs)


if __name__ == "__main__":
    try:
        n = asyncio.run(main())
    except Exception as e:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump({"error": str(e), "count": 0}, f, ensure_ascii=False)
        print(f"Erreur: {e}", file=sys.stderr)
        n = 0
    print(f"Total : {n} offres")
    sys.exit(0 if n > 0 else 1)
