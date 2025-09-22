# Makefile pour la plateforme SaaS Data Platform

.PHONY: help build up down restart logs clean test lint format

# Variables
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = saas-platform

# Couleurs pour les messages
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Afficher l'aide
	@echo "$(GREEN)SaaS Data Platform - Commandes disponibles$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Construire toutes les images Docker
	@echo "$(GREEN)Construction des images Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Démarrer tous les services
	@echo "$(GREEN)Démarrage des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

up-build: ## Construire et démarrer tous les services
	@echo "$(GREEN)Construction et démarrage des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up --build -d

down: ## Arrêter tous les services
	@echo "$(RED)Arrêt des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart: ## Redémarrer tous les services
	@echo "$(YELLOW)Redémarrage des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

logs: ## Afficher les logs de tous les services
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Afficher les logs de l'API Dashboard
	docker-compose -f $(COMPOSE_FILE) logs -f api-dashboard-service

logs-db: ## Afficher les logs de la base de données
	docker-compose -f $(COMPOSE_FILE) logs -f warehouse-service

logs-nifi: ## Afficher les logs de NiFi
	docker-compose -f $(COMPOSE_FILE) logs -f nifi-service

status: ## Afficher le statut de tous les services
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Vérifier la santé de tous les services
	@echo "$(GREEN)Vérification de la santé des services...$(NC)"
	@curl -s http://localhost/health | jq . || echo "$(RED)Service API non disponible$(NC)"
	@curl -s http://localhost:8001/health | jq . || echo "$(RED)Service DBT non disponible$(NC)"
	@curl -s http://localhost:8002/health | jq . || echo "$(RED)Service Réconciliation non disponible$(NC)"
	@curl -s http://localhost:8003/health | jq . || echo "$(RED)Service Contrôle Qualité non disponible$(NC)"
	@curl -s http://localhost:8004/health | jq . || echo "$(RED)Service RCA non disponible$(NC)"

clean: ## Nettoyer les containers, images et volumes
	@echo "$(RED)Nettoyage complet...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

clean-volumes: ## Nettoyer uniquement les volumes
	@echo "$(RED)Nettoyage des volumes...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v

# Commandes de développement
dev-setup: ## Configuration de l'environnement de développement
	@echo "$(GREEN)Configuration de l'environnement de développement...$(NC)"
	pip install -r tests/requirements.txt
	cp .env.example .env

# Tests
test: ## Exécuter tous les tests
	@echo "$(GREEN)Exécution des tests...$(NC)"
	pytest tests/ -v

test-unit: ## Exécuter les tests unitaires
	@echo "$(GREEN)Exécution des tests unitaires...$(NC)"
	pytest tests/unit/ -v

test-integration: ## Exécuter les tests d'intégration
	@echo "$(GREEN)Exécution des tests d'intégration...$(NC)"
	pytest tests/integration/ -v

test-coverage: ## Exécuter les tests avec couverture
	@echo "$(GREEN)Exécution des tests avec couverture...$(NC)"
	pytest tests/ --cov=. --cov-report=html --cov-report=term

# Linting et formatage
lint: ## Vérifier le code avec flake8
	@echo "$(GREEN)Vérification du code...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Formater le code avec black
	@echo "$(GREEN)Formatage du code...$(NC)"
	black .
	isort .

# Base de données
db-init: ## Initialiser la base de données
	@echo "$(GREEN)Initialisation de la base de données...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec warehouse-service psql -U warehouse_user -d data_warehouse -f /docker-entrypoint-initdb.d/init.sql

db-backup: ## Sauvegarder la base de données
	@echo "$(GREEN)Sauvegarde de la base de données...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec warehouse-service pg_dump -U warehouse_user data_warehouse > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restaurer la base de données (usage: make db-restore BACKUP_FILE=backup.sql)
	@echo "$(GREEN)Restauration de la base de données...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec -T warehouse-service psql -U warehouse_user -d data_warehouse < $(BACKUP_FILE)

# Monitoring
monitor: ## Démarrer le monitoring (Prometheus + Grafana)
	@echo "$(GREEN)Démarrage du monitoring...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d prometheus grafana

