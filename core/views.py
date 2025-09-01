# ==============================================================================
# FICHIER : core/views.py (Version finale, complète et organisée)
# ==============================================================================
import traceback
import base64
from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from weasyprint import HTML

# --- Imports des modèles et formulaires ---
from .forms import CSVUploadForm
from .models import Collaborateur, Anomalie, EmailHistory, Pointage, Direction, Departement

# --- Imports des fonctions métier et de service ---
from .utils.etl import import_csv
from analytics.services import generate_rh_dashboard_stats, generate_performance_dashboard_stats
from .tasks import process_csv_import_task, send_email_task

# ----------------------------
# Constantes
# ----------------------------
PDF_EXPORT_LIMIT = 500  # Limite le nombre de lignes dans les exports PDF

# ----------------------------
# Fonctions de vérification des permissions
# ----------------------------
def is_rh(user):
    return user.groups.filter(name='RH').exists()

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

# ----------------------------
# Vues publiques
# ----------------------------
def landing_page(request):
    return render(request, 'landing.html')

# ==============================================================================
# VUES POUR LE GROUPE RH
# ==============================================================================

@login_required
@user_passes_test(is_rh)
def rh_dashboard(request):
    """Affiche le tableau de bord principal pour les RH."""
    context = generate_rh_dashboard_stats()
    return render(request, "core/rh_dashboard.html", context)

@login_required
@user_passes_test(is_rh)
def upload_csv(request):
    """Gère l'upload de CSV et lance la tâche de traitement en arrière-plan."""
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['file']
            try:
                file_content_b64 = base64.b64encode(csv_file.read()).decode('utf-8')
                process_csv_import_task.delay(
                    file_content_b64, request.user.id, csv_file.name
                )
                messages.success(request, "Fichier reçu. Le traitement a commencé en arrière-plan.")
                return redirect('core:liste_anomalies')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue avant le traitement : {e}")
    else:
        form = CSVUploadForm()
    return render(request, 'core/upload_csv.html', {'form': form})

@login_required
@user_passes_test(is_rh)
def liste_anomalies(request):
    """Affiche la liste des anomalies avec options de filtrage."""
    pointages_qs = Pointage.objects.filter(anomalies__isnull=False).distinct()
    filters = request.GET
    
    start_date = filters.get('start', '')
    end_date = filters.get('end', '')
    matricule = filters.get('matricule', '')
    anomaly_type = filters.get('type', '')
    direction_id = filters.get('direction', '')
    departement_id = filters.get('departement', '')
    query = filters.get('q', '')

    if start_date: pointages_qs = pointages_qs.filter(date__gte=start_date)
    if end_date: pointages_qs = pointages_qs.filter(date__lte=end_date)
    if matricule: pointages_qs = pointages_qs.filter(collaborateur__matricule__icontains=matricule)
    if anomaly_type: pointages_qs = pointages_qs.filter(anomalies__type=anomaly_type)
    if direction_id: pointages_qs = pointages_qs.filter(collaborateur__direction_id=direction_id)
    if departement_id: pointages_qs = pointages_qs.filter(collaborateur__departement_id=departement_id)
    if query:
        pointages_qs = pointages_qs.filter(
            Q(collaborateur__nom__icontains=query) | Q(collaborateur__prenom__icontains=query) | Q(anomalies__detail__icontains=query)
        ).distinct()

    context = {
        "pointages": pointages_qs.select_related("collaborateur__departement", "collaborateur__direction").prefetch_related('anomalies').order_by('-date'),
        "directions": Direction.objects.all(),
        "departements": Departement.objects.all(),
        "anomalie_types": Anomalie.TYPE_CHOICES,
        "filters": filters
    }
    return render(request, 'core/anomalies.html', context)

@login_required
@user_passes_test(is_rh)
def apercu_email(request, pointage_id):
    pointage = get_object_or_404(Pointage.objects.prefetch_related('anomalies'), id=pointage_id)
    return render(request, 'core/apercu_email.html', {'pointage': pointage})

@login_required
@user_passes_test(is_rh)
def send_single_email(request, pointage_id):
    """Met en file d'attente Celery l'envoi d'un email unique."""
    if not EmailHistory.objects.filter(pointage_id=pointage_id, status="SENT").exists():
        send_email_task.delay(pointage_id)
        messages.success(request, "L'envoi de l'email a été mis en file d'attente.")
    else:
        messages.warning(request, "Un email pour ce pointage a déjà été envoyé.")
    return redirect('core:liste_anomalies')

