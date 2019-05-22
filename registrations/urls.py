from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('info/', views.GeneralInfoView.as_view(), name='info'),
    path('all_users/', views.AllExtendedUsersView.as_view(), name='all_users'),
    path('account-products/', views.AccountProductList.as_view(), name='account_products'),
    path('account-products/<int:pk>/', views.AccountProductDetail.as_view(), name='account_products_detail'),
    path('currencies/', views.CurrencyList.as_view(), name='currencies'),
    path('currencies/<int:pk>/', views.AccountProductDetail.as_view(), name='currencies_detail'),
    path('customers/', views.CustomerList.as_view(), name='customers'),
    path('customers/<int:pk>/', views.CustomerDetail.as_view(), name='customers_detail'),
    path('persons/', views.PersonList.as_view(), name='persons'),
    path('persons/<int:pk>/', views.PersonDetail.as_view(), name='persons_detail'),
    path('accountants/', views.AccountantList.as_view(), name='accountants'),
    path('accountants/<int:pk>/', views.AccountantDetail.as_view(), name='accountants_detail'),
    path('managers/', views.ManagerList.as_view(), name='managers'),
    path('managers/<int:pk>/', views.ManagerDetail.as_view(), name='managers_detail'),
    path('accounts/', views.AccountList.as_view(), name='accounts'),
    path('accounts/<int:pk>/', views.AccountDetail.as_view(), name='accounts_detail'),
    path('accounts/<int:pk>/user/<int:user_pk>/', views.AccountUser.as_view(), name='accounts_user'),
]
