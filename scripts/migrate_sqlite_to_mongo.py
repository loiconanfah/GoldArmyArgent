import sqlite3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Ajouter le dossier racine au path pour importer core.database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "goldarmy.db")

async def migrate():
    print("🚀 Début de la migration SQLite vers MongoDB...")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ Erreur: Base de données SQLite introuvable à {SQLITE_DB_PATH}")
        return

    # 1. Connexion SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("✅ Connecté à SQLite.")
    except Exception as e:
        print(f"❌ Erreur de connexion à SQLite: {e}")
        return

    # 2. Connexion MongoDB
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri)
        db = client[settings.mongodb_db_name]
        # Test connection
        await client.admin.command('ping')
        print(f"✅ Connecté à MongoDB Atlas (Database: {settings.mongodb_db_name}).")
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        return

    # --- Migration: USERS ---
    print("\n📦 Migration de la table 'users'...")
    cursor.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    
    if users:
        # Convert sqlite ID to MongoDB 'id' 
        # (we don't map to _id to avoid collision if they format it differently, keeping 'id' for app logic)
        try:
            # Clear existing to avoid duplicate emails if script ran twice
            await db.users.delete_many({"id": {"$in": [u["id"] for u in users]}})
            result = await db.users.insert_many(users)
            print(f"   ✅ {len(result.inserted_ids)} Utilisateurs migrés.")
        except Exception as e:
            print(f"   ❌ Erreur migration users: {e}")
    else:
        print("   ℹ️ Aucun utilisateur à migrer.")

    # --- Migration: CONTACTS ---
    print("\n📦 Migration de la table 'contacts'...")
    try:
        cursor.execute("SELECT * FROM contacts")
        contacts = [dict(row) for row in cursor.fetchall()]
        
        if contacts:
            # Contacts in SQLite were flat. MongoDB version uses '$addToSet' for emails array
            # We'll adapt them to match the new schema structure.
            adapted_contacts = []
            for c in contacts:
                adapted_c = c.copy()
                if "email" in adapted_c:
                    # Transform standard string email to emails array if not empty
                    email_val = adapted_c.pop("email", None)
                    adapted_c["emails"] = [email_val] if email_val else []
                # Same for phone/linkedin if they existed as string
                phone_val = adapted_c.pop("phone", None)
                adapted_c["phones"] = [phone_val] if phone_val else []
                linkedin_val = adapted_c.pop("linkedin", None)
                adapted_c["linkedins"] = [linkedin_val] if linkedin_val else []
                
                adapted_contacts.append(adapted_c)

            # Insert adapted
            await db.contacts.delete_many({"id": {"$in": [c["id"] for c in contacts]}})
            result = await db.contacts.insert_many(adapted_contacts)
            print(f"   ✅ {len(result.inserted_ids)} Contacts migrés.")
        else:
            print("   ℹ️ Aucun contact à migrer.")
    except sqlite3.OperationalError:
        print("   ℹ️ Table 'contacts' absente de SQLite.")

    # --- Migration: APPLICATIONS (CRM) ---
    print("\n📦 Migration de la table 'applications'...")
    try:
        cursor.execute("SELECT * FROM applications")
        apps = [dict(row) for row in cursor.fetchall()]
        
        if apps:
            await db.applications.delete_many({"id": {"$in": [a["id"] for a in apps]}})
            result = await db.applications.insert_many(apps)
            print(f"   ✅ {len(result.inserted_ids)} Candidatures migrées.")
        else:
            print("   ℹ️ Aucune candidature à migrer.")
    except sqlite3.OperationalError:
        print("   ℹ️ Table 'applications' absente.")

    # --- Migration: USAGE LOGS ---
    print("\n📦 Migration de la table 'usage_logs'...")
    try:
        cursor.execute("SELECT * FROM usage_logs")
        logs = [dict(row) for row in cursor.fetchall()]
        
        if logs:
            await db.usage_logs.delete_many({"id": {"$in": [l["id"] for l in logs]}})
            result = await db.usage_logs.insert_many(logs)
            print(f"   ✅ {len(result.inserted_ids)} Logs d'utilisation migrés.")
        else:
            print("   ℹ️ Aucun usage log à migrer.")
    except sqlite3.OperationalError:
        print("   ℹ️ Table 'usage_logs' absente.")


    conn.close()
    print("\n🎉 Migration terminée avec succès!")

if __name__ == "__main__":
    asyncio.run(migrate())
