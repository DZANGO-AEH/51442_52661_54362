from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def creator_required(view_func):
    """
    Decorator to ensure the user is a content creator.

    This decorator checks if the logged-in user has the `is_content_creator` attribute set to `True`.
    If the user is a content creator, the view function is executed. Otherwise, the user is redirected to the home page
    with an error message.

    Args:
        view_func (function): The view function to be wrapped by this decorator.

    Returns:
        function: The wrapped view function that includes the content creator check.
    """

    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        """
        Wrapper function to perform the content creator check.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments passed to the view function.
            **kwargs: Additional keyword arguments passed to the view function.

        Returns:
            HttpResponse: The response from the view function if the user is a content creator.
            Otherwise, a redirect response to the home page.
        """
        if hasattr(request.user, 'is_content_creator') and request.user.is_content_creator:
            # User is a content creator, proceed to the view function
            return view_func(request, *args, **kwargs)
        else:
            # User is not a content creator, redirect to the home page with an error message
            messages.error(request, "You need to be a content creator to access this page.")
            return redirect('home')

    return wrapper_func
