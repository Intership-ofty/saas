"""
Modèles Pydantic pour le service API/Dashboard
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """Rôles utilisateur"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"

class AlertSeverity(str, Enum):
    """Sévérité des alertes"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Statut des alertes"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"

class ServiceStatus(str, Enum):
    """Statut des services"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"
    DEGRADED = "degraded"

class User(BaseModel):
    """Utilisateur du système"""
    id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True

class DashboardData(BaseModel):
    """Données du dashboard"""
    widgets: List[Dict[str, Any]]
    layout: str
    refresh_interval: int
    user_preferences: Optional[Dict[str, Any]] = None

class KPIMetric(BaseModel):
    """Métrique KPI"""
    name: str
    value: float
    unit: Optional[str] = None
    trend: Optional[str] = None
    target: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.now)

class Alert(BaseModel):
    """Alerte système"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    service: Optional[str] = None
    metric: Optional[str] = None
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AlertRule(BaseModel):
    """Règle d'alerte"""
    id: str
    name: str
    description: Optional[str] = None
    condition: str
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    service: Optional[str] = None
    metric: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ServiceHealth(BaseModel):
    """Santé d'un service"""
    name: str
    status: ServiceStatus
    response_time: Optional[float] = None
    last_check: datetime = Field(default_factory=datetime.now)
    uptime: Optional[float] = None
    error_rate: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None

class DataQualityMetric(BaseModel):
    """Métrique de qualité des données"""
    completeness: float
    accuracy: float
    consistency: float
    validity: float
    uniqueness: float
    timeliness: float
    overall_score: float
    measured_at: datetime = Field(default_factory=datetime.now)

class ProcessingMetric(BaseModel):
    """Métrique de traitement"""
    throughput: float
    latency: float
    error_rate: float
    success_rate: float
    queue_size: int
    active_workers: int
    measured_at: datetime = Field(default_factory=datetime.now)

class SystemMetric(BaseModel):
    """Métrique système"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    measured_at: datetime = Field(default_factory=datetime.now)

class DataSource(BaseModel):
    """Source de données"""
    id: str
    name: str
    type: str  # "database", "api", "file", "stream"
    connection_config: Dict[str, Any]
    status: str
    last_sync: Optional[datetime] = None
    sync_frequency: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class DataTransformation(BaseModel):
    """Transformation de données"""
    id: str
    name: str
    source_id: str
    target_id: str
    transformation_type: str
    configuration: Dict[str, Any]
    status: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    success_rate: float
    created_at: datetime = Field(default_factory=datetime.now)

class Report(BaseModel):
    """Rapport généré"""
    id: str
    name: str
    type: str
    format: str  # "pdf", "html", "json", "csv"
    parameters: Dict[str, Any]
    status: str
    file_path: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str
    size_bytes: Optional[int] = None

class LogEntry(BaseModel):
    """Entrée de log"""
    id: str
    timestamp: datetime
    level: str  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    service: str
    message: str
    context: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    user_id: Optional[str] = None

class Notification(BaseModel):
    """Notification utilisateur"""
    id: str
    user_id: str
    title: str
    message: str
    type: str  # "info", "warning", "error", "success"
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None

class Widget(BaseModel):
    """Widget de dashboard"""
    id: str
    type: str  # "chart", "gauge", "table", "kpi", "map"
    title: str
    description: Optional[str] = None
    data_source: str
    configuration: Dict[str, Any]
    position: Dict[str, int]  # x, y
    size: Dict[str, int]  # width, height
    refresh_interval: int = 30
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Dashboard(BaseModel):
    """Dashboard"""
    id: str
    name: str
    description: Optional[str] = None
    widgets: List[str]  # IDs des widgets
    layout: str = "grid"
    is_public: bool = False
    owner_id: str
    shared_with: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class APIKey(BaseModel):
    """Clé API"""
    id: str
    name: str
    key: str
    user_id: str
    permissions: List[str]
    is_active: bool = True
    last_used: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

class AuditLog(BaseModel):
    """Log d'audit"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=datetime.now)

class Configuration(BaseModel):
    """Configuration système"""
    key: str
    value: Any
    description: Optional[str] = None
    category: str
    is_encrypted: bool = False
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.now)

class Backup(BaseModel):
    """Sauvegarde"""
    id: str
    name: str
    type: str  # "full", "incremental", "differential"
    status: str  # "running", "completed", "failed"
    size_bytes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
