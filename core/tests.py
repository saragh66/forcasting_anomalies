# ==============================================================================
# FICHIER : core/tests.py
# ==============================================================================

from unittest import mock
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Direction, Departement, Collaborateur, Pointage, Anomalie

User = get_user_model()

class CoreFunctionalityTestCase(TestCase):
    """
    Suite de tests pour les fonctionnalités de base de l'application 'core'.
    Cette classe utilise setUpTestData pour une configuration efficace.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Configuration initiale exécutée une seule fois pour toute la suite de tests.
        On crée les utilisateurs, groupes, et la structure de base de l'entreprise.
        """
        # Créer les groupes d'utilisateurs nécessaires
        cls.rh_group = Group.objects.create(name='RH')
        cls.manager_group = Group.objects.create(name='Manager')

        # Créer des utilisateurs pour chaque rôle
        cls.rh_user = User.objects.create_user(username='rh.test', password='password123')
        cls.rh_user.groups.add(cls.rh_group)

        cls.manager_user = User.objects.create_user(username='manager.test', password='password123')
        cls.manager_user.groups.add(cls.manager_group)

        cls.normal_user = User.objects.create_user(username='user.test', password='password123')
    
    def test_rh_dashboard_access(self):
        """
        Test d'intégration : Vérifie que seul un utilisateur RH peut accéder au dashboard RH.
        """
        print("Test : Accès au Dashboard RH")
        # Un utilisateur non connecté doit être redirigé vers la page de connexion
        response = self.client.get(reverse('core:rh_dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('core:rh_dashboard')}")

        # Un manager ne doit pas pouvoir y accéder (Erreur 403 Forbidden)
        self.client.login(username='manager.test', password='password123')
        response = self.client.get(reverse('core:rh_dashboard'))
        self.assertEqual(response.status_code, 403)

        # Un utilisateur RH doit pouvoir y accéder
        self.client.login(username='rh.test', password='password123')
        response = self.client.get(reverse('core:rh_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/rh_dashboard.html')

    @mock.patch('core.views.process_csv_import_task.delay')
    def test_upload_csv_triggers_celery_task(self, mock_celery_task):
        """
        Test d'intégration : Vérifie que l'upload d'un CSV lance bien une tâche Celery.
        Le `@mock.patch` remplace la vraie fonction `delay` par un "espion" qui enregistre les appels.
        """
        print("Test : Lancement de la tâche ETL via upload CSV")
        self.client.login(username='rh.test', password='password123')
        
        # Créer un faux fichier CSV en mémoire (contenu minimal pour passer la validation)
        csv_content = "MATRICULE,NOM,PRENOM,Date,Departement,Direction\nM123,Test,User,01/01/2024,Marketing,Corporate"
        csv_file = SimpleUploadedFile(
            "test_import.csv", 
            csv_content.encode('utf-8'), 
            content_type="text/csv"
        )
        
        # Simuler la requête POST sur l'URL d'upload
        response = self.client.post(reverse('core:upload_csv'), {'file': csv_file})

        # Vérifier que l'on est bien redirigé vers la liste des anomalies
        self.assertRedirects(response, reverse('core:liste_anomalies'))
        
        # Vérifier que la tâche Celery `.delay()` a bien été appelée une et une seule fois
        self.assertTrue(mock_celery_task.called)
        self.assertEqual(mock_celery_task.call_count, 1)

    @mock.patch('core.views.send_email_task.delay')
    def test_send_single_email_triggers_celery_task(self, mock_celery_task):
        """
        Test d'intégration : Vérifie que l'envoi d'un e-mail individuel lance une tâche Celery.
        """
        print("Test : Lancement de la tâche d'envoi d'e-mail")
        self.client.login(username='rh.test', password='password123')
        
        # Créer les données nécessaires pour le test
        direction = Direction.objects.create(nom='Test Direction')
        departement = Departement.objects.create(nom='Test Dept', direction=direction)
        collaborateur = Collaborateur.objects.create(matricule='M999', nom='Doe', prenom='John', departement=departement)
        pointage = Pointage.objects.create(collaborateur=collaborateur, date='2024-01-01')

        # Appeler l'URL d'envoi d'e-mail
        self.client.get(reverse('core:send_single_email', args=[pointage.id]))
        
        # Vérifier que la tâche Celery `.delay()` a bien été appelée
        self.assertTrue(mock_celery_task.called)
        self.assertEqual(mock_celery_task.call_count, 1)
        # Vérifier que la tâche a été appelée avec le bon ID de pointage
        mock_celery_task.assert_called_with(pointage.id)
