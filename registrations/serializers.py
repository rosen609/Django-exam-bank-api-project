from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from django_iban.generator import IBANGenerator
from django.db import transaction

from sequences import get_next_value

from .models import *
from .validators import *


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


class AccountProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountProduct
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'name', 'type')


class PersonSerializer(serializers.ModelSerializer):
    '''
    Personal extended user serializer for creation
    '''
    user = UserSerializer()

    class Meta:
        model = Person
        fields = ('id', 'user', 'personal_identity_number', 'date_of_birth', 'address', 'mobile_phone')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = get_user_model().objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        person = Person.objects.create(user=user, **validated_data)
        person.user.password = ''
        return person


class PersonDetailSerializer(serializers.ModelSerializer):
    '''
    Personal extended user serializer for RUD
    '''
    user = UserDetailSerializer()
    customer = CustomerDetailSerializer()

    class Meta:
        model = Person
        fields = ('id', 'user', 'personal_identity_number', 'date_of_birth', 'address', 'mobile_phone', 'customer')
        read_only_fields = ('id',)
        validators = [CustomerTypeValidator('P')]

    def update(self, instance, validated_data):
        customer_data = validated_data['customer']
        customer = Customer.objects.get(cbs_customer_number=customer_data['cbs_customer_number'])
        instance.customer = customer
        user_data = validated_data['user']
        user = get_user_model().objects.get_or_create(username=user_data['username'])[0]
        user.email = user_data['email']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()
        instance.user = user
        instance.save()
        return instance


class AccountantSerializer(serializers.ModelSerializer):
    '''
    Accountant extended user serializer for creation
    '''
    user = UserSerializer()

    class Meta:
        model = Accountant
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = get_user_model().objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        accountant = Accountant.objects.create(user=user, **validated_data)
        accountant.user.password = ''
        return accountant


class AccountantDetailSerializer(serializers.ModelSerializer):
    '''
    Accountant extended user serializer for RUD
    '''
    user = UserDetailSerializer()
    customer = CustomerDetailSerializer()

    class Meta:
        model = Accountant
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone', 'customer')
        read_only_fields = ('id',)
        validators = [CustomerTypeValidator('C')]

    def update(self, instance, validated_data):
        customer_data = validated_data['customer']
        customer = Customer.objects.get(cbs_customer_number=customer_data['cbs_customer_number'])
        instance.customer = customer
        user_data = validated_data['user']
        user = get_user_model().objects.get_or_create(username=user_data['username'])[0]
        user.email = user_data['email']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()
        instance.user = user
        instance.save()
        return instance


class ManagerSerializer(serializers.ModelSerializer):
    '''
    Manager extended user serializer for creation
    '''
    user = UserSerializer()

    class Meta:
        model = Manager
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone', 'limit_per_transfer')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = get_user_model().objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        manager = Manager.objects.create(user=user, **validated_data)
        manager.user.password = ''
        return manager


class ManagerDetailSerializer(serializers.ModelSerializer):
    '''
    Manager extended user serializer for RUD
    '''
    user = UserDetailSerializer()
    customer = CustomerDetailSerializer()

    class Meta:
        model = Manager
        fields = ('id', 'user', 'personal_identity_number', 'mobile_phone', 'limit_per_transfer', 'customer')
        read_only_fields = ('id',)
        validators = [CustomerTypeValidator('C')]

    def update(self, instance, validated_data):
        customer_data = validated_data['customer']
        customer = Customer.objects.get(cbs_customer_number=customer_data['cbs_customer_number'])
        instance.customer = customer
        user_data = validated_data['user']
        user = get_user_model().objects.get_or_create(username=user_data['username'])[0]
        user.email = user_data['email']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()
        instance.user = user
        instance.save()
        return instance


class AccountSerializer(serializers.ModelSerializer):
    users = UserDetailSerializer(many=True, read_only=True)
    customer = CustomerDetailSerializer(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('id', 'customer', 'users', 'iban', 'balance', 'created_at', 'status')

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            extended_user = Person.objects.get(user__pk=user.id)
        except Person.DoesNotExist:
            try:
                extended_user = Manager.objects.get(user__pk=user.id)
            except Manager.DoesNotExist:
                raise ValidationError('Wrong user type!')

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
