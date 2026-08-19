"""Scoreur ATS déterministe (réel, pas inventé par le LLM).

Évalue un CV (texte brut ou cv_data structuré) sur 5 axes + score global 0-100,
selon des signaux mesurables : sections présentes, coordonnées, densité de
mots-clés / correspondance à l'offre, verbes d'action, quantification réelle,
lisibilité (longueur des puces). Utilisé pour afficher un score honnête dans le
rapport du Mentor, à la place d'un score halluciné.
"""
import re
import json
import unicodedata

_STRONG_VERBS = {
    # FR (infinitif + participe)
    "developper", "developpe", "concevoir", "concu", "architecturer", "architecture",
    "optimiser", "optimise", "deployer", "deploye", "automatiser", "automatise",
    "reduire", "reduit", "augmenter", "augmente", "piloter", "pilote", "integrer",
    "integre", "refactoriser", "refactorise", "implementer", "implemente", "migrer",
    "migre", "securiser", "securise", "coordonner", "coordonne", "livrer", "livre",
    "encadrer", "encadre", "ameliorer", "ameliore", "gerer", "gere", "creer", "cree",
    "maintenir", "maintenu", "resoudre", "resolu", "diriger", "dirige",
    # EN
    "developed", "designed", "architected", "optimized", "deployed", "automated",
    "reduced", "increased", "led", "integrated", "refactored", "implemented",
    "migrated", "secured", "coordinated", "delivered", "managed", "built",
    "created", "maintained", "resolved", "improved", "launched", "drove",
}

_SECTION_HINTS = [
    "experience", "experiences", "formation", "education", "competence", "competences",
    "skills", "resume", "summary", "profil", "profile", "projet", "project", "langue",
    "language", "certification",
]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def cv_data_to_text(cv_data: dict) -> str:
    """Aplati un cv_data structuré en texte, pour un scoring homogène avec l'original."""
    if not isinstance(cv_data, dict):
        return str(cv_data or "")
    parts = []
    for k in ("full_name", "title", "email", "phone", "location", "linkedin", "github", "summary"):
        if cv_data.get(k):
            parts.append(str(cv_data[k]))
    for e in (cv_data.get("experiences") or []):
        if isinstance(e, dict):
            parts.append(" ".join(str(e.get(x, "")) for x in ("title", "company", "location", "start_date", "end_date")))
            parts += [str(b) for b in (e.get("bullets") or [])]
    for p in (cv_data.get("projects") or []):
        if isinstance(p, dict):
            parts.append(str(p.get("name", "")) + " " + str(p.get("description", "")))
            parts += [str(b) for b in (p.get("bullets") or [])]
    sk = cv_data.get("skills") or {}
    if isinstance(sk, dict):
        for v in sk.values():
            parts += [str(x) for x in (v if isinstance(v, list) else [v])]
    elif isinstance(sk, list):
        parts += [str(x) for x in sk]
    for key in ("education", "languages", "certifications"):
        for it in (cv_data.get(key) or []):
            parts.append(json.dumps(it, ensure_ascii=False) if isinstance(it, dict) else str(it))
    return "\n".join(parts)


