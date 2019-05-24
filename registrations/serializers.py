from random import randint
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import transaction
from rest_framework import serializers

from django_iban.generator import IBANGenerator
from sequences import get_next_value

from .models import *
from .utils import ExtendedTools, CustomerTypeValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator()],
            }
        }


class UserShortSerializer(serializers.ModelSerializer):
    """
    User Serializer for short presentation purposes
    """
    class Meta:
        model = User
        fields = ('id', 'username')
        read_only_fields = ('id',)


class AccountProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountProduct
        fields = '__all__'


class AccountProductShortSerializer(serializers.ModelSerializer):
    """
    Account Product Serializer for short presentation purposes
    """
    class Meta:
        model = AccountProduct
        fields = ('id', 'type', 'name')
        read_only_fields = ('id',)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class CurrencyShortSerializer(serializers.ModelSerializer):
    """
    Currency Serializer for short presentation purposes
    """
    class Meta:
        model = Currency
        fields = ('id', 'code')
        read_only_fields = ('id',)
        extra_kwargs = {
            'code': {
                'validators': [],
            }
        }


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'name', 'type')


class PersonSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Personal extended user serializer for creation
    """
    user = UserSerializer()

    class Meta:
        model = Person
        fields = ('id', 'user', 'personal_identity_number', 'date_of_birth', 'address', 'mobile_phone', 'pin')
        read_only_fields = ('id',)

    def create(self, validated_data):
        extended_user = self.create_extended(model_instance=Person, validated_data=validated_data)
        return extended_user


class PersonDetailSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Personal extended user serializer for RUD
    """
    user = UserDetailSerializer()
    customer = CustomerDetailSerializer()

    class Meta:
        model = Person
        fields = ('id', 'user', 'personal_identity_number', 'date_of_birth', 'address', 'mobile_phone', 'customer')
        read_only_fields = ('id',)
        validators = [CustomerTypeValidator('P')]

    def update(self, instance, validated_data):
        instance = self.update_extended(instance=instance, validated_data=validated_data)
        return instance


class AccountantSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Accountant extended user serializer for creation
    """
    user = UserSerializer()

    class Meta:
        model = Accountant
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone')
        read_only_fields = ('id',)

    def create(self, validated_data):
        extended_user = self.create_extended(model_instance=Accountant, validated_data=validated_data)
        return extended_user


class AccountantDetailSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Accountant extended user serializer for RUD
    """
    user = UserDetailSerializer()
    customer = CustomerDetailSerializer()

    class Meta:
        model = Accountant
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone', 'customer')
        read_only_fields = ('id',)
        validators = [CustomerTypeValidator('C')]

    def update(self, instance, validated_data):
        instance = self.update_extended(instance=instance, validated_data=validated_data)
        return instance


class ManagerSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Manager extended user serializer for creation
    """
    user = UserSerializer()

    class Meta:
        model = Manager
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone', 'limit_per_transfer', 'pin')
        read_only_fields = ('id',)

    def create(self, validated_data):
        extended_user = self.create_extended(model_instance=Manager, validated_data=validated_data)
        return extended_user


class ManagerDetailSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Manager extended user serializer for RUD
    """
    user = UserDetailSerializer()
    customer = CustomerDetailSerializer()

    class Meta:
        model = Manager
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone', 'limit_per_transfer', 'customer')
        read_only_fields = ('id',)
        validators = [CustomerTypeValidator('C')]

    def update(self, instance, validated_data):
        instance = self.update_extended(instance=instance, validated_data=validated_data)
        return instance


class AccountSerializer(ExtendedTools, serializers.ModelSerializer):
    """
    Serializer for Account creation with some validations.
    """
    users = UserDetailSerializer(many=True, read_only=True)
    customer = CustomerDetailSerializer(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('id', 'customer', 'users', 'iban', 'balance', 'created_at', 'status')

    def create(self, validated_data):
        user = self.context['request'].user
        extended_user = self.get_person_manager_extended_user(user=user)

        validated_data['customer'] = extended_user.customer

        generator = IBANGenerator()

        with transaction.atomic():
            iban_sequence = get_next_value('iban_sequence')
            iban = generator.generate(country_code='BG',
                                      bank=Account.DJANGO_BANK_BIC,
                                      account=f"{validated_data['product'].code[:2]}{validated_data['currency'].code}{iban_sequence:05d}")

        validated_data['iban'] = iban['generated_iban']

        validated_data['balance'] = randint(1, 77) * 1000

        instance = Account.objects.create(**validated_data)

        instance.users.add(user)

        return instance


class AccountStatusSerializer(serializers.ModelSerializer):
    users = UserShortSerializer(many=True, read_only=True)
    customer = CustomerDetailSerializer(read_only=True)
    product = AccountProductSerializer(read_only=True)
    currency = CurrencyShortSerializer(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('id', 'customer', 'users', 'iban', 'balance', 'created_at', 'product', 'currency')


class AccountReadOnlySerializer(serializers.ModelSerializer):
    users = UserShortSerializer(many=True, read_only=True)
    customer = CustomerDetailSerializer(read_only=True)
    product = AccountProductShortSerializer(read_only=True)
    currency = CurrencyShortSerializer(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('__all__',)


class AccountShortSerializer(serializers.ModelSerializer):
    currency = CurrencyShortSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'iban', 'currency')
        read_only_fields = ('id', 'currency')
        extra_kwargs = {
            'iban': {
                'validators': [],
            }
        }
