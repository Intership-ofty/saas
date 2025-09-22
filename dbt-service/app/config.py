"""
Configuration du service DBT
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuration du service"""
    
    # Configuration de base
    service_name: str = "dbt-transformation-service"
    version: str = "1.0.0"
    debug: bool = False
    
    # Configuration de la base de données
    database_url: str = "postgresql://warehouse_user:warehouse_password@warehouse-service:5432/data_warehouse"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Configuration des transformations
    max_transformation_time: int = 300  # 5 minutes
    max_data_size_mb: int = 100  # 100 MB
    default_chunk_size: int = 1000
    
    # Configuration des KPI
    kpi_cache_ttl: int = 3600  # 1 heure
    max_kpi_metrics: int = 50
    
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
