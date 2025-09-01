# ==============================================================================
# FICHIER : core/utils/anomaly.py
# (Version finale avec la logique métier correcte et la nouvelle anomalie)
# ==============================================================================

from datetime import timedelta
import pandas as pd
from dateutil import parser 

# --- Fonctions Utilitaires (inchangées) ---

def str_to_timedelta(s):
    """
    Convertit une chaîne 'HH:MM' ou 'HH:MM:SS' en timedelta.
    Retourne un timedelta de zéro si la chaîne est invalide, vide ou nulle.
    """
    if not s or pd.isna(s):
        return timedelta(0)
    
    s_val = str(s).strip()
    if s_val.lower() in ["oui", "non"]:
        return timedelta(0)
        
    try:
        parts = s_val.split(':')
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        return timedelta(hours=h, minutes=m, seconds=s)
    except (ValueError, TypeError):
        return timedelta(0)

# --- Moteur de Détection d'Anomalies (entièrement revu) ---

def detect_anomalies(pointage_obj, is_holiday, is_leave, is_telework):
    """
    Détecte les anomalies réelles pour un objet Pointage en se basant sur la logique métier.
    Retourne une liste de tuples : (TYPE_ANOMALIE, "Message de détail").
    """
    anomalies = []
    
    # --- RÈGLE MÉTIER PRINCIPALE ---
    # On détermine si c'est un jour spécial où les anomalies de temps ne s'appliquent pas.
    is_special_day = is_leave() or is_holiday() or is_telework()

    # Si c'est un jour de congé, férié ou de télétravail...
    if is_special_day:
        # ...la seule anomalie possible est un problème technique de badgeage si la personne
        # a badgé quand même.
        if pointage_obj.badgeage_impair:
            anomalies.append(("BADGEAGE_IMPAIR", "Badgeage impair détecté."))
    
    # --- Si c'est un jour de travail normal ---
    else:
        # 1. Entrée Tardive
        if pointage_obj.entree_tardive and pointage_obj.entree_tardive > timedelta(0):
            anomalies.append(("ENTREE_TARDIVE", f"Entrée tardive de {pointage_obj.entree_tardive}."))

        # 2. Sortie Anticipée
        if pointage_obj.sortie_anticipee and pointage_obj.sortie_anticipee > timedelta(0):
            anomalies.append(("SORTIE_ANTICIPEE", f"Sortie anticipée de {pointage_obj.sortie_anticipee}."))

        # 3. Absence Non Justifiée
        # Votre modèle utilise un DecimalField, la comparaison est correcte.
        if pointage_obj.absence_non_justifiee > 0:
            anomalies.append(("ABSENCE_NON_JUSTIFIEE", f"Absence non justifiée de {pointage_obj.absence_non_justifiee}h."))
        
        # 4. Badgeage Impair (peut aussi arriver un jour normal)
        if pointage_obj.badgeage_impair:
            anomalies.append(("BADGEAGE_IMPAIR", "Badgeage impair détecté."))

        # 5. NOUVELLE ANOMALIE : Temps de présence inférieur au temps théorique
        # On ne vérifie que si les temps sont valides et qu'il n'y a pas déjà une absence.
        if (pointage_obj.temps_presence_reel is not None and 
            pointage_obj.temps_presence_theorique is not None and
            pointage_obj.temps_presence_theorique > timedelta(0) and
            pointage_obj.temps_presence_reel < pointage_obj.temps_presence_theorique and
            pointage_obj.absence_non_justifiee == 0):
            
            diff = pointage_obj.temps_presence_theorique - pointage_obj.temps_presence_reel
            # On ne lève cette anomalie que si la différence est significative (ex: > 1 minute)
            if diff > timedelta(minutes=1):
                anomalies.append(("PRESENCE_INSUFFISANTE", f"Temps de présence inférieur au théorique (manque {diff})."))
    
    # Le retour ne contient que les vraies anomalies.
    return anomalies