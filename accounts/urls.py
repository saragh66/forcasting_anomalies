from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path
from .views import RHLoginView, ManagerLoginView

urlpatterns = [
    path('login_rh/', RHLoginView.as_view(), name='login_rh'),
    path('login_sup/', ManagerLoginView.as_view(), name='login_sup'),
       # MODIFIÉ : Ajoutez cette ligne pour la déconnexion
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='core:landing_page'), name='logout'),
    
]