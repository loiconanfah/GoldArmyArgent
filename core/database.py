"""
Core Database Manager pour GoldArmy Agent V2.
Fournit une connexion SQLite centralisée et initialise les tables du système (Carnet d'Adresses, CRM).
"""
import sqlite3
import os
from loguru import logger

DB_FILENAME = "goldarmy.db"
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
DB_PATH = os.path.join(STORAGE_DIR, DB_FILENAME)

def get_db_connection():
    """Retourne une connexion SQLite avec le format de dictionnaire (Row) optimisée pour la concurrence."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    # timeout: if DB is locked by another write, wait up to 5s instead of failing immediately
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    # Enable WAL mode for high concurrent read/writes
    conn.execute("PRAGMA journal_mode=WAL;")
    # Synchronous NORMAL for WAL provides good balance of safety and speed
    conn.execute("PRAGMA synchronous=NORMAL;")
    # Permet d'accéder aux colonnes par leur nom comme un dictionnaire
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise le schéma de la base de données (ex: création de tables)."""
    logger.info("🗄️ Initialisation de la base de données SQLite (SaaS)...")
    os.makedirs(STORAGE_DIR, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Table Users (Authentification)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                bio TEXT,
                cv_text TEXT,
                portfolio_url TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table Contacts (Carnet d'Adresses OSINT)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company_name TEXT NOT NULL,
                site_url TEXT,
                emails TEXT, -- Stocké en JSON string ou texte séparé par virgule
                source_job TEXT,
                category TEXT DEFAULT 'Non catégorisée',
                phone TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Migration: add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            logger.warning("Migration: Adding user_id to contacts table. Previous data might be orphaned.")
            cursor.execute("ALTER TABLE contacts ADD COLUMN user_id TEXT DEFAULT 'system_user'")
        if 'category' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN category TEXT DEFAULT 'Non catégorisée'")
        if 'phone' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN phone TEXT")
            
        # Index pour optimiser la recherche par nom d'entreprise et utilisateur
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_user_company ON contacts(user_id, company_name)')
        
        # Table pour le CRM (Suivi des candidatures)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company_name TEXT NOT NULL,
                url TEXT,
                reference TEXT,
                status TEXT DEFAULT 'TO_APPLY',
                applied_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Migration: add user_id column if it doesn't exist to applications
        cursor.execute("PRAGMA table_info(applications)")
        app_columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in app_columns:
            logger.warning("Migration: Adding user_id to applications table. Previous data might be orphaned.")
            cursor.execute("ALTER TABLE applications ADD COLUMN user_id TEXT DEFAULT 'system_user'")
            
        # Migration for users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        if 'full_name' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        if 'bio' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        if 'cv_text' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN cv_text TEXT")
        if 'portfolio_url' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN portfolio_url TEXT")
        if 'avatar_url' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        if 'subscription_tier' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'FREE'")
        if 'stripe_customer_id' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN stripe_customer_id TEXT")
        if 'stripe_subscription_id' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT")
        # Google OAuth migration
        if 'google_id' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
        # Make hashed_password nullable for Google OAuth users (SQLite doesn't allow ALTER COLUMN,
        # so the CREATE TABLE already uses NOT NULL; new rows from Google OAuth will use a placeholder)
            
        # Table Usage Logs (Pour l'enforcedement des limites SaaS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                feature TEXT NOT NULL, -- 'sniper_search', 'cv_audit', 'hr_interview', 'headhunter', 'cv_adaptation'
                used_at DATE DEFAULT CURRENT_DATE,
                count INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        # Index pour recherche rapide par utilisateur et date
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_user_feature_date ON usage_logs(user_id, feature, used_at)')

        conn.commit()
        logger.info("✅ Schéma DB SQLite vérifié et mis à jour pour SaaS multi-user.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de SQLite: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
