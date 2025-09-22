# 📖 GUIDE UTILISATEUR - Plateforme SaaS Data Platform

## 🎯 Vue d'ensemble

Cette plateforme SaaS offre une solution complète de traitement et d'analyse de données avec une interface centralisée pour orchestrer tous les services. Elle permet d'ingérer, transformer, réconcilier, contrôler la qualité et analyser les données depuis une interface web unique.

## 🚀 Accès à la Plateforme

### URLs Principales

| Service | URL | Description | Identifiants |
|---------|-----|-------------|--------------|
| **Dashboard Principal** | http://localhost | Interface web centralisée | - |
| **Documentation API** | http://localhost/docs | Documentation Swagger interactive | - |
| **NiFi (Ingestion)** | http://localhost/nifi | Interface d'ingestion de données | - |
| **Grafana (Monitoring)** | http://localhost/grafana | Dashboards de monitoring | admin/admin |
| **Prometheus (Métriques)** | http://localhost/prometheus | Métriques système | - |

### Démarrage Rapide

```bash
# 1. Démarrer la plateforme
docker-compose up -d

# 2. Vérifier le statut
docker-compose ps

# 3. Accéder au dashboard
# Ouvrir http://localhost dans votre navigateur
```

## 🏠 Interface Principale - Dashboard Central

### Widgets Disponibles

Le dashboard principal propose 5 widgets configurables :

#### 1. **État des Services** (System Health)
- **Fonction** : Monitoring en temps réel de tous les services
- **Données** : Statut (healthy/unhealthy/unreachable) de chaque service
- **Services surveillés** :
  - nifi-service (Ingestion)
  - dbt-service (Transformation)
  - reconciliation-service (Réconciliation)
  - quality-control-service (Contrôle qualité)
  - rca-service (Analyse RCA)
  - warehouse-service (Base de données)

#### 2. **Score de Qualité** (Data Quality)
- **Fonction** : Score global de qualité des données
- **Métriques** :
  - Complétude : 98.2%
  - Précision : 96.8%
  - Consistance : 94.5%
  - Validité : 97.1%
- **Tendance** : Évolution du score dans le temps

#### 3. **Débit de Traitement** (Processing Throughput)
- **Fonction** : Volume de données traitées par minute
- **Unité** : records/min
- **Historique** : Graphique temporel des performances

#### 4. **Taux d'Erreur** (Error Rate)
- **Fonction** : Surveillance des erreurs système
- **Unité** : Pourcentage
- **Seuils** : Alertes automatiques si > 5%

#### 5. **Résumé KPI** (KPI Summary)
- **Fonction** : Indicateurs clés de performance
- **Métriques** :
  - Qualité : 95.5%
  - Débit : 1250 rec/min
  - Erreurs : 0.5%
  - Uptime : 99.9%

### Configuration du Dashboard

```bash
# Personnaliser la disposition des widgets
curl -X GET "http://localhost/dashboard/config"

# Sauvegarder une nouvelle configuration
curl -X POST "http://localhost/dashboard/config" \
  -H "Content-Type: application/json" \
  -d '{
    "layout": "grid",
    "refresh_interval": 30,
    "widgets": [...]
  }'
```

## 🔄 Workflows d'Utilisation

### 1. **Workflow d'Ingestion de Données**

#### Via l'Interface Web (Recommandé)
1. **Accéder à NiFi** : http://localhost/nifi
2. **Créer un flux** : Glisser-déposer les processeurs
3. **Configurer les sources** : CRM, ERP, fichiers, APIs
4. **Démarrer le flux** : Bouton "Start" sur le processeur

#### Via l'API REST
```bash
# Ingestion directe via API
curl -X POST "http://localhost/data/ingest" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "id": "1",
      "name": "John Doe",
      "email": "john@example.com",
      "value": 100.50,
      "source": "CRM"
    }
  ]'
```

### 2. **Workflow de Transformation des Données**

#### Via l'API DBT Service
```bash
# Transformation avec normalisation
curl -X POST "http://localhost:8001/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "transformation_type": "normalize",
    "parameters": {
      "normalize_numeric": true,
      "trim_strings": true,
      "standardize_dates": true
    }
  }'

# Calcul de KPI
curl -X POST "http://localhost:8001/kpi/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "kpi_type": "revenue_metrics",
    "time_period": "monthly"
  }'
```

### 3. **Workflow de Contrôle Qualité**

#### Via l'API Quality Control Service
```bash
# Vérification complète de qualité
curl -X POST "http://localhost:8003/check" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "quality_rules": [
      {
        "type": "required_field",
        "field": "email",
        "severity": "error"
      },
      {
        "type": "format_validation",
        "field": "email",
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
      }
    ],
    "check_completeness": true,
    "check_validity": true,
    "check_consistency": true
  }'

# Détection d'anomalies
curl -X POST "http://localhost:8003/detect-anomalies" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "anomaly_types": ["statistical", "pattern", "outlier"],
    "sensitivity": 0.8
  }'
```

### 4. **Workflow de Réconciliation**

#### Via l'API Reconciliation Service
```bash
# Réconciliation d'entités
curl -X POST "http://localhost:8002/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
    "datasets": [
      {"name": "CRM", "data": [...]},
      {"name": "ERP", "data": [...]}
    ],
    "matching_rules": {
      "email": {"weight": 0.4, "threshold": 0.8},
      "phone": {"weight": 0.3, "threshold": 0.7},
      "name": {"weight": 0.3, "threshold": 0.6}
    }
  }'

# Déduplication
curl -X POST "http://localhost:8002/deduplicate" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "duplicate_threshold": 0.85,
    "merge_strategy": "keep_most_complete"
  }'
```

### 5. **Workflow d'Analyse RCA**

