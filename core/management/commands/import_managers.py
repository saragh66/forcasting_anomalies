# FICHIER : core/management/commands/import_managers.py (VERSION FINALE CORRIGÉE)
# ==============================================================================
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from core.models import Departement, Direction

User = get_user_model()

class Command(BaseCommand):
    help = 'Importe les managers depuis un CSV et les assigne aux départements, en créant les directions et départements si nécessaire.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Le chemin vers le fichier managers.csv')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write(self.style.SUCCESS('Groupe "Manager" créé.'))

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                direction_nom = row['direction_nom']
                departement_nom = row['departement_nom']
                manager_email = row['manager_email']

                try:
                    # ÉTAPE 1 : On crée ou on récupère la Direction. C'est la nouveauté.
                    direction, _ = Direction.objects.get_or_create(
                        nom__iexact=direction_nom, 
                        defaults={'nom': direction_nom}
                    )
                    
                    # ÉTAPE 2 : On crée ou on récupère le Département EN LE LIANT À SA DIRECTION.
                    departement, _ = Departement.objects.get_or_create(
                        nom__iexact=departement_nom, 
                        defaults={'nom': departement_nom, 'direction': direction} # <-- La correction est ici !
                    )

                    # ÉTAPE 3 : On crée ou on récupère l'utilisateur Manager.
                    manager_user, created = User.objects.get_or_create(
                        email=manager_email,
                        defaults={'username': manager_email}
                    )
                    
                    if created:
                        manager_user.set_unusable_password()
                        manager_user.save()
                        self.stdout.write(self.style.NOTICE(f"Utilisateur manager créé : {manager_email}"))

                    manager_user.groups.add(manager_group)
                    
                    # ÉTAPE 4 : On assigne le manager au département.
                    departement.manager = manager_user
                    departement.save()

                    self.stdout.write(self.style.SUCCESS(
                        f"'{manager_email}' assigné avec succès au département '{departement_nom}' (Direction: {direction_nom})"
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Erreur pour la ligne du département '{departement_nom}'. Détail : {e}"
                    ))
        
        self.stdout.write(self.style.SUCCESS('Importation des managers terminée.'))