# 🔄 Mise à Jour des Ports Serveur - 9000+ vers 10000+

## 📋 Résumé des Changements

Tous les ports du serveur ont été mis à jour de la série **9000+** vers la série **10000+** pour éviter les conflits avec les services existants.

## 🚀 Nouveaux Ports

### Services Principaux
| Service | Ancien Port | Nouveau Port | URL Directe |
|---------|-------------|--------------|-------------|
| **Dashboard Principal** | 9000 | **10000** | `http://[IP]:10000` |
| **DBT Service** | 9001 | **10001** | `http://[IP]:10001` |
| **Réconciliation** | 9002 | **10002** | `http://[IP]:10002` |
| **Contrôle Qualité** | 9003 | **10003** | `http://[IP]:10003` |
| **RCA Service** | 9004 | **10004** | `http://[IP]:10004` |
| **NiFi** | 9080 | **10080** | `http://[IP]:10080` |

### Base de Données
| Service | Ancien Port | Nouveau Port | URL Directe |
|---------|-------------|--------------|-------------|
| **PostgreSQL** | 9543 | **10543** | `[IP]:10543` |
| **Redis** | 9637 | **10637** | `[IP]:10637` |

### Monitoring
| Service | Ancien Port | Nouveau Port | URL Directe |
|---------|-------------|--------------|-------------|
| **Grafana** | 9300 | **10300** | `http://[IP]:10300` |
| **Prometheus** | 9090 | **10090** | `http://[IP]:10090` |

### Streaming (Optionnel)
| Service | Ancien Port | Nouveau Port | URL Directe |
|---------|-------------|--------------|-------------|
| **Zookeeper** | 9218 | **10218** | `[IP]:10218` |
| **Kafka** | 9092/9093 | **10092/10093** | `[IP]:10092` |

## 📁 Fichiers Modifiés

### 1. **docker-compose.server.yml**
- ✅ Tous les ports des services mis à jour
- ✅ Configuration Kafka mise à jour
- ✅ Commentaires mis à jour

### 2. **env.server.example**
- ✅ Variables de ports mises à jour
- ✅ Configuration pare-feu mise à jour

### 3. **deploy-server.sh**
- ✅ Vérification des ports mise à jour
- ✅ URLs d'accès mises à jour
- ✅ Configuration pare-feu mise à jour

### 4. **nginx/nginx.server.conf**
- ✅ Page d'information mise à jour
- ✅ URLs d'accès direct mises à jour

### 5. **DEPLOYMENT-SERVER.md**
- ✅ Documentation mise à jour
- ✅ Exemples de configuration pare-feu mis à jour

### 6. **Makefile.server**
- ✅ Commandes de vérification des ports mises à jour

## 🔧 Configuration Pare-feu

### UFW (Ubuntu/Debian)
```bash
sudo ufw allow 10000:10004/tcp
sudo ufw allow 10080/tcp
sudo ufw allow 10090/tcp
sudo ufw allow 10300/tcp
sudo ufw allow 10543/tcp
sudo ufw allow 10637/tcp
```

### Firewalld (CentOS/RHEL)
```bash
sudo firewall-cmd --permanent --add-port=10000-10004/tcp
sudo firewall-cmd --permanent --add-port=10080/tcp
sudo firewall-cmd --permanent --add-port=10090/tcp
sudo firewall-cmd --permanent --add-port=10300/tcp
sudo firewall-cmd --permanent --add-port=10543/tcp
sudo firewall-cmd --permanent --add-port=10637/tcp
sudo firewall-cmd --reload
```

## 🌐 Accès via Nginx (Port 80)

Les URLs via Nginx restent **inchangées** :
- **Dashboard** : `http://[IP_SERVEUR]/dashboard/`
- **API Docs** : `http://[IP_SERVEUR]/api/docs`
- **NiFi** : `http://[IP_SERVEUR]/nifi/`
- **Grafana** : `http://[IP_SERVEUR]/grafana/`
- **Prometheus** : `http://[IP_SERVEUR]/prometheus/`

## 🚀 Déploiement

### 1. Arrêter les services existants
```bash
./deploy-server.sh stop
# ou
docker-compose -f docker-compose.server.yml down
```

### 2. Redéployer avec les nouveaux ports
```bash
./deploy-server.sh deploy
# ou
docker-compose -f docker-compose.server.yml up -d
```

### 3. Vérifier les nouveaux ports
```bash
./deploy-server.sh urls
# ou
make -f Makefile.server urls
```

## ✅ Vérification

### 1. Vérifier les ports utilisés
```bash
netstat -tulpn | grep -E ':(10000|10001|10002|10003|10004|10080|10090|10300|10543|10637)'
```

### 2. Tester la connectivité
```bash
curl http://[IP_SERVEUR]:10000/health
curl http://[IP_SERVEUR]:10080/nifi/
curl http://[IP_SERVEUR]:10300/
```

### 3. Vérifier via Makefile
```bash
make -f Makefile.server check-ports
make -f Makefile.server test-connectivity
```

## 📝 Notes Importantes

1. **Ports 80 et 443** : Restent inchangés pour HTTP/HTTPS
2. **Port 10090** : Prometheus maintenant sur 10090 (cohérence avec la série 10000+)
3. **Accès Nginx** : Les URLs via port 80 restent identiques
4. **Configuration** : Tous les fichiers de configuration ont été mis à jour
5. **Documentation** : Toute la documentation reflète les nouveaux ports

## 🔄 Migration

Si vous aviez déjà déployé avec les anciens ports :

1. **Arrêter** les services existants
2. **Mettre à jour** les fichiers de configuration
3. **Redéployer** avec les nouveaux ports
4. **Vérifier** que tout fonctionne correctement

## 📞 Support

En cas de problème avec les nouveaux ports :

1. Vérifiez que les ports ne sont pas déjà utilisés
2. Consultez les logs : `./deploy-server.sh logs`
3. Vérifiez le statut : `docker-compose -f docker-compose.server.yml ps`
4. Testez la connectivité : `./deploy-server.sh health`

---

**🎯 Vos services sont maintenant configurés pour utiliser les ports 10000+ !**