#### Via l'API RCA Service
```bash
# Analyse des causes racines
curl -X POST "http://localhost:8004/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "analysis_type": "comprehensive",
    "target_metric": "error_rate",
    "time_window": "30d",
    "correlation_threshold": 0.7
  }'

# Prédiction d'échecs
curl -X POST "http://localhost:8004/predict-failure" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "prediction_horizon": "7d",
    "confidence_threshold": 0.8
  }'
```

## 📊 Monitoring et Alertes

### Dashboard Grafana

1. **Accéder à Grafana** : http://localhost/grafana
2. **Identifiants** : admin/admin
3. **Dashboards disponibles** :
   - **Système** : Métriques d'infrastructure
   - **Qualité** : Métriques de qualité des données
   - **Performance** : Métriques de performance
   - **Business** : KPI métier

### Configuration des Alertes

#### Via l'API Alertes
```bash
# Créer une règle d'alerte
curl -X POST "http://localhost/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Score de qualité critique",
    "condition": "data_quality_score < 80",
    "threshold": 80.0,
    "severity": "critical",
    "enabled": true
  }'

# Consulter les alertes actives
curl -X GET "http://localhost/alerts/active"

# Résoudre une alerte
curl -X POST "http://localhost/alerts/alerts/{alert_id}/resolve"
```

### Types d'Alertes Disponibles

1. **Qualité des Données**
   - Score de qualité < seuil
   - Taux de complétude faible
   - Anomalies détectées

2. **Performance Système**
   - Temps de réponse élevé
   - Utilisation CPU/Mémoire élevée
   - Débit de traitement faible

3. **Disponibilité Services**
   - Service indisponible
   - Erreurs de connexion
   - Timeout de requêtes

## 🔧 Gestion des Données

### Consultation des Données

```bash
# Récupérer des données avec filtres
curl -X GET "http://localhost/api/data?limit=100&offset=0&filters=status:active"

# Export des données
curl -X GET "http://localhost/api/data/export?format=json&filters=date:2024-01-01"

# Analytics avancées
curl -X GET "http://localhost/api/analytics?metric=revenue&time_range=30d&granularity=day"
```

### Opérations CRUD

```bash
# Créer des données
curl -X POST "http://localhost/api/data" \
  -H "Content-Type: application/json" \
  -d '{"name": "Nouveau Record", "value": 150.0}'

# Mettre à jour
curl -X PUT "http://localhost/api/data/{record_id}" \
  -H "Content-Type: application/json" \
  -d '{"value": 200.0}'

# Supprimer
curl -X DELETE "http://localhost/api/data/{record_id}"
```

## 🚨 Gestion des Erreurs

### Codes d'Erreur Courants

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Requête malformée | Vérifier le format JSON |
| 401 | Non autorisé | Vérifier les identifiants |
| 404 | Service non trouvé | Vérifier l'URL du service |
| 500 | Erreur serveur | Consulter les logs |
| 503 | Service indisponible | Vérifier le statut du service |

### Diagnostic des Problèmes

```bash
# Vérifier l'état de santé global
curl -X GET "http://localhost/health"

# Logs d'un service spécifique
docker-compose logs -f api-dashboard-service

# Logs de tous les services
docker-compose logs -f
```

## 📈 Optimisation des Performances

### Recommandations

1. **Monitoring Continu**
   - Surveiller le dashboard principal
   - Configurer des alertes proactives
   - Analyser les tendances Grafana

2. **Gestion des Ressources**
   - Surveiller l'utilisation CPU/Mémoire
   - Ajuster les limites Docker si nécessaire
   - Optimiser les requêtes de base de données

3. **Qualité des Données**
   - Configurer des règles de qualité appropriées
   - Surveiller les scores de qualité
   - Traiter rapidement les anomalies

### Scaling Horizontal

```bash
# Augmenter le nombre d'instances d'un service
docker-compose up -d --scale dbt-service=3
docker-compose up -d --scale quality-control-service=2
```

## 🔐 Sécurité

### Bonnes Pratiques

1. **Authentification**
   - Utiliser des clés API sécurisées
   - Changer les mots de passe par défaut
   - Implémenter l'authentification multi-facteurs

2. **Réseau**
   - Utiliser HTTPS en production
   - Configurer un firewall approprié
   - Isoler les services sensibles

3. **Données**
   - Chiffrer les données sensibles
   - Implémenter des sauvegardes régulières
   - Auditer les accès aux données

## 🆘 Support et Dépannage

### Ressources de Support

1. **Documentation API** : http://localhost/docs
2. **Logs système** : `docker-compose logs`
3. **Monitoring** : http://localhost/grafana
4. **Métriques** : http://localhost/prometheus

### Commandes de Dépannage

```bash
# Redémarrer un service
docker-compose restart api-dashboard-service

# Redémarrer tous les services
docker-compose restart

# Vérifier l'espace disque
docker system df

# Nettoyer les ressources inutilisées
docker system prune
```

### Contacts Support

- **Email** : support@saas-platform.com
- **Documentation** : Voir README.md
- **Issues** : GitHub Issues du projet

## 📚 Ressources Supplémentaires

### Documentation Technique

- [Architecture détaillée](CONCEPTION.md)
- [Guide de déploiement](DEPLOYMENT-SERVER.md)
- [Configuration Kafka](KAFKA-KRAFT-SUMMARY.md)

### Formation

1. **Tutoriels API** : Utiliser la documentation Swagger interactive
2. **Exemples de code** : Voir le dossier `tests/`
3. **Cas d'usage** : Consulter les exemples dans le README

---

**🎯 Ce guide vous permet de maîtriser complètement la plateforme SaaS Data Platform. Pour toute question, consultez la documentation API interactive ou contactez le support.**
