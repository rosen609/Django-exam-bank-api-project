from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('auth/register/', views.UserCreate.as_view(), name='register'),
    path('info/', views.GeneralInfoAPIView.as_view(), name='info'),
    path('account-products/', views.AccountProductList.as_view(), name='account-products'),
    path('account-products/<int:pk>/', views.AccountProductDetail.as_view(), name='account-products-detail'),
    path('currencies/', views.CurrencyList.as_view(), name='currencies'),
    path('currencies/<int:pk>/', views.AccountProductDetail.as_view(), name='currencies-detail'),
    path('customers/', views.CustomerList.as_view(), name='customer'),
    path('customers/<int:pk>/', views.CustomerDetail.as_view(), name='customer-detail'),

    path('accounts/', views.AccountList.as_view(), name='accounts'),
]