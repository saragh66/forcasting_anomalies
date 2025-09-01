from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Prefetch
from core.models import Anomalie, EmailHistory, Collaborateur, Pointage

def is_manager(user):
    """Vérifie si l'utilisateur est dans le groupe 'Manager'."""
    return user.groups.filter(name='Manager').exists()

# managers/views.py

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    """
    Affiche le dashboard pour le manager, avec les KPIs et la liste de son équipe.
    """
    # 1. Identifier les collaborateurs de l'équipe du manager connecté
    collaborateurs_equipe = Collaborateur.objects.filter(
        departement__manager=request.user
    )
    
    # 2. Compter les anomalies et préparer les données pour le tableau et le graphique
    collaborateurs_avec_anomalies = collaborateurs_equipe.annotate(
        total_anomalies=Count('pointage__anomalies')
    ).order_by('-total_anomalies')

    # 3. Calculer les KPIs
    total_collaborateurs = collaborateurs_equipe.count()
    collab_avec_anomalie = collaborateurs_equipe.filter(pointage__anomalies__isnull=False).distinct().count()
    collab_sans_anomalie = total_collaborateurs - collab_avec_anomalie
    
    # 4. MODIFIÉ : Convertir le QuerySet en une liste de dictionnaires pour le JSON
    # On sélectionne uniquement les champs dont le JavaScript a besoin.
    collaborateurs_pour_json = list(collaborateurs_avec_anomalies.values(
        'prenom', 'nom', 'total_anomalies'
    ))

    # 5. Préparer les données pour le template
    context = {
        'stats': {
            'total_collaborateurs': total_collaborateurs,
            'collab_avec_anomalie': collab_avec_anomalie,
            'collab_sans_anomalie': collab_sans_anomalie,
        },
        'collaborateurs_table': collaborateurs_avec_anomalies, # Pour la boucle du tableau HTML
        'collaborateurs_json': collaborateurs_pour_json,    # Pour le script json_script
    }
    return render(request, 'managers/dashboard.html', context)

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