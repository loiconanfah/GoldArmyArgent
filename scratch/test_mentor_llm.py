import os
import sys
import json
import asyncio

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.unified_client import UnifiedLLMClient
from config.settings import settings

async def run_test():
    client = UnifiedLLMClient()
    
    cv_text = """
    John Doe
    Développeur Python
    john.doe@email.com
    Expérience:
    - Développeur chez TechCorp (2020-2022)
    - Développeur chez WebSoft (2022-2024)
    Compétences: Python, Django, SQL
    """
    
    # Test Passe 1
    prompt_p1 = f"""Tu es l'Expert Recruteur Tech "GoldArmy Mentor" — mode Optimisation Triple Pass.
PHASE 1 : Diagnostic strict du CV original. Tu DOIS UNIQUEMENT évaluer le CV fourni et lister ses failles réelles. Ne génère AUCUN `cv_data`.

**RÈGLES D'OR ABSOLUES :**
1. **Score Honnête (Phase 1) :** Basé STRICTEMENT sur le CV fourni (généralement 25-55/100). Jamais inventé.
2. **JSON ATTENDU :**
{{
  "audit": {{
    "ats_score": 0,
    "candidate_name": "...",
    "candidate_title": "...",
    "scores": {{ "mots_cles": 0, "impact_resultats": 0, "mise_en_forme": 0, "lisibilite": 0, "experience_pertinence": 0 }},
    "failles": ["Failles trouvées dans le CV original"],
    "mot_cles_manquants": ["Mots-clés importants absents"]
  }}
}}

**CONTEXTE :**
{cv_text}
"""
    res1 = await client.generate(prompt_p1, model="google/gemini-2.5-flash")
    print("PASSE 1 RESPONSE:")
    print(res1)
    
    # Test Passe 3
    prompt_p3 = f"""Tu es l'Expert Recruteur Tech "GoldArmy Mentor" — mode Optimisation Triple Pass.
PHASE 3 : Vérification Finale & Mapping. Analyse le CV hyper-optimisé que tu viens de générer. Assure-toi qu'il corrige bien TOUTES les failles initiales : []. Génère le `correction_mapping` pour prouver tes actions. Évalue de manière stricte mais réaliste le NOUVEAU score ATS de ce CV généré (qui doit impérativement s'approcher de 100/100 vu les optimisations appliquées). NE REGÉNÈRE PAS LE CV.

**RÈGLES D'OR ABSOLUES :**
1. **JSON ATTENDU :**
{{
  "audit": {{
    "ats_score": 0,
    "scores": {{ "mots_cles": 0, "impact_resultats": 0, "mise_en_forme": 0, "lisibilite": 0, "experience_pertinence": 0 }},
    "correction_mapping": {{ "Faille identifiée dans l'original": "Solution appliquée dans le nouveau CV" }},
    "tech_ajoutees": ["Technologies ou mots-clés injectés"]
  }}
}}

**CONTEXTE :**
[PREVIOUS_DRAFT_JSON]
{{"cv_data": {{"full_name": "John Doe"}}}}
"""
    res3 = await client.generate(prompt_p3, model="google/gemini-2.5-flash")
    print("\nPASSE 3 RESPONSE:")
    print(res3)

if __name__ == "__main__":
    asyncio.run(run_test())
