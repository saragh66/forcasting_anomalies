# ==============================================================================
# FICHIER : core/utils/etl.py (Version finale avec la correction du lien Pointage)
# ==============================================================================
import pandas as pd
import traceback
import re
from datetime import timedelta
from dateutil import parser
from django.db import transaction

from ..models import (
    ImportBatch, Direction, Departement, Collaborateur, Pointage, Anomalie, TeleworkDay, HolidayMA
)
from .anomaly import detect_anomalies
from ..emails import send_anomaly_notification_and_log

def parse_duration(val):
    if pd.isna(val) or val == "": return None
    s_val = str(val).strip()
    if not s_val or s_val.lower() in ["oui", "non"]: return None
    try:
        parts = s_val.split(":")
        h, m, s = (list(map(int, parts)) + [0, 0])[:3]
        return timedelta(hours=h, minutes=m, seconds=s)
    except (ValueError, TypeError): return None

def parse_float_or_zero(val):
    if pd.isna(val) or val == "": return 0.0
    try: return float(str(val).replace(',', '.'))
    except (ValueError, TypeError): return 0.0

@transaction.atomic
def import_csv(file, user, send_emails_auto=False):
    df = pd.read_csv(file, sep=',')
    batch = ImportBatch.objects.create(uploaded_by=user, filename=getattr(file, "name", "upload.csv"))

    holidays_set = set(HolidayMA.objects.values_list('date', flat=True))
    pointages_avec_anomalies = []

    for index, row in df.iterrows():
        try:
            mat = str(row.get("MATRICULE", "")).strip()
            if not mat: continue

            date_j = pd.to_datetime(row["Date"], dayfirst=True).date()

            direction_nom = str(row.get("Direction", "N/A")).strip()
            departement_nom = str(row.get("Departement", "N/A")).strip()

            direction, _ = Direction.objects.get_or_create(
                nom__iexact=direction_nom, defaults={'nom': direction_nom}
            )
            departement, _ = Departement.objects.get_or_create(
                nom__iexact=departement_nom, direction=direction,
                defaults={'nom': departement_nom, 'direction': direction}
            )
            
            nom = str(row.get("NOM", "")).strip()
            prenom = str(row.get("PRENOM", "")).strip()
            email_factice = f"{re.sub(r'[^a-z]', '', prenom.lower())}.{re.sub(r'[^a-z]', '', nom.lower())}.factice@orange.com"

            collab, created = Collaborateur.objects.update_or_create(
                matricule=mat,
                defaults={"nom": nom, "prenom": prenom, "direction": direction, "departement": departement}
            )
            if not collab.email:
                collab.email = email_factice
                collab.save(update_fields=['email'])

            # === LA CORRECTION EST ICI ===
            p, _ = Pointage.objects.update_or_create(
                collaborateur=collab, date=date_j,
                defaults={
                    'batch': batch,
                    # LIGNES CRUCIALES AJOUTÉES POUR LIER LE POINTAGE À LA DIRECTION ET AU DÉPARTEMENT
                    'direction': direction,
                    'departement': departement,
                    # ---
                    'entree': parser.parse(str(row["Entrée"])).time() if pd.notna(row["Entrée"]) and str(row["Entrée"]).strip() else None,
                    'sortie': parser.parse(str(row["Sortie"])).time() if pd.notna(row["Sortie"]) and str(row["Sortie"]).strip() else None,
                    'temps_presence_reel': parse_duration(row.get("Temps de présence réel")),
                    'temps_presence_theorique': parse_duration(row.get("Temps de présence théorique")),
                    'entree_tardive': parse_duration(row.get("Entrée tardive")),
                    'sortie_anticipee': parse_duration(row.get("Sortie anticipée")),
                    'absence_justifiee_heures': parse_float_or_zero(row.get("Absence Justifiée (par heure)")),
                    'absence_non_justifiee': parse_float_or_zero(row.get("Absence non justifiée")),
                    'badgeage_impair': str(row.get("Anomalie(badgeage impair)", "")).strip().lower() == "oui",
                    'jour_tt_planifie': str(row.get("Jour TT Planifié", "")).strip().lower() == "oui",
                }
            )
            # === FIN DE LA CORRECTION ===
            
            p.anomalies.all().delete()
            
            holiday = date_j in holidays_set
            anomalies_detectees = detect_anomalies(p, lambda: holiday, lambda: p.absence_justifiee_heures > 0, lambda: p.jour_tt_planifie)
            
            if anomalies_detectees:
                for type_code, detail_text in anomalies_detectees:
                    Anomalie.objects.create(pointage=p, type=type_code, detail=detail_text, is_holiday=holiday)
                pointages_avec_anomalies.append(p)

            if p.jour_tt_planifie:
                TeleworkDay.objects.get_or_create(collaborateur=collab, date=date_j)

        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Erreur à la ligne {index + 2} (Matricule: {mat}). L'import a été annulé.")
            
    if send_emails_auto:
        for pointage in pointages_avec_anomalies:
            send_anomaly_notification_and_log(pointage)

    return batch