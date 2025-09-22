"""
Configuration du service API/Dashboard
"""

from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    """Configuration du service API/Dashboard"""
    
    # Configuration de base
    service_name: str = "api-dashboard-service"
    version: str = "1.0.0"
    debug: bool = False
    
    # Configuration de l'API
    api_title: str = "SaaS Data Platform API"
    api_description: str = "API principale pour la plateforme de données SaaS"
    api_version: str = "1.0.0"
    
    # Configuration de la base de données
    database_url: str = "postgresql://warehouse_user:warehouse_password@warehouse-service:5432/data_warehouse"
    database_pool_size: int = 20
    database_max_overflow: int = 30
    
    # Configuration des services
    nifi_service_url: str = "http://nifi-service:8080"
    dbt_service_url: str = "http://dbt-service:8001"
    reconciliation_service_url: str = "http://reconciliation-service:8002"
    quality_control_service_url: str = "http://quality-control-service:8003"
    rca_service_url: str = "http://rca-service:8004"
    warehouse_service_url: str = "postgresql://warehouse_user:warehouse_password@warehouse-service:5432/data_warehouse"
    
    # Configuration de l'authentification
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Configuration du dashboard
    dashboard_refresh_interval: int = 30
    max_widgets_per_dashboard: int = 20
    default_dashboard_layout: str = "grid"
    
    # Configuration des alertes
    alert_check_interval: int = 60  # secondes
    alert_retention_days: int = 30
    max_alerts_per_user: int = 1000
    
    # Configuration des notifications
    email_enabled: bool = False
    email_smtp_server: str = "localhost"
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_from: str = "noreply@saas-platform.com"
    
    # Configuration du cache
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 heure
    cache_max_size: int = 1000
    redis_url: str = "redis://redis:6379"
    
    # Configuration de la sécurité
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # Configuration des limites de taux
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # secondes
    
    # Configuration des logs
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/api-dashboard.log"
    max_log_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    
    # Configuration du monitoring
    metrics_enabled: bool = True
    health_check_interval: int = 30
    prometheus_port: int = 9090
    
    # Configuration des fichiers
    upload_max_size: int = 100 * 1024 * 1024  # 100 MB
    upload_allowed_extensions: List[str] = [".csv", ".json", ".xlsx", ".parquet"]
    upload_directory: str = "uploads"
    
    # Configuration des exports
    export_max_records: int = 100000
    export_formats: List[str] = ["csv", "json", "xlsx", "pdf"]
    export_directory: str = "exports"
    export_retention_days: int = 7
    
    # Configuration des rapports
    report_generation_timeout: int = 300  # 5 minutes
    report_formats: List[str] = ["pdf", "html", "json"]
    report_template_directory: str = "templates/reports"
    
    # Configuration des widgets
    widget_types: List[str] = [
        "line-chart", "bar-chart", "pie-chart", "gauge", "table", 
        "kpi-cards", "heatmap", "scatter-plot", "area-chart"
    ]
    widget_refresh_intervals: List[int] = [10, 30, 60, 300, 600]  # secondes
    
    # Configuration des thèmes
    available_themes: List[str] = ["light", "dark", "auto"]
    default_theme: str = "light"
    
    # Configuration de la pagination
    default_page_size: int = 50
    max_page_size: int = 1000
    page_size_options: List[int] = [10, 25, 50, 100, 250, 500]
    
    # Configuration des sessions
    session_timeout: int = 3600  # 1 heure
    session_cleanup_interval: int = 300  # 5 minutes
    
    # Configuration des tâches en arrière-plan
    background_tasks_enabled: bool = True
    max_concurrent_tasks: int = 10
    task_timeout: int = 600  # 10 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()
