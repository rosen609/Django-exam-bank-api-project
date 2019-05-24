from django.urls import path
from . import views

urlpatterns = [
    path('', views.FundTransfersList.as_view(), name='transfers'),
    path('<int:pk>/', views.FundTransfersList.as_view(), name='transfers_details'),
]