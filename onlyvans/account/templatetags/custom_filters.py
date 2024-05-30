from django import template

register = template.Library()


@register.filter
def ends_with(value, arg):
    """
    Custom template filter that checks if a given value ends with the specified suffix.

    Args:
        value (str): The string to be checked.
        arg (str): The suffix to check for.

    Returns:
        bool: True if the value ends with the specified suffix, False otherwise.
    """
    return str(value).endswith(arg)


@register.filter
def starts_with(value, prefix):
    """
    Custom template filter that checks if a given value starts with the specified prefix.

    Args:
        value (str): The string to be checked.
        prefix (str): The prefix to check for.

    Returns:
        bool: True if the value starts with the specified prefix, False otherwise.
    """
    return str(value).startswith(str(prefix))