def _bullets_from_text(text: str):
    """Extrait des lignes de type puce (commençant par -, •, ▸, * ou une puce implicite)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return [re.sub(r"^[\-•▸*·]\s*", "", l) for l in lines if len(l.split()) >= 3]


def _job_keywords(job_text: str):
    toks = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", _norm(job_text))
    stop = {"and", "the", "for", "with", "les", "des", "une", "avec", "pour", "dans",
            "vous", "nous", "notre", "votre", "sur", "qui", "que", "est", "sont"}
    return {t for t in toks if len(t) >= 3 and t not in stop}


def score_text(text: str, job_text: str = None) -> dict:
    """Score ATS réel (0-100) + détail par catégorie, à partir d'un texte de CV."""
    if not text or len(text.strip()) < 40:
        return {"ats_score": 20, "scores": {"mots_cles": 20, "impact_resultats": 20,
                                             "mise_en_forme": 20, "lisibilite": 20, "experience_pertinence": 20}}
    n_text = _norm(text)
    bullets = _bullets_from_text(text)
    nb = len(bullets) or 1

    # Mise en forme : sections reconnues + coordonnées
    sections = sum(1 for h in set(_SECTION_HINTS) if h in n_text)
    has_email = bool(re.search(r"[\w.\-]+@[\w.\-]+", text))
    has_phone = bool(re.search(r"(\+?\d[\d ().\-]{7,})", text))
    mise_en_forme = min(100, 30 + min(48, sections * 8) + (12 if has_email else 0) + (10 if has_phone else 0))

    # Impact & résultats : verbes d'action forts + quantification RÉELLE (mesurée, pas exigée)
    strong = sum(1 for b in bullets if _norm(b).split()[:1] and _norm(b).split()[0] in _STRONG_VERBS)
    quant = sum(1 for b in bullets if re.search(r"\d", b))
    impact = min(100, int(65 * strong / nb) + min(35, int(70 * quant / nb)))

    # Mots-clés : correspondance à l'offre si fournie, sinon densité technique
    if job_text and len(job_text) > 40:
        jk = _job_keywords(job_text)
        cv_toks = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", n_text))
        overlap = len(jk & cv_toks) / (len(jk) or 1)
        mots_cles = min(100, 35 + int(65 * overlap))
    else:
        tech = len(re.findall(r"[A-Za-z][A-Za-z0-9+#.]*", text))
        mots_cles = min(100, 45 + min(55, tech // 15))

    # Lisibilité : longueur des puces dans une fourchette saine (5-32 mots)
    good = sum(1 for b in bullets if 5 <= len(b.split()) <= 32)
    lisibilite = min(100, 45 + int(55 * good / nb))

    # Pertinence expérience : volume de contenu structuré
    exp_signal = min(4, n_text.count("experience") + n_text.count("experiences"))
    pertinence = min(100, 40 + min(40, nb * 5) + exp_signal * 5)

    overall = round(0.25 * mots_cles + 0.25 * impact + 0.20 * mise_en_forme
                    + 0.15 * lisibilite + 0.15 * pertinence)
    return {
        "ats_score": max(0, min(100, overall)),
        "scores": {
            "mots_cles": mots_cles, "impact_resultats": impact,
            "mise_en_forme": mise_en_forme, "lisibilite": lisibilite,
            "experience_pertinence": pertinence,
        },
    }


_STOP = {
    "and", "the", "for", "with", "of", "to", "in", "on", "at", "les", "des", "une", "un",
    "avec", "pour", "dans", "sur", "au", "aux", "par", "en", "qui", "que", "est", "sont",
    "vous", "nous", "notre", "votre", "ses", "son", "sa", "ce", "cette", "nos", "vos",
    "poste", "emploi", "job", "offre", "role", "team", "equipe", "experience", "annees",
    "ans", "candidat", "profil", "recherche", "mission", "missions", "will", "you", "your",
    "we", "our", "are", "have", "work", "working", "join", "about", "plus", "type", "temps",
}


def _tok(text: str) -> set:
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{2,}", _norm(text or ""))
    return {t.strip(".-") for t in raw if t.strip(".-")}


def _offer_keywords(job_text: str) -> set:
    return {t for t in _tok(job_text) if t not in _STOP and not t.isdigit() and len(t) >= 3}


def offer_match(cv_text_or_data, job_text: str) -> dict:
    """Correspondance déterministe CV ↔ offre : % de mots-clés de l'offre présents
    dans le CV, mots-clés couverts et non couverts."""
    cv_text = cv_data_to_text(cv_text_or_data) if isinstance(cv_text_or_data, dict) else str(cv_text_or_data or "")
    jk = _offer_keywords(job_text)
    if not jk:
        return {"score": 0, "matched": [], "missing": []}
    cv_toks = _tok(cv_text)
    matched = sorted(jk & cv_toks)
    missing = sorted(jk - cv_toks)
    score = round(100 * len(matched) / len(jk))
    return {"score": max(0, min(100, score)), "matched": matched, "missing": missing}


def score_cv(cv_data: dict, job_text: str = None) -> dict:
    """Score ATS réel d'un cv_data structuré (mesure sur les VRAIES puces)."""
    if not isinstance(cv_data, dict):
        return score_text(str(cv_data or ""), job_text)
    exps = cv_data.get("experiences") or []
    projs = cv_data.get("projects") or []
    bullets = [str(b) for e in exps if isinstance(e, dict) for b in (e.get("bullets") or [])]
    bullets += [str(b) for p in projs if isinstance(p, dict) for b in (p.get("bullets") or [])]
    nb = len(bullets) or 1

    # Mise en forme : sections structurées + coordonnées
    sections = sum(1 for k in ("summary", "experiences", "education", "skills") if cv_data.get(k))
    contact = sum(1 for k in ("email", "phone", "location") if cv_data.get(k))
    mise_en_forme = min(100, 30 + sections * 14 + contact * 6)

    # Impact : verbes d'action forts + quantification réelle (mesurée)
    strong = sum(1 for b in bullets if _norm(b).split()[:1] and _norm(b).split()[0] in _STRONG_VERBS)
    quant = sum(1 for b in bullets if re.search(r"\d", b))
    impact = min(100, int(65 * strong / nb) + min(35, int(70 * quant / nb)))

    # Mots-clés : correspondance offre ou densité de compétences
    skills_flat = []
    sk = cv_data.get("skills") or {}
    if isinstance(sk, dict):
        for v in sk.values():
            skills_flat += (v if isinstance(v, list) else [v])
    elif isinstance(sk, list):
        skills_flat = sk
    if job_text and len(job_text) > 40:
        jk = _job_keywords(job_text)
        cv_toks = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", _norm(cv_data_to_text(cv_data))))
        overlap = len(jk & cv_toks) / (len(jk) or 1)
        mots_cles = min(100, 35 + int(65 * overlap))
    else:
        mots_cles = min(100, 45 + min(55, len(skills_flat) * 5))

    # Lisibilité : longueur des puces
    good = sum(1 for b in bullets if 5 <= len(b.split()) <= 32)
    lisibilite = min(100, 45 + int(55 * good / nb))

    # Pertinence : expériences pourvues de puces + formation
    exp_b = sum(1 for e in exps if isinstance(e, dict) and e.get("bullets"))
    pertinence = min(100, 40 + exp_b * 15 + (10 if cv_data.get("education") else 0))

    overall = round(0.25 * mots_cles + 0.25 * impact + 0.20 * mise_en_forme
                    + 0.15 * lisibilite + 0.15 * pertinence)
    return {
        "ats_score": max(0, min(100, overall)),
        "scores": {
            "mots_cles": mots_cles, "impact_resultats": impact,
            "mise_en_forme": mise_en_forme, "lisibilite": lisibilite,
            "experience_pertinence": pertinence,
        },
    }
