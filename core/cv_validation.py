"""Règle 8 — Validation bloquante avant export du CV.

Deux passes :
- Passe 1 : checks DÉTERMINISTES (code, instantané) — dates, chevauchements,
  bullets orphelines, doublons, ratio de chiffres, titres gonflés.
- Passe 2 : un seul appel LLM pour repérer les technologies présentes dans le CV
  généré mais absentes de la source (prose libre — le seul trou que le code ne
  ferme pas). Les helpers de prompt/parse sont ici ; l'appel LLM est fait par la route.

Chaque « finding » : {id, level: 'fail'|'warning', code, message, meta:{...}, actions:[...]}
"""
import re
import unicodedata

_SENIORITY = ["lead", "senior", "principal", "expert", "chef", "directeur", "director", "head", "sr"]
_MONTHS = {
    "janvier": 1, "jan": 1, "january": 1, "fevrier": 2, "fev": 2, "february": 2, "feb": 2,
    "mars": 3, "mar": 3, "march": 3, "avril": 4, "avr": 4, "april": 4, "apr": 4,
    "mai": 5, "may": 5, "juin": 6, "jun": 6, "june": 6, "juillet": 7, "juil": 7, "jul": 7, "july": 7,
    "aout": 8, "aou": 8, "august": 8, "aug": 8, "septembre": 9, "sep": 9, "sept": 9, "september": 9,
    "octobre": 10, "oct": 10, "october": 10, "novembre": 11, "nov": 11, "november": 11,
    "decembre": 12, "dec": 12, "december": 12,
}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


def _all_bullets(cv_data):
    """Retourne [(where, text)] pour toutes les puces (expériences + projets)."""
    out = []
    for i, e in enumerate(cv_data.get("experiences") or []):
        if isinstance(e, dict):
            for b in (e.get("bullets") or []):
                out.append((("experience", i, e.get("company") or e.get("title") or ""), str(b)))
    for i, p in enumerate(cv_data.get("projects") or []):
        if isinstance(p, dict):
            for b in (p.get("bullets") or []):
                out.append((("project", i, p.get("name") or ""), str(b)))
    return out


def _rank(date_str, is_end=False):
    """(année, mois) -> entier comparable. Vide/Présent -> très grand si fin, None sinon."""
    ns = _norm(date_str)
    if not ns:
        return 9999 * 12 if is_end else None
    if any(w in ns for w in ("present", "aujourd", "actuel", "en cours", "now", "current")):
        return 9999 * 12
    ym = re.search(r"(19|20)\d{2}", ns)
    if not ym:
        return None
    year = int(ym.group(0))
    month = 1
    for name, num in _MONTHS.items():
        if re.search(r"\b" + name + r"\b", ns):
            month = num
            break
    return year * 12 + month


