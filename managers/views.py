from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Prefetch
from core.models import Anomalie, EmailHistory, Collaborateur, Pointage

# managers/views.py
# Fichier : managers/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from core.models import Collaborateur, Pointage, Departement

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    """
    Affiche un dashboard de performance pour l'équipe du manager connecté.
    (VERSION AVEC LOGIQUE DE CALCUL DÉFINITIVE)
    """
    # 1. Identifier les DÉPARTEMENTS gérés par le manager. C'est la source de vérité.
    departements_equipe = Departement.objects.filter(manager=request.user)

    # 2. Identifier les collaborateurs ACTUELLEMENT dans ces départements (pour le KPI total)
    collaborateurs_actuels_equipe = Collaborateur.objects.filter(departement__in=departements_equipe)
    total_collaborateurs = collaborateurs_actuels_equipe.count()

    # 3. Identifier les collaborateurs (actuels ou passés) ayant eu des anomalies DANS CES DÉPARTEMENTS
    collaborateurs_avec_anomalies = Collaborateur.objects.filter(
        pointage__anomalies__isnull=False,
        pointage__departement__in=departements_equipe
    ).distinct()
    
    nombre_avec_anomalies = collaborateurs_avec_anomalies.count()
    
    # 4. Calculer les KPIs logiques
    kpis = {
        'total_collaborateurs': total_collaborateurs,
        'avec_anomalies': nombre_avec_anomalies,
        'sans_anomalie': total_collaborateurs - nombre_avec_anomalies
    }
    
    # 5. Préparer les données pour le graphique et la liste
    # On annote les collaborateurs avec le compte de leurs anomalies UNIQUEMENT dans les départements du manager
    collaborateurs_par_anomalie = collaborateurs_avec_anomalies.annotate(
        total_anomalies=Count(
            'pointage__anomalies', 
            filter=Q(pointage__departement__in=departements_equipe)
        )
    ).order_by('-total_anomalies')

    # 6. Créer le contexte pour le template
    context = {
        'kpis': kpis,
        'collaborateurs_par_anomalie': collaborateurs_par_anomalie,
    }

    return render(request, "managers/dashboard.html", context)

# ... (le reste de vos vues ne change pas)

@login_required
@user_passes_test(is_manager)
def team_anomalies_list(request):
    """
    Affiche un dashboard interactif des anomalies pour l'équipe du manager.
    """
    # 1. Identifier les collaborateurs de l'équipe
    collaborateurs_equipe = Collaborateur.objects.filter(departement__manager=request.user)
    
    # 2. Récupérer la base de toutes les anomalies de l'équipe
    anomalies_equipe_qs = Anomalie.objects.filter(
        pointage__collaborateur__in=collaborateurs_equipe
    ).select_related('pointage__collaborateur')

    # 3. Appliquer les filtres de la page
    filters = request.GET
    selected_collab_id = filters.get('collaborateur')
    start_date = filters.get('start_date')

    if selected_collab_id:
        anomalies_equipe_qs = anomalies_equipe_qs.filter(pointage__collaborateur_id=selected_collab_id)
    if start_date:
        try:
            anomalies_equipe_qs = anomalies_equipe_qs.filter(pointage__date__gte=start_date)
        except: pass # Ignorer les dates invalides

    # 4. Calculer les KPIs basés sur la sélection filtrée
    total_anomalies_filtrees = anomalies_equipe_qs.count()
    
    type_plus_frequent_query = anomalies_equipe_qs.values('type').annotate(count=Count('type')).order_by('-count').first()
    type_plus_frequent = dict(Anomalie.TYPE_CHOICES).get(type_plus_frequent_query['type']) if type_plus_frequent_query else "N/A"

    # 5. Préparer les données pour le graphique (collaborateurs avec le plus d'anomalies)
    chart_data = list(anomalies_equipe_qs
        .values('pointage__collaborateur__prenom', 'pointage__collaborateur__nom')
        .annotate(count=Count('id'))
        .order_by('-count')[:10] # Top 10
    )
    
    context = {
        'anomalies': anomalies_equipe_qs.order_by('-pointage__date', 'pointage__collaborateur__nom'),
        'collaborateurs_equipe': collaborateurs_equipe, # Pour le menu déroulant du filtre
        'kpis': {
            'total': total_anomalies_filtrees,
            'type_frequent': type_plus_frequent
        },
        'chart_data': chart_data,
        'filters': filters,
    }
    return render(request, 'managers/team_anomalies.html', context)

@login_required
@user_passes_test(is_manager)
def team_email_history(request):
    """Affiche l'historique des emails envoyés à l'équipe du manager."""
    
    collaborateurs_equipe = Collaborateur.objects.filter(departement__manager=request.user)
    
    email_history = EmailHistory.objects.filter(
        collaborator__in=collaborateurs_equipe
    ).select_related(
        'collaborator', 'pointage'
    ).prefetch_related(
        'pointage__anomalies'
    ).order_by('-created_at')
    
    context = {'emails': email_history}
    return render(request, 'managers/team_email_history.html', context)