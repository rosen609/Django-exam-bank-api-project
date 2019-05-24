from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import FundTransfer
from .serializers import FundTransferSerializer, FundTransferDetailSerializer
from .permissions import IsFundTransferAccountOwner, IsProperStatus

from registrations.utils import ExtendedTools
from registrations.models import Accountant, Manager, Person
from registrations.permissions import IsAccountant


class FundTransfersList(ExtendedTools, generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = FundTransferSerializer

    def get_queryset(self):
        query_set = FundTransfer.objects.all()

        user = self.request.user

        if not user.is_staff:
            extended_user = self.get_extended_user(user=user)

            if isinstance(extended_user, Accountant):
                query_set = query_set.filter(users__pk=user.pk)
            elif isinstance(extended_user, Manager) or isinstance(extended_user, Person):
                query_set = query_set.filter(account__customer=extended_user.customer)

        return query_set


class FundTransfersDetail(ExtendedTools, generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated, IsFundTransferAccountOwner, ~IsAccountant, IsProperStatus]

    serializer_class = FundTransferDetailSerializer

    def get_queryset(self):
        query_set = FundTransfer.objects.all()

        user = self.request.user

        if not user.is_staff:
            extended_user = self.get_extended_user(user=user)

            if isinstance(extended_user, Accountant):
                query_set = query_set.filter(users__pk=user.pk)
            elif isinstance(extended_user, Manager) or isinstance(extended_user, Person):
                query_set = query_set.filter(account__customer=extended_user.customer)

        return query_set
