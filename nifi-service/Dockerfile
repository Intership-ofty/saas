FROM apache/nifi:1.25.0
USER root
RUN mkdir -p /opt/nifi/nifi-current/logs && touch /opt/nifi/nifi-current/logs/nifi-app.log
CMD ["/opt/nifi/nifi-current/bin/nifi.sh", "run"]

# FROM apache/nifi:1.25.0

# USER root

# Forcer root complètement
# ENV USER=root
# ENV NIFI_RUN_AS_USER=root

# Créer les répertoires nécessaires
# RUN mkdir -p /opt/nifi/nifi-current/logs && \
#    mkdir -p /opt/nifi/nifi-current/lib && \
#    mkdir -p /opt/nifi/nifi-current/work/nar && \
#    mkdir -p /opt/nifi/nifi-current/extensions && \
#    chmod -R 777 /opt/nifi/nifi-current

# Modifier directement le script nifi.sh pour enlever la vérification utilisateur et le tail
# RUN sed -i '/run\.as.*user.*does not exist/d' /opt/nifi/nifi-current/bin/nifi.sh && \
#     sed -i '/specified run\.as user.*does not exist/d' /opt/nifi/nifi-current/bin/nifi.sh && \
#     sed -i 's/tail -f.*nifi-app\.log.*/echo "NiFi démarré - logs disponibles dans \/opt\/nifi\/nifi-current\/logs\/"/' /opt/nifi/nifi-current/bin/nifi.sh

# Configuration des répertoires NAR
# ENV NIFI_NAR_LIBRARY_DIRECTORY=/opt/nifi/nifi-current/lib
# ENV NIFI_EXTENSIONS_DIRECTORY=/opt/nifi/nifi-current/extensions

# Exposition des ports
# EXPOSE 8080 8443 10000 8000

# Démarrage direct de NiFi (les fichiers de log sont maintenant présents sur l'hôte)
# CMD ["/opt/nifi/nifi-current/bin/nifi.sh", "run"]


# Configuration en tant que root
# USER root

# Installation des outils nécessaires
#RUN apt-get update && apt-get install -y curl && apt-get clean

# Variables pour forcer l'exécution en root
# ENV NIFI_RUN_AS_USER=""

# Création des répertoires et permissions
# RUN mkdir -p /opt/nifi/nifi-current/lib && \
#    mkdir -p /opt/nifi/nifi-current/work/nar && \
#    mkdir -p /opt/nifi/nifi-current/extensions && \
#    mkdir -p /opt/nifi/nifi-current/logs && \
#    chown -R nifi:nifi /opt/nifi/nifi-current


# Configuration du répertoire NAR
# ENV NIFI_NAR_LIBRARY_DIRECTORY=/opt/nifi/nifi-current/lib
# ENV NIFI_EXTENSIONS_DIRECTORY=/opt/nifi/nifi-current/extensions

# Exposition des ports
# EXPOSE 8080 8443 10000 8000

# Retour à l'utilisateur nifi
# USER nifi

# Point d'entrée par défaut - utilisation du script standard NiFi
# CMD ["/opt/nifi/nifi-current/bin/nifi.sh", "run"]
