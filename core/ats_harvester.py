"""Harvester « Direct-to-Company » : récupère les offres directement depuis les
ATS des entreprises (offres souvent absentes des plateformes d'agrégation).

Connecteurs à API publiques gratuites (sans clé) : Greenhouse, Lever, Ashby,
SmartRecruiters, Recruitee, Workable. On génère des slugs candidats à partir du
nom d'entreprise et on sonde chaque ATS jusqu'à trouver le bon.

Tout est best-effort : la moindre erreur réseau est avalée, jamais bloquante.
"""
import re
import asyncio
import unicodedata
from loguru import logger

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

_TIMEOUT = 3.5
_HEADERS = {"User-Agent": "GoldArmyBot/1.0 (+https://goldarmyai.com)"}

# Socle d'entreprises à FORT volume d'offres sur des ATS publics (Greenhouse/Lever/
# Ashby/…). Sert à garantir un plancher d'offres « direct-employeur » quand la
# recherche seule n'en remonte pas assez. Le slug-prober résout l'ATS de chacune.
_SEED_COMPANIES = [
    "Stripe", "Airbnb", "Dropbox", "Coinbase", "DoorDash", "Instacart", "Robinhood",
    "Pinterest", "Reddit", "Discord", "Figma", "Ramp", "Brex", "Plaid", "Datadog",
    "GitLab", "Notion", "Airtable", "Asana", "Twilio", "Cloudflare", "Lightspeed",
    "Wealthsimple", "Coveo", "Hopper", "Nuvei", "Squarespace", "Affirm",
]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def slug_candidates(company: str) -> list:
    """Génère des slugs plausibles à partir d'un nom d'entreprise."""
    base = _norm(company)
    base = re.sub(r"\b(inc|ltd|llc|corp|co|sa|sas|sarl|gmbh|group|groupe|technologies|technologie|solutions|inc\.)\b", "", base)
    base = re.sub(r"[^a-z0-9 ]", " ", base).strip()
    words = [w for w in base.split() if w]
    if not words:
        return []
    joined = "".join(words)
    hyphen = "-".join(words)
    out = []
    for c in (joined, hyphen, words[0]):
        if c and c not in out:
            out.append(c)
    return out[:3]


def detect_source(url: str) -> str:
    """Déduit la plateforme d'origine d'une offre à partir de son URL."""
    u = (url or "").lower()
    if not u:
        return "other"
    if "linkedin." in u:
        return "linkedin"
    if "indeed." in u:
        return "indeed"
    if "glassdoor." in u:
        return "glassdoor"
    if "jobillico." in u:
        return "jobillico"
    if "jooble." in u:
        return "jooble"
    if "welcometothejungle" in u or "wttj" in u:
        return "wttj"
    if any(a in u for a in ("greenhouse.io", "lever.co", "ashbyhq", "smartrecruiters", "recruitee", "workable", "myworkdayjobs", "teamtailor")):
        return "direct"
    return "other"


def _match_loc(text: str, location: str) -> bool:
    if not location:
        return True
    loc = _norm(location).split(",")[0].strip()
    return not loc or loc in _norm(text)


# ── Connecteurs ATS (retournent des offres normalisées) ──────────────────────

async def _greenhouse(client, slug, company):
    r = await client.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", params={"content": "true"})
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("jobs") or []
    if not jobs:
        return None
    out = []
    for j in jobs:
        out.append({"title": j.get("title", ""), "company": company or slug,
                    "location": (j.get("location") or {}).get("name", ""),
                    "url": j.get("absolute_url", ""),
                    "description": re.sub(r"<[^>]+>", " ", j.get("content", "") or "")[:1500],
                    "source": "direct", "ats": "greenhouse"})
    return out


async def _lever(client, slug, company):
    r = await client.get(f"https://api.lever.co/v0/postings/{slug}", params={"mode": "json"})
    if r.status_code != 200:
        return None
    data = r.json()
    if not isinstance(data, list) or not data:
        return None
    out = []
    for j in data:
        cats = j.get("categories") or {}
        out.append({"title": j.get("text", ""), "company": company or slug,
                    "location": cats.get("location", ""),
                    "url": j.get("hostedUrl", ""),
                    "description": (j.get("descriptionPlain") or "")[:1500],
                    "source": "direct", "ats": "lever"})
    return out


async def _ashby(client, slug, company):
    r = await client.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("jobs") or []
    if not jobs:
        return None
    out = []
    for j in jobs:
        out.append({"title": j.get("title", ""), "company": company or slug,
                    "location": j.get("location", "") or j.get("locationName", ""),
                    "url": j.get("jobUrl", "") or j.get("applyUrl", ""),
                    "description": (j.get("descriptionPlain") or "")[:1500],
                    "source": "direct", "ats": "ashby"})
    return out


