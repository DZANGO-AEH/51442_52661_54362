from django import template
register = template.Library()


@register.filter
def ends_with(value, arg):
    return str(value).endswith(arg)


@register.filter
def starts_with(value, prefix):
    return str(value).startswith(str(prefix))