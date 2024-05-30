import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_twitter_url(value):
    """
    Validates that the given value is a valid Twitter URL.

    Args:
        value (str): The URL to validate.

    Raises:
        ValidationError: If the URL is not a valid Twitter URL.
    """
    twitter_pattern = r"^https:\/\/(www\.)?(twitter\.com\/|x\.com\/)[a-zA-Z0-9_]{1,15}\/?$"
    if not re.match(twitter_pattern, value):
        raise ValidationError(
            _('Invalid Twitter URL.'),
            params={'value': value},
        )

def validate_instagram_url(value):
    """
    Validates that the given value is a valid Instagram URL.

    Args:
        value (str): The URL to validate.

    Raises:
        ValidationError: If the URL is not a valid Instagram URL.
    """
    instagram_pattern = r"^https:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9._]{1,30}\/?$"
    if not re.match(instagram_pattern, value):
        raise ValidationError(
            _('Invalid Instagram URL.'),
            params={'value': value},
        )
