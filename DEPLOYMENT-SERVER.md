# 🚀 Guide de Déploiement Serveur - SaaS Data Platform

Guide complet pour déployer la plateforme SaaS Data Platform sur un serveur sans IP fixe en utilisant les ports à partir de 9000.

## 📋 Prérequis

### Serveur
- **OS** : Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM** : 8 GB minimum (16 GB recommandé)
- **Stockage** : 50 GB minimum
- **CPU** : 4 cœurs minimum
- **Réseau** : Accès internet avec ports ouverts

### Logiciels
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Curl
- Netstat (pour vérifier les ports)

## 🔧 Installation des Prérequis

### Ubuntu/Debian
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Installation de Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Installation des outils
sudo apt install -y git curl net-tools

# Redémarrer la session pour les groupes
newgrp docker
```

### CentOS/RHEL
```bash
# Installation de Docker
sudo yum install -y docker docker-compose git curl net-tools
sudo systemctl start docker
sudo systemctl enable docker

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

## 📥 Déploiement

### 1. Téléchargement du Projet
```bash
# Cloner le projet
git clone <repository-url>
cd saas

# Ou télécharger l'archive
wget <archive-url>
tar -xzf saas-platform.tar.gz
cd saas
```

### 2. Configuration
```bash
# Copier le fichier de configuration serveur
cp env.server.example .env

# Éditer la configuration
nano .env
```

**Configuration importante à modifier dans `.env` :**
```env
# Mots de passe sécurisés
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=your_very_secure_secret_key_here
GRAFANA_ADMIN_PASSWORD=your_secure_admin_password

# Configuration serveur
BASE_URL=http://[IP_DE_VOTRE_SERVEUR]
```

### 3. Déploiement Automatique
```bash
# Rendre le script exécutable
chmod +x deploy-server.sh

# Déploiement complet
./deploy-server.sh deploy
```

### 4. Déploiement Manuel
```bash
# Construction des images
docker-compose -f docker-compose.server.yml build

# Démarrage des services
docker-compose -f docker-compose.server.yml up -d

# Vérification du statut
docker-compose -f docker-compose.server.yml ps
```

## 🌐 Accès aux Services

### URLs Principales
| Service | URL | Port Direct |
|---------|-----|-------------|
| **Dashboard** | `http://[IP_SERVEUR]/dashboard/` | 10000 |
| **API Docs** | `http://[IP_SERVEUR]/api/docs` | 10000 |
| **NiFi** | `http://[IP_SERVEUR]/nifi/` | 10080 |
| **Grafana** | `http://[IP_SERVEUR]/grafana/` | 10300 |
| **Prometheus** | `http://[IP_SERVEUR]/prometheus/` | 10090 |

### Services de Traitement
| Service | Port | Description |
|---------|------|-------------|
| DBT Service | 10001 | Transformation de données |
| Réconciliation | 10002 | Matching et déduplication |
| Contrôle Qualité | 10003 | Validation et anomalies |
| RCA Service | 10004 | Analyse des causes racines |

### Base de Données
| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 10543 | Data warehouse |
| Redis | 10637 | Cache et sessions |

## 🔒 Configuration Sécurisée

### 1. Pare-feu (UFW)
```bash
# Activer UFW
sudo ufw enable

# Ouvrir les ports nécessaires
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 10000:10004/tcp
sudo ufw allow 10080/tcp
sudo ufw allow 10090/tcp
sudo ufw allow 10300/tcp
sudo ufw allow 10543/tcp
sudo ufw allow 10637/tcp

# Vérifier le statut
sudo ufw status
```

### 2. SSL/TLS (Optionnel)
```bash
# Installation de Certbot
sudo apt install certbot python3-certbot-nginx

# Génération du certificat (remplacer par votre domaine)
sudo certbot --nginx -d your-domain.com

# Configuration Nginx SSL dans nginx/nginx.server.conf
```

### 3. Mots de Passe Sécurisés
```bash
# Générer des mots de passe sécurisés
openssl rand -base64 32  # Pour SECRET_KEY
openssl rand -base64 16  # Pour POSTGRES_PASSWORD
```

## 📊 Monitoring et Maintenance

### 1. Vérification de Santé
```bash
# Script automatique
./deploy-server.sh health

# Manuel
curl http://[IP_SERVEUR]/health
```

### 2. Logs
```bash
# Tous les services
./deploy-server.sh logs

# Service spécifique
docker-compose -f docker-compose.server.yml logs -f api-dashboard-service
```

### 3. Sauvegarde
```bash
# Sauvegarde base de données
docker-compose -f docker-compose.server.yml exec warehouse-service pg_dump -U warehouse_user data_warehouse > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde volumes
docker run --rm -v saas_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

### 4. Mise à Jour
```bash
# Arrêter les services
./deploy-server.sh stop

# Mettre à jour le code
git pull

