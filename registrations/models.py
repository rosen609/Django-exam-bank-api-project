from django.db import models
from django.contrib.auth.models import User


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    egn = models.CharField(max_length=10)
    lnc = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=200)
    mobile_phone = models.CharField(max_length=17,)
