# 🌐 Recherche Web Activée !

## ✅ L'Agent Peut Maintenant Chercher sur Internet !

Ton **JobSearchAgent** peut maintenant chercher de **vraies offres d'emploi** sur internet ! 🎉

### Sites Supportés

- ✅ **Indeed Canada** - Plus grand site d'emploi
- ✅ **Jobboom** - Spécialisé Québec
- 🔄 **Fallback automatique** - Données de test si problème

---

## 🚀 Utilisation

### Recherche Web Réelle

```powershell
cd d:\GoldArmyArgent
python test_web_search.py
```

L'agent va :
1. 🌐 Chercher sur Indeed Canada
2. 🌐 Chercher sur Jobboom
3. 🎯 Matcher les offres avec ton CV
4. 📊 Trier par score de compatibilité

### Avec Ton CV

Modifie `test_web_search.py` :

```python
MON_CV = """
[Ton nom]
[Tes compétences: Python, React, etc.]
[Ton expérience]
[Ta formation]
"""

task = {
    "cv_text": MON_CV,
    "filters": {
        "location": "Québec",  # ou "Montréal"
        "job_type": "stage",
        "domain": "informatique"
    }
}
```

---

## 📊 Exemple de Résultat

```
🌐 Recherche sur Indeed et Jobboom...
📍 Localisation: Québec
🎯 Type: stage

✅ 15 offres trouvées
🎯 Top 5 recommandations:

1. Stage développeur Python - Startup Tech
   📍 TechCorp - Québec
   🎯 Score: 92%
   🌐 Source: Indeed
   🔗 https://ca.indeed.com/viewjob?jk=abc123...

2. Stagiaire développement web
   📍 WebAgency - Montréal
   🎯 Score: 85%
   🌐 Source: Jobboom
   🔗 https://www.jobboom.com/emploi/...
```

---

## ⚙️ Installation (Optionnel)

Si beautifulsoup4 n'est pas installé, l'agent utilisera les données de test.

Pour activer la recherche web :

```powershell
# Essayer d'installer (si pip fonctionne)
python -m pip install beautifulsoup4 requests lxml

# OU télécharger manuellement les wheels depuis PyPI
```

### Vérifier si Web Search est Actif

Lance le test - tu verras :
- ✅ **"🌐 Recherche web activée"** → Web search fonctionne
- ⚠️ **"📦 Utilisation des offres de test"** → Fallback aux données de test

---

## 🔍 Comment Ça Marche

### 1. Recherche Indeed

```python
# Construit l'URL
url = "https://ca.indeed.com/jobs?q=stage+informatique&l=Québec"

# Parse les résultats
- Titre du poste
- Entreprise
- Localisation
- Description
- Lien vers l'offre
```

### 2. Recherche Jobboom

```python
# URL Jobboom (spécialisé Québec)
url = "https://www.jobboom.com/recherche/emplois?keywords=..."

# Extrait les offres québécoises
```

### 3. Extraction de Compétences

L'agent extrait automatiquement les compétences des descriptions :
- Langages : Python, Java, JavaScript, etc.
- Frameworks : React, Django, Spring, etc.
- Outils : Git, Docker, AWS, etc.

### 4. Matching Intelligent

Chaque offre est scorée (0-100%) selon :
- Compétences matchées
- Expérience requise vs profil
- Localisation
- Formation
- Langues

---

## 💡 Conseils

### Pour Plus de Résultats

1. **Varie les mots-clés** dans ton CV
2. **Mentionne plusieurs technologies**
3. **Utilise "Montréal"** pour plus d'offres
4. **Essaie "Remote"** pour télétravail

### Meilleurs Moments pour Chercher

- 🌅 **Matin** : Nouvelles offres postées
- 📅 **Lundi-Mercredi** : Plus d'activité
- 🎓 **Janvier-Avril** : Saison des stages d'été

---

## 🔮 Prochaines Améliorations

### Sites Additionnels

- LinkedIn Jobs API
- Emploi Québec
- Sites universitaires (Laval, McGill, etc.)
- Glassdoor Canada

### Fonctionnalités Avancées

- **Alertes** : Notification de nouvelles offres
- **Historique** : Suivi des candidatures
- **Auto-apply** : Candidature automatique (avec ton accord)
- **Analyse de salaire** : Comparer les offres

---

## 🆘 Dépannage

### Pas de résultats web

```
⚠️ Module web_searcher non disponible
```

**Solution** : beautifulsoup4 n'est pas installé. L'agent utilise les données de test.

### Timeout

```
⏱️ Timeout Indeed
```

**Solution** : Connexion internet lente. Réessaye ou utilise les données de test.

### Erreur de parsing

```
⚠️ Erreur recherche web: ...
```

**Solution** : Le site a changé sa structure. L'agent utilise le fallback.

---

## 📚 Fichiers Créés

- [test_web_search.py](file:///d:/GoldArmyArgent/test_web_search.py) - Test recherche web
- [web_searcher.py](file:///d:/GoldArmyArgent/tools/web_searcher.py) - Outil de scraping
- [job_searcher.py](file:///d:/GoldArmyArgent/agents/job_searcher.py) - Agent mis à jour

---

**Ton agent peut maintenant chercher de VRAIES offres sur internet ! 🌐🎯**
