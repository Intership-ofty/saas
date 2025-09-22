"""
Service API/Dashboard principal
Ce service expose l'API REST et gère le dashboard pour visualisation, alertes et KPI
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json
import httpx

from endpoints import dashboard_endpoints, api_endpoints, alert_endpoints
from models import DashboardData, KPIMetric, Alert, User
from config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SaaS Data Platform API",
    description="API principale et dashboard pour la plateforme de données SaaS",
    version="1.0.0"
)

# Configuration des templates et fichiers statiques
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des routes
app.include_router(dashboard_endpoints.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(api_endpoints.router, prefix="/api", tags=["api"])
app.include_router(alert_endpoints.router, prefix="/alerts", tags=["alerts"])

class HealthResponse(BaseModel):
    """Réponse de santé du système"""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    uptime: float

class ServiceStatus(BaseModel):
    """Statut d'un service"""
    name: str
    status: str
    response_time: float
    last_check: datetime

# Variables globales pour le monitoring
service_statuses = {}
start_time = datetime.now()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Page d'accueil du dashboard"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "SaaS Data Platform",
        "version": settings.version
    })

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état du système complet"""
    try:
        # Vérification des services
        services = await check_all_services()
        
        # Calcul de l'uptime
        uptime = (datetime.now() - start_time).total_seconds()
        
        # Détermination du statut global
        overall_status = "healthy"
        for service_name, status in services.items():
            if status != "healthy":
                overall_status = "degraded"
                break
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            services=services,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            services={"error": str(e)},
            uptime=(datetime.now() - start_time).total_seconds()
        )

@app.get("/services/status")
async def get_services_status():
    """Statut détaillé de tous les services"""
    try:
        detailed_status = await get_detailed_services_status()
        return detailed_status
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut des services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/overview")
async def get_metrics_overview():
    """Vue d'ensemble des métriques du système"""
    try:
        metrics = await collect_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Erreur lors de la collecte des métriques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/data")
async def get_dashboard_data():
    """Données pour le dashboard principal"""
    try:
        dashboard_data = await collect_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Erreur lors de la collecte des données du dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/ingest")
