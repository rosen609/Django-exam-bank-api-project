from rest_framework.permissions import BasePermission

from .models import Account


class IsFundTransferAccountOwner(BasePermission):
    """
    Only user with access to fund may see fund transfers from it
    """
    def has_object_permission(self, request, view, obj):
        return Account.objects.filter(pk=obj.account.id).filter(users__pk=request.user.id).exists()


class IsProperStatus(BasePermission):
    """
    Fund transfer with status Initiated could be Updated / Deleted
    """
    def has_object_permission(self, request, view, obj):
        return obj.status == 'I'