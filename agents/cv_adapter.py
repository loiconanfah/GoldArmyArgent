import json
import re
import unicodedata
from loguru import logger
from typing import Dict, Any

from core.agent_base import BaseAgent


# Valeurs "placeholder" que l'IA ne doit jamais laisser sur des champs factuels
_PLACEHOLDER_VALUES = {
    "", "à venir", "a venir", "non spécifiée", "non specifiee", "non spécifié",
    "non specifie", "n/a", "na", "en cours", "tbd", "inconnu", "inconnue",
    "not specified", "unknown", "present?", "-", "—",
}
# Mots de séniorité à ne PAS ajouter si absents du CV source (garde-fou titres)
_SENIORITY_WORDS = {"lead", "senior", "sr", "principal", "head", "vp", "staff"}
# Plafonds dégressifs de bullets par expérience (récent → ancien) + plafond global
_BULLET_CAPS = [4, 3, 2]
_BULLET_GLOBAL_CAP = 12


def _norm_text(s: str) -> str:
    """Minuscule, sans accents, alphanumérique — pour comparaison/dédup robuste."""
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


_FR_STOPWORDS = {"le", "la", "les", "des", "une", "un", "et", "de", "du", "avec",
                 "pour", "dans", "sur", "au", "aux", "par", "en", "ans", "compétences",
                 "expérience", "formation", "développeur", "gestion", "projet"}
_EN_STOPWORDS = {"the", "and", "with", "for", "of", "to", "in", "on", "at", "years",
                 "experience", "skills", "management", "developer", "project", "team"}


def _detect_lang_from_text(text: str) -> str:
    """Détecte fr/en à partir du texte source (comptage de mots-outils)."""
    tokens = _norm_text(text).split()
    if not tokens:
        return "fr"
    fr = sum(1 for t in tokens if t in _FR_STOPWORDS)
    en = sum(1 for t in tokens if t in _EN_STOPWORDS)
    return "en" if en > fr else "fr"


def _fallback_questions(lang: str) -> list:
    """Jeu de questions par défaut si le LLM échoue (dans la langue du CV)."""
    if lang == "en":
        return [
            {"id": "q1", "category": "metrics", "question": "What real, verifiable numbers can you share (performance gains, volumes, budget, team size, deadlines)?", "hint": "Only figures you can back up."},
            {"id": "q2", "category": "achievement", "question": "What are your 2-3 most concrete achievements for this kind of role?", "hint": "With the context and outcome."},
            {"id": "q3", "category": "seniority", "question": "What is your exact official job title and real level of responsibility?", "hint": "Avoid inflating (Lead/Senior)."},
            {"id": "q4", "category": "focus", "question": "For THIS offer, what should we highlight and what should we downplay?", "hint": ""},
        ]
    return [
        {"id": "q1", "category": "metrics", "question": "Quels chiffres réels et vérifiables peux-tu donner (gains de performance, volumes, budget, taille d'équipe, délais) ?", "hint": "Uniquement ce que tu peux justifier."},
        {"id": "q2", "category": "achievement", "question": "Quelles sont tes 2-3 réalisations les plus concrètes pour ce type de poste ?", "hint": "Avec le contexte et le résultat."},
        {"id": "q3", "category": "seniority", "question": "Quel est ton intitulé de poste officiel exact et ton niveau réel de responsabilité ?", "hint": "Évite de gonfler (Lead/Senior)."},
        {"id": "q4", "category": "focus", "question": "Pour CETTE offre, qu'est-ce qu'on met en avant et qu'est-ce qu'on minimise ?", "hint": ""},
    ]


def _clean_factual(v):
    """Vide les valeurs placeholder sur les champs factuels (dates, années)."""
    if not isinstance(v, str):
        return v
    return "" if _norm_text(v) in _PLACEHOLDER_VALUES or v.strip().lower() in _PLACEHOLDER_VALUES else v.strip()


