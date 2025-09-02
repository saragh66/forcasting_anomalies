# ==============================================================================
# Dockerfile (VERSION FINALE PROPRE ET SIMPLIFIÉE)
# ==============================================================================

# --- Étape 1: Image de base ---
FROM python:3.11-slim

# --- Étape 2: Variables d'environnement ---
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Étape 3: Créer et définir le répertoire de travail ---
WORKDIR /app

# --- Étape 4: Installer les dépendances système ---
# Requis pour la connexion à MySQL et la génération de PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    default-mysql-client \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgobject-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 5: Installer les dépendances Python ---
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 6: Copier le code de l'application ---
COPY . /app/

# --- Étape 7: Collecter les fichiers statiques ---
# Utilisation d'une fausse DB pour que la commande fonctionne sans se connecter
RUN IN_BUILD_MODE=True SECRET_KEY="build-secret-key" python manage.py collectstatic --noinput

# --- Étape 8: Exposer le port ---
EXPOSE 8000