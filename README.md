# Plateforme d'Analyse et de Prédiction des Anomalies RH

**Projet réalisé dans le cadre de mon stage en tant que Data Scientist au sein du département Data & IA d'Orange Maroc.**

## 1. Contexte et Objectif

Ce projet vise à développer une solution complète pour la valorisation des données de pointage des collaborateurs. L'objectif est de passer d'un simple suivi manuel à une plateforme intelligente capable de :
- **Ingérer et traiter** des volumes importants de données brutes.
- **Détecter automatiquement** les anomalies de présence (retards, absences, etc.).
- **Fournir des dashboards** analytiques pour les équipes RH et les managers.
- **Implémenter un modèle prédictif** pour anticiper les tendances futures et permettre une gestion proactive des ressources humaines.

![Aperçu du Dashboard RH](https://i.imgur.com/your-screenshot-link.png)
*(Pensez à remplacer ce lien par une capture d'écran de votre dashboard principal)*

---

## 2. Fonctionnalités Clés

-   **Pipeline ETL Asynchrone :** Import de fichiers CSV lourds en arrière-plan sans bloquer l'interface, grâce à une architecture robuste avec **Celery & Redis**.
-   **Dashboards Analytiques :** Visualisation des KPIs clés, répartition des anomalies par direction et département via des graphiques interactifs avec **Chart.js**.
-   **Analyse de Performance :** Suivi des tendances d'anomalies (hausse/baisse) sur des périodes définies.
-   **Modélisation Prédictive :** Utilisation de la bibliothèque **Prophet** pour prévoir le nombre futur d'anomalies à un niveau global, par direction ou par département.
-   **Espace Manager Sécurisé :** Portail dédié où chaque manager a une vue filtrée et sécurisée sur les performances et l'historique de sa propre équipe.
-   **Export de Rapports :** Génération de synthèses en **PDF** à la volée avec **WeasyPrint**.
-   **Déploiement Conteneurisé :** L'ensemble de l'application et de ses services (Django, MySQL, Redis, Celery) est conteneurisé avec **Docker** pour un déploiement et une portabilité simplifiés.

---

## 3. Stack Technologique

| Catégorie | Technologie | Rôle |
| :--- | :--- | :--- |
| **Backend** | Django, Django REST Framework | Framework web, gestion des modèles et de la logique métier. |
| **Frontend** | HTML, CSS, JavaScript, Bootstrap | Interface utilisateur et graphiques interactifs. |
| **Tâches Asynchrones**| Celery, Redis | Traitement en arrière-plan des imports ETL et de l'envoi d'e-mails. |
| **Base de Données** | MySQL | Stockage des données relationnelles. |
| **Analyse & Prédiction** | Pandas, Prophet | Manipulation des données, analyse de séries temporelles et prédiction. |
| **Déploiement** | Docker, Docker Compose | Conteneurisation et orchestration des services. |

---

## 4. Guide de Démarrage Rapide

### Prérequis
-   Docker
-   Docker Compose

### Instructions

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/VOTRE_NOM/VOTRE_DEPOT.git
    cd VOTRE_NOM_DE_DEPOT
    ```

2.  **Configurer l'environnement :**
    Créez un fichier nommé `.env` à la racine du projet et remplissez-le en utilisant ce modèle.
    ```env
    # Fichier .env
    SECRET_KEY=votre_cle_secrete_django
    DEBUG=1
    ALLOWED_HOSTS=127.0.0.1,localhost
    
    # Base de Données (pour Docker)
    DB_NAME=plateforme_rh
    DB_USER=rh_user
    DB_PASSWORD=your_strong_password
    DB_HOST=db
    DB_PORT=3306
    
    # Email (exemple avec Gmail)
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=votre_email@gmail.com
    EMAIL_HOST_PASSWORD=votre_mot_de_passe_application_gmail
    
    # Redis (pour Docker)
    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0
    ```

3.  **Lancer l'application avec Docker Compose :**
    Cette commande va construire les images et démarrer tous les conteneurs.
    ```bash
    docker-compose up --build
    ```

4.  **Accéder à l'application :**
    Ouvrez votre navigateur et allez sur `http://127.0.0.1:8000`.

5.  **(Première fois uniquement) Créer les comptes :**
    Ouvrez un **nouveau terminal** et lancez ces commandes :
    -   **Créer un superutilisateur (admin) :**
        ```bash
        docker-compose exec web python manage.py createsuperuser
        ```
    -   **Créer les comptes Managers :**
        ```bash
        docker-compose exec web python manage.py import_managers managers.csv
        ```

---

## 5. Auteur

**[Votre Nom Complet]** - Data Scientist (Stagiaire)
*   **Département :** Data & IA, Orange Maroc
*   **Email :**  saraelghayati726@gmail.com
*   **LinkedIn :** https://github.com/saragh66/forcasting_anomalies