def deterministic_checks(cv_data: dict, source_text: str) -> list:
    findings = []
    if not isinstance(cv_data, dict):
        return findings
    src = _norm(source_text)
    src_years = set(re.findall(r"\b(?:19|20)\d{2}\b", source_text or ""))
    src_tokens = set(src.split())
    experiences = [e for e in (cv_data.get("experiences") or []) if isinstance(e, dict)]

    def _in_source_title(word):
        return word in src_tokens

    # Check C — bullets orphelines (structure)
    if isinstance(cv_data.get("bullets"), list) and cv_data["bullets"]:
        findings.append({"id": "orphan", "level": "fail", "code": "orphan_bullets",
                         "message": "Des puces ne sont rattachées à aucun poste.",
                         "meta": {}, "actions": ["reattach"]})

    # Check A — dates inventées (année absente de la source)
    def _check_date(label, d, idx, kind):
        yrs = set(re.findall(r"\b(?:19|20)\d{2}\b", d or ""))
        if yrs and not (yrs & src_years):
            findings.append({"id": f"date_{kind}_{idx}", "level": "fail", "code": "date_modified",
                             "message": f"Date absente de vos données : « {label} » indique « {d} ».",
                             "meta": {"kind": kind, "index": idx, "value": d}, "actions": ["confirm_date"]})

    for i, e in enumerate(experiences):
        co = e.get("company") or e.get("title") or f"Poste {i+1}"
        if e.get("start_date"):
            _check_date(co, e.get("start_date"), i, "exp_start")
        if e.get("end_date"):
            _check_date(co, e.get("end_date"), i, "exp_end")
    for i, ed in enumerate(cv_data.get("education") or []):
        if isinstance(ed, dict) and ed.get("year"):
            _check_date(ed.get("institution") or f"Formation {i+1}", ed.get("year"), i, "edu")

    # Check B — chevauchements de dates (warning)
    spans = []
    for i, e in enumerate(experiences):
        s = _rank(e.get("start_date", ""))
        en = _rank(e.get("end_date", ""), is_end=True)
        if s is not None and en is not None:
            spans.append((i, s, en, e.get("company") or e.get("title") or f"Poste {i+1}"))
    for a in range(len(spans)):
        for b in range(a + 1, len(spans)):
            ia, sa, ea, na = spans[a]
            ib, sb, eb, nb = spans[b]
            if sa < eb - 1 and sb < ea - 1:  # chevauchement > 1 mois
                findings.append({"id": f"overlap_{ia}_{ib}", "level": "warning", "code": "date_overlap",
                                 "message": f"Chevauchement de dates : « {na} » et « {nb} ».",
                                 "meta": {"a": ia, "b": ib}, "actions": ["add_precision", "ignore"]})

    # Check D — doublons de puces
    bullets = _all_bullets(cv_data)
    seen = {}
    for where, text in bullets:
        key = _norm(text)
        if len(key) < 4:
            continue
        if key in seen:
            findings.append({"id": f"dup_{abs(hash(key)) % 100000}", "level": "fail", "code": "duplicate_bullet",
                             "message": f"Puce dupliquée : « {text[:80]}… ».",
                             "meta": {"text": text}, "actions": ["remove_duplicate"]})
        else:
            seen[key] = where

    # Check E — ratio de chiffres
    total = len(bullets) or 1
    with_num = [t for _, t in bullets if re.search(r"\d+\s*(?:%|h|heures?|jours?|\$|€|utilisateurs?|k)\b", t, re.I) or "%" in t]
    ratio = len(with_num) / total
    pcts = re.findall(r"(\d+)\s*%", " ".join(with_num))
    all_round = pcts and all(int(p) % 10 == 0 for p in pcts)
    if ratio >= 0.99 and all_round and total >= 3:
        findings.append({"id": "ratio_fab", "level": "fail", "code": "metric_fabrication",
                         "message": "Presque chaque puce a un pourcentage arrondi — signal de fabrication.",
                         "meta": {"ratio": round(ratio, 2)}, "actions": ["dequantify"]})
    elif ratio > 0.40 and total >= 3:
        findings.append({"id": "ratio_warn", "level": "warning", "code": "metric_ratio",
                         "message": f"{round(ratio*100)}% des puces contiennent un chiffre — envisagez de varier.",
                         "meta": {"ratio": round(ratio, 2)}, "actions": ["dequantify"]})

    # Check F — titres gonflés
    def _check_title(title, idx, kind):
        nt = _norm(title)
        for w in _SENIORITY:
            if re.search(r"\b" + w + r"\b", nt) and not _in_source_title(w):
                findings.append({"id": f"title_{kind}_{idx}", "level": "fail", "code": "title_inflated",
                                 "message": f"Titre enrichi d'un niveau non fourni : « {w} » dans « {title} ».",
                                 "meta": {"kind": kind, "index": idx, "word": w, "title": title},
                                 "actions": ["revert_title", "confirm_title"]})
                break

    if cv_data.get("title"):
        _check_title(cv_data["title"], -1, "profile")
    for i, e in enumerate(experiences):
        if e.get("title"):
            _check_title(e["title"], i, "exp")

    return findings


# ── Passe 2 — vérification croisée des technologies (helpers, appel LLM côté route) ──

def build_tech_check_prompt(source_text: str, generated_text: str) -> str:
    return f'''Tu es un vérificateur factuel strict. Voici deux textes.

TEXTE SOURCE (unique vérité factuelle) :
"""
{(source_text or "")[:6000]}
"""

CV GÉNÉRÉ (à vérifier) :
"""
{(generated_text or "")[:6000]}
"""

Tâche : liste chaque technologie, outil, framework, méthodologie ou compétence technique
NOMMÉ dans le CV GÉNÉRÉ qui n'apparaît PAS dans le TEXTE SOURCE, ni littéralement ni comme
synonyme direct non ambigu (« JS » = « JavaScript » est valide ; « Python » n'implique PAS
« Pandas » ni « NumPy » — bibliothèques distinctes, à signaler).
Ignore la reformulation stylistique, les verbes d'action et les résultats chiffrés.

Réponds UNIQUEMENT en JSON, aucun texte autour :
{{"termes_non_confirmes": [{{"terme": "...", "contexte": "...phrase complète où il apparaît..."}}]}}
Si rien : {{"termes_non_confirmes": []}}'''


def parse_tech_findings(raw: str) -> list:
    import json
    findings = []
    try:
        cleaned = re.sub(r"```json|```", "", raw or "").strip()
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        data = json.loads(m.group(0) if m else cleaned)
        for i, item in enumerate((data.get("termes_non_confirmes") or [])[:20]):
            term = str(item.get("terme", "")).strip()
            if not term:
                continue
            findings.append({
                "id": f"tech_{i}_{abs(hash(term)) % 100000}",
                "level": "fail", "code": "tech_unconfirmed",
                "message": f"Technologie non confirmée dans vos données : « {term} ».",
                "meta": {"term": term, "phrase": str(item.get("contexte", "")).strip()},
                "actions": ["remove_tech", "confirm_tech"],
            })
    except Exception:
        pass
    return findings
