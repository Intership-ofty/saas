"""
Configuration du service de contrôle qualité
"""

from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    """Configuration du service de contrôle qualité"""
    
    # Configuration de base
    service_name: str = "quality-control-service"
    version: str = "1.0.0"
    debug: bool = False
    
    # Configuration de la base de données
    database_url: str = "postgresql://warehouse_user:warehouse_password@warehouse-service:5432/data_warehouse"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Configuration Soda
    soda_config_path: str = "/app/soda_config"
    soda_checks_path: str = "/app/soda_checks"
    
    # Configuration des seuils de qualité
    completeness_threshold: float = 90.0
    consistency_threshold: float = 95.0
    validity_threshold: float = 98.0
    duplicate_threshold: float = 0.9
    
    # Configuration de détection d'anomalies
    anomaly_contamination: float = 0.1
    anomaly_threshold: float = 0.5
    supported_anomaly_methods: List[str] = [
        "isolation_forest", 
        "local_outlier_factor", 
        "statistical", 
        "clustering"
    ]
    
    # Configuration des règles de validation
    email_regex: str = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_regex: str = r'^\+?[\d\s\-\(\)]{10,}$'
    date_formats: List[str] = [
        "%Y-%m-%d", 
        "%d/%m/%Y", 
        "%m/%d/%Y", 
        "%Y-%m-%d %H:%M:%S"
    ]
    
    # Configuration de performance
    max_batch_size: int = 10000
    quality_check_timeout: int = 300  # 5 minutes
    anomaly_detection_timeout: int = 600  # 10 minutes
    
    # Configuration de cache
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 heure
    max_cache_size: int = 1000
    
    # Configuration de reporting
    report_formats: List[str] = ["json", "html", "pdf"]
    default_report_format: str = "json"
    include_visualizations: bool = True
    
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
