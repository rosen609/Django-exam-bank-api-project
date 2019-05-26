from rest_framework.test import APITestCase
from rest_framework import status
from .models import *


class BaseRegistrationsTestCase(APITestCase):

    def setUp(self):
        self.base_url = 'http://127.0.0.1:8000/api/v1/registrations/'

        self.admin_user = User.objects.create_user('admin', 'admin@test.com', '123')
        self.admin_user.is_staff = True
        self.admin_user.save()

        # create customers, currencies, account product, person, accountant, manager for account purposes
        self.customer_person = Customer()
        self.customer_person.cbs_customer_number = '000000001'
        self.customer_person.name = 'Peter Petrov'
        self.customer_person.type = 'P'
        self.customer_person.save()

        self.customer_company = Customer()
        self.customer_company.cbs_customer_number = '000000002'
        self.customer_company.name = 'SGB Ltd.'
        self.customer_company.type = 'C'
        self.customer_company.save()

        data = {
            "user": {
                "username": "person",
                "password": "123",
                "email": "person@mail.bg",
                "first_name": "Peter",
                "last_name": "Petrov"
            },
            "personal_identity_number": "987654321",
            "date_of_birth": "1990-12-12",
            "address": "Sofia, Gurko 7",
            "mobile_phone": "+359885001483",
            "pin": "0000"
        }
        self.client.post(self.base_url + 'persons/', data=data, format='json')

        data = {
            "user": {
                "username": "accountant",
                "password": "123",
                "email": "accountant@mail.bg",
                "first_name": "Peter",
                "last_name": "Petrov"
            },
            "personal_identity_number": "123456789",
            "mobile_phone": "+359885001483"
        }
        self.client.post(self.base_url + 'accountants/', data=data, format='json')

        data = {
            "user": {
                "username": "manager",
                "password": "123",
                "email": "accountant@mail.bg",
                "first_name": "Svilen",
                "last_name": "Noev"
            },
            "personal_identity_number": "123456789",
            "mobile_phone": "+359885001483",
            "limit_per_transfer": "6000",
            "pin": "0000"
        }
        self.client.post(self.base_url + 'managers/', data=data, format='json')

        self.person = Person.objects.all()[0]
        self.person.customer = self.customer_person
        self.person.save()

        self.accountant = Accountant.objects.all()[0]
        self.accountant.customer = self.customer_company
        self.accountant.save()

        self.manager = Manager.objects.all()[0]
        self.manager.customer = self.customer_company
        self.manager.save()

        self.account_product = AccountProduct()
        self.account_product.code = '10CA'
        self.account_product.name = 'Current account'
        self.account_product.type = 'C'
        self.account_product.description = 'Current account with very attractive interest rate'
        self.account_product.interest_rate = 0.1
        self.account_product.save()

        self.bgn = Currency()
        self.bgn.code = 'BGN'
        self.bgn.name = 'Bulgarian lev'
        self.bgn.rate_to_bgn = 1
        self.bgn.save()

        self.eur = Currency()
        self.eur.code = 'EUR'
        self.eur.name = 'Euro'
        self.eur.rate_to_bgn = 1.95583
        self.eur.save()

        self.usd = Currency()
        self.usd.code = 'USD'
        self.usd.name = 'US Dollar'
        self.usd.rate_to_bgn = 1.75584
        self.usd.save()

        self.account_1_customer_person = Account()
        self.account_1_customer_person.product = self.account_product
        self.account_1_customer_person.customer = self.customer_person
        self.account_1_customer_person.iban = 'BG88DJNG828010BGN00012'
        self.account_1_customer_person.balance = 1000
        self.account_1_customer_person.currency = self.bgn
        self.account_1_customer_person.save()
        self.account_1_customer_person.users.add(self.person.user)
        self.account_1_customer_person.save()

        self.account_2_customer_person = Account()
        self.account_2_customer_person.product = self.account_product
        self.account_2_customer_person.customer = self.customer_person
        self.account_2_customer_person.iban = 'BG84DJNG828010EUR00013'
        self.account_2_customer_person.balance = 2000
        self.account_2_customer_person.currency = self.eur
        self.account_2_customer_person.save()
        self.account_2_customer_person.users.add(self.person.user)
        self.account_2_customer_person.save()

        self.account_1_customer_company = Account()
        self.account_1_customer_company.product = self.account_product
        self.account_1_customer_company.customer = self.customer_company
        self.account_1_customer_company.iban = 'BG79DJNG828042BGN00014'
        self.account_1_customer_company.balance = 12000
        self.account_1_customer_company.currency = self.bgn
        self.account_1_customer_company.save()
        self.account_1_customer_company.users.add(self.manager.user)
        self.account_1_customer_company.users.add(self.accountant.user)
        self.account_1_customer_company.save()

        self.account_2_customer_company = Account()
        self.account_2_customer_company.product = self.account_product
        self.account_2_customer_company.customer = self.customer_company
        self.account_2_customer_company.iban = 'BG97DJNG828020USD00015'
        self.account_2_customer_company.balance = 24000
        self.account_2_customer_company.currency = self.usd
        self.account_2_customer_company.save()
        self.account_2_customer_company.users.add(self.manager.user)
        self.account_2_customer_company.save()


