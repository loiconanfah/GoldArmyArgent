import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/api/main.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the update_profile function
old_code = """@app.post("/api/profile")
async def update_profile(request: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    \"\"\"Met à jour les informations du profil utilisateur.\"\"\"
    from core.database import get_db
    db = get_db()
    try:
        fields = request.dict(exclude_unset=True)
        if not fields:
            return {"status": "success", "message": "Aucun champ à mettre à jour"}
        
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": fields}
        )
        return {"status": "success", "message": "Profil mis à jour avec succès"}"""

new_code = """@app.post("/api/profile")
async def update_profile(request: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    \"\"\"Met à jour les informations du profil utilisateur.\"\"\"
    from core.database import get_db
    from datetime import datetime
    db = get_db()
    try:
        fields = request.dict(exclude_unset=True)
        if not fields:
            return {"status": "success", "message": "Aucun champ à mettre à jour"}
        
        # --- LOGIQUE HISTORIQUE CV ---
        if "cv_text" in fields:
            old_user = await db.users.find_one({"id": current_user["id"]}, {"cv_text": 1})
            if old_user and old_user.get("cv_text") and old_user.get("cv_text") != fields["cv_text"]:
                history_entry = {
                    "cv_text": old_user["cv_text"],
                    "updated_at": datetime.utcnow().isoformat(),
                    "name": f"Version du {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
                }
                await db.users.update_one(
                    {"id": current_user["id"]},
                    {"$push": {"cv_history": {"$each": [history_entry], "$position": 0, "$slice": 10}}}
                )
        # -----------------------------

        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": fields}
        )
        return {"status": "success", "message": "Profil mis à jour avec succès"}"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("done")
else:
    # Try a more flexible match if whitespace differs
    print("Exact match failed, trying regex...")
    pattern = r'@app\.post\("/api/profile"\)\s+async def update_profile.*?await db\.users\.update_one\(.*?\)\s+return {"status": "success", "message": "Profil mis à jour avec succès"}'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_code + content[match.end():]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("done (regex)")
    else:
        print("Function not found")
