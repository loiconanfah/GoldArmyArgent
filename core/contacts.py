"""
Gestionnaire du Carnet d'Adresses (Network Database)
Sauvegarde localement les contacts (Entreprise, Emails, Site Web) extraits lors des recherches, en utilisant MongoDB Atlas.
"""
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime
from core.database import get_db
import uuid

class ContactsManager:
    def __init__(self):
        pass # La DB est auto-initialisée ailleurs

    async def save_contact(self, company_name: str, site_url: str = "", emails: List[str] = None, source_job: str = "", category: str = "Réseau Général", phone: str = "", user_id: str = "system_user") -> bool:
        """
        Ajoute ou met à jour une entreprise dans la collection MongoDB.
        Fusionne les e-mails sans créer de doublons.
        """
        if not company_name or company_name.lower() in ["confidentiel", "anonyme", "incognito", "non spécifié"]:
            return False

        emails_list = emails if emails else []
        if not site_url and not emails_list:
            return False
            
        try:
            db = get_db()
            
            # Recherche d'un contact existant (insensible à la casse sur company_name + même user_id)
            # MongoDB $regex allows case-insensitive search
            existing = await db.contacts.find_one({
                "company_name": {"$regex": f"^{company_name}$", "$options": "i"},
                "user_id": user_id
            })
            
            if existing:
                update_fields = {"last_updated": datetime.utcnow()}
                
                # Mise à jour du site Web si vide
                if site_url and not existing.get("site_url"):
                    update_fields["site_url"] = site_url
                
                if category and category != "Réseau Général":
                    update_fields["category"] = category
                    
                if phone and not existing.get("phone"):
                    update_fields["phone"] = phone
                    
                # Utilisation de $addToSet pour ajouter les emails (évite les doublons au niveau DB)
                update_query = {"$set": update_fields}
                if emails_list:
                    # Si on l'ajoute directement:
                    update_query["$addToSet"] = {"emails": {"$each": emails_list}}
                    
                await db.contacts.update_one({"_id": existing["_id"]}, update_query)
                logger.info(f"🔄 Contact MongoDB mis à jour: {company_name}")
                return True
                
            else:
                # Nouvel ajout
                contact_id = str(uuid.uuid4())
                new_contact = {
                    "id": contact_id,
                    "user_id": user_id,
                    "company_name": company_name,
                    "site_url": site_url,
                    "emails": emails_list,
                    "source_job": source_job,
                    "category": category,
                    "phone": phone,
                    "added_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow()
                }
                
                await db.contacts.insert_one(new_contact)
                logger.info(f"💾 Nouveau contact MongoDB enregistré: {company_name} ({category})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur MongoDB (save_contact): {e}")
            return False
        
    async def get_all_contacts(self, user_id: str = "system_user") -> List[Dict]:
        """Récupère l'intégralité du carnet d'adresses MongoDB."""
        try:
            db = get_db()
            cursor = db.contacts.find({"user_id": user_id}).sort("last_updated", -1)
            contacts = await cursor.to_list(length=None)
            
            # Formater l'_id BSON pour le frontend qui attend de l'ObjectId -> String
            for contact in contacts:
                contact["_id"] = str(contact["_id"])
                
            return contacts
        except Exception as e:
            logger.error(f"❌ Erreur MongoDB (get_all_contacts): {e}")
            return []

# Instance globale
contacts_manager = ContactsManager()

