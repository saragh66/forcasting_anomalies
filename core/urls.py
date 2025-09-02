# ==============================================================================
# FICHIER : core/urls.py
# ==============================================================================
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'core'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.rh_dashboard, name='rh_dashboard'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('anomalies/', views.liste_anomalies, name='liste_anomalies'),
    path('anomalies/export-pdf/', views.export_anomalies_pdf, name='export_anomalies_pdf'),
    path('pointage/<int:pointage_id>/apercu-email/', views.apercu_email, name='apercu_email'),
    path('pointage/<int:pointage_id>/send-email/', views.send_single_email, name='send_single_email'),
    path('historique/', views.historique_emails, name='historique_emails'),
    path('historique/export-pdf/', views.export_email_pdf, name='export_email_pdf'),
    path('statistiques/', views.statistiques_view, name='statistiques_view'),
    path('anomalies/send-pending/', views.send_pending_emails, name='send_pending_emails'),
        # URL de Déconnexion (la ligne la plus importante)
    # Elle utilise la vue intégrée de Django et redirige vers la page d'accueil après la déconnexion
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)