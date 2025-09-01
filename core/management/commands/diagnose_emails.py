# ==============================================================================
# FICHIER : core/management/commands/diagnose_emails.py
# ==============================================================================
from django.core.management.base import BaseCommand
from core.models import Collaborateur, Anomalie

class Command(BaseCommand):
    """
    Commande de diagnostic pour trouver les collaborateurs qui posent problème.
    Ce script ne modifie AUCUNE donnée.
    
    Utilisation :
        python manage.py diagnose_emails
    """
    help = "Diagnostique les collaborateurs sans email valide selon la logique de l'application."

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Début du diagnostic des emails ---")
        
        tous_les_collaborateurs = Collaborateur.objects.all()
        collaborateurs_problematiques = []

        # 1. On imite exactement la condition de la fonction d'envoi d'email
        for c in tous_les_collaborateurs:
            if not c.email:
                collaborateurs_problematiques.append(c)

        if not collaborateurs_problematiques:
            self.stdout.write(self.style.SUCCESS("Diagnostic 1/2 : Aucun collaborateur problématique trouvé dans toute la base. Tous les emails semblent non-vides."))
        else:
            self.stdout.write(self.style.WARNING(f"Diagnostic 1/2 : {len(collaborateurs_problematiques)} collaborateur(s) problématique(s) trouvé(s) dans la base :"))
            for c in collaborateurs_problematiques:
                # repr() nous montrera des caractères cachés s'il y en a
                self.stdout.write(f"  - Matricule: {c.matricule}, Nom: {c.nom}, Email (valeur brute): {repr(c.email)}")

        self.stdout.write("\n--- Analyse des collaborateurs liés à des anomalies ---")

        # 2. On vérifie spécifiquement les collaborateurs qui ont des anomalies
        ids_collaborateurs_avec_anomalies = Anomalie.objects.select_related('pointage__collaborateur').values_list('pointage__collaborateur__id', flat=True).distinct()
        
        collaborateurs_anomalies_problematiques = Collaborateur.objects.filter(id__in=ids_collaborateurs_avec_anomalies)
        
        found_issue = False
        for c in collaborateurs_anomalies_problematiques:
            if not c.email:
                if not found_issue:
                    self.stdout.write(self.style.ERROR("Diagnostic 2/2 : Problème confirmé ! Collaborateurs liés à des anomalies SANS email valide :"))
                    found_issue = True
                self.stdout.write(f"  - Matricule: {c.matricule}, Nom: {c.nom}, Email (valeur brute): {repr(c.email)}")
        
        if not found_issue:
            self.stdout.write(self.style.SUCCESS("Diagnostic 2/2 : Tous les collaborateurs spécifiquement liés à des anomalies ont un email qui semble valide."))

        self.stdout.write("\n--- Fin du diagnostic ---")