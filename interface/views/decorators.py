from functools import wraps 

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import login

# From http://djangosnippets.org/snippets/2357/ 
def login_required(view_callable):
    def check_login(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_callable(request, *args, **kwargs)

        assert hasattr(request, 'session'), "Session middleware needed."
        login_kwargs = {
            'extra_context': {
                REDIRECT_FIELD_NAME: request.get_full_path(),
            },
        }
        return login(request, **login_kwargs)
    return wraps(view_callable)(check_login)
