import json
import re
from loguru import logger
from typing import Dict, Any

from core.agent_base import BaseAgent


def _markdown_to_minimal_cv_json(markdown: str) -> Dict[str, Any]:
    """Fallback : construit une structure cv_json minimale à partir du markdown (sans titre 'Résumé adapté')."""
    lines = [s.strip() for s in (markdown or "").split("\n") if s.strip()]
    name = lines[0].replace("#", "").strip() if lines else "Candidat"
    return {
        "full_name": name,
        "summary": "",
        "experiences": [{"title": "Expérience professionnelle", "company": "", "start_date": "", "end_date": "", "bullets": lines}],
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
        
    async def adapt(self, job_title: str, job_desc: str, cv_text: str) -> Dict[str, Any]:
        """
        Analyse l'offre et le CV, puis génère un CV adapté en Markdown 
        et des projets recommandés en JSON.
        """
        
        system_prompt = """Tu es un expert en recrutement. Tu adaptes le CV à une offre en CONSERVANT tout et en AJOUTANT uniquement ce qui manque.

RÈGLES OBLIGATOIRES :
1. NE SUPPRIME RIEN du CV. Le "markdown" doit contenir l'intégralité du CV (identité, expériences, compétences, formation, projets) — chaque section et paragraphe du candidat doit apparaître.
2. N'AJOUTE JAMAIS de section ni de titre du type "Résumé adapté à l'offre", "Profil ciblé", "Profil ciblé pour ce poste", "Résumé adapté", etc. Aucune inscription de ce genre dans le CV. Enrichis uniquement le contenu EXISTANT (bullet points, phrases) avec les mots-clés de l'offre.
3. Pour correspondre à l'offre : insère les mots-clés dans les sections existantes, reformule légèrement une phrase pour y intégrer un terme de l'offre, sans créer de nouvelle section générique.

Tu dois aussi produire "cv_json" pour un PDF bien structuré. Structure EXACTE requise :
{
  "full_name": "...",
  "title": "Titre du poste visé",
  "email": "...", "phone": "...", "location": "...", "linkedin": "...", "github": "...",
  "summary": "Résumé de profil enrichi",
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
    "Catégorie (ex: Langages)": ["Compétence 1", "Compétence 2"]
  },
  "languages": [{"language": "Anglais", "proficiency": "Courant"}],
  "certifications": [{"name": "...", "issuer": "...", "year": "..."}]
}

FORMAT DE RÉPONSE OBLIGATOIRE (pour éviter les erreurs d'échappement JSON) :

---MARKDOWN---
[Écris ici le CV COMPLET en markdown, tout le contenu conservé + enrichissements. Pas de délimiteurs à l'intérieur.]
---END MARKDOWN---

---JSON---
{"projects": [{"title": "...", "desc": "..."}], "cv_json": { ... STRUCTURE CI-DESSUS ... }}
---END JSON---

Important : le CV markdown va entre ---MARKDOWN--- et ---END MARKDOWN--- (pas dans une chaîne JSON). Le JSON (projects + cv_json) va entre ---JSON--- et ---END JSON---. Échappe correctement les guillemets dans le JSON (pas de retours à la ligne bruts dans les chaînes).
"""

        user_prompt = f"""
OFFRE : {job_title}
DESCRIPTION DE L'OFFRE :
{job_desc[:3000]}

CV DU CANDIDAT (à adapter sans rien retirer, sans ajouter de section "Résumé adapté" ou "Profil ciblé") :
{cv_text[:5000]}

Produis la réponse en 2 blocs : (1) Entre ---MARKDOWN--- et ---END MARKDOWN--- : le CV COMPLET en markdown. (2) Entre ---JSON--- et ---END JSON--- : un seul objet JSON avec "projects" et "cv_json". Aucun titre "Résumé adapté à l'offre" dans le CV.
"""
        
        try:
            # We explicitly use gemini by forcing the model tag or relying on UnifiedClient priority
            # Increased max_tokens to 8192 to prevent the massive JSON payload from dropping midway
            response = await self.generate_response(
                prompt=user_prompt, 
                system=system_prompt, 
                model="gemini-3.1-pro-preview",
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
