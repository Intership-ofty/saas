FROM apache/nifi:1.25.0

# Installation des outils nécessaires
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Configuration NiFi
COPY nifi-conf/flow.xml.gz /opt/nifi/nifi-current/conf/
COPY nifi-conf/nifi.properties /opt/nifi/nifi-current/conf/

# Configuration des permissions
RUN chown -R nifi:nifi /opt/nifi/nifi-current/conf/

# Exposition des ports
EXPOSE 8080 8443 10000 8000

# Retour à l'utilisateur nifi
USER nifi

# Démarrage de NiFi
CMD ["/opt/nifi/nifi-current/bin/nifi.sh", "run"]
