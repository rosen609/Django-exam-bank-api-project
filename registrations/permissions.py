from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Manager, Accountant, Person, Account
from fund_transfers.models import FundTransfers


class IsSuperUser(BasePermission):
    """
    Allows only superuser access
    Intended for Core Bank System objects administration
    """

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsReadOnly(BasePermission):
    """
    Allows readonly access for Account Products and Currencies
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsMethodPOST(BasePermission):
    """
    Allows extended users creation
    """

    def has_permission(self, request, view):
        return request.method == 'POST'


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
    """
    Only accounts without transfers could be deleted
    """
    def has_object_permission(self, request, view, obj):
        account_transfers_exist = FundTransfers.objects.filter(account__pk=obj.id).exists()
        return (request.method == 'DELETE' or request.method in SAFE_METHODS) and not account_transfers_exist


class IsManagerAndAccountOwner(BasePermission):
    """
    Manager with access to account could add more users to it
    """
    def has_object_permission(self, request, view, obj):
        is_manager = Manager.objects.filter(user__pk=request.user.id).exists()
        is_account_owner = request.user in Account.objects.filter(pk=obj.id).users
        return is_manager and is_account_owner
