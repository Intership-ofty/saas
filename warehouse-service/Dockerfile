FROM postgres:15-alpine

# Variables d'environnement pour PostgreSQL
ENV POSTGRES_DB=data_warehouse \
    POSTGRES_USER=warehouse_user \
    POSTGRES_PASSWORD=warehouse_password

# Installation des outils Python pour les scripts d'initialisation
RUN apk add --no-cache python3 py3-pip

# Création du répertoire pour les scripts d'initialisation
WORKDIR /docker-entrypoint-initdb.d

# Copie du script d'initialisation SQL
COPY init.sql .

# Exposition du port PostgreSQL
EXPOSE 5432

# Les données seront persistées via un volume Docker
VOLUME ["/var/lib/postgresql/data"]
