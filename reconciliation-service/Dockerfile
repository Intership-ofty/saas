FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des requirements et installation des dépendances Python
COPY requirements.txt .
RUN pip install --timeout 300 --retries 5 -r requirements.txt

# Copie du code applicatif (cette étape ne sera reconstruite que si le code change)
COPY app/ .

# Exposition du port
EXPOSE 8002

# Démarrage de l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
