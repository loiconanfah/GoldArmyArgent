import json
import os

def update_json(path, data_to_add):
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # Merge nested dictionaries
    def deep_update(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    deep_update(content, data_to_add)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

fr_data = {
    "agent_chat": {
        "title": "Mentor IA",
        "tagline": "Préparez votre succès",
        "initial_message": "Bonjour ! Je suis votre Mentor IA. Comment puis-je vous aider aujourd'hui ? Je peux auditer votre CV, simuler un entretien ou générer votre portfolio.",
        "placeholders": {
            "location": "Localisation (facultatif)",
            "message": "Tapez votre message ici..."
        },
        "audit": {
            "candidate": "Candidat",
            "title": "Titre",
            "ats_report": "Rapport ATS",
            "global_score": "Score Global",
            "good_profile": "✅ Bon profil ATS",
            "to_improve": "⚠️ Profil à optimiser",
            "risk_rejection": "❌ Risque de rejet",
            "initial_flaws": "Défauts Initiaux",
            "critical_flaws": "Failles Critiques",
            "priority_actions": "🛠️ Actions Prioritaires",
            "missing_tech": "Technologies Manquantes",
            "strengths": "Points Forts",
            "transformations_impact": "Impact des Transformations",
            "flaw": "Défaut",
            "impact": "Impact",
            "choose_template": "Choisir un Modèle de CV",
            "generating_file": "Génération du fichier...",
            "download_cv": "Télécharger le CV Corrigé",
            "download_cv_rewritten": "Télécharger le CV Réécrit",
            "ats_friendly": "Format 100% compatible ATS (.docx)",
            "categories": {
                "keywords": "Mots-clés",
                "impact": "Impact & Résultats",
                "formatting": "Mise en forme",
                "readability": "Lisibilité",
                "relevance": "Pertinence Exp."
            }
        },
        "workspace": {
            "new_project": "Nouveau Projet",
            "restored_project": "Projet Portfolio (Restauré)",
            "app": "Application",
            "code": "Code",
            "terminal": "Terminal",
            "save": "Enregistrer",
            "saving": "Enregistrement...",
            "zip": "Exporter ZIP",
            "deploy": "Déployer",
            "soon": "Bientôt"
        },
        "terminal": {
            "init": "Initialisation du moteur de rendu GoldArmy...",
            "build_success": "Build terminé avec succès en 1.2s.",
            "listening": "Serveur à l'écoute sur http://localhost:3000"
        }
    },
    "common": {
        "detail_by_category": "Détail par catégorie"
    }
}

en_data = {
    "agent_chat": {
        "title": "AI Mentor",
        "tagline": "Prepare for success",
        "initial_message": "Hello! I am your AI Mentor. How can I help you today? I can audit your resume, simulate an interview, or generate your portfolio.",
        "placeholders": {
            "location": "Location (optional)",
            "message": "Type your message here..."
        },
        "audit": {
            "candidate": "Candidate",
            "title": "Title",
            "ats_report": "ATS Report",
            "global_score": "Global Score",
            "good_profile": "✅ Good ATS Profile",
            "to_improve": "⚠️ Profile to optimize",
            "risk_rejection": "❌ Rejection Risk",
            "initial_flaws": "Initial Flaws",
            "critical_flaws": "Critical Flaws",
            "priority_actions": "🛠️ Priority Actions",
            "missing_tech": "Missing Technologies",
            "strengths": "Strengths",
            "transformations_impact": "Transformations Impact",
            "flaw": "Flaw",
            "impact": "Impact",
            "choose_template": "Choose Resume Template",
            "generating_file": "Generating file...",
            "download_cv": "Download Corrected Resume",
            "download_cv_rewritten": "Download Rewritten Resume",
            "ats_friendly": "100% ATS-friendly format (.docx)",
            "categories": {
                "keywords": "Keywords",
                "impact": "Impact & Results",
                "formatting": "Formatting",
                "readability": "Readability",
                "relevance": "Exp. Relevance"
            }
        },
        "workspace": {
            "new_project": "New Project",
            "restored_project": "Portfolio Project (Restored)",
            "app": "App",
            "code": "Code",
            "terminal": "Terminal",
            "save": "Save",
            "saving": "Saving...",
            "zip": "Export ZIP",
            "deploy": "Deploy",
            "soon": "Soon"
        },
        "terminal": {
            "init": "Initializing GoldArmy rendering engine...",
            "build_success": "Build completed successfully in 1.2s.",
            "listening": "Server listening on http://localhost:3000"
        }
    },
    "common": {
        "detail_by_category": "Detail by category"
    }
}

update_json('c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/fr.json', fr_data)
update_json('c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/en.json', en_data)
print("done")
