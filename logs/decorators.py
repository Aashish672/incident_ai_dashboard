from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def admin_required(view_func):
    """
    Decorator to allow only logged-in users with role 'admin' to access a view.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has a profile and is an admin
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    return _wrapped_view
