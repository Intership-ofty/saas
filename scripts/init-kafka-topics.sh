#!/bin/bash

# Script d'initialisation des topics Kafka en mode KRaft
# Ce script configure les topics nécessaires pour le SaaS Data Platform

set -e

KAFKA_BOOTSTRAP_SERVER=${KAFKA_BOOTSTRAP_SERVER:-"localhost:9092"}
WAIT_TIME=${WAIT_TIME:-30}

echo "🚀 Initialisation des topics Kafka en mode KRaft..."
echo "📡 Serveur Kafka: $KAFKA_BOOTSTRAP_SERVER"

# Attendre que Kafka soit prêt
echo "⏳ Attente que Kafka soit prêt (${WAIT_TIME}s)..."
sleep $WAIT_TIME

# Fonction pour créer un topic s'il n'existe pas
create_topic_if_not_exists() {
    local topic_name=$1
    local partitions=${2:-3}
    local replication_factor=${3:-1}
    
    echo "🔍 Vérification du topic: $topic_name"
    
    if kafka-topics --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --list | grep -q "^$topic_name$"; then
        echo "✅ Topic '$topic_name' existe déjà"
    else
        echo "📝 Création du topic: $topic_name (partitions: $partitions, replication: $replication_factor)"
        kafka-topics --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
            --create \
            --topic $topic_name \
            --partitions $partitions \
            --replication-factor $replication_factor \
            --if-not-exists
        echo "✅ Topic '$topic_name' créé avec succès"
    fi
}

# Créer les topics principaux
echo "📋 Création des topics principaux..."

# Topics pour les événements CDR (Call Detail Records)
create_topic_if_not_exists "cdr-events" 3 1
create_topic_if_not_exists "cdr-raw" 3 1
create_topic_if_not_exists "cdr-processed" 3 1

# Topics pour les alertes et notifications
create_topic_if_not_exists "alerts" 3 1
create_topic_if_not_exists "notifications" 3 1

# Topics pour les métriques et monitoring
create_topic_if_not_exists "metrics" 3 1
create_topic_if_not_exists "health-checks" 3 1

# Topics pour les données de qualité
create_topic_if_not_exists "quality-events" 3 1
create_topic_if_not_exists "data-quality-reports" 3 1

# Topics pour la réconciliation
create_topic_if_not_exists "reconciliation-events" 3 1
create_topic_if_not_exists "matching-results" 3 1

# Topics pour l'analyse des causes racines
create_topic_if_not_exists "rca-events" 3 1
create_topic_if_not_exists "anomaly-detection" 3 1

# Topics pour DBT et transformations
create_topic_if_not_exists "dbt-events" 3 1
create_topic_if_not_exists "transformation-status" 3 1

# Topics pour les logs et audit
create_topic_if_not_exists "audit-logs" 3 1
create_topic_if_not_exists "system-logs" 3 1

# Topics pour les données de test
create_topic_if_not_exists "test-events" 1 1

echo ""
echo "📊 Liste des topics créés:"
kafka-topics --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --list

echo ""
echo "✅ Initialisation des topics Kafka terminée avec succès!"
echo ""
echo "🔧 Commandes utiles:"
echo "  - Lister les topics: kafka-topics --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --list"
echo "  - Décrire un topic: kafka-topics --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --describe --topic <topic-name>"
echo "  - Consommer un topic: kafka-console-consumer --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --topic <topic-name> --from-beginning"
echo "  - Produire vers un topic: kafka-console-producer --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --topic <topic-name>"
