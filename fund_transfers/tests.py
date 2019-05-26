from registrations.tests import *


class BaseFundTransfersTestCase(BaseRegistrationsTestCase):

    def setUp(self):
        BaseRegistrationsTestCase.setUp(self)
        self.base_url = 'http://127.0.0.1:8000/api/v1/fund_transfers/'


class FundTransfersTestCase(BaseFundTransfersTestCase):

    def test_create_fund_transfer_without_account_should_(self):
        self.client.login(username=self.manager.user.username, password='123')
        data = {
            "iban_beneficiary": "BG79DJNG828042BGN00014",
            "bic_beneficiary": "",
            "bank_beneficiary": "",
            "name_beneficiary": "Our company",
            "details": "Test fund transfer",
            "amount": "250",
            "currency": {
                "code": "BGN"
            },
            "account": {
                "iban": "BG97DJNG828020USD00015"
            },
            "payment_system": "I"
        }
        response = self.client.post(self.base_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
