import json
import os

def update_json(path, data_to_add):
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
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
        "cv_history": {
            "title": "Historique des CV",
            "no_history": "Aucun historique disponible.",
            "restore": "Restaurer",
            "current": "Actuel",
            "versions_desc": "Retrouvez vos 10 dernières versions analysées ou modifiées."
        },
        "view_history": "Voir l'historique"
    }
}

en_data = {
    "agent_chat": {
        "cv_history": {
            "title": "CV History",
            "no_history": "No history available.",
            "restore": "Restore",
            "current": "Current",
            "versions_desc": "Find your last 10 analyzed or modified versions."
        },
        "view_history": "View History"
    }
}

update_json('c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/fr.json', fr_data)
update_json('c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/en.json', en_data)
print("done")
