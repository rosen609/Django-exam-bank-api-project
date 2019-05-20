from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django_iban.fields import IBANField
from registrations.models import Account, Currency
from .enums import TransferStatusEnum


class FundTransfers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    iban_beneficiary = IBANField()
    bic_beneficiary = models.CharField(max_length=11)
    bank_beneficiary = models.CharField(max_length=200, blank=True)
    name_beneficiary = models.CharField(max_length=150, blank=True)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)
    details = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[(s.name, s.value) for s in TransferStatusEnum])
    otp_generated = models.CharField(max_length=10, blank=True)
    otp_received = models.CharField(max_length=10, blank=True)
    user_approver = models.ForeignKey(User, related_name='user_approver', on_delete=models.CASCADE, blank=True, null=True)
    reference_cbs = models.CharField(max_length=20, blank=True)
