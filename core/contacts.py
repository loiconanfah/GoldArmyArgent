"""
Gestionnaire du Carnet d'Adresses (Network Database)
Sauvegarde localement les contacts (Entreprise, Emails, Site Web) extraits lors des recherches, en utilisant SQLite.
"""
import os
import json
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime
from core.database import get_db_connection

class ContactsManager:
    def __init__(self):
        pass # La DB est auto-initialisée ailleurs

    def save_contact(self, company_name: str, site_url: str = "", emails: List[str] = None, source_job: str = "", category: str = "Réseau Général", phone: str = "", user_id: str = "system_user") -> bool:
        """
        Ajoute ou met à jour une entreprise dans le carnet SQLite.
        Fusionne les e-mails sans créer de doublons.
        """
        if not company_name or company_name.lower() in ["confidentiel", "anonyme"]:
            return False
            
        emails = set(emails) if emails else set()
        if not site_url and not emails:
            return False
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Chercher si l'entreprise existe (insensible à la casse)
            cursor.execute("SELECT * FROM contacts WHERE LOWER(company_name) = ? AND user_id = ?", (company_name.lower(), user_id))
            existing = cursor.fetchone()
            
            if existing:
                updated = False
                new_site_url = existing["site_url"]
                
                # Mise à jour du site Web
                if site_url and not existing["site_url"]:
                    new_site_url = site_url
                    updated = True
                    
                # Fusion des emails (désérialisation JSON -> maj -> sérialisation JSON)
                existing_emails = set()
                if existing["emails"]:
                    try:
                        existing_emails = set(json.loads(existing["emails"]))
                    except:
                        existing_emails = set(existing["emails"].split(",")) if existing["emails"] else set()
                        
                prev_len = len(existing_emails)
                existing_emails.update(emails)
                
                if len(existing_emails) > prev_len:
                    updated = True
                    
                if updated:
                    emails_json = json.dumps(list(existing_emails))
                    cursor.execute('''
                        UPDATE contacts 
                        SET site_url = ?, emails = ?, category = ?, phone = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (new_site_url, emails_json, category, phone, existing["id"]))
                    conn.commit()
                    logger.info(f"🔄 Contact SQLite mis à jour: {company_name}")
                    return True
            else:
                # Nouvel ajout
                contact_id = str(hash(company_name + datetime.now().isoformat()))[-8:]
                emails_json = json.dumps(list(emails))
                
                cursor.execute('''
                    INSERT INTO contacts (id, user_id, company_name, site_url, emails, source_job, category, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (contact_id, user_id, company_name, site_url, emails_json, source_job, category, phone))
                conn.commit()
                logger.info(f"💾 Nouveau contact SQLite enregistré: {company_name} ({category})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur DB SQLite (save_contact): {e}")
            if 'conn' in locals() and conn:
                conn.rollback()
        finally:
            if 'conn' in locals() and conn:
                conn.close()
                
        return False
        
    def get_all_contacts(self, user_id: str = "system_user") -> List[Dict]:
        """Récupère l'intégralité du carnet d'adresses SQLite."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE user_id = ? ORDER BY last_updated DESC", (user_id,))
            rows = cursor.fetchall()
            
            contacts = []
            for row in rows:
                contact = dict(row)
                # Parse le JSON des emails pour le frontend
                if contact["emails"]:
                    try:
                        contact["emails"] = json.loads(contact["emails"])
                    except:
                        contact["emails"] = contact["emails"].split(",")
                else:
                    contact["emails"] = []
                contacts.append(contact)
                
            return contacts
        except Exception as e:
            logger.error(f"❌ Erreur DB SQLite (get_all_contacts): {e}")
            return []
        finally:
            if 'conn' in locals() and conn:
                conn.close()

# Instance globale
contacts_manager = ContactsManager()
