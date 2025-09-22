#!/bin/bash

echo "🚀 Démarrage personnalisé de NiFi..."

# Variables
NIFI_HOME="/opt/nifi/nifi-current"
NIFI_LOGS="$NIFI_HOME/logs"

# Créer tous les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p "$NIFI_LOGS"
mkdir -p "$NIFI_HOME/run"
mkdir -p "$NIFI_HOME/database_repository"
mkdir -p "$NIFI_HOME/flowfile_repository"
mkdir -p "$NIFI_HOME/content_repository"
mkdir -p "$NIFI_HOME/provenance_repository"

# Créer TOUS les fichiers de log que NiFi pourrait chercher
echo "📝 Création des fichiers de log..."
touch "$NIFI_LOGS/nifi-app.log"
touch "$NIFI_LOGS/nifi-bootstrap.log"
touch "$NIFI_LOGS/nifi-user.log"

# Permissions complètes
chmod -R 755 "$NIFI_HOME"

# Configuration des propriétés si variables d'environnement présentes
if [ ! -z "$NIFI_WEB_HTTP_HOST" ]; then
    echo "⚙️  Configuration HTTP Host: $NIFI_WEB_HTTP_HOST"
    sed -i "s/^nifi.web.http.host=.*/nifi.web.http.host=$NIFI_WEB_HTTP_HOST/" "$NIFI_HOME/conf/nifi.properties"
fi

if [ ! -z "$NIFI_WEB_HTTP_PORT" ]; then
    echo "⚙️  Configuration HTTP Port: $NIFI_WEB_HTTP_PORT"
    sed -i "s/^nifi.web.http.port=.*/nifi.web.http.port=$NIFI_WEB_HTTP_PORT/" "$NIFI_HOME/conf/nifi.properties"
fi

if [ ! -z "$NIFI_SENSITIVE_PROPS_KEY" ]; then
    echo "⚙️  Configuration Sensitive Props Key"
    sed -i "s/^nifi.sensitive.props.key=.*/nifi.sensitive.props.key=$NIFI_SENSITIVE_PROPS_KEY/" "$NIFI_HOME/conf/nifi.properties"
fi

echo "🎯 Démarrage de NiFi..."

# Démarrer NiFi avec le script original mais en supprimant la partie tail problématique
cd "$NIFI_HOME"

# Modifier temporairement le script nifi.sh pour enlever le tail
cp bin/nifi.sh bin/nifi.sh.backup
sed -i '/tail.*nifi-app\.log/d' bin/nifi.sh

# Démarrer NiFi en mode run (pas de tail, juste le processus)
exec bin/nifi.sh run
