# core/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Connecte le signal post_migrate pour créer les groupes et permissions
        post_migrate.connect(create_default_groups, sender=self)


def create_default_groups(sender, **kwargs):
    """
    Crée les groupes RH et Manager et leurs permissions après les migrations.
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from django.apps import apps

    try:
        # Récupérer le modèle Anomalie de façon sûre
        Anomalie = apps.get_model("core", "Anomalie")

        # --- Groupe RH ---
        rh_group, _ = Group.objects.get_or_create(name='RH')
        for perm in Permission.objects.all():
            rh_group.permissions.add(perm)

        # --- Groupe Manager ---
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        content_type = ContentType.objects.get_for_model(Anomalie)
        perms = Permission.objects.filter(content_type=content_type, codename__startswith="view_")
        for perm in perms:
            manager_group.permissions.add(perm)

    except Exception as e:
        # Affiche l’erreur mais ne bloque pas le démarrage
        print("Erreur dans create_default_groups():", e)
