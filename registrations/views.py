from rest_framework import generics
from rest_framework import exceptions
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from drf_multiple_model.views import ObjectMultipleModelAPIView

from .serializers import *
from .permissions import *


class MethodSerializerView(object):
    '''
    Utility class for get different serializer class by method.
    For example:
    method_serializer_classes = {
        ('GET', ): MyModelListViewSerializer,
        ('PUT', 'PATCH'): MyModelCreateUpdateSerializer
    }
    '''
    method_serializer_classes = None

    def get_serializer_class(self):
        assert self.method_serializer_classes is not None, (
            'Expected view %s should contain method_serializer_classes '
            'to get right serializer class.' %
            (self.__class__.__name__, )
        )
        for methods, serializer_cls in self.method_serializer_classes.items():
            if self.request.method in methods:
                return serializer_cls

        raise exceptions.MethodNotAllowed(self.request.method)


class GeneralInfoView(ObjectMultipleModelAPIView):
    '''
    General info multiple view for unauthenticated access
    Shows both Account Products and Currencies info
    '''

    querylist = [
        {'queryset': AccountProduct.objects.all(), 'serializer_class': AccountProductSerializer},
        {'queryset': Currency.objects.all(), 'serializer_class': CurrencySerializer},
    ]


class AllExtendedUsersView(ObjectMultipleModelAPIView):
    '''
    Admins-only All extended users list
    Lists Persons, Accountants and Managers info
    '''

    querylist = [
        {'queryset': Person.objects.all(), 'serializer_class': PersonDetailSerializer},
        {'queryset': Accountant.objects.all(), 'serializer_class': AccountantDetailSerializer},
        {'queryset': Manager.objects.all(), 'serializer_class': ManagerDetailSerializer},
    ]

    permission_classes = [IsAdminUser]


class AccountProductList(generics.ListCreateAPIView):
    queryset = AccountProduct.objects.all()
    serializer_class = AccountProductSerializer

    permission_classes = [IsSuperUser|IsReadOnly]


class AccountProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountProduct.objects.all()
    serializer_class = AccountProductSerializer

    permission_classes = [IsSuperUser]


class CurrencyList(generics.ListCreateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    permission_classes = [IsSuperUser | IsReadOnly]


class CurrencyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    permission_classes = [IsSuperUser]


class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    permission_classes = [IsSuperUser]


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    permission_classes = [IsSuperUser]


class PersonList(MethodSerializerView, generics.ListCreateAPIView):
    method_serializer_classes = {
        ('GET',): PersonDetailSerializer,
        ('POST',): PersonSerializer,
    }

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return Person.objects.all()
        return Person.objects.none()


class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonDetailSerializer
    queryset = Person.objects.all()

    permission_classes = [IsAdminUser]


class AccountantList(MethodSerializerView, generics.ListCreateAPIView):
    method_serializer_classes = {
        ('GET',): AccountantDetailSerializer,
        ('POST',): AccountantSerializer,
    }

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return Accountant.objects.all()
        return Accountant.objects.none()


class AccountantDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountantDetailSerializer
    queryset = Accountant.objects.all()

    permission_classes = [IsAdminUser]


class ManagerList(MethodSerializerView, generics.ListCreateAPIView):
    method_serializer_classes = {
        ('GET',): ManagerDetailSerializer,
        ('POST',): ManagerSerializer,
    }

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return Manager.objects.all()
        return Manager.objects.none()


class ManagerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerDetailSerializer

    permission_classes = [IsAdminUser]


class AccountList(generics.ListCreateAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        query_set = Account.objects.all()
        user = self.request.user

        if not user.is_staff:
            query_set = query_set.filter(users__pk=user.pk)

        return query_set

    permission_classes = [IsAuthenticated, IsAdminUser | IsPerson | IsManager | IsAccountant & IsReadOnly]


class AccountDetail(generics.DestroyAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        query_set = Account.objects.all()
        user = self.request.user

        if not user.is_staff:
            query_set = query_set.filter(users__pk=user.pk)

        return query_set

    permission_classes = [IsAuthenticated, AccountDeletePermission, IsAdminUser | IsPerson | IsManager]
