import datetime
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.utils import model_meta

from .models import FundTransfer

from registrations.models import Currency, Account, Manager
from registrations.serializers import CurrencyShortSerializer, UserShortSerializer, AccountShortSerializer
from registrations.utils import ExtendedTools
from notifications.tasks import send_sms


class FundTransferSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_approved = UserShortSerializer(read_only=True)
    account = AccountShortSerializer()
    currency = CurrencyShortSerializer()

    class Meta:
        model = FundTransfer

        fields = ('id', 'user', 'iban_beneficiary', 'bic_beneficiary', 'bank_beneficiary',
                  'name_beneficiary', 'details', 'amount', 'currency', 'amount_bgn', 'created', 'last_updated',
                  'user_approved', 'reference_cbs', 'account', 'payment_system', 'status')

        read_only_fields = ('id', 'user', 'amount_bgn', 'created', 'last_updated', 'status', 'user_approved',
                            'reference_cbs')

    def create(self, validated_data):

        user = self.context['request'].user
        validated_data['user'] = user

        account_data = validated_data.pop('account')
        account = get_object_or_404(Account, iban=account_data['iban'], users__pk=user.id)
        validated_data['account'] = account

        currency_data = validated_data.pop('currency')
        currency = get_object_or_404(Currency, code=currency_data['code'])
        validated_data['currency'] = currency

        validated_data['amount_bgn'] = round(validated_data['amount'] * currency.rate_to_bgn, 2)

        return super(FundTransferSerializer, self).create(validated_data)


class FundTransferDetailSerializer(ExtendedTools, serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_approved = UserShortSerializer(read_only=True)
    account = AccountShortSerializer()
    currency = CurrencyShortSerializer()

    class Meta:
        model = FundTransfer

        fields = ('id', 'user', 'iban_beneficiary', 'bic_beneficiary', 'bank_beneficiary',
                  'name_beneficiary', 'details', 'amount', 'currency', 'created', 'last_updated', 'status',
                  'user_approved', 'reference_cbs', 'account', 'payment_system', 'pin_otp')

        read_only_fields = ('id', 'user', 'created', 'last_updated', 'user_approved', 'reference_cbs')

    @staticmethod
    def update_account_balance(account, amount_bgn):
        # If we got account instance - it is the debit account
        # Otherwise it should be IBAN for credit account
        if not isinstance(account, Account):
            try:
                account = Account.objects.get(iban=account)
            except Account.DoesNotExist:
                return

        amount = round(amount_bgn / account.currency.rate_to_bgn, 2)
        if account.balance + amount >= 0:
            account.balance = account.balance + amount
            account.save()
        else:
            raise ValidationError('Not sufficient account balance! Transfer rejected!')

    def update(self, instance, validated_data):
        """
        Fund transfers update and processing
        :param instance:
        :param validated_data:
        :return:
        """

        user = self.context['request'].user
        validated_data['user_approved'] = user

        account_data = validated_data.pop('account')
        account = get_object_or_404(Account, iban=account_data['iban'], users__pk=user.id)
        validated_data['account'] = account

        currency_data = validated_data.pop('currency')
        currency = get_object_or_404(Currency, code=currency_data['code'])
        validated_data['currency'] = currency

        validated_data['amount_bgn'] = round(validated_data['amount'] * currency.rate_to_bgn, 2)

        # Status should be Initiated, Approved or Rejected
        if validated_data['status'] not in ['I', 'A', 'R']:
            raise ValidationError('Transfers should be Approved or Rejected!')

        # We process FT only if it is in Authorized status
        if validated_data['status'] == 'A' or (validated_data['status'] == 'I' and validated_data['pin_otp']):
            extended_user = self.get_extended_user(user)

            if validated_data['pin_otp']:
                # Validate correct PIN + OTP
                if validated_data['pin_otp'] != extended_user.pin + instance.otp_generated:
                    raise ValidationError("Invalid PIN + OTP!")

            if isinstance(extended_user, Manager):
                if validated_data['amount_bgn'] > extended_user.limit_per_transfer:
                    raise ValidationError("Manager's limit per transfer exceeded!")

            self.update_account_balance(account, -validated_data['amount_bgn'])
            self.update_account_balance(validated_data['iban_beneficiary'], validated_data['amount_bgn'])

            validated_data['status'] = 'P'
            validated_data['reference_cbs'] = f'FT{datetime.date.today().strftime("%Y%m%d")}{instance.id:06d}'

            send_sms(to_phone_number=extended_user.mobile_phone,
                     message_body=f'Ordered transfer {instance.id} '
                     f'({validated_data["amount"]:.2f} {validated_data["currency"].code})')

        # Same as in rest_framework.serializers
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance
