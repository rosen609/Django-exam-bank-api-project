from django.shortcuts import get_object_or_404
from django.db.models import F, Value, FloatField
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import FundTransfer
from .serializers import FundTransferSerializer, FundTransferDetailSerializer, StatementSerializer
from .permissions import IsFundTransferAccountOwner, IsProperStatus

from registrations.utils import ExtendedTools
from registrations.models import Accountant, Manager, Person, Account
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
            if key == 'account_id':
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

        return query_set


class StatementList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]

    serializer_class = StatementSerializer

    def get_queryset(self):

        account_id = self.request.query_params.get('account_id', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if account_id is None or from_date is None or to_date is None:
            return []

        account = get_object_or_404(Account, pk=account_id, users__pk=self.request.user.id)

        # Credit transfers query for account
        query_credits = FundTransfer.objects.filter(iban_beneficiary=account.iban,
                                                    last_updated__gte=from_date,
                                                    last_updated__lte=to_date,
                                                    status='P'
                                                    ).values(
            'id', 'last_updated', 'reference_cbs', 'name_beneficiary', 'details',
            amount_debit=Value(0, FloatField()), amount_credit=F('amount_bgn') / account.currency.rate_to_bgn
        )
        # Debit transfers query for account
        query_debits = FundTransfer.objects.filter(account__pk=account.id,
                                                   last_updated__gte=from_date,
                                                   last_updated__lte=to_date,
                                                   status='P'
                                                   ).values(
            'id', 'last_updated', 'reference_cbs', 'name_beneficiary', 'details',
            amount_debit=F('amount_bgn') / account.currency.rate_to_bgn, amount_credit=Value(0, FloatField())
        )

        query_all = query_credits.union(query_debits).order_by('last_updated')

        return query_all