async def ingest_data(data: List[Dict[str, Any]], background_tasks: BackgroundTasks):
    """Point d'entrée pour l'ingestion de données"""
    try:
        # Envoi vers NiFi pour traitement
        result = await send_to_nifi(data)
        
        # Traitement en arrière-plan
        background_tasks.add_task(process_ingested_data, data)
        
        return {
            "status": "accepted",
            "records_count": len(data),
            "processing_id": result.get("processing_id"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis")
async def get_kpis(time_range: str = "24h"):
    """Récupération des KPI"""
    try:
        kpis = await collect_kpis(time_range)
        return kpis
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des KPI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports")
async def get_reports(report_type: str = "summary"):
    """Génération de rapports"""
    try:
        reports = await generate_reports(report_type)
        return reports
    except Exception as e:
        logger.error(f"Erreur lors de la génération des rapports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/configure")
async def configure_alerts(alert_config: Dict[str, Any]):
    """Configuration des alertes"""
    try:
        result = await setup_alert_configuration(alert_config)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la configuration des alertes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
):
    """Récupération des logs système"""
    try:
        logs = await fetch_system_logs(service, level, limit)
        return logs
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fonctions utilitaires

async def check_all_services() -> Dict[str, str]:
    """Vérifie l'état de tous les services"""
    services = {
        "nifi-service": "http://nifi-service:8080",
        "dbt-service": "http://dbt-service:8001",
        "reconciliation-service": "http://reconciliation-service:8002",
        "quality-control-service": "http://quality-control-service:8003",
        "rca-service": "http://rca-service:8004",
        "warehouse-service": "http://warehouse-service:5432"
    }
    
    statuses = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, url in services.items():
            try:
                if service_name == "warehouse-service":
                    # PostgreSQL ne répond pas sur HTTP, on simule
                    statuses[service_name] = "healthy"
                else:
                    response = await client.get(f"{url}/health")
                    if response.status_code == 200:
                        statuses[service_name] = "healthy"
                    else:
                        statuses[service_name] = "unhealthy"
            except Exception:
                statuses[service_name] = "unreachable"
    
    return statuses

async def get_detailed_services_status() -> Dict[str, ServiceStatus]:
    """Statut détaillé de tous les services"""
    detailed_status = {}
    
    services = {
        "nifi-service": "http://nifi-service:8080",
        "dbt-service": "http://dbt-service:8001",
        "reconciliation-service": "http://reconciliation-service:8002",
        "quality-control-service": "http://quality-control-service:8003",
        "rca-service": "http://rca-service:8004"
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, url in services.items():
            start_check = datetime.now()
            
            try:
                response = await client.get(f"{url}/health")
                response_time = (datetime.now() - start_check).total_seconds()
                
                if response.status_code == 200:
                    status = "healthy"
                else:
                    status = "unhealthy"
                
                detailed_status[service_name] = ServiceStatus(
                    name=service_name,
                    status=status,
                    response_time=response_time,
                    last_check=datetime.now()
                )
                
            except Exception as e:
                response_time = (datetime.now() - start_check).total_seconds()
                detailed_status[service_name] = ServiceStatus(
                    name=service_name,
                    status="unreachable",
                    response_time=response_time,
                    last_check=datetime.now()
                )
    
    return detailed_status

async def collect_system_metrics() -> Dict[str, Any]:
    """Collecte les métriques du système"""
    metrics = {
        "system": {
            "uptime": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        },
        "services": {},
        "performance": {
            "total_requests": 0,  # À implémenter avec un compteur
            "average_response_time": 0.0,
            "error_rate": 0.0
        }
    }
    
    # Collecte des métriques de chaque service
    services = ["dbt-service", "reconciliation-service", "quality-control-service", "rca-service"]
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service in services:
            try:
                response = await client.get(f"http://{service}/metrics")
                if response.status_code == 200:
                    metrics["services"][service] = response.json()
            except Exception:
                metrics["services"][service] = {"status": "unreachable"}
    
    return metrics

async def collect_dashboard_data() -> Dict[str, Any]:
    """Collecte les données pour le dashboard"""
    dashboard_data = {
        "overview": {
            "total_services": 6,
            "healthy_services": 0,
            "total_data_processed": 0,
            "active_alerts": 0
        },
        "kpis": [],
        "charts": {
            "data_flow": [],
            "service_health": [],
            "performance_metrics": []
        },
        "recent_activities": []
    }
    
    # Vérification de l'état des services
    services_status = await check_all_services()
    dashboard_data["overview"]["healthy_services"] = sum(
        1 for status in services_status.values() if status == "healthy"
    )
    
    # Simulation de KPI
    dashboard_data["kpis"] = [
        {"name": "Data Quality Score", "value": 95.5, "trend": "up"},
        {"name": "Processing Speed", "value": 1250, "unit": "records/min", "trend": "up"},
        {"name": "Error Rate", "value": 0.5, "unit": "%", "trend": "down"},
        {"name": "System Uptime", "value": 99.9, "unit": "%", "trend": "stable"}
    ]
    
    return dashboard_data

async def send_to_nifi(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Envoie les données à NiFi pour traitement"""
    # Simulation de l'envoi vers NiFi
    processing_id = f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "processing_id": processing_id,
        "status": "queued",
        "records_count": len(data)
    }

async def process_ingested_data(data: List[Dict[str, Any]]):
    """Traitement en arrière-plan des données ingérées"""
    try:
        # Simulation du traitement
        logger.info(f"Traitement de {len(data)} enregistrements en arrière-plan")
        
        # Ici, on pourrait déclencher les autres services
        # - Transformation avec dbt-service
        # - Réconciliation avec reconciliation-service
        # - Contrôle qualité avec quality-control-service
        
        await asyncio.sleep(1)  # Simulation du temps de traitement
        
        logger.info("Traitement en arrière-plan terminé")
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement en arrière-plan: {str(e)}")

async def collect_kpis(time_range: str) -> Dict[str, Any]:
    """Collecte les KPI selon la période"""
    # Simulation de KPI
    kpis = {
        "time_range": time_range,
        "data_quality": {
            "completeness": 95.5,
            "accuracy": 98.2,
            "consistency": 97.8,
            "validity": 99.1
        },
        "processing": {
            "records_processed": 125000,
            "processing_time_avg": 2.5,
            "throughput": 1250
        },
        "system": {
            "uptime": 99.9,
            "response_time_avg": 150,
            "error_rate": 0.5
        }
    }
    
    return kpis

async def generate_reports(report_type: str) -> Dict[str, Any]:
    """Génère des rapports"""
    reports = {
        "report_type": report_type,
        "generated_at": datetime.now().isoformat(),
        "data": {}
    }
    
    if report_type == "summary":
        reports["data"] = {
            "total_records": 125000,
            "quality_score": 95.5,
            "processing_efficiency": 98.2,
            "system_health": "excellent"
        }
    
    return reports

async def setup_alert_configuration(alert_config: Dict[str, Any]) -> Dict[str, Any]:
    """Configure les alertes"""
    # Simulation de la configuration d'alertes
    return {
        "status": "configured",
        "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "configuration": alert_config
    }

async def fetch_system_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Récupère les logs système"""
    # Simulation de logs
    logs = {
        "service": service,
        "level": level,
        "limit": limit,
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "service": service or "api-dashboard",
                "message": "Service running normally"
            }
        ]
    }
    
    return logs

# Middleware pour le logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
