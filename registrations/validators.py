from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneNumberE164Validator(validators.RegexValidator):
    '''
    Validates E.164 international phone number format
    required for sending SMS
    '''
    regex = r'^\+?[1-9]\d{6,14}$'
    message = _(
        'Enter a valid phone number. This value may start with + followed by 7 to 15 numbers.'
    )
