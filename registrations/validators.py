from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneNumberE164Validator(validators.RegexValidator):
    regex = r'^\+\d{7,17}$'
    message = _(
        'Enter a valid phone number. This value may start with + followed by 7 to 17 numbers.'
    )
    flags = 0
