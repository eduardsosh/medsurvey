from functools import wraps
from django.shortcuts import redirect

def examiner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'examiner'):
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
