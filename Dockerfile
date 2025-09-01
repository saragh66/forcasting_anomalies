# ==============================================================================
# Dockerfile pour l'application Django "Plateforme RH" (CORRIGÉ POUR WEASYPRINT)
# ==============================================================================

# --- Étape 1: Utiliser une image de base Python officielle ---
FROM python:3.11-slim

# --- Étape 2: Définir les variables d'environnement ---
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Étape 3: Créer et définir le répertoire de travail ---
WORKDIR /app

# --- Étape 4: Installer les dépendances système ---
# MODIFIÉ : Ajout des bibliothèques requises par WeasyPrint
# (libpango-1.0-0, libpangoft2-1.0-0, libgobject-2.0-0, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dépendances pour mysqlclient
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    # Dépendances pour WeasyPrint
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgobject-2.0-0 \
    # Nettoyage
    && rm -rf /var/lib/apt/lists/*

# --- Étape 5: Installer les dépendances Python ---
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 6: Copier le code de l'application ---
COPY . /app/

# Le port 8000 sera exposé
EXPOSE 8000