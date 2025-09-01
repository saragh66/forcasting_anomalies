# ==============================================================================
# FICHIER : core/emails.py (VERSION FINALE CORRIGÉE)
# ==============================================================================
import logging
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Pointage, EmailHistory, Collaborateur

logger = logging.getLogger(__name__)

def send_anomaly_notification_and_log(pointage: Pointage) -> bool:
    """
    Construit et envoie un email d'anomalie, et le journalise.
    Vérifie d'abord si un email a déjà été envoyé pour ce pointage pour éviter les doublons.
    """
    
    # MODIFIÉ : Vérification anti-doublon robuste basée sur le lien direct au pointage.
    # Si un email avec le statut "SENT" existe déjà pour ce pointage, on arrête tout.
    if EmailHistory.objects.filter(pointage=pointage, status="SENT").exists():
        logger.warning(f"Envoi annulé : un email a déjà été envoyé pour le pointage ID {pointage.id}.")
        return False # Indique que l'envoi n'a pas eu lieu car déjà fait.

    collaborateur: Collaborateur = pointage.collaborateur
    
    # --- 1. Vérification des prérequis (INCHANGÉ) ---
    if not collaborateur.email:
        logger.warning(f"Envoi annulé : pas d'email pour le collaborateur {collaborateur.matricule}.")
        return False

    # --- 2. Récupération des informations du Manager (INCHANGÉ) ---
    manager_email = None
    manager_user = None
    try:
        if collaborateur.departement and collaborateur.departement.manager:
            manager_user = collaborateur.departement.manager
            if manager_user.email:
                manager_email = manager_user.email
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du manager pour {collaborateur.matricule}: {e}")

    # --- 3. Construction du contenu de l'email (INCHANGÉ) ---
    subject = f"Anomalies de pointage - {pointage.date.strftime('%d/%m/%Y')}"
    context = {
        'collaborateur': collaborateur,
        'pointage': pointage,
        'anomalies': pointage.anomalies.all(),
    }
    html_body = render_to_string('emails/notification_anomalie.html', context)
    
    # --- 4. Configuration des destinataires (INCHANGÉ) ---
    to_list = [collaborateur.email]
    cc_list = []
    if manager_email:
        cc_list.append(manager_email)

    try:
        # --- 5. Envoi de l'email (INCHANGÉ) ---
        email = EmailMessage(subject=subject, body=html_body, from_email=settings.DEFAULT_FROM_EMAIL, to=to_list, cc=cc_list)
        email.content_subtype = "html"
        email.send()

        # --- 6. Journalisation de l'envoi réussi (MODIFIÉ) ---
        EmailHistory.objects.create(
            collaborator=collaborateur,
            manager=manager_user,
            to_email=collaborateur.email,
            cc_manager=manager_email,
            subject=subject,
            body=html_body,
            status="SENT",
            pointage=pointage  # <-- Ligne cruciale pour lier l'historique au pointage
        )
        logger.info(f"Email envoyé à {collaborateur.email} (CC: {manager_email or 'aucun'}).")
        return True

    except Exception as e:
        logger.critical(f"Échec de l'envoi d'email pour {collaborateur.matricule}: {e}")
        
        # --- 7. Journalisation de l'échec (MODIFIÉ) ---
        EmailHistory.objects.create(
            collaborator=collaborateur,
            manager=manager_user,
            to_email=collaborateur.email,
            cc_manager=manager_email,
            subject=subject,
            body=f"Échec de l'envoi : {e}",
            status="FAILED",
            pointage=pointage # <-- On lie aussi le pointage en cas d'échec
        )
        return False