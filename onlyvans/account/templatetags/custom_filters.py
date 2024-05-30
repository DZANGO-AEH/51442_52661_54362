from django import template
import random

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


@register.simple_tag
def random_greeting():
    """
    Custom template tag that returns a random greeting message. The greeting is selected from
    a list of common greetings in different languages.

    Returns:
        str: A random greeting message.
    """
    greetings = [
        "Hello", "Hola", "Bonjour", "Cześć", "Hallo", "Ciao", "Olá",
        "Привет", "こんにちは", "你好", "안녕하세요", "Merhaba", "Hej",
        "Hei", "Namaste", "Salam", "Sawubona", "Halo"
    ]
    return random.choice(greetings)