monitor-stop: ## Arrêter le monitoring
	@echo "$(RED)Arrêt du monitoring...$(NC)"
	docker-compose -f $(COMPOSE_FILE) stop prometheus grafana

# Déploiement
deploy-prod: ## Déployer en production
	@echo "$(GREEN)Déploiement en production...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d

deploy-dev: ## Déployer en développement
	@echo "$(GREEN)Déploiement en développement...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d

# Utilitaires
shell-api: ## Ouvrir un shell dans le container API
	docker-compose -f $(COMPOSE_FILE) exec api-dashboard-service /bin/bash

shell-db: ## Ouvrir un shell dans le container base de données
	docker-compose -f $(COMPOSE_FILE) exec warehouse-service /bin/bash

shell-nifi: ## Ouvrir un shell dans le container NiFi
	docker-compose -f $(COMPOSE_FILE) exec nifi-service /bin/bash

# Scaling
scale-dbt: ## Scale le service DBT (usage: make scale-dbt REPLICAS=3)
	@echo "$(GREEN)Scaling du service DBT...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d --scale dbt-service=$(REPLICAS)

scale-quality: ## Scale le service de contrôle qualité (usage: make scale-quality REPLICAS=2)
	@echo "$(GREEN)Scaling du service de contrôle qualité...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d --scale quality-control-service=$(REPLICAS)

# Documentation
docs: ## Générer la documentation
	@echo "$(GREEN)Génération de la documentation...$(NC)"
	@echo "Documentation disponible sur:"
	@echo "  - API: http://localhost/docs"
	@echo "  - Dashboard: http://localhost"
	@echo "  - Grafana: http://localhost/grafana"
	@echo "  - Prometheus: http://localhost/prometheus"

# Quick start
quick-start: build up ## Démarrage rapide (build + up)
	@echo "$(GREEN)Démarrage rapide terminé!$(NC)"
	@echo "Services disponibles:"
	@echo "  - Dashboard: http://localhost"
	@echo "  - API Docs: http://localhost/docs"
	@echo "  - NiFi: http://localhost/nifi"
	@echo "  - Grafana: http://localhost/grafana"

# Nettoyage spécifique
clean-logs: ## Nettoyer les logs
	@echo "$(RED)Nettoyage des logs...$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs --tail=0 > /dev/null

clean-cache: ## Nettoyer le cache Docker
	@echo "$(RED)Nettoyage du cache Docker...$(NC)"
	docker system prune -f

# Statistiques
stats: ## Afficher les statistiques des containers
	@echo "$(GREEN)Statistiques des containers:$(NC)"
	docker stats --no-stream

# Mise à jour
update: ## Mettre à jour les images Docker
	@echo "$(GREEN)Mise à jour des images Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) pull
	docker-compose -f $(COMPOSE_FILE) up -d

# Vérification des ports
check-ports: ## Vérifier les ports utilisés
	@echo "$(GREEN)Vérification des ports:$(NC)"
	@netstat -tulpn | grep -E ':(80|443|8000|8001|8002|8003|8004|8080|5432|6379|9090|3000)' || echo "Aucun port en conflit détecté"

# Installation des dépendances de développement
install-dev: ## Installer les dépendances de développement
	@echo "$(GREEN)Installation des dépendances de développement...$(NC)"
	pip install -r tests/requirements.txt
	@echo "Dépendances installées avec succès!"

# Configuration initiale
init: ## Configuration initiale du projet
	@echo "$(GREEN)Configuration initiale...$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@mkdir -p logs uploads exports temp
	@echo "Configuration initiale terminée!"

# Afficher les URLs des services
urls: ## Afficher les URLs des services
	@echo "$(GREEN)URLs des services:$(NC)"
	@echo "  Dashboard:     http://localhost"
	@echo "  API Docs:      http://localhost/docs"
	@echo "  NiFi:          http://localhost/nifi"
	@echo "  Grafana:       http://localhost/grafana (admin/admin)"
	@echo "  Prometheus:    http://localhost/prometheus"
	@echo "  API Direct:    http://localhost:8000"
	@echo "  DBT Service:   http://localhost:8001"
	@echo "  Recon Service: http://localhost:8002"
	@echo "  Quality Svc:   http://localhost:8003"
	@echo "  RCA Service:   http://localhost:8004"
