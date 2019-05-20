from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('auth/register/', views.UserCreate.as_view(), name='register'),
    path('account-products/', views.AccountProductList.as_view(), name='account-products'),
    path('accounts/', views.AccountList.as_view(), name='accounts'),
]