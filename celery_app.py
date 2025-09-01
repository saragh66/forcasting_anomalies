import os
from celery import Celery

# Définir le module de settings par défaut pour le programme 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forcasting_anomalies.settings')

# Créer une instance de l'application Celery
app = Celery('forcasting_anomalies')

# Utiliser le namespace 'CELERY' signifie que tous les paramètres de configuration 
# de Celery dans settings.py doivent commencer par CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir et charger automatiquement les fichiers tasks.py de toutes les applications Django.
app.autodiscover_tasks()