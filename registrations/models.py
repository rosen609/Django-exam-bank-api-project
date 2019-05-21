from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django_iban.fields import IBANField
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from .enums import *


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


class Customer(models.Model):
    '''
    Customer is the owner of accounts.
    All details come from Core Banking System, based on Customer number.
    No active role in Bank API
    '''
    cbs_customer_number = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=7, choices=[(t.name, t.value) for t in CustomerTypeEnum])

    def __str__(self):
        return f"{self.cbs_customer_number} {self.name}"


class Currency(models.Model):
    '''
    All details come from Core Banking System
    '''
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    rate_to_BGN = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.code} {self.name}"

    class Meta:
        #ordering = ['code']
        verbose_name_plural = 'Currencies'


class Person(models.Model):
    '''
    Personal user.
    Has all rights on his accounts and transfers.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_identity_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=200)
    mobile_phone = models.CharField(max_length=17, validators=[PhoneNumberE164Validator()])
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.user.first_name} {self.user.last_name}"


class Accountant(models.Model):
    '''
    Limited company user. Has rights to create Fund transfers and see account details
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_identity_number = models.CharField(max_length=15)
    mobile_phone = models.CharField(max_length=17, validators=[PhoneNumberE164Validator()])
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.user.first_name} {self.user.last_name}"


class Manager(models.Model):
    '''
    Company user. Can confirm or reject Fund transfers, has full rights
    on Accounts:
    CRU, delete (if no transfers related to it)
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_identity_number = models.CharField(max_length=15)
    mobile_phone = models.CharField(max_length=17, validators=[PhoneNumberE164Validator()])
    limit_per_transfer = models.PositiveIntegerField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.user.first_name} {self.user.last_name}"


class AccountProduct(models.Model):
    '''
    Defines different Bank account products with some specific details
    '''
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=7, choices=[(t.name, t.value) for t in AccountProductTypeEnum])
    description = models.TextField()
    maturity_in_months = models.PositiveIntegerField(blank=True, null=True,
                                                     validators=[MinValueValidator(1), MaxValueValidator(60)])
    interest_rate = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name} : {self.description}"


class Account(models.Model):
    '''
    Bank account. All Fund transfers are initiated from an account
    '''
    DJANGO_BANK_BIC = 'DJNG8280'

    product = models.ForeignKey(AccountProduct, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    users = models.ManyToManyField(User)
    iban = IBANField(enforce_database_constraint=True, unique=True)
    balance = models.FloatField(validators=[MinValueValidator(0)], default=0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=7, choices=[(s.name, s.value) for s in AccountStatusEnum], default='A')

    def __str__(self):
        return f"{self.iban} {self.currency.code}"