@login_required
@user_passes_test(is_rh)
@require_POST
def send_pending_emails(request):
    """Met en file d'attente Celery les emails pour tous les pointages filtrés."""
    pointages_qs = Pointage.objects.filter(anomalies__isnull=False).distinct()
    filters = request.GET
    
    start_date = filters.get('start', '')
    end_date = filters.get('end', '')
    matricule = filters.get('matricule', '')
    anomaly_type = filters.get('type', '')
    direction_id = filters.get('direction', '')
    departement_id = filters.get('departement', '')
    query = filters.get('q', '')

    if start_date: pointages_qs = pointages_qs.filter(date__gte=start_date)
    if end_date: pointages_qs = pointages_qs.filter(date__lte=end_date)
    if matricule: pointages_qs = pointages_qs.filter(collaborateur__matricule__icontains=matricule)
    if anomaly_type: pointages_qs = pointages_qs.filter(anomalies__type=anomaly_type)
    if direction_id: pointages_qs = pointages_qs.filter(collaborateur__direction_id=direction_id)
    if departement_id: pointages_qs = pointages_qs.filter(collaborateur__departement_id=departement_id)
    if query:
        pointages_qs = pointages_qs.filter(
            Q(collaborateur__nom__icontains=query) | Q(collaborateur__prenom__icontains=query) | Q(anomalies__detail__icontains=query)
        ).distinct()
    
    pointages_a_notifier = pointages_qs.exclude(email_history__status="SENT")
    task_count = 0
    for pointage in pointages_a_notifier:
        send_email_task.delay(pointage.id)
        task_count += 1
    
    if task_count > 0:
        messages.success(request, f"{task_count} e-mail(s) ont été mis en file d'attente pour envoi.")
    else:
        messages.info(request, "Aucun nouvel e-mail à envoyer pour cette sélection.")
        
    return redirect(f"{reverse('core:liste_anomalies')}?{request.GET.urlencode()}")

@login_required
@user_passes_test(is_rh)
def historique_emails(request):
    """Affiche l'historique des emails envoyés avec une logique de filtrage robuste."""
    
    historiques_list = EmailHistory.objects.select_related(
        'collaborator', 'manager'
    ).prefetch_related(
        'pointage__anomalies'
    ).order_by('-created_at')
    
    filters = request.GET
    
    # --- LOGIQUE DE FILTRAGE CLARIFIÉE ---
    mode = filters.get('mode', 'email')
    
    if mode == 'email':
        query = filters.get('q', '')
        if query:
            historiques_list = historiques_list.filter(Q(to_email__icontains=query) | Q(cc_manager__icontains=query))
            
    elif mode == 'matricule':
        query = filters.get('q', '')
        if query:
            historiques_list = historiques_list.filter(collaborator__matricule__icontains=query)
            
    elif mode == 'date':
        date_query_str = filters.get('date', '')
        if date_query_str:
            print(f"Filtrage par Date : '{date_query_str}'")
            try:
                # On crée un objet datetime au début de la journée
                start_of_day = datetime.strptime(date_query_str, '%Y-%m-%d')
                # On crée un objet datetime à la fin de la journée
                end_of_day = start_of_day + timedelta(days=1)
                
                # On filtre sur la plage de 24h
                historiques_list = historiques_list.filter(created_at__gte=start_of_day, created_at__lt=end_of_day)
            except (ValueError, TypeError):
                messages.warning(request, "Format de date invalide.")
                
    elif mode == 'week':
        week_query_str = filters.get('week', '')
        if week_query_str:
            try:
                year_str, week_str = week_query_str.split('-W')
                start_of_week = datetime.fromisocalendar(int(year_str), int(week_str), 1)
                end_of_week = start_of_week + timedelta(days=7)
                historiques_list = historiques_list.filter(created_at__gte=start_of_week, created_at__lt=end_of_week)
            except: pass

    paginator = Paginator(historiques_list, 10)
    page_obj = paginator.get_page(filters.get('page'))
    
    context = {
        'page_obj': page_obj, 'filters': filters,
        'modes': {'email': 'Email', 'matricule': 'Matricule', 'date': 'Date', 'week': 'Semaine'}
    }
    return render(request, "core/historique_emails.html", context)

