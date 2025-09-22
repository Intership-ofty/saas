**Objectif :**
Générer un projet SaaS conteneurisé avec Docker, utilisant Python 3.11+, Apache NiFi pour l’ingestion et des microservices pour :

* Transformation (dbt)
* Reconciliation (Zingg)
* Contrôle qualité (Soda)
* RCA (Root Cause Analysis)
* API / Dashboard (FastAPI)
* Stockage historique (PostgreSQL ou MongoDB)

Le projet doit être **opérationnel, production-ready, modulaire, scalable**, avec endpoints REST, tests unitaires et README détaillé.

---

## 1️⃣ Services à générer explicitement

1. **nifi-service** : ingestion batch et streaming depuis toutes les sources (CRM, ERP, Billing, CDR, OSS, tickets, fichiers externes).
2. **dbt-service** : transformation, normalisation, calcul KPI, préparation des tables analytiques.
3. **reconciliation-service (Zingg)** : résolution d’identité et consolidation via API Python Zingg.
4. **quality-control-service (Soda)** : détection d’anomalies et doublons.
5. **rca-service** : analyse des causes racines.
6. **api-dashboard-service** : REST API + dashboard pour visualisation, alertes et KPI.
7. **warehouse-service** : stockage historique et audit des données avec volumes persistants.

---

## 2️⃣ Structure complète des dossiers et fichiers à générer

```
saas-project/
│
├─ nifi-service/
│   ├─ Dockerfile
│   ├─ nifi-conf/ (flow.xml.gz)
│
├─ dbt-service/
│   ├─ Dockerfile
│   ├─ app/
│   │   ├─ main.py           # FastAPI endpoints
│   │   ├─ models.py         # ORM ou Pydantic
│   │   ├─ services.py       # Transformation, calcul KPI
│   │   └─ config.yaml
│   └─ requirements.txt
│
├─ reconciliation-service/
│   ├─ Dockerfile
│   ├─ app/
│   │   ├─ main.py
│   │   ├─ zingg_client.py   # logique Zingg
│   │   └─ config.yaml
│   └─ requirements.txt
│
├─ quality-control-service/
│   ├─ Dockerfile
│   ├─ app/
│   │   ├─ main.py
│   │   ├─ quality_checks.py # anomalies/doublons
│   │   └─ config.yaml
│   └─ requirements.txt
│
├─ rca-service/
│   ├─ Dockerfile
│   ├─ app/
│   │   ├─ main.py
│   │   ├─ analysis.py       # RCA
│   │   └─ config.yaml
│   └─ requirements.txt
│
├─ api-dashboard-service/
│   ├─ Dockerfile
│   ├─ app/
│   │   ├─ main.py           # FastAPI endpoints
│   │   ├─ endpoints.py
│   │   ├─ models.py
│   │   └─ config.yaml
│   └─ requirements.txt
│
├─ warehouse-service/
│   ├─ Dockerfile
│   ├─ init.sql              # initialisation PostgreSQL/Mongo
│   └─ requirements.txt
│
└─ docker-compose.yml        # orchestration complète
```

---

## 3️⃣ Consignes de génération pour Cursor

1. Générer **Dockerfile** pour chaque service, exposant les ports nécessaires et installant toutes les dépendances Python et NiFi.
2. Générer **requirements.txt** pour chaque service.
3. Générer **docker-compose.yml global**, orchestrant **tous les services** avec ports exposés et dépendances.
4. Chaque microservice doit être **indépendant et scalable**, avec **endpoints REST opérationnels**.
5. NiFi doit être configuré pour router les flux vers les microservices appropriés.
6. Warehouse-service doit être initialisé via `init.sql` et connecté à tous les microservices nécessitant accès aux données.
7. Fournir **README.md** détaillé :

   * Comment builder chaque conteneur
   * Comment lancer le projet complet avec Docker Compose
   * Comment tester endpoints REST et dashboard
   * Diagrammes UML/SysML/TOGAF en commentaires :

     * Diagramme de flux global
     * Diagramme de composants
     * Diagramme de séquence
     * Diagramme de déploiement Docker
8. Inclure **tests unitaires et d’intégration** pour chaque service (pytest ou unittest).
9. Générer **logique minimale opérationnelle** pour chaque microservice :

   * dbt-service → transformation de données
   * reconciliation-service → match avec Zingg API
   * quality-control-service → détection anomalies/doublons
   * rca-service → analyse causes racines
   * api-dashboard → REST API + visualisation
   * warehouse-service → CRUD historique
10. Prioriser **production-ready code, modularité, observabilité, maintenabilité et scalabilité**.


