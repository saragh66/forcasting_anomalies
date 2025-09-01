# ==============================================================================
# FICHIER : analytics/services.py (Version finale et complète)
# ==============================================================================
import pandas as pd
from django.db.models import Count
from core.models import Anomalie, Direction, Departement
from datetime import date, timedelta

# --- FONCTION POUR LE DASHBOARD SIMPLE (rh_dashboard) ---
# ==============================================================================
# FICHIER : analytics/services.py (Version finale, complète et cohérente)
# ==============================================================================
import pandas as pd
from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from core.models import Collaborateur, Anomalie, Direction, Departement

# --- SERVICE POUR LE DASHBOARD PRINCIPAL RH (rh_dashboard.html) ---

def generate_rh_dashboard_stats():
    """
    Calcule toutes les statistiques pour le dashboard RH principal.
    C'est la SEULE fonction à appeler pour cette page.
    """
    total_collaborateurs = Collaborateur.objects.count()
    total_anomalies = Anomalie.objects.count()

    # Agrégation par Direction
    stats_direction = list(Anomalie.objects
        .values('pointage__direction__nom')  # On groupe par le nom de la direction
        .annotate(total=Count('id'))         # On compte les anomalies
        .filter(total__gt=0)                 # On exclut les directions sans anomalies
        .order_by('-total')                  # On trie par le plus grand nombre
    )

    # Agrégation par Département (Top 5)
    stats_departement = list(Anomalie.objects
        .values('pointage__departement__nom') # On groupe par le nom du département
        .annotate(total=Count('id'))
        .filter(total__gt=0)
        .order_by('-total')[:5]               # On ne garde que les 5 premiers
    )
    
    return {
        "total_collaborateurs": total_collaborateurs,
        "total_anomalies": total_anomalies,
        "stats_par_direction": stats_direction,
        "stats_par_departement": stats_departement,
    }


# --- SERVICES POUR LE DASHBOARD DE PERFORMANCE (statistiques.html) ---

def generate_performance_dashboard_stats():
    """
    Calcule les KPIs et les tendances pour le dashboard de performance.
    Cette version est spécifiquement adaptée pour analyser les données de 2024.
    """
    # MODIFIÉ : On fixe une date de référence à la fin de votre jeu de données de test.
    today_reference = date(2024, 12, 31)

    # Période Actuelle : Décembre 2024 (du 2 au 31 Décembre)
    end_date_current = today_reference
    start_date_current = end_date_current - timedelta(days=29)
    
    # Période Précédente : Novembre 2024 (du 2 Novembre au 1er Décembre)
    end_date_previous = start_date_current - timedelta(days=1)
    start_date_previous = end_date_previous - timedelta(days=29)

    def get_timeseries_data(qs_base):
        # MODIFIÉ : On filtre sur `pointage__date` qui est la date de l'événement.
        timeseries = (qs_base
            .filter(pointage__date__range=[start_date_current, end_date_current])
            .values('pointage__date')
            .annotate(y=Count('id'))
            .order_by('pointage__date')
        )
        df = pd.DataFrame(list(timeseries))
        if not df.empty:
            df['pointage__date'] = pd.to_datetime(df['pointage__date'])
            df = df.set_index('pointage__date').rename(columns={'pointage__date': 'ds'})
            date_range = pd.date_range(start=start_date_current, end=end_date_current, freq='D')
            df = df.reindex(date_range, fill_value=0)
            return {'ds': df.index.strftime('%Y-%m-%d').tolist(), 'y': df['y'].tolist()}
        return {'ds': [], 'y': []}

    def calculate_kpis(qs_base):
        # MODIFIÉ : On filtre sur `pointage__date` pour des calculs précis.
        current_count = qs_base.filter(pointage__date__range=[start_date_current, end_date_current]).count()
        previous_count = qs_base.filter(pointage__date__range=[start_date_previous, end_date_previous]).count()
        
        if previous_count > 0:
            trend = round(((current_count - previous_count) / previous_count) * 100, 1)
        else:
            trend = 100.0 if current_count > 0 else 0.0

        direction = 'up' if trend > 5 else ('down' if trend < -5 else 'stable')
        
        return {
            'total_observed': current_count,
            'trend_percentage': trend,
            'trend_direction': direction
        }

    direction_stats = []
    for direction in Direction.objects.all().order_by('nom'):
        qs_base = Anomalie.objects.filter(pointage__direction=direction)
        # On ne calcule que s'il y a des anomalies dans les deux périodes concernées
        if qs_base.filter(pointage__date__range=[start_date_previous, end_date_current]).exists():
            direction_stats.append({
                'name': direction.nom,
                'kpis': calculate_kpis(qs_base),
                'timeseries': get_timeseries_data(qs_base)
            })

    departement_stats = []
    for departement in Departement.objects.all().order_by('nom'):
        qs_base = Anomalie.objects.filter(pointage__departement=departement)
        if qs_base.filter(pointage__date__range=[start_date_previous, end_date_current]).exists():
             departement_stats.append({
                'name': departement.nom,
                'kpis': calculate_kpis(qs_base),
                'timeseries': get_timeseries_data(qs_base)
            })

    return {
        'stats_by_direction': direction_stats,
        'stats_by_departement': departement_stats
    }

