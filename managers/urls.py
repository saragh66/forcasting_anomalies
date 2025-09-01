# managers/urls.py
from django.urls import path
from . import views

app_name = 'managers'

urlpatterns = [
    # La page d'accueil du manager
    path('dashboard/', views.manager_dashboard, name='dashboard'),
    # La liste des anomalies de son équipe
    path('team/anomalies/', views.team_anomalies_list, name='team_anomalies'),
    # L'historique des emails de son équipe
    path('team/email-history/', views.team_email_history, name='team_email_history'),
]
