from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional

class Settings(BaseSettings):
    # Core settings
    app_name: str = "olKAN"
    debug: bool = False
    storage_backend: str = "hybrid"
    data_dir: str = "data"
    
    # Database settings
    database_url: str = "sqlite:///./olkan.db"
    
    # AI/ML settings
    openai_api_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    openai_embedding_model: str = "text-embedding-ada-002"
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Weaviate settings
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Monitoring settings
    enable_monitoring: bool = False
    datadog_api_key: Optional[str] = None
    
    # Agent settings
    max_concurrent_agents: int = 10
    agent_task_timeout: int = 300  # 5 minutes
    
    # Quality assessment settings
    quality_assessment_enabled: bool = True
    quality_threshold: float = 0.7
    
    # Knowledge graph settings
    knowledge_graph_enabled: bool = True
    entity_extraction_enabled: bool = True
    relationship_mapping_enabled: bool = True

    @validator('debug', pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    @validator('quality_threshold')
    def validate_quality_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Quality threshold must be between 0.0 and 1.0')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
