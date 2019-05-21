from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Manager, Accountant, Person
from fund_transfers.models import FundTransfers


class IsSuperUser(BasePermission):
    '''
    Allows only superuser access
    Intended for Core Bank System objects and user-related administration
    '''

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsReadOnly(BasePermission):
    '''
    Allows readonly access for Account Products and Currencies
    '''

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsManager(BasePermission):
    def has_permission(self, request, view):
        is_manager = Manager.objects.filter(user__pk=request.user.id).exists()

        return is_manager


class IsPerson(BasePermission):
    def has_permission(self, request, view):
        is_person = Person.objects.filter(user__pk=request.user.id).exists()

        return is_person


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        is_accountant = Accountant.objects.filter(user__pk=request.user.id).exists()

        return is_accountant


class AccountDeletePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        account_transfers_exist = FundTransfers.objects.filter(account__pk=obj.id).exists()
        return request.method == 'DELETE' and not account_transfers_exist

