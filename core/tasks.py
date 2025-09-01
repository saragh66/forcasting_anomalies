import base64
from io import BytesIO
from celery import shared_task
from django.contrib.auth import get_user_model
from .utils.etl import import_csv
from .emails import send_anomaly_notification_and_log
from .models import Pointage

@shared_task(bind=True)
def process_csv_import_task(self, file_content_b64, user_id, filename):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        file_content = base64.b64decode(file_content_b64)
        file_in_memory = BytesIO(file_content)
        file_in_memory.name = filename
        print(f"Worker Celery: Démarrage de l'import pour '{filename}'...")
        import_csv(file_in_memory, user)
        print(f"Worker Celery: Importation de '{filename}' terminée.")
        return f"Importation réussie pour {filename}"
    except Exception as e:
        print(f"Worker Celery: Échec de l'importation. Erreur: {e}")
        self.update_state(state='FAILURE', meta={'exc': str(e)})
        raise e

@shared_task(bind=True)
def send_email_task(self, pointage_id):
    try:
        pointage = Pointage.objects.get(id=pointage_id)
        print(f"Worker Celery: Envoi de l'email pour pointage ID {pointage_id}...")
        send_anomaly_notification_and_log(pointage)
        print(f"Worker Celery: Email pour pointage ID {pointage_id} traité.")
        return f"Email traité pour {pointage_id}"
    except Exception as e:
        print(f"Worker Erreur lors de l'envoi pour pointage ID {pointage_id}: {e}")
        self.update_state(state='FAILURE', meta={'exc': str(e)})
        raise e