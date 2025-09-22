"""
Tests d'intégration pour l'API Dashboard
"""

import pytest
import httpx
import asyncio
from datetime import datetime

class TestAPIDashboardIntegration:
    """Tests d'intégration pour l'API Dashboard"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, http_client, service_urls):
        """Test de vérification de santé de l'API Dashboard"""
        response = await http_client.get(f"{service_urls['api_dashboard']}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert "uptime" in data
        
        # Vérifier que le statut est sain ou dégradé (pas unhealthy)
        assert data["status"] in ["healthy", "degraded"]
    
    @pytest.mark.asyncio
    async def test_dashboard_data_endpoint(self, http_client, service_urls):
        """Test de l'endpoint de données du dashboard"""
        response = await http_client.get(f"{service_urls['api_dashboard']}/dashboard/data")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overview" in data
        assert "kpis" in data
        assert "charts" in data
        assert "recent_activities" in data
        
        # Vérifier la structure de l'overview
        overview = data["overview"]
        assert "total_services" in overview
        assert "healthy_services" in overview
        assert "total_data_processed" in overview
        assert "active_alerts" in overview
    
    @pytest.mark.asyncio
    async def test_metrics_overview_endpoint(self, http_client, service_urls):
        """Test de l'endpoint de vue d'ensemble des métriques"""
        response = await http_client.get(f"{service_urls['api_dashboard']}/metrics/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "system" in data
        assert "services" in data
        assert "performance" in data
        
        # Vérifier la structure système
        system = data["system"]
        assert "uptime" in system
        assert "timestamp" in system
        
        # Vérifier la structure performance
        performance = data["performance"]
        assert "total_requests" in performance
        assert "average_response_time" in performance
        assert "error_rate" in performance
    
    @pytest.mark.asyncio
    async def test_kpis_endpoint(self, http_client, service_urls):
        """Test de l'endpoint des KPI"""
        response = await http_client.get(f"{service_urls['api_dashboard']}/kpis")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "time_range" in data
        assert "data_quality" in data
        assert "processing" in data
        assert "system" in data
        
        # Vérifier la structure data_quality
        data_quality = data["data_quality"]
        assert "completeness" in data_quality
        assert "accuracy" in data_quality
        assert "consistency" in data_quality
        assert "validity" in data_quality
    
    @pytest.mark.asyncio
    async def test_data_ingestion_endpoint(self, http_client, service_urls, sample_data):
        """Test de l'endpoint d'ingestion de données"""
        response = await http_client.post(
            f"{service_urls['api_dashboard']}/data/ingest",
            json=sample_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "records_count" in data
        assert "processing_id" in data
        assert "timestamp" in data
        
        assert data["status"] == "accepted"
        assert data["records_count"] == len(sample_data)
    
    @pytest.mark.asyncio
    async def test_reports_endpoint(self, http_client, service_urls):
        """Test de l'endpoint de génération de rapports"""
        response = await http_client.get(
            f"{service_urls['api_dashboard']}/reports",
            params={"report_type": "summary"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "report_type" in data
        assert "generated_at" in data
        assert "data" in data
        
        assert data["report_type"] == "summary"
    
    @pytest.mark.asyncio
    async def test_alert_configuration_endpoint(self, http_client, service_urls):
        """Test de l'endpoint de configuration des alertes"""
        alert_config = {
            "name": "Test Alert",
            "condition": "error_rate > 5",
            "threshold": 5.0,
            "severity": "warning"
        }
        
        response = await http_client.post(
            f"{service_urls['api_dashboard']}/alerts/configure",
            json=alert_config
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "alert_id" in data
        assert "configuration" in data
        
        assert data["status"] == "configured"
    
    @pytest.mark.asyncio
    async def test_logs_endpoint(self, http_client, service_urls):
        """Test de l'endpoint de récupération des logs"""
        response = await http_client.get(
            f"{service_urls['api_dashboard']}/logs",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "limit" in data
        assert "logs" in data
        
        assert data["limit"] == 10
        assert isinstance(data["logs"], list)

class TestServiceIntegration:
    """Tests d'intégration pour les services individuels"""
    
    @pytest.mark.asyncio
    async def test_dbt_service_health(self, http_client, service_urls):
        """Test de santé du service DBT"""
        try:
            response = await http_client.get(f"{service_urls['dbt_service']}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "service" in data
            assert data["service"] == "dbt-transformation"
        except httpx.ConnectError:
            pytest.skip("Service DBT non disponible")
    
    @pytest.mark.asyncio
    async def test_reconciliation_service_health(self, http_client, service_urls):
        """Test de santé du service de réconciliation"""
        try:
            response = await http_client.get(f"{service_urls['reconciliation_service']}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "service" in data
            assert data["service"] == "reconciliation-service"
        except httpx.ConnectError:
            pytest.skip("Service de réconciliation non disponible")
    
    @pytest.mark.asyncio
    async def test_quality_control_service_health(self, http_client, service_urls):
        """Test de santé du service de contrôle qualité"""
        try:
            response = await http_client.get(f"{service_urls['quality_control_service']}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "service" in data
            assert data["service"] == "quality-control-service"
        except httpx.ConnectError:
            pytest.skip("Service de contrôle qualité non disponible")
    
    @pytest.mark.asyncio
    async def test_rca_service_health(self, http_client, service_urls):
        """Test de santé du service RCA"""
        try:
            response = await http_client.get(f"{service_urls['rca_service']}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "service" in data
            assert data["service"] == "rca-service"
        except httpx.ConnectError:
            pytest.skip("Service RCA non disponible")
    
    @pytest.mark.asyncio
    async def test_nifi_service_health(self, http_client, service_urls):
        """Test de santé du service NiFi"""
        try:
            response = await http_client.get(f"{service_urls['nifi_service']}/nifi/")
            assert response.status_code == 200
        except httpx.ConnectError:
            pytest.skip("Service NiFi non disponible")

class TestDataFlowIntegration:
    """Tests d'intégration pour le flux de données"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self, http_client, service_urls, sample_data):
        """Test du flux de données de bout en bout"""
        # 1. Ingestion via l'API Dashboard
        ingest_response = await http_client.post(
            f"{service_urls['api_dashboard']}/data/ingest",
            json=sample_data
        )
        
        assert ingest_response.status_code == 200
        ingest_data = ingest_response.json()
        
        # 2. Vérifier que les données sont acceptées
        assert ingest_data["status"] == "accepted"
        assert ingest_data["records_count"] == len(sample_data)
        
        # 3. Attendre un peu pour le traitement
        await asyncio.sleep(2)
        
        # 4. Vérifier les métriques système
        metrics_response = await http_client.get(
            f"{service_urls['api_dashboard']}/metrics/overview"
        )
        
        assert metrics_response.status_code == 200
        metrics_data = metrics_response.json()
        
        # Vérifier que les métriques sont mises à jour
        assert "system" in metrics_data
        assert "services" in metrics_data
    
    @pytest.mark.asyncio
    async def test_service_communication(self, http_client, service_urls):
        """Test de communication entre services"""
        # Test de l'endpoint de statut des services
        services_response = await http_client.get(
            f"{service_urls['api_dashboard']}/services/status"
        )
        
        assert services_response.status_code == 200
        services_data = services_response.json()
        
        # Vérifier que nous avons des informations sur les services
        assert isinstance(services_data, dict)
        
        # Au moins quelques services devraient être présents
        expected_services = ["api-dashboard-service", "warehouse-service"]
        for service in expected_services:
            if service in services_data:
                service_info = services_data[service]
                assert "name" in service_info
                assert "status" in service_info
                assert "last_check" in service_info

class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, http_client, service_urls):
        """Test de réponse à un endpoint invalide"""
        response = await http_client.get(f"{service_urls['api_dashboard']}/invalid-endpoint")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_data_ingestion(self, http_client, service_urls):
        """Test d'ingestion de données invalides"""
        invalid_data = "invalid json data"
        
        response = await http_client.post(
            f"{service_urls['api_dashboard']}/data/ingest",
            content=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    @pytest.mark.asyncio
    async def test_missing_parameters(self, http_client, service_urls):
        """Test avec des paramètres manquants"""
        response = await http_client.get(f"{service_urls['api_dashboard']}/kpis")
        
        # Devrait fonctionner avec des paramètres par défaut
        assert response.status_code == 200

class TestPerformance:
    """Tests de performance"""
    
    @pytest.mark.asyncio
    async def test_response_times(self, http_client, service_urls):
        """Test des temps de réponse des endpoints"""
        endpoints = [
            "/health",
            "/dashboard/data",
            "/metrics/overview",
            "/kpis"
        ]
        
        max_response_time = 5.0  # 5 secondes maximum
        
        for endpoint in endpoints:
            start_time = datetime.now()
            response = await http_client.get(f"{service_urls['api_dashboard']}{endpoint}")
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            assert response.status_code == 200
            assert response_time < max_response_time, f"Endpoint {endpoint} trop lent: {response_time}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, http_client, service_urls):
        """Test de requêtes concurrentes"""
        async def make_request():
            response = await http_client.get(f"{service_urls['api_dashboard']}/health")
            return response.status_code == 200
        
        # Faire 10 requêtes concurrentes
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Toutes les requêtes devraient réussir
        assert all(results)
        assert len(results) == 10