class RegistrationsTestCases(BaseRegistrationsTestCase):

    def test_unauthorized_get_all_users(self):
        response = self.client.get(self.base_url + 'all_users/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_register_valid_person(self):
        data = {
            "user": {
                "username": "new_person",
                "password": "123",
                "email": "person@mail.bg",
                "first_name": "Peter",
                "last_name": "Petrov"
            },
            "personal_identity_number": "987654321",
            "date_of_birth": "1990-12-12",
            "address": "Sofia, Gurko 7",
            "mobile_phone": "+359885001483",
            "pin": "0000"
        }
        response = self.client.post(self.base_url + 'persons/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_duplicate_person_should_fail(self):
        data = {
            "user": {
                "username": "new_person",
                "password": "123",
                "email": "person@mail.bg",
                "first_name": "Peter",
                "last_name": "Petrov"
            },
            "personal_identity_number": "987654321",
            "date_of_birth": "1990-12-12",
            "address": "Sofia, Gurko 7",
            "mobile_phone": "+359885001483",
            "pin": "0000"
        }
        self.client.post(self.base_url + 'persons/', data=data, format='json')
        response = self.client.post(self.base_url + 'persons/', data=data, format='json')
        # print(response.status_code)
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_person_with_invalid_phone_should_fail(self):
        data = {
            "user": {
                "username": "new_person",
                "password": "123",
                "email": "person@mail.bg",
                "first_name": "Peter",
                "last_name": "Petrov"
            },
            "personal_identity_number": "987654321",
            "date_of_birth": "1990-12-12",
            "address": "Sofia, Gurko 7",
            "mobile_phone": "+35988500148",
            "pin": "0000"
        }
        response = self.client.post(self.base_url + 'persons/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_accountant_without_personal_identity_number_should_fail(self):
        data = {
            "user": {
                "username": "accountant_invalid",
                "password": "123",
                "email": "accountant@mail.bg",
                "first_name": "Peter",
                "last_name": "Petrov"
            },
            "mobile_phone": "+359885001483"
        }
        response = self.client.post(self.base_url + 'accountants/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_person_should_not_get_all_users(self):
        self.client.login(username=self.person.user.username, password='123')
        response = self.client.get(self.base_url + 'all_users/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_should_not_change_accountants_profile(self):
        self.client.login(username=self.manager.user.username, password='123')
        data = {"mobile_phone": "+359885001484"}
        response = self.client.patch(self.base_url + 'accountants/', data=data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_creates_own_account(self):
        self.client.login(username=self.manager.user.username, password='123')
        data = {"product": 1, "currency": 1}
        before_create = Account.objects.count()
        response = self.client.post(self.base_url + 'accounts/', data=data, format='json')
        after_create = Account.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(before_create + 1, after_create)

    def test_manager_should_delete_own_accounts_only(self):
        self.client.login(username=self.manager.user.username, password='123')
        before_delete = Account.objects.count()
        self.client.delete(self.base_url + 'accounts/1/')
        after_delete = Account.objects.count()
        self.assertEqual(before_delete, after_delete)
