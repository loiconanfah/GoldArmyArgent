import os

tools_dir = r"d:\GoldArmyArgent\tools"
for f in os.listdir(tools_dir):
    if f.endswith(".py"):
        path = os.path.join(tools_dir, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            
        new_content = content.replace('"location": location,', '"location": "Non spécifié",')
        new_content = new_content.replace('"location": loc,', '"location": "Non spécifié",')
        
        if content != new_content:
            with open(path, "w", encoding="utf-8") as file:
                file.write(new_content)
                print(f"Patched {f}")
