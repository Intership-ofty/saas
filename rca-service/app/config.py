"""
Configuration du service RCA
"""

from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    """Configuration du service RCA"""
    
    # Configuration de base
    service_name: str = "rca-service"
    version: str = "1.0.0"
    debug: bool = False
    
    # Configuration de la base de données
    database_url: str = "postgresql://warehouse_user:warehouse_password@warehouse-service:5432/data_warehouse"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Configuration RCA
    max_analysis_depth: int = 5
    default_analysis_depth: int = 3
    correlation_threshold: float = 0.7
    significance_threshold: float = 0.05
    
    # Configuration des algorithmes
    supported_correlation_methods: List[str] = ["pearson", "spearman", "kendall"]
    default_correlation_method: str = "pearson"
    
    supported_anomaly_methods: List[str] = [
        "statistical", 
        "isolation_forest", 
        "local_outlier_factor", 
        "one_class_svm"
    ]
    default_anomaly_method: str = "statistical"
    
    # Configuration des seuils
    anomaly_contamination: float = 0.1
    trend_significance_threshold: float = 0.05
    impact_threshold: float = 0.5
    
    # Configuration de performance
    max_batch_size: int = 10000
    analysis_timeout: int = 600  # 10 minutes
    correlation_timeout: int = 300  # 5 minutes
    
    # Configuration de cache
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 heure
    max_cache_size: int = 1000
    
    # Configuration de reporting
    report_formats: List[str] = ["json", "html", "pdf"]
    default_report_format: str = "json"
    include_visualizations: bool = True
    max_visualizations: int = 10
    
    # Configuration des modèles de prédiction
    prediction_models: List[str] = [
        "isolation_forest", 
        "local_outlier_factor", 
        "one_class_svm", 
        "statistical"
    ]
    default_prediction_model: str = "isolation_forest"
    prediction_threshold: float = 0.7
    
    # Configuration de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuration de monitoring
    metrics_enabled: bool = True
    health_check_interval: int = 30
    
    # Configuration des alertes
    alert_enabled: bool = True
    alert_thresholds: Dict[str, float] = {
        "high_risk": 0.8,
        "medium_risk": 0.6,
        "low_risk": 0.4
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()
