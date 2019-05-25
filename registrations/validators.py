from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneNumberE164Validator(validators.RegexValidator):
    """
    Validates E.164 international phone number format
    required for sending SMS
    """
    regex = r'^\+359\d{9}$'
    message = _(
        'Enter a valid Bulgarian mobile phone number. This value should start with +359 '
        'followed by 9 digits.'
    )


class PinValidator(validators.RegexValidator):
    """
    Validates 4 digit PIN number
    required for Fund Transfers approval
    """
    regex = r'^\d{4}$'
    message = _(
        'Enter a valid 4-digit PIN.'
    )