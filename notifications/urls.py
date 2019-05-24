from django.urls import path

from . import views

urlpatterns = [
    path('send_otp/<int:transfer_pk>/', views.NotificationOTP.as_view(), name='send_otp')
]
