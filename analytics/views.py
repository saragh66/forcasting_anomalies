# ==============================================================================
# FICHIER : analytics/views.py (Version corrigée)
# ==============================================================================
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Direction, Departement, Collaborateur, Anomalie

# --- IMPORT CORRIGÉ ---
# On n'importe que les fonctions "chef d'orchestre"
from .services import anomalies_timeseries, run_heuristic_forecast

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Direction, Departement, Collaborateur, Anomalie

@login_required
def dashboard(request):
    """Affiche la page principale du dashboard d'analyse."""

    # La conversion des QuerySets en listes de dictionnaires est la solution.
    # On sélectionne uniquement les champs 'id' et 'nom' qui sont nécessaires
    # pour le JavaScript du dashboard. C'est plus performant.
    directions_list = list(Direction.objects.values('id', 'nom'))
    departements_list = list(Departement.objects.values('id', 'nom'))

    context = {
        # On passe les listes au lieu des QuerySets
        "directions": directions_list,
        "departements": departements_list,

        # Ces objets ne sont pas passés au tag json_script, donc ils peuvent rester tels quels.
        "collaborateurs": Collaborateur.objects.all(),
        "anomalie_types": Anomalie.TYPE_CHOICES,
    }
    return render(request, "analytics/dashboard.html", context)

@login_required
def api_timeseries_forecast(request):
    """API qui utilise le sélecteur heuristique pour les prévisions."""
    level = request.GET.get("level", "global")
    key_id = request.GET.get("key_id")
    freq = request.GET.get("freq", "W")
    periods = int(request.GET.get("periods", 12))
    
    ts_df = anomalies_timeseries(level, key_id, freq)
    forecast_df, model_used, kpis = run_heuristic_forecast(ts_df, periods=periods, freq=freq)
    
    return JsonResponse({
        "timeseries_data": ts_df.to_dict(orient="records"),
        "forecast": None if forecast_df is None else forecast_df.to_dict(orient="records"),
        "model_used": model_used,
        "kpis": kpis,
    })