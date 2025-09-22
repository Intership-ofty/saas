"""
Configuration globale pour les tests
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any
import json
from datetime import datetime

@pytest.fixture(scope="session")
def event_loop():
    """Créer une boucle d'événements pour les tests asynchrones"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def http_client():
    """Client HTTP pour les tests"""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture
def sample_data():
    """Données d'exemple pour les tests"""
    return [
        {
            "id": "1",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "value": 100.50,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "2",
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1234567891",
            "value": 200.75,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "3",
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "phone": "+1234567892",
            "value": 150.25,
            "timestamp": datetime.now().isoformat()
        }
    ]

@pytest.fixture
def sample_quality_rules():
    """Règles de qualité d'exemple pour les tests"""
    return [
        {
            "type": "required_field",
            "field": "email",
            "description": "Email obligatoire"
        },
        {
            "type": "email_validation",
            "field": "email",
            "description": "Format email valide"
        },
        {
            "type": "phone_validation",
            "field": "phone",
            "description": "Format téléphone valide"
        },
        {
            "type": "value_range",
            "field": "value",
            "min_value": 0,
            "max_value": 1000,
            "description": "Valeur entre 0 et 1000"
        }
    ]

@pytest.fixture
def sample_transformation_config():
    """Configuration de transformation d'exemple"""
    return {
        "transformation_type": "normalize",
        "parameters": {
            "normalize_numeric": True,
            "normalize_dates": True,
            "trim_strings": True,
            "lowercase_strings": False
        }
    }

@pytest.fixture
def sample_matching_config():
    """Configuration de matching d'exemple"""
    return {
        "matching_fields": ["name", "email"],
        "similarity_threshold": 0.8,
        "similarity_fields": ["name", "email", "phone"]
    }

@pytest.fixture
def sample_rca_request():
    """Requête RCA d'exemple"""
    return {
        "problem_description": "Baisse de la qualité des données",
        "affected_metrics": ["data_quality_score", "processing_speed"],
        "time_window": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-31T23:59:59Z"
        },
        "analysis_depth": 3,
        "include_correlations": True,
        "include_trend_analysis": True,
        "include_anomaly_detection": True
    }

@pytest.fixture
def mock_database_url():
    """URL de base de données pour les tests"""
    return "postgresql://test_user:test_password@localhost:5432/test_db"

@pytest.fixture
def service_urls():
    """URLs des services pour les tests d'intégration"""
    return {
        "api_dashboard": "http://localhost:8000",
        "dbt_service": "http://localhost:8001",
        "reconciliation_service": "http://localhost:8002",
        "quality_control_service": "http://localhost:8003",
        "rca_service": "http://localhost:8004",
        "nifi_service": "http://localhost:8080"
    }

@pytest.fixture
def expected_service_responses():
    """Réponses attendues des services"""
    return {
        "health_check": {
            "status": "healthy",
            "service": None,  # Sera défini par chaque test
            "timestamp": None  # Sera généré dynamiquement
        }
    }
