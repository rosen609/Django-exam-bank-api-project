from django.urls import re_path
from django_twilio.views import message

urlpatterns = [
    re_path(r'^message/$', message, {
        'message': 'Hello world',
        'to': '+359885001483',
        'sender': '+18882223333',
        'status_callback': '/sms/completed/',
    }, name='send_message'),
]
