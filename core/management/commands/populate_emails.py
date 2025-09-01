# ==============================================================================
# FICHIER : core/management/commands/populate_emails.py (VERSION DÉFINITIVE)
# ==============================================================================
import re
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.functions import Trim  # <--- IMPORTEZ Trim
from core.models import Collaborateur

class Command(BaseCommand):
    help = "Génère des adresses email factices pour les collaborateurs qui n'en ont pas, ont un email vide ou contenant uniquement des espaces."

    def handle(self, *args, **kwargs):
        self.stdout.write("Début de la recherche des collaborateurs sans email, avec email vide ou contenant des espaces...")

        # 1. On annote chaque collaborateur avec une version "nettoyée" de son email
        #    La fonction Trim retire les espaces au début et à la fin.
        collaborateurs = Collaborateur.objects.annotate(
            email_trimmed=Trim('email')
        )

        # 2. On filtre sur ce champ nettoyé. On cherche ceux où l'email est NULL
        #    OU est devenu une chaîne vide après le nettoyage.
        collaborateurs_sans_email = collaborateurs.filter(
            Q(email_trimmed__isnull=True) | Q(email_trimmed='')
        )
        
        count = collaborateurs_sans_email.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("Tous les collaborateurs ont déjà une adresse email valide. Aucune action n'est requise."))
            return

        self.stdout.write(self.style.NOTICE(f"{count} collaborateur(s) trouvé(s) sans email valide. Génération en cours..."))

        collaborateurs_a_mettre_a_jour = []
        # On itère sur la liste filtrée pour ne modifier que les objets nécessaires
        for collaborateur in collaborateurs_sans_email:
            prenom_clean = re.sub(r'\s+', '-', collaborateur.prenom.lower().strip())
            nom_clean = re.sub(r'\s+', '-', collaborateur.nom.lower().strip())
            
            email_factice = f"{prenom_clean}.{nom_clean}.factice@orange.com"
            
            collaborateur.email = email_factice
            collaborateurs_a_mettre_a_jour.append(collaborateur)

        Collaborateur.objects.bulk_update(collaborateurs_a_mettre_a_jour, ['email'])

        self.stdout.write(self.style.SUCCESS(
            f"Opération terminée ! {count} adresse(s) email ont été créées avec succès."
        ))