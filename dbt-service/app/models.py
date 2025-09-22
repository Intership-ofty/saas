"""
Modèles Pydantic pour le service DBT
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class TransformationType(str, Enum):
    """Types de transformations supportées"""
    CLEAN = "clean"
    NORMALIZE = "normalize"
    AGGREGATE = "aggregate"
    JOIN = "join"
    FILTER = "filter"
    PIVOT = "pivot"
    CUSTOM = "custom"

class KPIMetric(str, Enum):
    """Métriques KPI disponibles"""
    COUNT = "count"
    SUM = "sum"
    AVG = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    STANDARD_DEVIATION = "std_dev"
    PERCENTILE = "percentile"
    GROWTH_RATE = "growth_rate"
    CUSTOM = "custom"

class TransformationRequest(BaseModel):
    """Requête de transformation de données"""
    data: List[Dict[str, Any]] = Field(..., description="Données à transformer")
    transformation_type: TransformationType = Field(..., description="Type de transformation")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Paramètres de transformation")
    calculate_kpis: bool = Field(default=False, description="Calculer les KPI après transformation")
    kpi_metrics: Optional[List[KPIMetric]] = Field(default=None, description="Métriques KPI à calculer")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées additionnelles")

class TransformationResponse(BaseModel):
    """Réponse de transformation de données"""
    transformation_id: str = Field(..., description="ID unique de la transformation")
    status: str = Field(..., description="Statut de la transformation")
    transformed_data: List[Dict[str, Any]] = Field(..., description="Données transformées")
    metrics: Dict[str, Any] = Field(..., description="Métriques de la transformation")
    kpi_results: Optional[Dict[str, Any]] = Field(default=None, description="Résultats des KPI")
    execution_time: float = Field(..., description="Temps d'exécution en secondes")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")

class KPICalculation(BaseModel):
    """Calcul de KPI"""
    metric_name: str = Field(..., description="Nom de la métrique")
    metric_value: Any = Field(..., description="Valeur de la métrique")
    calculation_method: str = Field(..., description="Méthode de calcul")
    confidence_level: Optional[float] = Field(default=None, description="Niveau de confiance")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées du calcul")

class TransformationHistory(BaseModel):
    """Historique des transformations"""
    transformation_id: str
    transformation_type: TransformationType
    input_records: int
    output_records: int
    execution_time: float
    status: str
    timestamp: datetime
    error_message: Optional[str] = None

class ServiceMetrics(BaseModel):
    """Métriques du service"""
    total_transformations: int
    successful_transformations: int
    failed_transformations: int
    average_execution_time: float
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    last_updated: datetime

class NormalizationRule(BaseModel):
    """Règle de normalisation"""
    field_name: str = Field(..., description="Nom du champ à normaliser")
    normalization_type: str = Field(..., description="Type de normalisation")
    parameters: Dict[str, Any] = Field(..., description="Paramètres de normalisation")
    priority: int = Field(default=1, description="Priorité d'application")

class DataQualityMetrics(BaseModel):
    """Métriques de qualité des données"""
    completeness: float = Field(..., description="Taux de complétude")
    accuracy: float = Field(..., description="Taux d'exactitude")
    consistency: float = Field(..., description="Taux de cohérence")
    validity: float = Field(..., description="Taux de validité")
    uniqueness: float = Field(..., description="Taux d'unicité")
    timeliness: float = Field(..., description="Taux de fraîcheur")
    overall_score: float = Field(..., description="Score global de qualité")