def _source_numbers(cv_text: str) -> set:
    """Ensemble des nombres réellement présents dans le CV source."""
    return set(re.findall(r'\d+(?:[.,]\d+)?', cv_text or ""))


def _strip_fabricated_metrics(text: str, src_nums: set, force: bool = False) -> str:
    """Retire les métriques ABSENTES du CV source (anti-invention), en gardant la
    phrase grammaticale. Si force=True, retire TOUTES les métriques (pour plafonner
    le ratio de bullets chiffrés), qu'elles soient réelles ou non."""
    if not text:
        return text

    def foreign(frag: str) -> bool:
        if force:
            return True
        nums = re.findall(r'\d+(?:[.,]\d+)?', frag)
        return any(n.replace(',', '.') not in src_nums and n not in src_nums for n in nums)

    def drop(m):
        return '' if foreign(m.group(0)) else m.group(0)

    t = text
    # 1) Parenthèses contenant un nombre étranger : (de 500ms à 350ms), (-66%)
    t = re.sub(r'\s*\([^)]*\d[^)]*\)', drop, t)
    # 2) Plages "de X à Y" (unités/heures) étrangères
    t = re.sub(r'\s*\bde\s+\d[\d.,]*\s*\w*\s+à\s+\d[\d.,]*\s*\w*', drop, t, flags=re.I)
    # 3) "... de/of/by X%" étranger
    t = re.sub(r'\s*\b(?:de|of|by|d[\'’]|à|to)\s*[-+]?\d[\d.,]*\s*%', drop, t, flags=re.I)
    # 4) Pourcentages restants étrangers
    t = re.sub(r'\s*[-+]?\d[\d.,]*\s*%', drop, t)
    # 5) Valeurs à unité étrangères : 5000€, 500ms, 8h, 50k, 12Go
    t = re.sub(r'\s*\b\d[\d.,]*\s*(?:ms|€|\$|k|h|Mo|Go|s)\b', drop, t, flags=re.I)
    # Nettoyage : espaces/ponctuation orphelins (sans casser ".NET")
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'\s+([,;:])', r'\1', t)
    t = re.sub(r'\s+\.(?=\s|$)', '.', t)         # point de fin seulement → préserve " .NET"
    t = re.sub(r'([,;:])\s*\.', '.', t)
    t = re.sub(r'\bde\s+et\b', 'et', t, flags=re.I)
    t = re.sub(r'\s*,\s*$', '', t).strip()
    if t and t[-1] not in '.!?':
        t += '.'
    return t


def _guard_title(title: str, source_tokens: set) -> str:
    """Retire un mot de séniorité d'un intitulé s'il n'est pas présent dans le CV source."""
    if not title:
        return title
    out = title
    for kw in _SENIORITY_WORDS:
        toks = _norm_text(out).split()
        if kw in toks and kw not in source_tokens:
            # supprime le mot (et 'technique' accolé type "Lead Technique") en respectant la casse
            out = re.sub(r'(?i)\b' + re.escape(kw) + r'\b\.?\s*', '', out).strip()
            out = re.sub(r'\s{2,}', ' ', out).strip(" -–—/")
    return out or title


