"""
Service de réconciliation avec Zingg
Ce service gère la résolution d'identité et la consolidation des données
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
import json

from zingg_client import ZinggClient
from config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reconciliation Service",
    description="Service de réconciliation et résolution d'identité avec Zingg",
    version="1.0.0"
)

# Initialisation du client Zingg
zingg_client = ZinggClient()

class ReconciliationRequest(BaseModel):
    """Requête de réconciliation"""
    data: List[Dict[str, Any]]
    matching_config: Dict[str, Any]
    entity_type: str = "customer"
    threshold: float = 0.8
    deduplication: bool = True
    merge_strategy: str = "latest_wins"

class ReconciliationResponse(BaseModel):
    """Réponse de réconciliation"""
    reconciliation_id: str
    status: str
    original_records: int
    deduplicated_records: int
    matched_pairs: int
    merged_records: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    execution_time: float
    timestamp: datetime

class EntityMatch(BaseModel):
    """Résultat de matching d'entités"""
    entity_id_1: str
    entity_id_2: str
    similarity_score: float
    match_type: str
    confidence_level: float
    matching_fields: List[str]

@app.get("/health")
async def health_check():
    """Vérification de l'état du service"""
    return {
        "status": "healthy",
        "service": "reconciliation-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/reconcile", response_model=ReconciliationResponse)
async def reconcile_data(request: ReconciliationRequest, background_tasks: BackgroundTasks):
    """
    Endpoint principal pour la réconciliation de données
    """
    try:
        logger.info(f"Début de la réconciliation pour {len(request.data)} enregistrements")
        
        # Exécution de la réconciliation
        result = await zingg_client.reconcile_entities(
            data=request.data,
            matching_config=request.matching_config,
            entity_type=request.entity_type,
            threshold=request.threshold,
            deduplication=request.deduplication,
            merge_strategy=request.merge_strategy
        )
        
        return ReconciliationResponse(
            reconciliation_id=result["reconciliation_id"],
            status="completed",
            original_records=result["original_records"],
            deduplicated_records=result["deduplicated_records"],
            matched_pairs=result["matched_pairs"],
            merged_records=result["merged_records"],
            confidence_scores=result["confidence_scores"],
            execution_time=result["execution_time"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la réconciliation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match")
async def match_entities(
    data: List[Dict[str, Any]], 
    matching_config: Dict[str, Any],
    threshold: float = 0.8
):
    """
    Matching d'entités sans fusion
    """
    try:
        matches = await zingg_client.find_matches(
            data=data,
            matching_config=matching_config,
            threshold=threshold
        )
        return matches
    except Exception as e:
        logger.error(f"Erreur lors du matching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deduplicate")
async def deduplicate_data(
    data: List[Dict[str, Any]],
    deduplication_config: Dict[str, Any]
):
    """
    Déduplication de données
    """
    try:
        deduplicated = await zingg_client.deduplicate_data(
            data=data,
            config=deduplication_config
        )
        return deduplicated
    except Exception as e:
        logger.error(f"Erreur lors de la déduplication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reconciliations")
async def list_reconciliations(limit: int = 100, offset: int = 0):
    """
    Liste des réconciliations effectuées
    """
    try:
        reconciliations = await zingg_client.get_reconciliation_history(
            limit=limit, offset=offset
        )
        return reconciliations
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des réconciliations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reconciliations/{reconciliation_id}")
async def get_reconciliation(reconciliation_id: str):
    """
    Détails d'une réconciliation spécifique
    """
    try:
        reconciliation = await zingg_client.get_reconciliation_by_id(reconciliation_id)
        if not reconciliation:
            raise HTTPException(status_code=404, detail="Réconciliation non trouvée")
        return reconciliation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la réconciliation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate-matches")
async def validate_matches(
    matches: List[EntityMatch],
    validation_rules: Dict[str, Any]
):
    """
    Validation des matches trouvés
    """
    try:
        validated_matches = await zingg_client.validate_matches(
            matches=matches,
            rules=validation_rules
        )
        return validated_matches
    except Exception as e:
        logger.error(f"Erreur lors de la validation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_service_metrics():
    """
    Métriques du service de réconciliation
    """
    try:
        metrics = await zingg_client.get_service_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train-model")
async def train_matching_model(
    training_data: List[Dict[str, Any]],
    model_config: Dict[str, Any]
):
    """
    Entraînement du modèle de matching
    """
    try:
        model_result = await zingg_client.train_model(
            training_data=training_data,
            config=model_config
        )
        return model_result
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
