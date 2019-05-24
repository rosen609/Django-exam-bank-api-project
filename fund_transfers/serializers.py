from rest_framework import serializers
from django.shortcuts import get_object_or_404

from .models import FundTransfer
from registrations.models import Currency, Account
from registrations.serializers import CurrencyShortSerializer, UserShortSerializer, AccountShortSerializer


class FundTransferSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_approve = UserShortSerializer(read_only=True)
    account = AccountShortSerializer()
    currency = CurrencyShortSerializer()

    class Meta:
        model = FundTransfer

        fields = ('id', 'user', 'iban_beneficiary', 'bic_beneficiary', 'bank_beneficiary',
                  'name_beneficiary', 'details', 'amount', 'currency', 'created', 'last_updated', 'status',
                  'user_approved', 'reference_cbs', 'account', 'payment_system')

        read_only_fields = ('id', 'user', 'created', 'last_updated', 'status', 'user_approved', 'reference_cbs')

    def create(self, validated_data):

        user = self.context['request'].user
        validated_data['user'] = user

        account_data = validated_data.pop('account')
        account = get_object_or_404(Account, iban=account_data['iban'], users__pk=user.id)
        validated_data['account'] = account

        currency_data = validated_data.pop('currency')
        currency = get_object_or_404(Currency, code=currency_data['code'])
        validated_data['currency'] = currency

        validated_data['amount_bgn'] = round(validated_data['amount'] * currency.rate_to_BGN)

        return super(FundTransferSerializer, self).create(validated_data)


class FundTransferDetailSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_approve = UserShortSerializer(read_only=True)
    account = AccountShortSerializer()
    currency = CurrencyShortSerializer()

    class Meta:
        model = FundTransfer

        fields = ('id', 'user', 'iban_beneficiary', 'bic_beneficiary', 'bank_beneficiary',
                  'name_beneficiary', 'details', 'amount', 'currency', 'created', 'last_updated', 'status',
                  'user_approved', 'reference_cbs', 'account', 'payment_system', 'otp_received')

        read_only_fields = ('id', 'user', 'created', 'last_updated', 'user_approved', 'reference_cbs')

    def update(self, instance, validated_data):

        user = self.context['request'].user
        validated_data['user'] = user

        account_data = validated_data.pop('account')
        account = get_object_or_404(Account, iban=account_data['iban'], users__pk=user.id)
        validated_data['account'] = account

        currency_data = validated_data.pop('currency')
        currency = get_object_or_404(Currency, code=currency_data['code'])
        validated_data['currency'] = currency

        validated_data['amount_bgn'] = round(validated_data['amount'] * currency.rate_to_BGN)

        return instance
