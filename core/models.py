# ==============================================================================
# FICHIER : core/models.py (Version finale et corrigée)
# ==============================================================================
from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

# ─────────────────────────────────────────────
# Référentiels
# ─────────────────────────────────────────────
class Direction(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    class Meta:
        ordering = ["nom"]
    def __str__(self):
        return self.nom

# ...
class Departement(models.Model):
    nom = models.CharField(max_length=120)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    
    # --- CE CHAMP DOIT ABSOLUMENT ÊTRE LÀ ---
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departements_managed",
    )

    class Meta:
        unique_together = ("nom", "direction")
# ...
# ─────────────────────────────────────────────
# Collaborateurs & managers
# ─────────────────────────────────────────────
class Collaborateur(models.Model):
    matricule = models.CharField(max_length=32, unique=True)
    nom = models.CharField(max_length=120)
    prenom = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Ce champ est utile si un collaborateur a un N+1 différent du manager de département.
    # Pour l'instant, notre logique d'email se base sur Departement.manager.
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
    )
    class Meta:
        ordering = ["matricule"]
    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"

# ─────────────────────────────────────────────
# Import batch & jours spéciaux
# ─────────────────────────────────────────────
class ImportBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    filename = models.CharField(max_length=255)

class HolidayMA(models.Model):
    date = models.DateField(unique=True, db_index=True)
    label = models.CharField(max_length=120)

class Leave(models.Model):
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class TeleworkDay(models.Model):
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)

# ─────────────────────────────────────────────
# Pointages & anomalies
# ─────────────────────────────────────────────
class Pointage(models.Model):
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    entree = models.TimeField(null=True, blank=True)
    sortie = models.TimeField(null=True, blank=True)
    temps_presence_reel = models.DurationField(null=True, blank=True)
    temps_presence_theorique = models.DurationField(null=True, blank=True)
    entree_tardive = models.DurationField(null=True, blank=True)
    sortie_anticipee = models.DurationField(null=True, blank=True)
    absence_justifiee_heures = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    absence_non_justifiee = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    badgeage_impair = models.BooleanField(default=False)
    jour_tt_planifie = models.BooleanField(default=False)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="pointages", null=True, blank=True)
    
    class Meta:
        # Contrainte plus robuste : un seul pointage par collaborateur par jour.
        unique_together = ("collaborateur", "date")
        ordering = ["-date", "collaborateur__matricule"]

class Anomalie(models.Model):
    LATE = "ENTREE_TARDIVE"
    EARLY_LEAVE = "SORTIE_ANTICIPEE"
    ABS_UNJ = "ABSENCE_NON_JUSTIFIEE"
    BADGE = "BADGEAGE_IMPAIR"
    INSUF_PRES = "PRESENCE_INSUFFISANTE"
    TYPE_CHOICES = [
        (LATE, "Entrée tardive"), (EARLY_LEAVE, "Sortie anticipée"), (ABS_UNJ, "Absence non justifiée"),
        (BADGE, "Badgeage impair"), (INSUF_PRES, "Présence insuffisante"),
    ]
    pointage = models.ForeignKey(Pointage, on_delete=models.CASCADE, related_name="anomalies")
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    detail = models.TextField(blank=True, default="")
    is_holiday = models.BooleanField(default=False)
    is_leave = models.BooleanField(default=False)
    is_telework = models.BooleanField(default=False)
    date_detection = models.DateTimeField(default=timezone.now, db_index=True)

# ─────────────────────────────────────────────
# Historique des emails
# ─────────────────────────────────────────────
class EmailHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    to_email = models.EmailField()
    cc_manager = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    pdf = models.FileField(upload_to="emails_pdfs/", null=True, blank=True)
    collaborator = models.ForeignKey(Collaborateur, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.ForeignKey(ImportBatch, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default="SENT")

    # AJOUTEZ CE CHAMP POUR LIER L'EMAIL AU POINTAGE SPÉCIFIQUE
    pointage = models.ForeignKey(
        Pointage, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="email_history"
    )