# Redéployer
./deploy-server.sh deploy
```

## 🔧 Commandes Utiles

### Gestion des Services
```bash
# Démarrage
./deploy-server.sh deploy

# Arrêt
./deploy-server.sh stop

# Redémarrage
./deploy-server.sh restart

# Logs
./deploy-server.sh logs

# Santé
./deploy-server.sh health

# URLs
./deploy-server.sh urls
```

### Docker Compose Direct
```bash
# Statut
docker-compose -f docker-compose.server.yml ps

# Logs spécifiques
docker-compose -f docker-compose.server.yml logs -f [service-name]

# Redémarrage d'un service
docker-compose -f docker-compose.server.yml restart [service-name]

# Shell dans un container
docker-compose -f docker-compose.server.yml exec [service-name] /bin/bash
```

### Maintenance
```bash
# Nettoyage complet
./deploy-server.sh clean

# Nettoyage Docker
docker system prune -f

# Vérification des ports
netstat -tulpn | grep -E ':(80|10000|10001|10002|10003|10004|10080|10090|10300|10543|10637)'
```

## 🌍 Accès Externe

### 1. Sans Domaine (IP Publique)
```bash
# Obtenir l'IP publique
curl ifconfig.me

# Accès via IP
http://[IP_PUBLIQUE]/dashboard/
```

### 2. Avec Domaine Dynamique
```bash
# Configuration No-IP ou DuckDNS
# Mise à jour automatique de l'IP

# Accès via domaine
http://your-domain.duckdns.org/dashboard/
```

### 3. Reverse Proxy Externe
```bash
# Configuration Nginx/Apache externe
# Redirection vers les ports internes

# Exemple Nginx externe
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚨 Dépannage

### Problèmes Courants

#### 1. Ports Occupés
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :9000

# Arrêter le processus
sudo kill -9 [PID]

# Ou changer le port dans docker-compose.server.yml
```

#### 2. Services Non Démarrés
```bash
# Vérifier les logs
docker-compose -f docker-compose.server.yml logs [service-name]

# Redémarrer le service
docker-compose -f docker-compose.server.yml restart [service-name]

# Vérifier les ressources
docker stats
```

#### 3. Base de Données Non Accessible
```bash
# Vérifier la connexion
docker-compose -f docker-compose.server.yml exec warehouse-service pg_isready -U warehouse_user -d data_warehouse

# Vérifier les logs
docker-compose -f docker-compose.server.yml logs warehouse-service

# Redémarrer la base
docker-compose -f docker-compose.server.yml restart warehouse-service
```

#### 4. Problèmes de Mémoire
```bash
# Vérifier l'utilisation mémoire
free -h
docker stats

# Limiter les ressources dans docker-compose.server.yml
services:
  api-dashboard-service:
    deploy:
      resources:
        limits:
          memory: 1G
```

## 📈 Optimisation Performance

### 1. Configuration Serveur
```bash
# Augmenter les limites système
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimiser Docker
sudo nano /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 2. Configuration Base de Données
```sql
-- Optimisations PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### 3. Monitoring Avancé
```bash
# Installation de monitoring système
sudo apt install htop iotop nethogs

# Surveillance en temps réel
htop
iotop
nethogs
```

## 🔄 Sauvegarde et Restauration

### Script de Sauvegarde Automatique
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde base de données
docker-compose -f docker-compose.server.yml exec -T warehouse-service pg_dump -U warehouse_user data_warehouse > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarde volumes
docker run --rm -v saas_postgres-data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/volumes_backup_$DATE.tar.gz /data

# Nettoyage des anciennes sauvegardes (garde 7 jours)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Sauvegarde terminée: $DATE"
```

### Cron Job pour Sauvegarde Automatique
```bash
# Éditer le crontab
crontab -e

# Ajouter la ligne pour sauvegarde quotidienne à 2h du matin
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

## 📞 Support

### Logs Importants
- **Application** : `docker-compose -f docker-compose.server.yml logs -f`
- **Système** : `/var/log/syslog`
- **Nginx** : `docker-compose -f docker-compose.server.yml logs nginx`
- **Base de données** : `docker-compose -f docker-compose.server.yml logs warehouse-service`

### Informations de Debug
```bash
# Collecter les informations système
./deploy-server.sh urls > server_info.txt
docker-compose -f docker-compose.server.yml ps >> server_info.txt
docker stats --no-stream >> server_info.txt
free -h >> server_info.txt
df -h >> server_info.txt
```

---

**🎯 Votre plateforme SaaS Data Platform est maintenant déployée et accessible sur votre serveur !**

**📋 Prochaines étapes :**
1. Tester l'accès aux services via les URLs fournies
2. Configurer les mots de passe sécurisés
3. Mettre en place les sauvegardes automatiques
4. Configurer le monitoring avancé
5. Optimiser selon vos besoins spécifiques
