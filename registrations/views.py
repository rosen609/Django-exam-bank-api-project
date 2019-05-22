from rest_framework import generics
from rest_framework import exceptions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from drf_multiple_model.views import ObjectMultipleModelAPIView

from .serializers import *
from .permissions import *
from .models import *


class MethodSerializerView(object):
    """
    Utility class for get different serializer class by method.
    For example:
    method_serializer_classes = {
        ('GET', ): MyModelListViewSerializer,
        ('PUT', 'PATCH'): MyModelCreateUpdateSerializer
    }
    """
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
    """
    General info multiple view for unauthenticated access
    Shows both Account Products and Currencies info
    """

    querylist = [
        {'queryset': AccountProduct.objects.all(), 'serializer_class': AccountProductSerializer},
        {'queryset': Currency.objects.all(), 'serializer_class': CurrencySerializer},
    ]


class AllExtendedUsersView(ObjectMultipleModelAPIView):
    """
    Admins-only All extended users list
    Lists Persons, Accountants and Managers info
    """

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
            # Admin users should be able to view list of all Accountants
            return Accountant.objects.all()
        else:
            # Managers should be able to view list of Accountants for the same customer
            try:
                manager = Manager.objects.get(user__pk=self.request.user.pk)
                if manager.customer:
                    return Accountant.objects.filter(customer__pk=manager.customer.pk)
            except Accountant.DoesNotExist:
                pass
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
            # Admin users should be able to view list of all Managers
            return Manager.objects.all()
        else:
            # Managers should be able to view list of Managers for the same customer
            try:
                manager = Manager.objects.get(user__pk=self.request.user.pk)
                if manager.customer:
                    return Manager.objects.filter(customer__pk=manager.customer.pk)
            except Manager.DoesNotExist:
                pass
        return Manager.objects.none()


class ManagerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerDetailSerializer

    permission_classes = [IsAdminUser]


class AccountList(MethodSerializerView, generics.ListCreateAPIView):
    method_serializer_classes = {
        ('GET',): AccountReadOnlySerializer,
        ('POST',): AccountSerializer,
    }

    def get_queryset(self):
        query_set = Account.objects.all()
        user = self.request.user

        if not user.is_staff:
            query_set = query_set.filter(users__pk=user.pk)

        return query_set

    permission_classes = [IsAuthenticated, IsAdminUser | IsPerson | IsManager | IsAccountant & IsReadOnly]


class AccountDetail(MethodSerializerView, generics.RetrieveUpdateDestroyAPIView):
    method_serializer_classes = {
        ('GET',): AccountReadOnlySerializer,
        ('PUT', 'PATCH', 'DELETE',): AccountStatusSerializer,
    }

    def get_queryset(self):
        query_set = Account.objects.all()
        user = self.request.user

        if not user.is_staff:
            query_set = query_set.filter(users__pk=user.pk)

        return query_set

    permission_classes = [IsAuthenticated, AccountDeletePermission, IsAdminUser | IsPerson | IsManager]


class AccountUser(ExtendedTools, APIView):
    """
    Add / remove users to / from account
    """
    permission_classes = [IsAdminUser | IsManagerAndAccountOwner]
    allowed_methods = ('GET', 'DELETE')

    def get(self, request, pk, user_pk):
        return_status = status.HTTP_201_CREATED

        account = self.get_object_or_404(model_object=Account, pk=pk)
        user_to_add = self.get_object_or_404(model_object=User, pk=user_pk)

        if not Account.objects.filter(pk=pk).filter(users__pk=user_pk).exists():
            extended_user = self.get_extended_user(user=user_to_add)
            if account.customer != extended_user.customer:
                raise ValidationError('Different customer in user and account!')
            account.users.add(user_to_add)
        else:
            return_status = status.HTTP_302_FOUND

        serializer = AccountReadOnlySerializer(account)
        return Response(data=serializer.data, status=return_status)

    def delete(self, request, pk, user_pk):
        account = self.get_object_or_404(model_object=Account, pk=pk)
        user_to_remove = self.get_object_or_404(model_object=User, pk=user_pk)
        if Account.objects.filter(pk=pk).filter(users__pk=user_pk).exists():
            account.users.remove(user_to_remove)
        serializer = AccountReadOnlySerializer(account)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


