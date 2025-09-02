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
         return reverse('core:upload_csv')

# --------------------
# Login Manager
# --------------------
class ManagerLoginView(LoginView):
    template_name = 'accounts/manager_login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        super().form_valid(form)
        
        if self.request.user.groups.filter(name='Manager').exists():
            return redirect(self.get_success_url())
        else:
            logout(self.request)
            messages.error(self.request, "Accès refusé. Cet espace est réservé aux managers.")
            # CORRECTION APPLIQUÉE ICI :
            return redirect('accounts:login_sup')

    def get_success_url(self):
        # Cette ligne est correcte, en supposant que vous avez une app 'managers' avec une url 'dashboard'
        return reverse('managers:dashboard')