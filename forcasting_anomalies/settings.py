import os
from pathlib import Path

from pathlib import Path
from decouple import config

# Charger le fichier .env

# ==========================
# Répertoires de base
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# Sécurité
# ==========================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-secret-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# ==========================
# Applications installées
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django_q',

    # Mes apps
    'accounts',
    'core',
    'analytics',
    'managers',
]

# ==========================
# Middleware
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==========================
# URLs et templates
# ==========================
ROOT_URLCONF = 'forcasting_anomalies.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # dossier global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'forcasting_anomalies.wsgi.application'
ASGI_APPLICATION = 'forcasting_anomalies.asgi.application'

# ==========================
# Auth & Custom User
# ==========================
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = 'upload_csv'
LOGOUT_REDIRECT_URL = "landing_page"


# ==========================
# Base de données MySQL
# ==========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'forecast_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# ==========================
# Validation mots de passe
# ==========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================
# Internationalisation
# ==========================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==========================
# Static & Media
# ==========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# ==========================
# Auto Field
# ==========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================
# Email SMTP
# ==========================

#==========================
#Email SMTP
#==========================
# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com" # Directly set
EMAIL_PORT = 587             # Directly set
EMAIL_HOST_USER = "saraelghayati726@gmail.com" # Directly set
EMAIL_HOST_PASSWORD = "mafb mvki floj zsyz"   # Directly set your App Password
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "saraelghayati726@gmail.com" # Directly set
# ==========================
# Celery / Redis
# ==========================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
# Ajoutez ce bloc à la fin de votre fichier settings.py
#Q_CLUSTER = {
    #'name': 'orange_rh_cluster',
    #'workers': 4,  # Nombre de workers, 4 est un bon début
    #'timeout': 90, # Temps max pour une tâche
    #'retry': 120,  # Réessayer après 2 minutes si ça échoue
    #'queue_limit': 50,
    #'bulk': 10,
    #'orm': 'default',
     #'sync': True, # Utilise la base de données Django par défaut comme file d'attente
#}
LOGOUT_REDIRECT_URL = 'core:landing_page'
LOGIN_REDIRECT_URL = 'core:redirect_after_login'
