import os

files = [
    'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Mentor.vue',
    'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content.replace('/logo_ga.png', '/logo.png')
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")
        else:
            print(f"No change for {file_path}")
    else:
        print(f"File not found: {file_path}")
