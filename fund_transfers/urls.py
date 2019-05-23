from django.urls import path
from . import views

urlpatterns = [
    path('transfers/', views.FundTransfersList.as_view(), name='transfers'),
    path('transfers/<int:pk>/', views.FundTransfersList.as_view(), name='transfers_details'),
]