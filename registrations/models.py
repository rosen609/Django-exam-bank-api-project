from django.db import models
from django.contrib.auth.models import User

from .validators import PhoneNumberE164Validator


phone_number_validator = PhoneNumberE164Validator()


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_identity_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=200)
    mobile_phone = models.CharField(max_length=17, validators=[phone_number_validator])

    def __str__(self):
        return f"{self.user} - {self.user.first_name} {self.user.last_name} {self.mobile_phone}"


class Company(models.Model):
    name = models.CharField(max_length=150)
    company_identity_number = models.CharField(max_length=30)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.company_identity_number}"


class Accountant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_identity_number = models.CharField(max_length=15)
    mobile_phone = models.CharField(max_length=17, validators=[phone_number_validator])

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.mobile_phone}"


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_identity_number = models.CharField(max_length=15)
    mobile_phone = models.CharField(max_length=17, validators=[phone_number_validator])
    limit_per_trasfer = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.mobile_phone}"
