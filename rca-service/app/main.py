"""
Service RCA (Root Cause Analysis)
Ce service analyse les causes racines des problèmes de données
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
import json

from analysis import RCAAnalysisService, CorrelationAnalysisService
from config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RCA Service",
    description="Service d'analyse des causes racines et corrélations",
    version="1.0.0"
)

# Initialisation des services
rca_service = RCAAnalysisService()
correlation_service = CorrelationAnalysisService()

class RCAAnalysisRequest(BaseModel):
    """Requête d'analyse des causes racines"""
    data: List[Dict[str, Any]]
    problem_description: str
    affected_metrics: List[str]
    time_window: Optional[Dict[str, Any]] = None
    analysis_depth: int = 3
    include_correlations: bool = True
    include_trend_analysis: bool = True
    include_anomaly_detection: bool = True

class RCAAnalysisResponse(BaseModel):
    """Réponse d'analyse des causes racines"""
    analysis_id: str
    status: str
    problem_summary: str
    root_causes: List[Dict[str, Any]]
    contributing_factors: List[Dict[str, Any]]
    correlation_analysis: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    anomaly_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str]
    confidence_score: float
    execution_time: float
    timestamp: datetime

class CorrelationAnalysisRequest(BaseModel):
    """Requête d'analyse de corrélation"""
    data: List[Dict[str, Any]]
    variables: List[str]
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    min_correlation_strength: float = 0.3

class CorrelationAnalysisResponse(BaseModel):
    """Réponse d'analyse de corrélation"""
    analysis_id: str
    correlation_matrix: Dict[str, Dict[str, float]]
    significant_correlations: List[Dict[str, Any]]
    correlation_strength: Dict[str, str]
    insights: List[str]
    execution_time: float
    timestamp: datetime

@app.get("/health")
async def health_check():
    """Vérification de l'état du service"""
    return {
        "status": "healthy",
        "service": "rca-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=RCAAnalysisResponse)
async def analyze_root_causes(request: RCAAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Endpoint principal pour l'analyse des causes racines
    """
    try:
        logger.info(f"Début de l'analyse RCA pour: {request.problem_description}")
        
        # Exécution de l'analyse RCA
        result = await rca_service.perform_rca_analysis(
            data=request.data,
            problem_description=request.problem_description,
            affected_metrics=request.affected_metrics,
            time_window=request.time_window,
            analysis_depth=request.analysis_depth,
            include_correlations=request.include_correlations,
            include_trend_analysis=request.include_trend_analysis,
            include_anomaly_detection=request.include_anomaly_detection
        )
        
        return RCAAnalysisResponse(
            analysis_id=result["analysis_id"],
            status="completed",
            problem_summary=result["problem_summary"],
            root_causes=result["root_causes"],
            contributing_factors=result["contributing_factors"],
            correlation_analysis=result.get("correlation_analysis"),
            trend_analysis=result.get("trend_analysis"),
            anomaly_analysis=result.get("anomaly_analysis"),
            recommendations=result["recommendations"],
            confidence_score=result["confidence_score"],
            execution_time=result["execution_time"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse RCA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/correlation", response_model=CorrelationAnalysisResponse)
async def analyze_correlations(request: CorrelationAnalysisRequest):
    """
    Analyse des corrélations entre variables
    """
    try:
        result = await correlation_service.analyze_correlations(
            data=request.data,
            variables=request.variables,
            method=request.correlation_method,
            significance_threshold=request.significance_threshold,
            min_correlation_strength=request.min_correlation_strength
        )
        
        return CorrelationAnalysisResponse(
            analysis_id=result["analysis_id"],
            correlation_matrix=result["correlation_matrix"],
            significant_correlations=result["significant_correlations"],
            correlation_strength=result["correlation_strength"],
            insights=result["insights"],
            execution_time=result["execution_time"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de corrélation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trend-analysis")
async def analyze_trends(
    data: List[Dict[str, Any]],
    time_field: str,
    metrics: List[str],
    trend_period: str = "daily"
):
    """
    Analyse des tendances temporelles
    """
    try:
        trend_result = await rca_service.analyze_trends(
            data=data,
            time_field=time_field,
            metrics=metrics,
            trend_period=trend_period
        )
        return trend_result
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des tendances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/anomaly-detection")
async def detect_anomalies(
    data: List[Dict[str, Any]],
    anomaly_fields: List[str],
    detection_method: str = "statistical"
):
    """
    Détection d'anomalies dans les données
    """
    try:
        anomaly_result = await rca_service.detect_anomalies(
            data=data,
            anomaly_fields=anomaly_fields,
            detection_method=detection_method
        )
        return anomaly_result
    except Exception as e:
        logger.error(f"Erreur lors de la détection d'anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/impact-analysis")
async def analyze_impact(
    data: List[Dict[str, Any]],
    problem_events: List[Dict[str, Any]],
    impact_metrics: List[str]
):
    """
    Analyse de l'impact des problèmes
    """
    try:
        impact_result = await rca_service.analyze_impact(
            data=data,
            problem_events=problem_events,
            impact_metrics=impact_metrics
        )
        return impact_result
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse d'impact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses")
async def list_rca_analyses(limit: int = 100, offset: int = 0):
    """
    Liste des analyses RCA effectuées
    """
    try:
        analyses = await rca_service.get_analysis_history(
            limit=limit, offset=offset
        )
        return analyses
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses/{analysis_id}")
async def get_rca_analysis(analysis_id: str):
    """
    Détails d'une analyse RCA spécifique
    """
    try:
        analysis = await rca_service.get_analysis_by_id(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analyse RCA non trouvée")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report")
async def generate_rca_report(
    analysis_id: str,
    report_format: str = "json",
    include_visualizations: bool = True
):
    """
    Génération d'un rapport RCA détaillé
    """
    try:
        report = await rca_service.generate_report(
            analysis_id=analysis_id,
            format=report_format,
            include_visualizations=include_visualizations
        )
        return report
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_service_metrics():
    """
    Métriques du service RCA
    """
    try:
        metrics = await rca_service.get_service_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-failure")
async def predict_failure(
    data: List[Dict[str, Any]],
    prediction_model: str = "isolation_forest",
    warning_threshold: float = 0.7
):
    """
    Prédiction des échecs futurs
    """
    try:
        prediction_result = await rca_service.predict_failure(
            data=data,
            model=prediction_model,
            warning_threshold=warning_threshold
        )
        return prediction_result
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
