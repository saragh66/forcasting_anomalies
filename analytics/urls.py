# ==============================================================================
# FICHIER : analytics/urls.py (Version Corrigée)
# ==============================================================================
from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    
    # --- CORRECTION ICI ---
    # On utilise le nom complet et correct de la fonction de la vue
    path("api/ts/", views.api_timeseries_forecast, name="api_ts"),
]