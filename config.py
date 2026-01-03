# src/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application configuration with environment variables."""
    
    # API Keys
    openai_api_key: str
    
    # Optional: Azure Blob Storage
    blob_connection_string: str = ""
    blob_container_name: str = ""
    knowledge_blob_name: str = "faq.jsonl"
    
    # Model Configuration
    classifier_model: str = "gpt-4o-mini"
    generator_model: str = "gpt-4o-mini"
    quality_check_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    
    # Paths
    knowledge_base_path: str = "data/knowledge_base"
    vector_db_path: str = "data/vector_db"
    
    # Pipeline Settings
    retrieval_top_k: int = 3
    min_confidence_threshold: float = 0.7
    quality_score_threshold: int = 70
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
