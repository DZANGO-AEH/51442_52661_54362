from django.http import HttpResponse
from django.shortcuts import redirect

def creator_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_creator:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrapper_func