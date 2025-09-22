# Migration Kafka vers le mode KRaft

## Vue d'ensemble

Ce document décrit la migration de Kafka du mode traditionnel (avec ZooKeeper) vers le mode KRaft (sans ZooKeeper) dans le SaaS Data Platform.

## Qu'est-ce que le mode KRaft ?

Le mode KRaft (Kafka Raft) est une nouvelle architecture de Kafka qui élimine la dépendance à ZooKeeper. Depuis Kafka 3.3 (août 2022), le mode KRaft est considéré comme prêt pour la production.

### Avantages du mode KRaft

- **Architecture simplifiée** : Plus besoin de ZooKeeper
- **Meilleure performance** : Gestion des métadonnées intégrée
- **Évolutivité améliorée** : Moins de composants à gérer
- **Démarrage plus rapide** : Moins de dépendances
- **Maintenance simplifiée** : Un seul service à gérer

## Changements apportés

### 1. Configuration Docker Compose

#### Avant (avec ZooKeeper)
```yaml
zookeeper:
  image: confluentinc/cp-zookeeper:6.2.0
  container_name: zookeeper
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
    ZOOKEEPER_TICK_TIME: 2000

kafka:
  image: confluentinc/cp-kafka:6.2.0
  environment:
    - KAFKA_BROKER_ID=1
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
  depends_on:
    - zookeeper
```

#### Après (mode KRaft)
```yaml
kafka:
  image: confluentinc/cp-kafka:7.4.0
  environment:
    # Configuration KRaft (sans ZooKeeper)
    - KAFKA_NODE_ID=1
    - KAFKA_PROCESS_ROLES=broker,controller
    - KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka:9093
    - KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER
    - KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT
    - KAFKA_LISTENERS=PLAINTEXT://kafka:9092,CONTROLLER://kafka:9093
    - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
    - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
```

### 2. Variables d'environnement

Les variables d'environnement Kafka restent les mêmes :
- `KAFKA_BOOTSTRAP_SERVERS=kafka:9092` (développement)
- `KAFKA_BOOTSTRAP_SERVERS=localhost:10092` (serveur)

### 3. Script d'initialisation

Un nouveau script `scripts/init-kafka-topics.sh` a été créé pour initialiser les topics Kafka en mode KRaft.

## Migration des données existantes

### 1. Sauvegarde des données

Avant la migration, sauvegardez vos données Kafka existantes :

```bash
# Sauvegarder les données Kafka
docker cp kafka:/var/lib/kafka/data ./backup/kafka-data-$(date +%Y%m%d)

# Sauvegarder la configuration ZooKeeper
docker cp zookeeper:/var/lib/zookeeper/data ./backup/zookeeper-data-$(date +%Y%m%d)
```

### 2. Arrêt des services

```bash
# Arrêter les services Kafka et ZooKeeper
docker-compose down kafka zookeeper
```

### 3. Nettoyage des volumes

```bash
# Supprimer les anciens volumes (ATTENTION: cela supprime les données)
docker volume rm saas_kafka-data saas_zookeeper-data
```

### 4. Démarrage en mode KRaft

```bash
# Démarrer Kafka en mode KRaft
docker-compose up -d kafka

# Vérifier que Kafka fonctionne
docker-compose logs kafka

# Initialiser les topics
./scripts/init-kafka-topics.sh
```

## Vérification de la migration

### 1. Vérifier le statut de Kafka

```bash
# Vérifier que Kafka fonctionne
docker-compose ps kafka

# Vérifier les logs
docker-compose logs kafka
```

### 2. Tester la connectivité

```bash
# Lister les topics
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Tester la production/consommation
docker exec kafka kafka-console-producer --bootstrap-server localhost:9092 --topic test-topic
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```

### 3. Vérifier les métriques

```bash
# Vérifier les métriques JMX
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

## Configuration des applications

Les applications qui utilisent Kafka n'ont pas besoin de modifications majeures. Seules les variables d'environnement de connexion peuvent nécessiter des ajustements :

### Variables d'environnement mises à jour

```bash
# Développement
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Serveur
KAFKA_BOOTSTRAP_SERVERS=localhost:10092
```

## Monitoring et observabilité

### 1. Métriques Prometheus

Les métriques Kafka restent les mêmes. Vérifiez que Prometheus collecte correctement les métriques :

```yaml
# Dans prometheus.yml
- job_name: 'kafka'
  static_configs:
    - targets: ['kafka:9092']
```

### 2. Dashboards Grafana

Les dashboards Grafana existants continuent de fonctionner avec le mode KRaft.

## Dépannage

### Problèmes courants

1. **Kafka ne démarre pas**
   - Vérifiez les logs : `docker-compose logs kafka`
   - Vérifiez la configuration des listeners
   - Vérifiez que les ports ne sont pas utilisés

2. **Erreurs de connexion**
   - Vérifiez que `KAFKA_BOOTSTRAP_SERVERS` est correct
   - Vérifiez la configuration des listeners
   - Vérifiez la connectivité réseau

3. **Topics non créés**
   - Exécutez le script d'initialisation : `./scripts/init-kafka-topics.sh`
   - Vérifiez les permissions sur les volumes

### Logs utiles

```bash
# Logs Kafka
docker-compose logs -f kafka

# Logs détaillés
docker exec kafka cat /var/log/kafka/server.log
```

## Rollback

En cas de problème, vous pouvez revenir au mode ZooKeeper :

1. Arrêter Kafka KRaft
2. Restaurer la configuration ZooKeeper
3. Restaurer les données sauvegardées
4. Redémarrer les services

## Support et documentation

- [Documentation officielle Kafka KRaft](https://kafka.apache.org/documentation/#kraft)
- [Guide de migration Confluent](https://docs.confluent.io/platform/current/kafka/deployment.html#kraft)
- [Configuration KRaft](https://kafka.apache.org/documentation/#kraftconfig)

## Conclusion

La migration vers le mode KRaft simplifie l'architecture du SaaS Data Platform en éliminant la dépendance à ZooKeeper. Cette migration améliore les performances et facilite la maintenance du système.