def _postprocess_cv_json(cv_json: Dict[str, Any], cv_text: str) -> Dict[str, Any]:
    """Garde-fous déterministes appliqués au cv_json avant génération du PDF :
    - dédoublonnage des bullets (exact + quasi-identique) sur tout le CV
    - plafonds dégressifs par expérience + plafond global (≈10-12 bullets)
    - nettoyage des dates/années placeholder ("À venir", "Non spécifiée"…)
    - garde-fou sur les intitulés (pas de "Lead"/"Senior" inventé)
    """
    if not isinstance(cv_json, dict):
        return cv_json

    # Langue figée depuis la source → tous les générateurs (PDF/Word/HTML) l'utilisent
    cv_json["lang"] = _detect_lang_from_text(cv_text)

    source_tokens = set(_norm_text(cv_text).split())
    src_nums = _source_numbers(cv_text)
    seen = set()
    total = 0

    # Résumé : retire les métriques inventées (absentes de la source)
    if cv_json.get("summary"):
        cv_json["summary"] = _strip_fabricated_metrics(cv_json["summary"], src_nums)

    experiences = cv_json.get("experiences") or []
    for idx, exp in enumerate(experiences):
        if not isinstance(exp, dict):
            continue
        exp["start_date"] = _clean_factual(exp.get("start_date", ""))
        exp["end_date"] = _clean_factual(exp.get("end_date", ""))
        exp["title"] = _guard_title(exp.get("title", "") or "", source_tokens)

        cap = _BULLET_CAPS[idx] if idx < len(_BULLET_CAPS) else 2
        kept = []
        for b in (exp.get("bullets") or []):
            b = _strip_fabricated_metrics(str(b).strip(), src_nums)
            nb = _norm_text(b)
            if len(nb) < 4 or nb in seen:
                continue
            if total >= _BULLET_GLOBAL_CAP or len(kept) >= cap:
                continue
            seen.add(nb)
            kept.append(b)
            total += 1
        exp["bullets"] = kept

    # Projets : dédoublonnage vs. le reste, plafond léger
    for proj in (cv_json.get("projects") or []):
        if not isinstance(proj, dict):
            continue
        kept = []
        for b in (proj.get("bullets") or []):
            b = _strip_fabricated_metrics(str(b).strip(), src_nums)
            nb = _norm_text(b)
            if len(nb) < 4 or nb in seen:
                continue
            seen.add(nb)
            kept.append(b)
            if len(kept) >= 3:
                break
        proj["bullets"] = kept

    # Plafond DUR : au plus ~40% des bullets contiennent un pourcentage.
    # (Un CV où chaque ligne a un % est la signature IA n°1 signalée par les recruteurs.)
    refs = []
    for e in experiences:
        if isinstance(e, dict):
            for i in range(len(e.get("bullets") or [])):
                refs.append((e["bullets"], i))
    for p in (cv_json.get("projects") or []):
        if isinstance(p, dict):
            for i in range(len(p.get("bullets") or [])):
                refs.append((p["bullets"], i))
    total_b = len(refs)
    if total_b >= 3:
        pct_refs = [(lst, i) for (lst, i) in refs if "%" in str(lst[i])]
        budget = max(1, int(0.40 * total_b))  # plancher → ratio garanti ≤ 40%
        if len(pct_refs) > budget:
            for (lst, i) in pct_refs[budget:]:  # garde les % des 1res expériences (récentes)
                lst[i] = _strip_fabricated_metrics(str(lst[i]), src_nums, force=True)

    # Formation : années placeholder → vide (cohérence inter-génération)
    for ed in (cv_json.get("education") or []):
        if isinstance(ed, dict):
            ed["year"] = _clean_factual(ed.get("year", ""))
    for cert in (cv_json.get("certifications") or []):
        if isinstance(cert, dict):
            cert["year"] = _clean_factual(cert.get("year", ""))

    return cv_json


def _markdown_to_minimal_cv_json(markdown: str) -> Dict[str, Any]:
    """Fallback : construit une structure cv_json minimale à partir du markdown (sans titre 'Résumé adapté').
    Dédoublonne et plafonne les bullets pour éviter un bloc massif d'items répétés."""
    lines = [s.strip() for s in (markdown or "").split("\n") if s.strip()]
    name = lines[0].replace("#", "").strip() if lines else "Candidat"
    # Ne garde que les lignes qui ressemblent à des bullets, dédoublonnées et plafonnées
    bullets, seen = [], set()
    for ln in lines[1:]:
        txt = ln.lstrip("-*•▸ ").strip()
        nb = _norm_text(txt)
        if len(nb) < 4 or nb in seen:
            continue
        seen.add(nb)
        bullets.append(txt)
        if len(bullets) >= _BULLET_GLOBAL_CAP:
            break
    return {
        "full_name": name,
        "summary": "",
        "experiences": [{"title": "Expérience professionnelle", "company": "", "start_date": "", "end_date": "", "bullets": bullets}],
        "skills": {},
        "education": [],
    }


