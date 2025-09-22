#!/bin/bash

# Script de démarrage rapide pour la plateforme SaaS Data Platform
# Usage: ./start.sh [dev|prod|stop|restart]

set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="saas-platform"

# Fonction pour afficher les messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  SaaS Data Platform${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    print_message "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier la version de Docker
    docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    if [[ $(echo "$docker_version 20.10" | awk '{print ($1 >= $2)}') == 0 ]]; then
        print_warning "Version de Docker recommandée: 20.10+ (actuelle: $docker_version)"
    fi
    
    print_message "Prérequis vérifiés ✓"
}

# Fonction pour créer le fichier .env
create_env_file() {
    if [ ! -f .env ]; then
        print_message "Création du fichier .env..."
        cp env.example .env
        print_message "Fichier .env créé. Veuillez l'adapter selon vos besoins."
    else
        print_message "Fichier .env existant ✓"
    fi
}

# Fonction pour construire les images
build_images() {
    print_message "Construction des images Docker..."
    docker-compose -f $COMPOSE_FILE build
    print_message "Images construites ✓"
}

# Fonction pour démarrer les services
start_services() {
    local mode=$1
    
    print_message "Démarrage des services en mode $mode..."
    
    case $mode in
        "dev")
            docker-compose -f $COMPOSE_FILE up -d
            ;;
        "prod")
            if [ -f "docker-compose.prod.yml" ]; then
                docker-compose -f docker-compose.prod.yml up -d
            else
                docker-compose -f $COMPOSE_FILE up -d
            fi
            ;;
        *)
            docker-compose -f $COMPOSE_FILE up -d
            ;;
    esac
    
    print_message "Services démarrés ✓"
}

# Fonction pour vérifier la santé des services
check_health() {
    print_message "Vérification de la santé des services..."
    
    # Attendre que les services soient prêts
    sleep 10
    
    # Vérifier l'API Dashboard
    if curl -s http://localhost/health > /dev/null; then
        print_message "API Dashboard: ✓"
    else
        print_warning "API Dashboard: ⚠ (peut prendre quelques minutes)"
    fi
    
    # Vérifier la base de données
    if docker-compose -f $COMPOSE_FILE exec -T warehouse-service pg_isready -U warehouse_user -d data_warehouse > /dev/null 2>&1; then
        print_message "Base de données: ✓"
    else
        print_warning "Base de données: ⚠"
    fi
    
    # Vérifier Redis
    if docker-compose -f $COMPOSE_FILE exec -T redis-cache redis-cli ping > /dev/null 2>&1; then
        print_message "Redis: ✓"
    else
        print_warning "Redis: ⚠"
    fi
}

# Fonction pour afficher les URLs des services
show_urls() {
    print_message "URLs des services:"
    echo ""
    echo -e "${BLUE}🌐 Interface Web:${NC}"
    echo "  Dashboard:     http://localhost"
    echo "  API Docs:      http://localhost/docs"
    echo ""
    echo -e "${BLUE}🔧 Services:${NC}"
    echo "  NiFi:          http://localhost/nifi"
    echo "  Grafana:       http://localhost/grafana (admin/admin)"
    echo "  Prometheus:    http://localhost/prometheus"
    echo ""
    echo -e "${BLUE}🔌 APIs Directes:${NC}"
    echo "  API Dashboard: http://localhost:8000"
    echo "  DBT Service:   http://localhost:8001"
    echo "  Recon Service: http://localhost:8002"
    echo "  Quality Svc:   http://localhost:8003"
    echo "  RCA Service:   http://localhost:8004"
    echo ""
}

# Fonction pour arrêter les services
stop_services() {
    print_message "Arrêt des services..."
    docker-compose -f $COMPOSE_FILE down
    print_message "Services arrêtés ✓"
}

# Fonction pour redémarrer les services
restart_services() {
    print_message "Redémarrage des services..."
    docker-compose -f $COMPOSE_FILE restart
    print_message "Services redémarrés ✓"
}

# Fonction pour afficher les logs
show_logs() {
    print_message "Affichage des logs (Ctrl+C pour quitter)..."
    docker-compose -f $COMPOSE_FILE logs -f
}

# Fonction pour nettoyer
cleanup() {
    print_warning "Nettoyage complet des containers, images et volumes..."
    read -p "Êtes-vous sûr ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        docker system prune -f
        print_message "Nettoyage terminé ✓"
    else
        print_message "Nettoyage annulé"
    fi
}

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev      Démarrer en mode développement"
    echo "  prod     Démarrer en mode production"
    echo "  stop     Arrêter tous les services"
    echo "  restart  Redémarrer tous les services"
    echo "  logs     Afficher les logs"
    echo "  health   Vérifier la santé des services"
    echo "  urls     Afficher les URLs des services"
    echo "  clean    Nettoyer complètement (supprime tout)"
    echo "  help     Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 dev     # Démarrage rapide en développement"
    echo "  $0 stop    # Arrêter les services"
    echo "  $0 logs    # Voir les logs"
}

# Fonction principale
main() {
    print_header
    
    case ${1:-dev} in
        "dev"|"development")
            check_prerequisites
            create_env_file
            build_images
            start_services "dev"
            check_health
            show_urls
            print_message "🚀 Plateforme démarrée en mode développement !"
            ;;
        "prod"|"production")
            check_prerequisites
            create_env_file
            build_images
            start_services "prod"
            check_health
            show_urls
            print_message "🚀 Plateforme démarrée en mode production !"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs
            ;;
        "health")
            check_health
            ;;
        "urls")
            show_urls
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Commande inconnue: $1"
            show_help
            exit 1
            ;;
    esac
}

# Exécution du script
main "$@"
