from rest_framework.validators import ValidationError

from .models import Customer


class CustomerTypeValidator(object):
    """
    Enforces consistent type for extended user and customer relation
    """
    def __init__(self, required_type):
        self._required_type = required_type

    def __call__(self, value):
        customer = Customer.objects.get(cbs_customer_number=value['customer']['cbs_customer_number'])
        if not customer:
            raise ValidationError("Incorrect CBS customer number.")
        if customer.type != self._required_type:
            raise ValidationError("Incorrect customer type.")
