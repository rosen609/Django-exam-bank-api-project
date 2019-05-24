from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from .models import *


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
        try:
            customer = Customer.objects.get(cbs_customer_number=value['customer']['cbs_customer_number'])
        except Customer.DoesNotExist:
            raise ValidationError("Incorrect CBS customer number.")
        if customer.type != self._required_type:
            raise ValidationError("Incorrect customer type.")


