#!/bin/bash

# Script de déploiement pour serveur sans IP fixe
# Utilise les ports à partir de 9000

set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.server.yml"
PROJECT_NAME="saas-platform-server"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  SaaS Data Platform - Serveur${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
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
    
    # Vérifier les ports disponibles
    print_message "Vérification des ports disponibles..."
    PORTS=(80 10000 10001 10002 10003 10004 10080 10090 10300 10543 10637)
    for port in "${PORTS[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            print_warning "Port $port déjà utilisé"
        else
            print_message "Port $port disponible ✓"
        fi
    done
    
    print_message "Prérequis vérifiés ✓"
}

# Fonction pour créer le fichier .env
create_env_file() {
    if [ ! -f .env ]; then
        print_message "Création du fichier .env..."
        cp env.server.example .env
        print_message "Fichier .env créé. Veuillez l'adapter selon vos besoins."
        print_warning "IMPORTANT: Changez les mots de passe par défaut !"
    else
        print_message "Fichier .env existant ✓"
    fi
}

# Fonction pour obtenir l'IP du serveur
get_server_ip() {
    # Essayer différentes méthodes pour obtenir l'IP
    if command -v hostname &> /dev/null; then
        SERVER_IP=$(hostname -I | awk '{print $1}')
    elif command -v ip &> /dev/null; then
        SERVER_IP=$(ip route get 1 | awk '{print $7; exit}')
    else
        SERVER_IP="localhost"
    fi
    
    echo "$SERVER_IP"
}

# Fonction pour afficher les URLs d'accès
show_access_urls() {
    local server_ip=$(get_server_ip)
    
    print_message "URLs d'accès aux services:"
    echo ""
    echo -e "${BLUE}🌐 Accès Principal (via Nginx):${NC}"
    echo "  Dashboard:     http://$server_ip/dashboard/"
    echo "  API Docs:      http://$server_ip/api/docs"
    echo "  NiFi:          http://$server_ip/nifi/"
    echo "  Grafana:       http://$server_ip/grafana/ (admin/[mot de passe configuré])"
    echo "  Prometheus:    http://$server_ip/prometheus/"
    echo ""
    echo -e "${BLUE}🔌 Accès Direct par Port:${NC}"
    echo "  Dashboard:     http://$server_ip:10000"
    echo "  NiFi:          http://$server_ip:10080"
    echo "  DBT Service:   http://$server_ip:10001"
    echo "  Réconciliation: http://$server_ip:10002"
    echo "  Contrôle Qualité: http://$server_ip:10003"
    echo "  RCA Service:   http://$server_ip:10004"
    echo "  Grafana:       http://$server_ip:10300"
    echo "  Prometheus:    http://$server_ip:10090"
    echo ""
    echo -e "${BLUE}💾 Base de Données:${NC}"
    echo "  PostgreSQL:    $server_ip:10543"
    echo "  Redis:         $server_ip:10637"
    echo ""
    echo -e "${BLUE}ℹ️  Information Serveur:${NC}"
    echo "  Page d'info:   http://$server_ip/info"
    echo "  Health Check:  http://$server_ip/health"
}

# Fonction pour construire et démarrer
deploy() {
    print_message "Déploiement de la plateforme SaaS..."
    
    # Arrêter les services existants
    print_message "Arrêt des services existants..."
    docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    
    # Construire les images
    print_message "Construction des images Docker..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # Démarrer les services
    print_message "Démarrage des services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    print_message "Déploiement terminé ✓"
}

# Fonction pour vérifier la santé des services
check_health() {
    print_message "Vérification de la santé des services..."
    
    # Attendre que les services soient prêts
    print_message "Attente du démarrage des services (30 secondes)..."
    sleep 30
    
    local server_ip=$(get_server_ip)
    
    # Vérifier l'API Dashboard
    if curl -s "http://$server_ip/health" > /dev/null; then
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
    
    # Afficher le statut des containers
    print_message "Statut des containers:"
    docker-compose -f $COMPOSE_FILE ps
}

# Fonction pour afficher les logs
show_logs() {
    print_message "Affichage des logs (Ctrl+C pour quitter)..."
    docker-compose -f $COMPOSE_FILE logs -f
}

# Fonction pour arrêter les services
stop_services() {
    print_message "Arrêt des services..."
    docker-compose -f $COMPOSE_FILE down
    print_message "Services arrêtés ✓"
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
    echo "  deploy   Déployer la plateforme sur le serveur"
    echo "  stop     Arrêter tous les services"
    echo "  restart  Redémarrer tous les services"
    echo "  logs     Afficher les logs"
    echo "  health   Vérifier la santé des services"
    echo "  urls     Afficher les URLs d'accès"
    echo "  clean    Nettoyer complètement (supprime tout)"
    echo "  help     Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 deploy    # Déploiement complet"
    echo "  $0 stop      # Arrêter les services"
    echo "  $0 logs      # Voir les logs"
    echo "  $0 urls      # Voir les URLs d'accès"
}

# Fonction pour configurer le pare-feu (optionnel)
configure_firewall() {
    print_message "Configuration du pare-feu (optionnel)..."
    
    if command -v ufw &> /dev/null; then
        print_message "Configuration UFW..."
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 10000:10004/tcp
        sudo ufw allow 10080/tcp
        sudo ufw allow 10090/tcp
        sudo ufw allow 10300/tcp
        sudo ufw allow 10543/tcp
        sudo ufw allow 10637/tcp
        print_message "Pare-feu configuré ✓"
    elif command -v firewall-cmd &> /dev/null; then
        print_message "Configuration firewalld..."
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --permanent --add-port=10000-10004/tcp
        sudo firewall-cmd --permanent --add-port=10080/tcp
        sudo firewall-cmd --permanent --add-port=10090/tcp
        sudo firewall-cmd --permanent --add-port=10300/tcp
        sudo firewall-cmd --permanent --add-port=10543/tcp
        sudo firewall-cmd --permanent --add-port=10637/tcp
        sudo firewall-cmd --reload
        print_message "Pare-feu configuré ✓"
    else
        print_warning "Aucun gestionnaire de pare-feu détecté"
        print_warning "Assurez-vous d'ouvrir les ports nécessaires manuellement"
    fi
}

# Fonction principale
main() {
    print_header
    
    case ${1:-deploy} in
        "deploy")
            check_prerequisites
            create_env_file
            deploy
            check_health
            show_access_urls
            print_message "🚀 Plateforme déployée sur le serveur !"
            print_message "📋 Consultez les URLs ci-dessus pour accéder aux services"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            docker-compose -f $COMPOSE_FILE restart
            print_message "Services redémarrés ✓"
            ;;
        "logs")
            show_logs
            ;;
        "health")
            check_health
            ;;
        "urls")
            show_access_urls
            ;;
        "clean")
            cleanup
            ;;
        "firewall")
            configure_firewall
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
