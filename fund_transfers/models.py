from django.db import models
from django.core.validators import MinValueValidator
from django_iban.fields import IBANField
from registrations.models import Account, Currency


class FundTransfers(models.Model):
    iban = models.ForeignKey(Account, on_delete=models.CASCADE)
    iban_receiver = IBANField()
    amount = models.FloatField(validators=[MinValueValidator(0)])
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)
