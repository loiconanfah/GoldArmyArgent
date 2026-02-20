# 🎯 Agent de Recherche d'Emploi - Guide d'Utilisation

## ✅ Agent JobSearcher Créé !

L'agent **JobSearcher** est maintenant opérationnel ! Il peut :
- ✅ Analyser un CV (compétences, expérience, formation, langues)
- ✅ Rechercher des offres de stage en informatique au Québec
- ✅ Calculer un score de compatibilité (0-100%)
- ✅ Utiliser Ollama pour justifier les matchs
- ✅ Trier les offres par pertinence

---

## 🚀 Utilisation

### Test Rapide

```powershell
cd d:\GoldArmyArgent
python test_job_search.py
```

Ce script utilise un CV d'exemple et recherche des stages au Québec.

### Personnaliser la Recherche

Modifie `test_job_search.py` pour utiliser ton propre CV :

```python
# Remplace EXEMPLE_CV par ton CV
MON_CV = """
[Ton nom]
[Ta formation]

COMPÉTENCES:
- [Tes compétences]

EXPÉRIENCE:
- [Ton expérience]

LANGUES:
- [Tes langues]
"""

# Modifie les filtres
task = {
    "id": "job-search-001",
    "description": "Rechercher des stages adaptés à mon profil",
    "agent_type": "job_searcher",
    "cv_text": MON_CV,
    "filters": {
        "location": "Québec",  # ou "Montréal", "Remote"
        "job_type": "stage",
        "domain": "informatique"
    }
}
```

---

## 📊 Comment Fonctionne le Matching

### Score de Compatibilité (0-100%)

L'agent calcule un score basé sur :

| Critère | Poids | Description |
|---------|-------|-------------|
| **Compétences** | 40% | Compétences techniques matchées |
| **Expérience** | 25% | Années d'expérience vs requis |
| **Formation** | 20% | Niveau d'éducation |
| **Localisation** | 10% | Québec, Montréal, Remote |
| **Langues** | 5% | Français, Anglais |

### Exemple de Résultat

```
1. Stage en développement web - Python/React
   📍 TechCorp Québec - Québec
   🎯 Score de compatibilité: 85%
   ✅ Compétences matchées: python, react, javascript, sql, git
   💡 Ce profil correspond bien car il possède Python et React...
   🔗 https://example.com/job1
```

---

## 🧠 Analyse de CV

L'agent extrait automatiquement :

### Compétences Techniques
- Langages de programmation (Python, Java, JavaScript, etc.)
- Frameworks (React, Django, Spring, etc.)
- Outils (Git, Docker, AWS, etc.)
- Bases de données (SQL, MongoDB, etc.)

### Expérience
- Détecte les patterns : "2 ans d'expérience", "3 years experience"
- Par défaut : 0 an (débutant)

### Formation
- Détecte : Doctorat, Maîtrise, Baccalauréat, DEC
- Mots-clés : PhD, Master, Bachelor, Collégial

### Langues
- Détecte : Français, Anglais, Espagnol
- Par défaut : Français (pour le Québec)

---

## 📝 Offres de Test Disponibles

L'agent utilise actuellement 5 offres de test :

1. **Stage développement web** - Python/React (Québec)
2. **Stagiaire développeur Java** (Montréal)
3. **Stage science des données** - ML/Python (Québec)
4. **Développeur mobile** - iOS/Android (Québec)
5. **Stage DevOps** - Docker/Kubernetes (Remote)

---

## 🔮 Prochaines Améliorations

### Phase 2 : Recherche Réelle

Pour intégrer de vraies offres d'emploi :

```powershell
# Installer les dépendances
python -m pip install beautifulsoup4 selenium requests
```

Puis ajouter dans `tools/web_scraper.py` :
- Scraping Indeed Canada
- API LinkedIn Jobs
- Jobboom (Québec)
- Emploi Québec

### Phase 3 : Parsing de CV

Pour supporter différents formats :

```powershell
# Installer les parsers
python -m pip install pypdf2 python-docx
```

Puis modifier `test_job_search.py` :
```python
# Charger depuis un fichier
with open("mon_cv.pdf", "rb") as f:
    cv_text = extract_text_from_pdf(f)
```

---

## 💡 Conseils pour un Meilleur CV

Pour maximiser les matchs :

### ✅ À Faire
- **Lister toutes les compétences techniques** (langages, frameworks, outils)
- **Quantifier l'expérience** ("2 ans", "6 mois de projet")
- **Mentionner la formation** clairement
- **Indiquer les langues** parlées

### ❌ À Éviter
- CV trop vague sans compétences spécifiques
- Oublier de mentionner les langues
- Ne pas quantifier l'expérience

### Exemple de Bon CV

```
COMPÉTENCES TECHNIQUES:
- Langages: Python, JavaScript, Java, SQL
- Frameworks: React, Flask, Spring Boot
- Outils: Git, Docker, Linux, VS Code
- Bases de données: PostgreSQL, MongoDB

EXPÉRIENCE:
- Projet universitaire (6 mois): Application web Python/React
- Stage (4 mois): Développement backend Java

FORMATION:
- Baccalauréat en informatique (en cours)

LANGUES:
- Français: Langue maternelle
- Anglais: Intermédiaire
```

---

## 🎓 Utilisation Programmatique

Tu peux aussi utiliser l'agent directement :

```python
from core.orchestrator import orchestrator
from agents import JobSearchAgent

async def search_jobs():
    await orchestrator.start()
    
    # Créer l'agent
    agent = await orchestrator.create_agent("job_searcher")
    
    # Créer la tâche
    task = {
        "id": "custom-search",
        "description": "Recherche personnalisée",
        "cv_text": "Mon CV...",
        "filters": {
            "location": "Québec",
            "job_type": "stage",
            "domain": "informatique"
        }
    }
    
    # Exécuter
    result = await agent.execute_task(task)
    
    # Traiter les résultats
    for job in result["matched_jobs"]:
        print(f"{job['title']} - Score: {job['match_score']}%")
    
    await orchestrator.stop()
```

---

## 🆘 Dépannage

### Aucune offre trouvée
- Vérifie que ton CV contient des compétences techniques
- Assure-toi que les filtres correspondent à ton profil

### Scores trop bas
- Ajoute plus de compétences techniques dans ton CV
- Quantifie ton expérience ("X mois", "X ans")
- Mentionne ta formation

### Erreur lors de l'exécution
- Vérifie qu'Ollama tourne : `ollama list`
- Redémarre le test : `python test_job_search.py`

---

## 📚 Ressources

- [test_job_search.py](file:///d:/GoldArmyArgent/test_job_search.py) - Script de test
- [job_searcher.py](file:///d:/GoldArmyArgent/agents/job_searcher.py) - Code de l'agent
- [job_search_plan.md](file:///C:/Users/yayzo/.gemini/antigravity/brain/3ae29fc5-cd53-45a0-9c28-3be8b21c5abd/job_search_plan.md) - Plan d'implémentation

---

**Prêt à chercher ton stage de rêve au Québec ! 🎯🇨🇦**
