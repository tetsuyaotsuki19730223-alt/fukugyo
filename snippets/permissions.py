from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def premium_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if hasattr(request.user, "profile") and request.user.profile.is_premium:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Premium only")
    return _wrapped