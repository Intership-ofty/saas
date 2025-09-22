"""
Configuration du service de réconciliation
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configuration du service de réconciliation"""
    
    # Configuration de base
    service_name: str = "reconciliation-service"
    version: str = "1.0.0"
    debug: bool = False
    
    # Configuration de la base de données
    database_url: str = "postgresql://warehouse_user:warehouse_password@warehouse-service:5432/data_warehouse"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Configuration Zingg
    zingg_workspace: str = "/tmp/zingg_workspace"
    zingg_model_path: str = "/tmp/zingg_models"
    default_similarity_threshold: float = 0.8
    max_batch_size: int = 10000
    
    # Configuration du matching
    matching_algorithm: str = "fuzzy"
    similarity_fields_weight: Dict[str, float] = {
        "name": 0.4,
        "email": 0.3,
        "phone": 0.2,
        "address": 0.1
    }
    
    # Configuration de la fusion
    merge_strategies: List[str] = ["latest_wins", "first_wins", "concatenate"]
    default_merge_strategy: str = "latest_wins"
    
    # Configuration de performance
    max_concurrent_matches: int = 1000
    similarity_cache_size: int = 10000
    batch_processing_size: int = 500
    
    # Configuration de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuration de monitoring
    metrics_enabled: bool = True
    health_check_interval: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()
