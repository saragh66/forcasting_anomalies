# ==============================================================================
# FICHIER : accounts/views.py (VERSION FINALE CORRIGÉE)
# ==============================================================================

from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

# --------------------
# Login RH
# --------------------
class RHLoginView(LoginView):
    template_name = 'accounts/login_rh.html'

    def get_success_url(self):
        # Cette redirection est correcte
        return reverse('core:rh_dashboard')

# --------------------
# Login Manager
# --------------------
class ManagerLoginView(LoginView):
    template_name = 'accounts/manager_login.html' # Assurez-vous que ce chemin est bon
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        """
        Cette méthode est appelée APRÈS que les identifiants sont validés,
        mais AVANT la redirection.
        """
        # On exécute la logique de connexion de Django en premier
        super().form_valid(form)
        
        # On vérifie si l'utilisateur qui vient de se connecter est bien un manager
        if self.request.user.groups.filter(name='Manager').exists():
            # Si c'est un manager, on le laisse continuer vers son dashboard
            return redirect(self.get_success_url())
        else:
            # Si un utilisateur RH ou autre essaie de se connecter ici,
            # on le déconnecte par sécurité et on affiche une erreur.
            logout(self.request)
            messages.error(self.request, "Accès refusé. Cet espace est réservé aux managers.")
            return redirect('login_sup') # Remplacez par le nom de votre URL de login manager

    def get_success_url(self):
        # MODIFIÉ : On utilise le bon namespace 'managers' (au pluriel)
        return reverse('managers:dashboard')