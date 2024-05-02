from django import template

register = template.Library()


@register.filter
def ends_with(value, arg):
    """Returns True if the value ends with the arg."""
    return str(value).endswith(arg)