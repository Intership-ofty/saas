"""
Tests unitaires pour le service DBT
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch

# Import des modules à tester
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../dbt-service/app'))

from services import DataTransformationService, KPIService
from models import TransformationType, KPIMetric

class TestDataTransformationService:
    """Tests pour le service de transformation de données"""
    
    @pytest.fixture
    def transformation_service(self):
        """Instance du service de transformation"""
        return DataTransformationService()
    
    @pytest.fixture
    def sample_data(self):
        """Données d'exemple pour les tests"""
        return [
            {"id": 1, "name": "John Doe", "value": 100.5, "date": "2024-01-01"},
            {"id": 2, "name": "Jane Smith", "value": 200.75, "date": "2024-01-02"},
            {"id": 3, "name": "Bob Johnson", "value": 150.25, "date": "2024-01-03"}
        ]
    
    @pytest.mark.asyncio
    async def test_clean_data_remove_duplicates(self, transformation_service, sample_data):
        """Test de nettoyage avec suppression des doublons"""
        # Ajout de doublons
        data_with_duplicates = sample_data + sample_data[:1]
        
        df = pd.DataFrame(data_with_duplicates)
        parameters = {"remove_duplicates": True}
        
        result = await transformation_service._clean_data(df, parameters)
        
        assert len(result) == len(sample_data)
        assert result["id"].nunique() == len(sample_data)
    
    @pytest.mark.asyncio
    async def test_clean_data_fill_missing_values(self, transformation_service):
        """Test de nettoyage avec remplissage des valeurs manquantes"""
        data_with_missing = [
            {"id": 1, "name": "John", "value": None},
            {"id": 2, "name": None, "value": 100},
            {"id": 3, "name": "Bob", "value": 200}
        ]
        
        df = pd.DataFrame(data_with_missing)
        parameters = {
            "missing_value_strategy": "fill",
            "fill_value": 0
        }
        
        result = await transformation_service._clean_data(df, parameters)
        
        assert result["value"].isna().sum() == 0
        assert result["name"].isna().sum() == 1  # Les strings ne sont pas remplies par défaut
    
    @pytest.mark.asyncio
    async def test_normalize_data_numeric(self, transformation_service):
        """Test de normalisation des données numériques"""
        data = [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20},
            {"id": 3, "value": 30}
        ]
        
        df = pd.DataFrame(data)
        parameters = {"normalize_numeric": True}
        
        result = await transformation_service._normalize_data(df, parameters)
        
        # Vérifier que les valeurs sont normalisées entre 0 et 1
        assert result["value"].min() >= 0
        assert result["value"].max() <= 1
        assert abs(result["value"].min()) < 0.01  # Proche de 0
        assert abs(result["value"].max() - 1) < 0.01  # Proche de 1
    
    @pytest.mark.asyncio
    async def test_aggregate_data(self, transformation_service):
        """Test d'agrégation des données"""
        data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 20},
            {"category": "B", "value": 15},
            {"category": "B", "value": 25}
        ]
        
        df = pd.DataFrame(data)
        parameters = {
            "group_by": ["category"],
            "aggregations": {"value": "sum"}
        }
        
        result = await transformation_service._aggregate_data(df, parameters)
        
        assert len(result) == 2  # Deux catégories
        assert result[result["category"] == "A"]["value"].iloc[0] == 30
        assert result[result["category"] == "B"]["value"].iloc[0] == 40
    
    @pytest.mark.asyncio
    async def test_filter_data(self, transformation_service, sample_data):
        """Test de filtrage des données"""
        df = pd.DataFrame(sample_data)
        parameters = {
            "filters": {
                "value": {
                    "operator": "greater_than",
                    "value": 150
                }
            }
        }
        
        result = await transformation_service._filter_data(df, parameters)
        
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Jane Smith"
    
    @pytest.mark.asyncio
    async def test_execute_transformation_clean(self, transformation_service, sample_data):
        """Test d'exécution de transformation de type clean"""
        result = await transformation_service.execute_transformation(
            data=sample_data,
            transformation_type=TransformationType.CLEAN,
            parameters={"remove_duplicates": True}
        )
        
        assert "transformation_id" in result
        assert result["status"] == "completed"
        assert len(result["transformed_data"]) == len(sample_data)
        assert "execution_time" in result
        assert result["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_execute_transformation_error_handling(self, transformation_service):
        """Test de gestion d'erreur lors de la transformation"""
        invalid_data = [{"invalid": "data"}]  # Données qui peuvent causer des erreurs
        
        with pytest.raises(Exception):
            await transformation_service.execute_transformation(
                data=invalid_data,
                transformation_type=TransformationType.AGGREGATE,
                parameters={"group_by": ["nonexistent_field"]}
            )

class TestKPIService:
    """Tests pour le service de calcul de KPI"""
    
    @pytest.fixture
    def kpi_service(self):
        """Instance du service KPI"""
        return KPIService()
    
    @pytest.fixture
    def sample_data_with_numeric(self):
        """Données avec des colonnes numériques pour les tests KPI"""
        return [
            {"id": 1, "value": 10, "score": 85},
            {"id": 2, "value": 20, "score": 90},
            {"id": 3, "value": 30, "score": 95},
            {"id": 4, "value": 40, "score": 88}
        ]
    
    @pytest.mark.asyncio
    async def test_calculate_kpis_count(self, kpi_service, sample_data_with_numeric):
        """Test de calcul du KPI count"""
        result = await kpi_service.calculate_kpis(
            data=sample_data_with_numeric,
            metrics=[KPIMetric.COUNT]
        )
        
        assert "count" in result
        assert result["count"] == 4
    
    @pytest.mark.asyncio
    async def test_calculate_kpis_sum(self, kpi_service, sample_data_with_numeric):
        """Test de calcul du KPI sum"""
        result = await kpi_service.calculate_kpis(
            data=sample_data_with_numeric,
            metrics=[KPIMetric.SUM]
        )
        
        assert "sum" in result
        assert "value" in result["sum"]
        assert "score" in result["sum"]
        assert result["sum"]["value"] == 100  # 10+20+30+40
        assert result["sum"]["score"] == 358  # 85+90+95+88
    
    @pytest.mark.asyncio
    async def test_calculate_kpis_average(self, kpi_service, sample_data_with_numeric):
        """Test de calcul du KPI average"""
        result = await kpi_service.calculate_kpis(
            data=sample_data_with_numeric,
            metrics=[KPIMetric.AVG]
        )
        
        assert "average" in result
        assert "value" in result["average"]
        assert "score" in result["average"]
        assert result["average"]["value"] == 25.0  # 100/4
        assert result["average"]["score"] == 89.5  # 358/4
    
    @pytest.mark.asyncio
    async def test_calculate_kpis_min_max(self, kpi_service, sample_data_with_numeric):
        """Test de calcul des KPI min et max"""
        result = await kpi_service.calculate_kpis(
            data=sample_data_with_numeric,
            metrics=[KPIMetric.MIN, KPIMetric.MAX]
        )
        
        assert "min" in result
        assert "max" in result
        assert result["min"]["value"] == 10
        assert result["max"]["value"] == 40
        assert result["min"]["score"] == 85
        assert result["max"]["score"] == 95
    
    @pytest.mark.asyncio
    async def test_calculate_kpis_multiple(self, kpi_service, sample_data_with_numeric):
        """Test de calcul de plusieurs KPI en une fois"""
        result = await kpi_service.calculate_kpis(
            data=sample_data_with_numeric,
            metrics=[KPIMetric.COUNT, KPIMetric.SUM, KPIMetric.AVG, KPIMetric.MIN, KPIMetric.MAX]
        )
        
        assert "count" in result
        assert "sum" in result
        assert "average" in result
        assert "min" in result
        assert "max" in result
        
        # Vérifier la cohérence des résultats
        assert result["count"] == 4
        assert result["sum"]["value"] / result["count"] == result["average"]["value"]
        assert result["min"]["value"] <= result["max"]["value"]

class TestTransformationTypes:
    """Tests pour les types de transformation"""
    
    def test_transformation_type_enum(self):
        """Test des valeurs de l'enum TransformationType"""
        assert TransformationType.CLEAN == "clean"
        assert TransformationType.NORMALIZE == "normalize"
        assert TransformationType.AGGREGATE == "aggregate"
        assert TransformationType.JOIN == "join"
        assert TransformationType.FILTER == "filter"
        assert TransformationType.PIVOT == "pivot"
        assert TransformationType.CUSTOM == "custom"
    
    def test_kpi_metric_enum(self):
        """Test des valeurs de l'enum KPIMetric"""
        assert KPIMetric.COUNT == "count"
        assert KPIMetric.SUM == "sum"
        assert KPIMetric.AVG == "average"
        assert KPIMetric.MIN == "min"
        assert KPIMetric.MAX == "max"
        assert KPIMetric.MEDIAN == "median"
        assert KPIMetric.STANDARD_DEVIATION == "std_dev"
        assert KPIMetric.PERCENTILE == "percentile"
        assert KPIMetric.GROWTH_RATE == "growth_rate"
        assert KPIMetric.CUSTOM == "custom"

@pytest.mark.asyncio
async def test_service_metrics():
    """Test de récupération des métriques du service"""
    service = DataTransformationService()
    
    # Exécuter quelques transformations pour avoir des métriques
    sample_data = [{"id": 1, "value": 10}]
    
    await service.execute_transformation(
        data=sample_data,
        transformation_type=TransformationType.CLEAN
    )
    
    metrics = await service.get_service_metrics()
    
    assert "total_transformations" in metrics
    assert "successful_transformations" in metrics
    assert "failed_transformations" in metrics
    assert "average_execution_time" in metrics
    assert "uptime_seconds" in metrics
    assert "memory_usage_mb" in metrics
    assert "cpu_usage_percent" in metrics
    
    assert metrics["total_transformations"] >= 1
    assert metrics["successful_transformations"] >= 1
    assert metrics["uptime_seconds"] > 0
