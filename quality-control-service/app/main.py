"""
Service de contrôle qualité avec Soda
Ce service détecte les anomalies et les doublons dans les données
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
import json

from quality_checks import QualityCheckService, AnomalyDetectionService
from config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quality Control Service",
    description="Service de contrôle qualité et détection d'anomalies avec Soda",
    version="1.0.0"
)

# Initialisation des services
quality_service = QualityCheckService()
anomaly_service = AnomalyDetectionService()

class QualityCheckRequest(BaseModel):
    """Requête de contrôle qualité"""
    data: List[Dict[str, Any]]
    quality_rules: List[Dict[str, Any]]
    data_source: str = "unknown"
    check_anomalies: bool = True
    check_duplicates: bool = True
    check_completeness: bool = True
    check_consistency: bool = True
    check_validity: bool = True

class QualityCheckResponse(BaseModel):
    """Réponse de contrôle qualité"""
    check_id: str
    status: str
    total_records: int
    quality_score: float
    issues_found: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    duplicates: List[Dict[str, Any]]
    completeness_report: Dict[str, Any]
    consistency_report: Dict[str, Any]
    validity_report: Dict[str, Any]
    recommendations: List[str]
    execution_time: float
    timestamp: datetime

class AnomalyDetectionRequest(BaseModel):
    """Requête de détection d'anomalies"""
    data: List[Dict[str, Any]]
    detection_method: str = "isolation_forest"
    contamination: float = 0.1
    features: List[str] = []
    threshold: float = 0.5

class AnomalyDetectionResponse(BaseModel):
    """Réponse de détection d'anomalies"""
    detection_id: str
    method_used: str
    total_records: int
    anomalies_detected: int
    anomaly_scores: List[float]
    anomalous_records: List[Dict[str, Any]]
    confidence_scores: List[float]
    execution_time: float
    timestamp: datetime

@app.get("/health")
async def health_check():
    """Vérification de l'état du service"""
    return {
        "status": "healthy",
        "service": "quality-control-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/check", response_model=QualityCheckResponse)
async def check_data_quality(request: QualityCheckRequest, background_tasks: BackgroundTasks):
    """
    Endpoint principal pour le contrôle qualité
    """
    try:
        logger.info(f"Début du contrôle qualité pour {len(request.data)} enregistrements")
        
        # Exécution du contrôle qualité
        result = await quality_service.perform_quality_check(
            data=request.data,
            quality_rules=request.quality_rules,
            data_source=request.data_source,
            check_anomalies=request.check_anomalies,
            check_duplicates=request.check_duplicates,
            check_completeness=request.check_completeness,
            check_consistency=request.check_consistency,
            check_validity=request.check_validity
        )
        
        return QualityCheckResponse(
            check_id=result["check_id"],
            status="completed",
            total_records=result["total_records"],
            quality_score=result["quality_score"],
            issues_found=result["issues_found"],
            anomalies=result["anomalies"],
            duplicates=result["duplicates"],
            completeness_report=result["completeness_report"],
            consistency_report=result["consistency_report"],
            validity_report=result["validity_report"],
            recommendations=result["recommendations"],
            execution_time=result["execution_time"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du contrôle qualité: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(request: AnomalyDetectionRequest):
    """
    Détection d'anomalies avec différents algorithmes
    """
    try:
        result = await anomaly_service.detect_anomalies(
            data=request.data,
            method=request.detection_method,
            contamination=request.contamination,
            features=request.features,
            threshold=request.threshold
        )
        
        return AnomalyDetectionResponse(
            detection_id=result["detection_id"],
            method_used=request.detection_method,
            total_records=result["total_records"],
            anomalies_detected=result["anomalies_detected"],
            anomaly_scores=result["anomaly_scores"],
            anomalous_records=result["anomalous_records"],
            confidence_scores=result["confidence_scores"],
            execution_time=result["execution_time"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la détection d'anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate-schema")
async def validate_schema(
    data: List[Dict[str, Any]],
    expected_schema: Dict[str, Any]
):
    """
    Validation du schéma des données
    """
    try:
        validation_result = await quality_service.validate_schema(
            data=data,
            expected_schema=expected_schema
        )
        return validation_result
    except Exception as e:
        logger.error(f"Erreur lors de la validation du schéma: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-completeness")
async def check_completeness(
    data: List[Dict[str, Any]],
    required_fields: List[str]
):
    """
    Vérification de la complétude des données
    """
    try:
        completeness_result = await quality_service.check_completeness(
            data=data,
            required_fields=required_fields
        )
        return completeness_result
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de complétude: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-consistency")
async def check_consistency(
    data: List[Dict[str, Any]],
    consistency_rules: List[Dict[str, Any]]
):
    """
    Vérification de la cohérence des données
    """
    try:
        consistency_result = await quality_service.check_consistency(
            data=data,
            rules=consistency_rules
        )
        return consistency_result
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de cohérence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-validity")
async def check_validity(
    data: List[Dict[str, Any]],
    validation_rules: List[Dict[str, Any]]
):
    """
    Vérification de la validité des données
    """
    try:
        validity_result = await quality_service.check_validity(
            data=data,
            rules=validation_rules
        )
        return validity_result
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de validité: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quality-checks")
async def list_quality_checks(limit: int = 100, offset: int = 0):
    """
    Liste des contrôles qualité effectués
    """
    try:
        checks = await quality_service.get_quality_check_history(
            limit=limit, offset=offset
        )
        return checks
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des contrôles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quality-checks/{check_id}")
async def get_quality_check(check_id: str):
    """
    Détails d'un contrôle qualité spécifique
    """
    try:
        check = await quality_service.get_quality_check_by_id(check_id)
        if not check:
            raise HTTPException(status_code=404, detail="Contrôle qualité non trouvé")
        return check
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contrôle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_service_metrics():
    """
    Métriques du service de contrôle qualité
    """
    try:
        metrics = await quality_service.get_service_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report")
async def generate_quality_report(
    data: List[Dict[str, Any]],
    report_config: Dict[str, Any]
):
    """
    Génération d'un rapport de qualité détaillé
    """
    try:
        report = await quality_service.generate_quality_report(
            data=data,
            config=report_config
        )
        return report
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
