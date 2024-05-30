from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def creator_required(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if hasattr(request.user, 'is_content_creator') and request.user.is_content_creator:
            return view_func(request, *args, **kwargs)
        else:
            print("User is not a creator, redirecting to account home")
            messages.error(request, "You need to be a content creator to access this page.")
            return redirect('')
    return wrapper_func