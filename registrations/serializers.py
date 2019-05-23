from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import ValidationError

from django_iban.generator import IBANGenerator
from sequences import get_next_value

from .models import *


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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'name', 'type')


class ExtendedTools:
    """
    Helper class for different types of extended users and more
    """
    @staticmethod
    def create_extended(model_instance, validated_data):
        """
        Same creation logic for all types of extended users (Person / Accountant / Manager)
        :param model_instance: Current model instance from serializer's create
        :param validated_data: validated_data from serializer's create
        :return: extended user (Person / Accountant / Manager) with populated data
        """
        user_data = validated_data.pop('user')
        user = get_user_model().objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        extended_user = model_instance.objects.create(user=user, **validated_data)
        extended_user.user.password = ''
        return extended_user

    @staticmethod
    def update_extended(instance, validated_data):
        """
        Same update logic for all types of extended users (Person / Accountant / Manager)
        :param instance: Current instance from serializer's update
        :param validated_data: validated_data from serializer's update
        :return: extended user (Person / Accountant / Manager) with updated data
        """
        customer_data = validated_data.pop('customer')
        customer = Customer.objects.get(cbs_customer_number=customer_data['cbs_customer_number'])
        instance.customer = customer
        user_data = validated_data.pop('user')
        user = get_user_model().objects.get_or_create(username=user_data['username'])[0]
        user.email = user_data['email']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()
        instance.user = user
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    @staticmethod
    def get_extended_user(user):
        """
        Gets extended user or raises ValidationError
        :param user:
        :return: extended user found
        """
        try:
            extended_user = Person.objects.get(user__pk=user.id)
        except Person.DoesNotExist:
            try:
                extended_user = Manager.objects.get(user__pk=user.id)
            except Manager.DoesNotExist:
                try:
                    extended_user = Accountant.objects.get(user__pk=user.id)
                except Accountant.DoesNotExist:
                    raise ValidationError('Wrong user type!')
        return extended_user

    @staticmethod
    def get_person_manager_extended_user(user):
        """
        Gets extended user(if he/she is Person or Manager) or raises ValidationError
        :param user:
        :return: extended user found
        """
        try:
            extended_user = Person.objects.get(user__pk=user.id)
        except Person.DoesNotExist:
            try:
                extended_user = Manager.objects.get(user__pk=user.id)
            except Manager.DoesNotExist:
                raise ValidationError('Wrong user type!')
        return extended_user

    @staticmethod
    def get_object_or_err(model_object, pk):
        """
        Helper function to retrieve instance of any class by pk provided
        :param model_object:
        :param pk:
        :return: instance
        """
        try:
            return model_object.objects.get(pk=pk)
        except model_object.DoesNotExist:
            raise ValidationError(f'{model_object.__name__} does not exists!')


class CustomerTypeValidator(object):
    """
    Enforces consistent type for extended user and customer relation
    """
    def __init__(self, required_type):
        self._required_type = required_type

    def __call__(self, value):
        customer = Customer.objects.get(cbs_customer_number=value['customer']['cbs_customer_number'])
        if not customer:
            raise ValidationError("Incorrect CBS customer number.")
        if customer.type != self._required_type:
            raise ValidationError("Incorrect customer type.")


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
                                      account=f"{validated_data['currency'].code}{iban_sequence:08d}")

        validated_data['iban'] = iban['generated_iban']

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