@login_required
@user_passes_test(is_rh)
def statistiques_view(request):
    stats_data = generate_performance_dashboard_stats()
    context = {
        'stats_by_direction': stats_data.get('stats_by_direction', []),
        'stats_by_departement': stats_data.get('stats_by_departement', []),
    }
    return render(request, "core/statistiques.html", context)

# --- Vues d'Export ---
@login_required
@user_passes_test(is_rh)
def export_anomalies_pdf(request):
    """Génère un export PDF des anomalies filtrées."""
    pointages_qs = Pointage.objects.filter(anomalies__isnull=False).distinct()
    filters = request.GET
    
    start_date = filters.get('start', '')
    end_date = filters.get('end', '')
    matricule = filters.get('matricule', '')
    anomaly_type = filters.get('type', '')
    direction_id = filters.get('direction', '')
    departement_id = filters.get('departement', '')
    query = filters.get('q', '')

    if start_date: pointages_qs = pointages_qs.filter(date__gte=start_date)
    if end_date: pointages_qs = pointages_qs.filter(date__lte=end_date)
    if matricule: pointages_qs = pointages_qs.filter(collaborateur__matricule__icontains=matricule)
    if anomaly_type: pointages_qs = pointages_qs.filter(anomalies__type=anomaly_type)
    if direction_id: pointages_qs = pointages_qs.filter(collaborateur__direction_id=direction_id)
    if departement_id: pointages_qs = pointages_qs.filter(collaborateur__departement_id=departement_id)
    if query:
        pointages_qs = pointages_qs.filter(
            Q(collaborateur__nom__icontains=query) | Q(collaborateur__prenom__icontains=query) | Q(anomalies__detail__icontains=query)
        ).distinct()
    
    pointages_filtres = pointages_qs.order_by('-date')
    total_results = pointages_filtres.count()
    pointages_a_exporter = pointages_filtres[:PDF_EXPORT_LIMIT]
    
    context = {
        'pointages': pointages_a_exporter,
        'total_results': total_results,
        'limit': PDF_EXPORT_LIMIT,
        'is_limited': total_results > PDF_EXPORT_LIMIT
    }
    html_string = render_to_string('pdf/anomalies_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_anomalies.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response

@login_required
@user_passes_test(is_rh)
def export_email_pdf(request):
    """Génère un export PDF de l'historique des emails filtrés."""
    historiques_list = EmailHistory.objects.select_related('collaborator', 'manager').order_by('-created_at')
    filters = request.GET
    
    mode = filters.get('mode', 'email')
    query_val = filters.get('q', '')
    date_val = filters.get('date', '')
    week_val = filters.get('week', '')

    if mode == 'email' and query_val:
        historiques_list = historiques_list.filter(Q(to_email__icontains=query_val) | Q(cc_manager__icontains=query_val))
    elif mode == 'matricule' and query_val:
        historiques_list = historiques_list.filter(collaborator__matricule__icontains=query_val)
        
    elif mode == 'date' and date_val:
        try:
            date_query = datetime.strptime(date_val, '%Y-%m-%d').date()
            historiques_list = historiques_list.filter(created_at__date=date_query)
        except (ValueError, TypeError): pass
    elif mode == 'week' and week_val:
        try:
            year, week_num_str = week_val.split('-W')
            start_of_week = datetime.fromisocalendar(int(year), int(week_num_str), 1).date()
            end_of_week = start_of_week + timedelta(days=6)
            historiques_list = historiques_list.filter(created_at__date__range=[start_of_week, end_of_week])
        except (ValueError, TypeError): pass

    emails_filtres = historiques_list
    total_results = emails_filtres.count()
    emails_a_exporter = emails_filtres[:PDF_EXPORT_LIMIT]
    
    context = {
        'emails': emails_a_exporter,
        'total_results': total_results,
        'limit': PDF_EXPORT_LIMIT,
        'is_limited': total_results > PDF_EXPORT_LIMIT
    }
    html_string = render_to_string('pdf/email_history_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="historique_emails.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response

# ==============================================================================
# VUES POUR LE GROUPE MANAGER
# ==============================================================================

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    """Affiche un tableau de bord pour le manager avec les anomalies de son équipe."""
    collaborateurs_equipe_ids = Collaborateur.objects.filter(departement__manager=request.user).values_list('id', flat=True)
    anomalies = Anomalie.objects.filter(
        pointage__collaborateur_id__in=collaborateurs_equipe_ids
    ).select_related('pointage__collaborateur').order_by('-pointage__date')
    
    context = { "anomalies": anomalies }
    return render(request, "managers/manager_dashboard.html", context)