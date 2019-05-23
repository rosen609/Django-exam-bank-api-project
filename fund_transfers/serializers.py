from rest_framework import serializers

from .models import FundTransfer
from registrations.serializers import CurrencyShortSerializer, UserShortSerializer, AccountShortSerializer


class FundTransferSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    account = AccountShortSerializer()
    currency = CurrencyShortSerializer(read_only=True)
    user_approve = UserShortSerializer(read_only=True)

    class Meta:
        model = FundTransfer

        fields = ('id', 'user', 'account', 'iban_beneficiary', 'bic_beneficiary', 'bank_beneficiary',
                  'name_beneficiary', 'amount', 'currency', 'details', 'created', 'last_updated', 'status',
                  'user_approve', 'reference_cbs', 'payment_system')

        read_only_fields = ('id', 'user', 'created', 'last_updated', 'status', 'user_approve', 'reference_cbs')

    def create(self, validated_data):
        pass
