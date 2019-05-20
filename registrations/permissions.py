from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    '''
    Allows only superuser access
    Intended for Core Bank System objects and user-related administration
    '''

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsSuperUserOrReadOnly(BasePermission):
    '''
    Allows readonly access for Account Products and Currencies
    '''

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        return False