def _extract_markdown_from_broken_json(raw: str) -> str:
    """
    Extrait la valeur de "markdown" d'un JSON invalide (ex: guillemets ou retours à la ligne non échappés).
    Parcourt la chaîne après "markdown": " et trouve la fin de la valeur en gérant \\ et \".
    """
    if not raw:
        return ""
    needle = '"markdown"'
    i = raw.find(needle)
    if i == -1:
        return ""
    i = raw.find('"', i + len(needle))
    if i == -1:
        return ""
    start = i + 1
    out = []
    j = start
    while j < len(raw):
        c = raw[j]
        if c == '\\':
            if j + 1 < len(raw):
                n = raw[j + 1]
                if n == 'n':
                    out.append('\n')
                elif n == '"':
                    out.append('"')
                elif n == '\\':
                    out.append('\\')
                else:
                    out.append(n)
                j += 2
                continue
            j += 1
            continue
        if c == '"':
            break
        out.append(c)
        j += 1
    return "".join(out)


class CVAdapterAgent(BaseAgent):
    """
    Agent spécialisé dans l'adaptation de CV et la génération de projets 
    pour combler les lacunes d'expérience via Gemini 3.1 Pro.
    """
    def __init__(self):
        super().__init__(name="CVAdapterAgent", agent_type="adapter")

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode abstraite requise par BaseAgent"""
        return {}
        
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode abstraite requise par BaseAgent"""
        return {}
        
    async def generate_questions(self, job_title: str, job_desc: str, cv_text: str) -> list:
        """Génère 4 à 6 questions ciblées à poser au candidat AVANT de générer le CV.
        Objectif : récupérer des faits réels (chiffres, réalisations, niveau, focus) pour
        rédiger un CV juste et personnalisé — sans rien inventer."""
        lang = _detect_lang_from_text(cv_text)
        system_prompt = (
            "Tu es un coach carrière expert. À partir du CV du candidat et de l'offre visée, "
            "tu poses des questions courtes et précises pour obtenir les informations MANQUANTES "
            "qui rendront le CV plus fort et crédible, SANS jamais inventer. "
            f"Rédige les questions dans la langue du CV (ici: {'anglais' if lang == 'en' else 'français'})."
        )
        user_prompt = f"""OFFRE : {job_title}
DESCRIPTION : {job_desc[:1500]}

CV DU CANDIDAT :
{cv_text[:6000]}

Génère 4 à 6 questions, chacune dans une de ces catégories :
- "metrics" : chiffres réels et vérifiables (performance, volumes, budget, taille d'équipe, délais)
- "achievement" : 1-2 réalisations concrètes marquantes, avec le contexte
- "seniority" : intitulé de poste officiel exact et niveau réel de responsabilité
- "focus" : ce que le candidat veut mettre en avant ou minimiser pour CETTE offre

Réponds UNIQUEMENT en JSON valide :
{{"questions": [{{"id": "q1", "category": "metrics", "question": "…", "hint": "…"}}]}}"""
        try:
            response = await self.generate_response(
                prompt=user_prompt, system=system_prompt,
                model="gemini-2.0-flash", max_tokens=1024,
            )
            raw = response.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group(0)) if match else json.loads(raw)
            questions = data.get("questions") or []
            clean = []
            for i, q in enumerate(questions[:6]):
                if isinstance(q, dict) and q.get("question"):
                    clean.append({
                        "id": q.get("id") or f"q{i+1}",
                        "category": q.get("category") or "focus",
                        "question": str(q["question"]).strip(),
                        "hint": str(q.get("hint") or "").strip(),
                    })
            if clean:
                return clean
        except Exception as e:
            logger.warning(f"generate_questions fallback: {e}")
        # Filet de secours : questions génériques dans la bonne langue
        return _fallback_questions(lang)

    async def adapt(self, job_title: str, job_desc: str, cv_text: str, answers: list = None) -> Dict[str, Any]:
        """
        Analyse l'offre et le CV, puis génère un CV adapté en Markdown
        et des projets recommandés en JSON.

        answers : réponses du candidat aux questions ciblées (source de vérité pour
        les chiffres et faits — l'IA doit s'en servir plutôt que d'inventer).
        """
        
        system_prompt = """Tu es un expert recrutement et ATS de haut niveau. Ton rôle est d'ADAPTER et RÉORGANISER le CV du candidat pour le poste ciblé, de façon CRÉDIBLE. Un CV crédible et ciblé bat toujours un CV « parfait » sur-optimisé : les recruteurs (et Reddit) détectent immédiatement un CV généré par IA. Tu ne dois JAMAIS inventer de faits.

LANGUE DE SORTIE (RÈGLE ABSOLUE) : Rédige l'INTÉGRALITÉ du CV DANS LA MÊME LANGUE que le CV source du candidat. En cas de doute, aligne-toi sur la langue de l'OFFRE. Ne traduis JAMAIS le CV.

RÈGLES CRITIQUES :

1. CIBLAGE, PAS EXHAUSTIVITÉ (priorité absolue) : Sélectionne et met en avant UNIQUEMENT ce qui sert le poste ciblé. Les expériences/compétences hors-sujet sont RÉSUMÉES en une seule ligne ou omises — ne liste pas tout par exhaustivité. Le résumé et le titre doivent annoncer la spécialité du poste dès le premier mot (jamais "polyvalent" / "touche-à-tout").

2. QUANTIFICATION MESURÉE (anti-signature IA) : AU MAXIMUM 40% des bullets contiennent un chiffre. JAMAIS plus de 2 bullets chiffrés consécutifs. N'INVENTE JAMAIS de pourcentage : n'utilise un chiffre QUE s'il est présent ou clairement déductible du CV source. Un CV où chaque ligne a un % rond est un rejet immédiat.

3. VARIE LE TYPE DE PREUVE : alterne entre pourcentage, chiffre brut (heures, utilisateurs, volume), résultat concret (fonctionnalité livrée, contrat, migration réussie) et preuve qualitative (retour client, montée en responsabilité). La majorité des bullets décrivent l'ACTION et l'IMPACT qualitatif SANS chiffre.

4. VOLUME & DÉGRESSIVITÉ : Rattache chaque bullet à SON expérience (jamais un bloc de bullets détaché). 3-4 bullets pour l'expérience la plus récente/pertinente, 2-3 pour la suivante, 1-2 pour les plus anciennes. TOTAL 10-12 bullets MAXIMUM sur tout le CV.

5. AUCUN DOUBLON : Ne répète jamais une même réalisation, même reformulée, dans deux bullets. Chaque bullet est unique.

6. FAITS FIGÉS (identité, coordonnées, dates, formation) : Recopie EXACTEMENT depuis le CV source l'identité, l'e-mail, le téléphone, les dates de début/fin, les diplômes, institutions et années. N'INVENTE JAMAIS un e-mail, un téléphone ou une date : si l'info est absente du CV source, laisse le champ VIDE (""). N'écris JAMAIS "À venir", "Non spécifiée", "N/A", "En cours" ou équivalent. Les périodes ne doivent pas se chevaucher de façon incohérente : conserve les dates telles quelles, sans créer de recouvrement.

7. INTITULÉS HONNÊTES : N'ajoute JAMAIS "Lead", "Senior", "Principal", "Head" ou "Chef" à un intitulé si ce n'est pas EXACTEMENT le titre figurant dans le CV source. Conserve les intitulés d'origine tels quels.

8. VERBES D'ACTION : chaque bullet commence par un verbe d'action fort. En français, INFINITIF (ex: "Développer", "Concevoir"). En anglais, prétérit CV (ex: "Developed", "Led").

9. PAS D'INVENTION DE LIENS : si le candidat n'a pas fourni GitHub/Portfolio, laisse ces champs VIDES ("").

10. PAS D'ÉMOJIS. STRUCTURE ATS plate (Expérience, Formation, Compétences), pas de colonnes ni tableaux.

11. cv_json COMPLET et VALIDE : chaque expérience a title, company, start_date, end_date, bullets. Compétences en objet { "Catégorie": ["item1", "item2"] }. Formation avec degree, institution, year.

Tu produis "cv_json" pour génération PDF. Structure EXACTE requise :
{
  "full_name": "...",
  "title": "Titre du poste visé",
  "email": "...", "phone": "...", "location": "...", "linkedin": "...", "github": "...",
  "summary": "Résumé professionnel percutant et ultra-ciblé pour l'offre",
  "experiences": [ 
    {"title": "...", "company": "...", "start_date": "...", "end_date": "...", "location": "...", "bullets": ["...", "..."]}
  ],
  "projects": [
    {"name": "...", "description": "...", "bullets": ["..."]}
  ],
  "education": [
    {"degree": "...", "institution": "...", "year": "...", "location": "..."}
  ],
  "skills": {
    "Expertises Techniques": ["...", "..."],
    "Outils & Logiciels": ["...", "..."],
    "Soft Skills": ["...", "..."]
  },
  "languages": [{"language": "...", "proficiency": "..."}],
  "certifications": [{"name": "...", "issuer": "...", "year": "..."}]
}

FORMAT DE RÉPONSE OBLIGATOIRE :

---MARKDOWN---
[CV COMPLET EN MARKDOWN - PRO - SANS ÉMOJI]
---END MARKDOWN---

---JSON---
{"projects": [{"title": "...", "desc": "..."}], "cv_json": { ... STRUCTURE CI-DESSUS ... }}
---END JSON---
"""

        # Réponses du candidat = faits réels autorisés (chiffres, réalisations…)
        answers_block = ""
        answers_text = ""
        if answers:
            lines = []
            for a in answers:
                if not isinstance(a, dict):
                    continue
                q = str(a.get("question", "")).strip()
                r = str(a.get("answer", "")).strip()
                if r:
                    lines.append(f"- {q} → {r}")
                    answers_text += " " + r
            if lines:
                answers_block = (
                    "\n\nRÉPONSES DU CANDIDAT (SOURCE DE VÉRITÉ — utilise ces chiffres et faits "
                    "RÉELS pour rédiger les bullets ; n'invente RIEN au-delà de ces réponses et du CV) :\n"
                    + "\n".join(lines)
                )

        user_prompt = f"""
POSTE CIBLÉ : {job_title}
DESCRIPTION DE L'OFFRE :
{job_desc[:3000]}

CV SOURCE DU CANDIDAT (seule source de vérité pour l'identité, les dates, les intitulés et la formation — ne rien inventer) :
{cv_text[:8000]}{answers_block}

Produis un CV CIBLÉ pour ce poste : priorise et réorganise les expériences pertinentes, résume/omets le hors-sujet, applique la dégressivité (10-12 bullets max), quantifie au maximum 40% des bullets sans jamais inventer de chiffre (utilise en priorité les chiffres RÉELS fournis par le candidat), et recopie fidèlement les faits (dates, formation, intitulés). RÉDIGE DANS LA MÊME LANGUE que le CV source ci-dessus.
"""
        
        try:
            # Modèle rapide pour réduire le temps de traitement (flash) tout en gardant la qualité
            response = await self.generate_response(
                prompt=user_prompt,
                system=system_prompt,
                model="gemini-2.0-flash",
                max_tokens=8192
            )
            
            logger.debug(f"Adapt Raw Gemini response length: {len(response)}")
            
            markdown = ""
            projects = []
            cv_json = None

            # 1) Format délimité personnalisé : ---MARKDOWN--- ... ---END MARKDOWN---
            md_match = re.search(r'-{2,}\s*MARKDOWN\s*-{2,}\s*(.*?)\s*-{2,}\s*END\s*MARKDOWN\s*-{2,}', response, re.DOTALL | re.IGNORECASE)
            json_match = re.search(r'-{2,}\s*JSON\s*-{2,}\s*(.*?)\s*-{2,}\s*END\s*JSON\s*-{2,}', response, re.DOTALL | re.IGNORECASE)
            
            # Formats standards markdown/json
            md_block = re.search(r'```(?:markdown|md)?\s*\n(.*?)\n```', response, re.DOTALL | re.IGNORECASE)
            json_block = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL | re.IGNORECASE)

            if md_match:
                markdown = md_match.group(1).strip()
            elif md_block:
                markdown = md_block.group(1).strip()

            if json_match:
                try:
                    raw_json_str = json_match.group(1).strip()
                    if raw_json_str.startswith("```json"):
                        raw_json_str = raw_json_str[7:].strip()
                    if raw_json_str.endswith("```"):
                        raw_json_str = raw_json_str[:-3].strip()
                        
                    obj = json.loads(raw_json_str)
                    projects = obj.get("projects", [])
                    cv_json = obj.get("cv_json")
                except json.JSONDecodeError as e:
                    logger.warning(f"Erreur décodage JSON personnalisé: {e}")
            elif json_block:
                try:
                    obj = json.loads(json_block.group(1).strip())
                    projects = obj.get("projects", [])
                    cv_json = obj.get("cv_json")
                except json.JSONDecodeError as e:
                    logger.warning(f"Erreur décodage bloc JSON standard: {e}")

            clean_resp = response.replace("```json", "").replace("```markdown", "").replace("```", "").strip()

            # 2) Fallback : tout le texte en un seul JSON (ancien format)
            if not markdown and not projects:
                try:
                    data = json.loads(clean_resp)
                    markdown = data.get("markdown", "")
                    projects = data.get("projects", [])
                    cv_json = data.get("cv_json")
                except json.JSONDecodeError as je:
                    logger.warning("JSON invalide (%s). Extraction manuelle du markdown.", je)
                    markdown = _extract_markdown_from_broken_json(clean_resp)
                    if not markdown:
                        md_raw = re.search(r'"markdown"\s*:\s*"((?:[^"\\]|\\.)*)"', clean_resp, re.DOTALL)
                        if md_raw:
                            markdown = md_raw.group(1).replace('\\n', '\n').replace('\\"', '"')
                    proj_raw = re.search(r'"projects"\s*:\s*(\[[\s\S]*?\])\s*[,}]', clean_resp)
                    if proj_raw:
                        try:
                            projects = json.loads(proj_raw.group(1))
                        except json.JSONDecodeError:
                            pass

            if not markdown and not projects:
                logger.warning("Impossible d'extraire markdown ou projects de la réponse.")
                markdown = "## CV\n\nErreur de formatage de la réponse. Veuillez réessayer."

            if not cv_json and markdown:
                cv_json = _markdown_to_minimal_cv_json(markdown)

            # Garde-fous déterministes (dédup, plafonds, dates, titres, anti-fabrication).
            # La source inclut les réponses du candidat → leurs chiffres RÉELS sont conservés.
            if cv_json:
                try:
                    cv_json = _postprocess_cv_json(cv_json, cv_text + " " + answers_text)
                except Exception as pe:
                    logger.warning(f"Post-traitement cv_json ignoré: {pe}")

            return {"markdown": markdown, "projects": projects, "cv_json": cv_json}

        except Exception as e:
            logger.error(f"❌ Erreur critique CVAdapterAgent: {e}")
            return {
                "markdown": "## Résumé Temporaire\n\nUne erreur est survenue lors de l'adaptation avec Gemini 3. Veuillez réessayer.",
                "projects": [
                    {
                        "title": "Debug API",
                        "desc": "Le serveur IA a rencontré une surcharge ou une erreur de parsing."
                    }
                ]
            }
