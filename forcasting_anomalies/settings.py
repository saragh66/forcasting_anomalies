import os
from pathlib import Path

# ==========================
# Répertoires de base
# ==========================
BASE_DIR = Path(__file__).resolve().parents[1]

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
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'DIRS': [BASE_DIR / "templates"],
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
# Auth & Custom User (SECTION CORRIGÉE ET FIABILISÉE)
# ==========================
AUTH_USER_MODEL = 'accounts.User'

# L'URL de connexion par défaut. Utilisée par @login_required.
# Doit correspondre au nom de votre URL de connexion dans accounts/urls.py
LOGIN_URL = "accounts:login_rh"

# La page par défaut où l'utilisateur est redirigé APRÈS une connexion réussie.
# Note : Cette valeur peut être surchargée par la méthode `get_success_url` dans vos vues de connexion.
LOGIN_REDIRECT_URL = 'core:rh_dashboard'

# La page où l'utilisateur est redirigé APRÈS une déconnexion.
LOGOUT_REDIRECT_URL = "core:landing_page"


# ==========================
# Base de données MySQL
# ==========================
IN_BUILD_MODE = os.getenv('IN_BUILD_MODE') == 'True'

if IN_BUILD_MODE:
    # Pendant le build, on utilise une fausse DB en mémoire pour que 'collectstatic' fonctionne
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    # Quand le conteneur tourne, on lit les variables du .env pour se connecter à la vraie DB MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==========================
# Auto Field
# ==========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================
# Email SMTP
# ==========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "saraelghayati726@gmail.com"
EMAIL_HOST_PASSWORD = "mafb mvki floj zsyz"
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "saraelghayati726@gmail.com"

# ==========================
# Celery / Redis
# ==========================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


