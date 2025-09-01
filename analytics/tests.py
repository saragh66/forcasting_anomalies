# ==============================================================================
# FICHIER : analytics/tests.py
# ==============================================================================

from django.test import TestCase
from datetime import date
from core.models import Direction, Departement, Collaborateur, Pointage, Anomalie
from .services import generate_rh_dashboard_stats, generate_performance_dashboard_stats

class AnalyticsServicesTestCase(TestCase):
    """
    Suite de tests unitaires pour les fonctions de calcul dans analytics/services.py.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Créer un jeu de données de test riche pour valider les calculs.
        """
        # Structure de l'entreprise
        dir_corp = Direction.objects.create(nom='Corporate')
        dir_tech = Direction.objects.create(nom='Tech')
        
        dept_mkt = Departement.objects.create(nom='Marketing', direction=dir_corp)
        dept_fin = Departement.objects.create(nom='Finance', direction=dir_corp)
        dept_cld = Departement.objects.create(nom='Cloud', direction=dir_tech)
        
        # Collaborateurs
        collab_mkt = Collaborateur.objects.create(matricule='MKT01', nom='A', prenom='A', departement=dept_mkt, direction=dir_corp)
        collab_fin = Collaborateur.objects.create(matricule='FIN01', nom='B', prenom='B', departement=dept_fin, direction=dir_corp)
        collab_cld = Collaborateur.objects.create(matricule='CLD01', nom='C', prenom='C', departement=dept_cld, direction=dir_tech)
        
        # Pointages et Anomalies
        p1 = Pointage.objects.create(collaborateur=collab_mkt, date=date(2024, 12, 10), direction=dir_corp, departement=dept_mkt)
        p2 = Pointage.objects.create(collaborateur=collab_fin, date=date(2024, 12, 11), direction=dir_corp, departement=dept_fin)
        p3 = Pointage.objects.create(collaborateur=collab_cld, date=date(2024, 12, 12), direction=dir_tech, departement=dept_cld)
        p4 = Pointage.objects.create(collaborateur=collab_mkt, date=date(2024, 11, 15), direction=dir_corp, departement=dept_mkt) # Mois précédent

        # Période actuelle (Décembre) : 3 anomalies pour Corporate (2 Mkt, 1 Fin), 1 pour Tech
        Anomalie.objects.create(pointage=p1, type=Anomalie.LATE, detail="Test")
        Anomalie.objects.create(pointage=p1, type=Anomalie.INSUF_PRES, detail="Test")
        Anomalie.objects.create(pointage=p2, type=Anomalie.LATE, detail="Test")
        Anomalie.objects.create(pointage=p3, type=Anomalie.BADGE, detail="Test")
        # Période précédente (Novembre) : 1 anomalie pour Corporate
        Anomalie.objects.create(pointage=p4, type=Anomalie.LATE, detail="Test")

    def test_generate_rh_dashboard_stats(self):
        """Test unitaire : Vérifie les calculs globaux du dashboard RH."""
        print("Test : Calculs du Dashboard RH")
        stats = generate_rh_dashboard_stats()

        self.assertEqual(stats['total_collaborateurs'], 3)
        self.assertEqual(stats['total_anomalies'], 5) # 4 en Déc, 1 en Nov
        
        # Vérifier que les agrégations sont correctes et triées
        stats_dir = stats['stats_par_direction']
        self.assertEqual(len(stats_dir), 2)
        self.assertEqual(stats_dir[0]['pointage__direction__nom'], 'Corporate')
        self.assertEqual(stats_dir[0]['total'], 4) # 3 en Déc + 1 en Nov
        self.assertEqual(stats_dir[1]['pointage__direction__nom'], 'Tech')
        self.assertEqual(stats_dir[1]['total'], 1)

    def test_generate_performance_dashboard_stats(self):
        """Test unitaire : Vérifie les calculs de tendance."""
        print("Test : Calculs du Dashboard de Performance")
        stats = generate_performance_dashboard_stats()
        
        # On cherche la statistique pour la direction "Corporate"
        stat_corp = next((item for item in stats['stats_by_direction'] if item['name'] == 'Corporate'), None)
        
        self.assertIsNotNone(stat_corp)
        
        # Période actuelle (Décembre) : 3 anomalies
        self.assertEqual(stat_corp['kpis']['total_observed'], 3)
        
        # Période précédente (Novembre) : 1 anomalie
        # Tendance = ((3 - 1) / 1) * 100 = 200%
        self.assertEqual(stat_corp['kpis']['trend_percentage'], 200.0)
        self.assertEqual(stat_corp['kpis']['trend_direction'], 'up')