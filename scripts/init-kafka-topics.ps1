# Script PowerShell d'initialisation des topics Kafka en mode KRaft
# Ce script configure les topics nécessaires pour le SaaS Data Platform

param(
    [string]$KafkaBootstrapServer = "localhost:9092",
    [int]$WaitTime = 30
)

Write-Host "🚀 Initialisation des topics Kafka en mode KRaft..." -ForegroundColor Green
Write-Host "📡 Serveur Kafka: $KafkaBootstrapServer" -ForegroundColor Cyan

# Attendre que Kafka soit prêt
Write-Host "⏳ Attente que Kafka soit prêt (${WaitTime}s)..." -ForegroundColor Yellow
Start-Sleep -Seconds $WaitTime

# Fonction pour créer un topic s'il n'existe pas
function Create-TopicIfNotExists {
    param(
        [string]$TopicName,
        [int]$Partitions = 3,
        [int]$ReplicationFactor = 1
    )
    
    Write-Host "🔍 Vérification du topic: $TopicName" -ForegroundColor Cyan
    
    try {
        $existingTopics = docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --list 2>$null
        if ($existingTopics -contains $TopicName) {
            Write-Host "✅ Topic '$TopicName' existe déjà" -ForegroundColor Green
        } else {
            Write-Host "📝 Création du topic: $TopicName (partitions: $Partitions, replication: $ReplicationFactor)" -ForegroundColor Yellow
            docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --create --topic $TopicName --partitions $Partitions --replication-factor $ReplicationFactor --if-not-exists
            Write-Host "✅ Topic '$TopicName' créé avec succès" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Erreur lors de la création du topic '$TopicName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Créer les topics principaux
Write-Host "📋 Création des topics principaux..." -ForegroundColor Green

# Topics pour les événements CDR (Call Detail Records)
Create-TopicIfNotExists "cdr-events" 3 1
Create-TopicIfNotExists "cdr-raw" 3 1
Create-TopicIfNotExists "cdr-processed" 3 1

# Topics pour les alertes et notifications
Create-TopicIfNotExists "alerts" 3 1
Create-TopicIfNotExists "notifications" 3 1

# Topics pour les métriques et monitoring
Create-TopicIfNotExists "metrics" 3 1
Create-TopicIfNotExists "health-checks" 3 1

# Topics pour les données de qualité
Create-TopicIfNotExists "quality-events" 3 1
Create-TopicIfNotExists "data-quality-reports" 3 1

# Topics pour la réconciliation
Create-TopicIfNotExists "reconciliation-events" 3 1
Create-TopicIfNotExists "matching-results" 3 1

# Topics pour l'analyse des causes racines
Create-TopicIfNotExists "rca-events" 3 1
Create-TopicIfNotExists "anomaly-detection" 3 1

# Topics pour DBT et transformations
Create-TopicIfNotExists "dbt-events" 3 1
Create-TopicIfNotExists "transformation-status" 3 1

# Topics pour les logs et audit
Create-TopicIfNotExists "audit-logs" 3 1
Create-TopicIfNotExists "system-logs" 3 1

# Topics pour les données de test
Create-TopicIfNotExists "test-events" 1 1

Write-Host ""
Write-Host "📊 Liste des topics créés:" -ForegroundColor Green
try {
    docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --list
} catch {
    Write-Host "❌ Erreur lors de la récupération de la liste des topics" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Initialisation des topics Kafka terminée avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Commandes utiles:" -ForegroundColor Cyan
Write-Host "  - Lister les topics: docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --list"
Write-Host "  - Décrire un topic: docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --describe --topic <topic-name>"
Write-Host "  - Consommer un topic: docker exec kafka kafka-console-consumer --bootstrap-server $KafkaBootstrapServer --topic <topic-name> --from-beginning"
Write-Host "  - Produire vers un topic: docker exec kafka kafka-console-producer --bootstrap-server $KafkaBootstrapServer --topic <topic-name>"
