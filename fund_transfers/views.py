from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from drf_multiple_model.views import ObjectMultipleModelAPIView

from .models import FundTransfer
from .serializers import FundTransferSerializer, FundTransferDetailSerializer
from .permissions import IsFundTransferAccountOwner, IsProperStatus

from registrations.utils import ExtendedTools
from registrations.models import Accountant, Manager, Person
from registrations.permissions import IsManager, IsPerson


class FundTransfersList(ExtendedTools, generics.ListCreateAPIView):
    # Authenticated users only
    permission_classes = [IsAuthenticated]

    serializer_class = FundTransferSerializer

    def get_queryset(self):
        query_set = FundTransfer.objects.all()

        user = self.request.user

        if not user.is_staff:
            extended_user = self.get_extended_user(user=user)

            # We filter transfers for different users according to their permissions to view FTs
            if isinstance(extended_user, Accountant):
                query_set = query_set.filter(user__pk=user.pk)
            elif isinstance(extended_user, Manager) or isinstance(extended_user, Person):
                query_set = query_set.filter(account__customer=extended_user.customer)

        # Some additional filters from request parameters
        for key, value in self.request.query_params.items():
            # Filter by account, from date, to date,
            if key == 'account' or key == 'account_id':
                try:
                    query_set = query_set.filter(account__pk=int(value))
                except:
                    return []
            elif key == 'from_date':
                try:
                    query_set = query_set.filter(created__gte=value + ' 00:00:00')
                except:
                    return []
            elif key == 'to_date':
                try:
                    query_set = query_set.filter(created__lte=value + ' 23:59:59')
                except:
                    return []
            elif key == 'fund_transfer':
                try:
                    query_set = query_set.filter(id=int(value))
                except:
                    return []

        return query_set


class FundTransfersDetail(ExtendedTools, generics.RetrieveUpdateDestroyAPIView):
    # Authenticated users with rights for account, no Accountants and only Initiated FTs
    permission_classes = [IsAuthenticated, IsFundTransferAccountOwner, IsManager | IsPerson, IsProperStatus]

    serializer_class = FundTransferDetailSerializer

    def get_queryset(self):
        query_set = FundTransfer.objects.all()

        user = self.request.user

        if not user.is_staff:
            extended_user = self.get_extended_user(user=user)

            # We filter transfers for different users according to their permissions to view FTs
            if isinstance(extended_user, Accountant):
                query_set = query_set.filter(user__pk=user.pk)
            elif isinstance(extended_user, Manager) or isinstance(extended_user, Person):
                query_set = query_set.filter(account__customer=extended_user.customer)

        return query_set


class Statement(ObjectMultipleModelAPIView):

    def get_queryset(self):

        # self.querylist = [
        #     {'queryset': AccountProduct.objects.all(), 'serializer_class': AccountProductSerializer},
        #     {'queryset': Currency.objects.all(), 'serializer_class': CurrencySerializer},
        # ]

        return None
