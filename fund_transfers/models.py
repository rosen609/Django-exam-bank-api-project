from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from django_iban.fields import IBANField

from registrations.models import Account, Currency
from .enums import TransferStatusEnum, PaymentSystemEnum


class FundTransfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    iban_beneficiary = IBANField()
    bic_beneficiary = models.CharField(max_length=11, blank=True)
    bank_beneficiary = models.CharField(max_length=200, blank=True)
    name_beneficiary = models.CharField(max_length=150, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0)])
    amount_bgn = models.FloatField(default=0, validators=[MinValueValidator(0)])
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)
    details = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[(s.name, s.value) for s in TransferStatusEnum], default='I')
    otp_generated = models.CharField(max_length=10, blank=True)
    otp_received = models.CharField(max_length=10, blank=True)
    user_approved = models.ForeignKey(User, related_name='ft_approval', on_delete=models.CASCADE, blank=True, null=True)
    reference_cbs = models.CharField(max_length=20, blank=True)
    payment_system = models.CharField(max_length=7, choices=[(p.name, p.value) for p in PaymentSystemEnum], default='B')