# --- SERVICES POUR L'ANALYSE PRÉDICTIVE ---
# Vos fonctions existantes (anomalies_timeseries, prophet_forecast, etc.) sont excellentes
# et peuvent rester ici pour être utilisées par la vue du dashboard prédictif.

# --- FONCTIONS POUR L'ANALYSE TEMPORELLE (analytics/dashboard) ---
def anomalies_timeseries(level="global", key_id=None, freq="W"):
    qs = Anomalie.objects.all()
    if level == "direction" and key_id: qs = qs.filter(pointage__direction_id=key_id)
    elif level == "departement" and key_id: qs = qs.filter(pointage__departement_id=key_id)
    
    df = pd.DataFrame(list(qs.values("pointage__date").annotate(n=Count("id")).order_by("pointage__date")))
    if df.empty: return pd.DataFrame(columns=["ds", "y"])
    
    df = df.rename(columns={"pointage__date": "ds", "n": "y"})
    df['ds'] = pd.to_datetime(df['ds'])
    series = df.set_index("ds")["y"].resample(freq).sum().fillna(0)
    return series.reset_index()

def prophet_forecast(ts_df, periods=12, freq="W"):
    if ts_df.empty or len(ts_df) < 2: return None, None
    try:
        from prophet import Prophet
        m = Prophet(weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=False)
        m.fit(ts_df)
        future = m.make_future_dataframe(periods=periods, freq=freq)
        fcst = m.predict(future)
        return m, fcst[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    except Exception: return None, None

import math # Assurez-vous d'importer math en haut du fichier

def calculate_kpis(ts_df, forecast_df):
    """Calcule des KPIs plus riches."""
    if ts_df.empty: return {}
    
    total_observed = int(ts_df['y'].sum())
    last_observed_value = ts_df['y'].iloc[-1] if not ts_df.empty else 0
    
    trend_direction = "stable"
    trend_percentage = 0
    next_period_forecast = 0.0 # On initialise en float

    if forecast_df is not None and not forecast_df.empty:
        first_pred = forecast_df['yhat'].iloc[0]
        
        # --- CORRECTION ICI ---
        # On arrondit à 1 décimale au lieu d'un entier
        next_period_forecast = round(first_pred, 1)

        # Si la prédiction est négative (ce qui peut arriver), on la met à 0
        if next_period_forecast < 0:
            next_period_forecast = 0.0

        last_pred = forecast_df['yhat'].iloc[-1]
        if last_observed_value > 0:
            trend_percentage = round(((first_pred - last_observed_value) / last_observed_value) * 100, 1)
        
        if trend_percentage > 10: trend_direction = "up"
        elif trend_percentage < -10: trend_direction = "down"
            
    return { 
        "total_observed": total_observed,
        "last_value": int(last_observed_value),
        "next_period_forecast": next_period_forecast, # La valeur sera maintenant un float
        "trend_direction": trend_direction,
        "trend_percentage": trend_percentage,
    }
def run_heuristic_forecast(ts_df, periods=12, freq="W"):
    if len(ts_df) < 4: return None, "Données insuffisantes", {} # Augmenté le seuil
    _, prophet_fcst = prophet_forecast(ts_df, periods=periods, freq=freq)
    if prophet_fcst is not None:
        return prophet_fcst, "Prophet", calculate_kpis(ts_df, prophet_fcst)
    return None, "Échec du modèle", calculate_kpis(ts_df, None)

# --- FONCTION POUR LE DASHBOARD DE PERFORMANCE (statistiques.html) ---
def generate_dashboard_stats():
    """Calcule les KPIs et les tendances pour chaque direction et département."""
    stats_by_direction, stats_by_departement = [], []
    
    for direction in Direction.objects.all():
        ts_df = anomalies_timeseries(level="direction", key_id=direction.id)
        if not ts_df.empty:
            _, model_used, kpis = run_heuristic_forecast(ts_df, periods=4) # Prévision sur 4 semaines
            stats_by_direction.append({
                "id": direction.id, "name": direction.nom, "kpis": kpis,
                "timeseries": ts_df.to_dict(orient='list')
            })
            
    for dept in Departement.objects.all():
        ts_df = anomalies_timeseries(level="departement", key_id=dept.id)
        if not ts_df.empty:
            _, model_used, kpis = run_heuristic_forecast(ts_df, periods=4)
            stats_by_departement.append({
                "id": dept.id, "name": dept.nom, "kpis": kpis,
                "timeseries": ts_df.to_dict(orient='list')
            })
            
    return {
        "by_direction": sorted(stats_by_direction, key=lambda x: x['kpis'].get('total_observed', 0), reverse=True),
        "by_departement": sorted(stats_by_departement, key=lambda x: x['kpis'].get('total_observed', 0), reverse=True)
    }