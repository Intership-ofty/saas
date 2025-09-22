"""
Service DBT pour la transformation de données
Ce service gère les transformations, normalisations et calculs de KPI
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import asyncio
import logging
from datetime import datetime, timedelta
import json

from models import TransformationRequest, TransformationResponse, KPICalculation
from services import DataTransformationService, KPIService
from config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DBT Transformation Service",
    description="Service de transformation de données avec dbt et calcul de KPI",
    version="1.0.0"
)

# Initialisation des services
transformation_service = DataTransformationService()
kpi_service = KPIService()

@app.get("/health")
async def health_check():
    """Vérification de l'état du service"""
    return {
        "status": "healthy",
        "service": "dbt-transformation",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/transform", response_model=TransformationResponse)
async def transform_data(request: TransformationRequest, background_tasks: BackgroundTasks):
    """
    Endpoint principal pour la transformation de données
    """
    try:
        logger.info(f"Traitement de la transformation: {request.transformation_type}")
        
        # Exécution de la transformation
        result = await transformation_service.execute_transformation(
            data=request.data,
            transformation_type=request.transformation_type,
            parameters=request.parameters
        )
        
        # Calcul des KPI si demandé
        kpi_results = None
        if request.calculate_kpis:
            background_tasks.add_task(
                kpi_service.calculate_kpis,
                result["transformed_data"],
                request.kpi_metrics
            )
        
        return TransformationResponse(
            transformation_id=result["transformation_id"],
            status="completed",
            transformed_data=result["transformed_data"],
            metrics=result["metrics"],
            kpi_results=kpi_results,
            execution_time=result["execution_time"]
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la transformation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kpi/calculate")
async def calculate_kpis(data: List[Dict], metrics: List[str]):
    """
    Calcul spécifique de KPI
    """
    try:
        kpi_results = await kpi_service.calculate_kpis(data, metrics)
        return kpi_results
    except Exception as e:
        logger.error(f"Erreur lors du calcul des KPI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transformations")
async def list_transformations(limit: int = 100, offset: int = 0):
    """
    Liste des transformations effectuées
    """
    try:
        transformations = await transformation_service.get_transformation_history(
            limit=limit, offset=offset
        )
        return transformations
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des transformations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transformations/{transformation_id}")
async def get_transformation(transformation_id: str):
    """
    Détails d'une transformation spécifique
    """
    try:
        transformation = await transformation_service.get_transformation_by_id(transformation_id)
        if not transformation:
            raise HTTPException(status_code=404, detail="Transformation non trouvée")
        return transformation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la transformation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/normalize")
async def normalize_data(data: List[Dict], normalization_rules: Dict[str, Any]):
    """
    Normalisation de données selon des règles spécifiques
    """
    try:
        normalized_data = await transformation_service.normalize_data(
            data, normalization_rules
        )
        return {
            "normalized_data": normalized_data,
            "normalization_rules_applied": normalization_rules,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la normalisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_service_metrics():
    """
    Métriques du service de transformation
    """
    try:
        metrics = await transformation_service.get_service_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
