"""Configuration centrale pour GoldArmyArgent."""
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration globale du système."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Ollama Configuration
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama API host")
    ollama_default_model: str = Field(default="llama3", description="Modèle par défaut")

    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(default=None, description="Clé API OpenRouter")
    openrouter_default_model: str = Field(default="mistralai/mistral-7b-instruct:free", description="Modèle par défaut OpenRouter")

    # Gemini Configuration
    gemini_api_key: Optional[str] = Field(default=None, description="Clé API Gemini")

    # Job Search APIs
    jooble_api_key: Optional[str] = Field(default="ee1009c8-7eb3-4e21-a7f6-4422bc8913ca", description="Clé API Jooble")
    rapidapi_key: Optional[str] = Field(default=None, description="Clé RapidAPI (JSearch/Glassdoor)")
    rapidapi_key_2: Optional[str] = Field(default="7e5b3739f9mshf676fb3b9e1dac4p1db4e8jsne93476e3132a", description="Clé RapidAPI Secondaire (JSearch)")
    findwork_api_key: Optional[str] = Field(default="b3daabb0d2e934cdc7c2c8c8d37ba85dd3a5bb6c", description="Clé API FindWork")
    rapidapi_host: str = Field(default="jsearch.p.rapidapi.com", description="RapidAPI Host JSearch")
    glassdoor_api_host: str = Field(default="glassdoor-real-time.p.rapidapi.com", description="RapidAPI Host Glassdoor")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    redis_enabled: bool = Field(default=False, description="Activer Redis")
    
    # ChromaDB Configuration
    chroma_persist_dir: Path = Field(default=Path("./storage/chroma_db"), description="ChromaDB persist directory")
    
    # Logging
    log_level: str = Field(default="INFO", description="Niveau de log")
    log_file: Path = Field(default=Path("./storage/logs/goldarmyargent.log"), description="Fichier de log")
    
    # Agent Configuration
    max_agents: int = Field(default=10, description="Nombre maximum d'agents simultanés")
    agent_timeout: int = Field(default=300, description="Timeout des agents en secondes")
    max_retries: int = Field(default=3, description="Nombre maximum de tentatives")
    
    # System
    debug: bool = Field(default=False, description="Mode debug")
    project_root: Path = Field(default=Path(__file__).parent.parent, description="Racine du projet")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Créer les répertoires nécessaires
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Instance globale
settings = Settings()