async def _smartrecruiters(client, slug, company):
    r = await client.get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings")
    if r.status_code != 200:
        return None
    data = r.json()
    postings = data.get("content") or []
    if not postings:
        return None
    out = []
    for j in postings:
        loc = j.get("location") or {}
        out.append({"title": j.get("name", ""), "company": company or slug,
                    "location": ", ".join(filter(None, [loc.get("city"), loc.get("country")])),
                    "url": f"https://jobs.smartrecruiters.com/{slug}/{j.get('id','')}",
                    "description": "", "source": "direct", "ats": "smartrecruiters"})
    return out


async def _recruitee(client, slug, company):
    r = await client.get(f"https://{slug}.recruitee.com/api/offers/")
    if r.status_code != 200:
        return None
    data = r.json()
    offers = data.get("offers") or []
    if not offers:
        return None
    out = []
    for j in offers:
        out.append({"title": j.get("title", ""), "company": company or slug,
                    "location": j.get("location", "") or j.get("city", ""),
                    "url": j.get("careers_url", "") or j.get("url", ""),
                    "description": re.sub(r"<[^>]+>", " ", j.get("description", "") or "")[:1500],
                    "source": "direct", "ats": "recruitee"})
    return out


async def _workable(client, slug, company):
    r = await client.get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}", params={"details": "true"})
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("jobs") or []
    if not jobs:
        return None
    out = []
    for j in jobs:
        out.append({"title": j.get("title", ""), "company": company or slug,
                    "location": ", ".join(filter(None, [j.get("city"), j.get("country")])),
                    "url": j.get("url", "") or j.get("shortlink", ""),
                    "description": (j.get("description") or "")[:1500],
                    "source": "direct", "ats": "workable"})
    return out


_CONNECTORS = [_greenhouse, _lever, _ashby, _smartrecruiters, _recruitee, _workable]


async def harvest_company(client, company: str):
    """Sonde les ATS pour une entreprise (tous les slugs × ATS en CONCURRENCE) ;
    renvoie les offres du premier ATS qui répond."""
    tasks = []
    for slug in slug_candidates(company)[:2]:
        for connector in _CONNECTORS:
            tasks.append(connector(client, slug, company))
    if not tasks:
        return []
    for res in await asyncio.gather(*tasks, return_exceptions=True):
        if isinstance(res, list) and res:
            return res
    return []


async def harvest_companies(companies, keywords=None, location=None,
                            min_target=0, max_companies=25, max_jobs=150):
    """Récupère les offres directes pour une liste d'entreprises (best-effort).

    Si min_target > 0, complète avec un socle d'entreprises à fort volume pour
    garantir un plancher d'offres, en priorisant : (1) mot-clé + lieu,
    (2) mot-clé seul, (3) n'importe quelle offre directe — jusqu'à atteindre min_target.
    """
    if not httpx:
        return []
    companies = [c for c in dict.fromkeys([c.strip() for c in (companies or []) if c and c.strip()])][:max_companies]
    pool = list(companies)
    if min_target:
        for c in _SEED_COMPANIES:
            if c.lower() not in [x.lower() for x in pool]:
                pool.append(c)
    if not pool:
        return []

    kw = [_norm(k) for k in (keywords or []) if k and len(k) > 1]
    all_jobs, seen = [], set()
    try:
        limits = httpx.Limits(max_connections=40, max_keepalive_connections=20)
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True, limits=limits) as client:
            results = await asyncio.gather(*[harvest_company(client, c) for c in pool], return_exceptions=True)
        for res in results:
            if not isinstance(res, list):
                continue
            for j in res:
                if not (j.get("title") and j.get("url")):
                    continue
                key = f"{_norm(j.get('title',''))}-{_norm(j.get('company',''))}"
                if key in seen:
                    continue
                seen.add(key)
                all_jobs.append(j)
    except Exception as e:
        logger.warning(f"[ATS] harvest_companies échec: {e}")

    def _kw_ok(j):
        if not kw:
            return True
        return any(k in _norm(f"{j.get('title','')} {j.get('description','')}") for k in kw)

    def _loc_ok(j):
        return _match_loc(f"{j.get('location','')} {j.get('description','')}", location)

    # Tier 1 : mot-clé + lieu
    picked, used = [], set()
    for j in all_jobs:
        if _kw_ok(j) and _loc_ok(j):
            picked.append(j); used.add(id(j))
    # Tier 2 : mot-clé seul (lieu relâché) pour atteindre le plancher
    if len(picked) < min_target:
        for j in all_jobs:
            if id(j) in used:
                continue
            if _kw_ok(j):
                picked.append(j); used.add(id(j))
                if len(picked) >= min_target:
                    break
    # Tier 3 : n'importe quelle offre directe pour honorer le plancher demandé
    if len(picked) < min_target:
        for j in all_jobs:
            if id(j) in used:
                continue
            picked.append(j); used.add(id(j))
            if len(picked) >= min_target:
                break

    logger.info(f"[ATS] {len(all_jobs)} offres directes récupérées → {len(picked)} retenues (plancher {min_target})")
    return picked[:max_jobs]
