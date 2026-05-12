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
        "preview": {
            "title": "Aperçu du CV"
        }
    }
}

en_data = {
    "agent_chat": {
        "preview": {
            "title": "Resume Preview"
        }
    }
}

update_json('c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/fr.json', fr_data)
update_json('c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/en.json', en_data)
print("done")
