from datetime import date
from core.models import HolidayMA

# PRATIQUE: la table HolidayMA est la source de vérité (modifiable via admin).
# Si vide, on peut mettre des fixes (Aïd variable -> à saisir dans l'admin).
DEFAULT_FIXES = [
    ("01-01","Nouvel an"), ("01-11","Manif. de l'indépendance"),
    ("05-01","Fête du Travail"), ("07-30","Fête du Trône"),
    ("08-14","Allégeance Oued Eddahab"), ("08-20","Révolution du Roi et du Peuple"),
    ("08-21","Fête de la Jeunesse"), ("11-06","Marche Verte"),
    ("11-18","Fête de l'Indépendance"),
]

def is_holiday(d: date) -> bool:
    # DB d'abord
    if HolidayMA.objects.filter(date=d).exists():
        return True
    # fallback: fixes
    mmdd = d.strftime("%m-%d")
    return any(mmdd == f for f,_ in DEFAULT_FIXES)
