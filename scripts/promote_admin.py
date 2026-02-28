
import asyncio
import sys
import os

# Add the project root to sys.path to import core.database
sys.path.append(os.getcwd())

from core.database import get_db

async def promote_me():
    db = get_db()
    # On cherche le premier utilisateur créé
    user = await db.users.find_one({}, sort=[("created_at", 1)])
    if not user:
        print("Aucun utilisateur trouvé dans la base.")
        return
    
    email = user.get("email")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"subscription_tier": "ADMIN"}}
    )
    print(f"SUCCÈS : L'utilisateur {email} (ID: {user['id']}) est maintenant ADMIN.")
    print("Veuillez rafraîchir l'application pour voir la console Admin.")

if __name__ == "__main__":
    asyncio.run(promote_me())
