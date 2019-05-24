from django.db import models


class Notification(models.Model):
    type = models.CharField(max_length=4, choices=[('M', 'Mail'), ('S', 'SMS')])
    to = models.CharField(max_length=200, default='')
    contents = models.TextField()
    status = models.CharField(max_length=10, choices=[('P', 'Pending'), ('S', 'Success'), ('F', 'Failed')], default='P')
