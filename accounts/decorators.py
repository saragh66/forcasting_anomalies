from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def rh_required(view):
    @wraps(view)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_rh():
            raise PermissionDenied("Accès RH requis.")
        return view(request, *args, **kwargs)
    return _wrapped

def manager_required(view):
    @wraps(view)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_manager():
            raise PermissionDenied("Accès Manager requis.")
        return view(request, *args, **kwargs)
    return _wrapped
