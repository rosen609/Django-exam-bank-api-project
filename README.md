# Django-exam-bank-api-project
My exam Django REST project. API for basic online bank operations

## Urls:

#### Registrations (api/v1/registrations/)

###### auth/login/ (non-authenticated)
###### persons/ (post - non-authenticated / admin)
###### persons/{pk}/ (admin)
###### accountants/ (post - non-authenticated / admin)
###### accountants/{pk}/ (admin)
###### managers/ (post - non-authenticated / admin)
###### managers/{pk}/ (admin)
###### all_users/ (admin)
###### info/ (non-authenticated)
###### account_products/ 
###### account_products/{pk}/
###### currencies/
###### currencies/{pk}/
###### customers/
###### customers/{pk}/
###### accounts/
###### accounts/{pk}/
###### accounts/{pk}/user/{pk}/

#### Fund Transfers (api/v1/fund_transfers/)

###### /
###### {pk}/
###### statement/

#### Notifications (api/v1/notifications/)
###### send_otp/{transfer_pk}/

## Business Requirements:
###### Our team received a request to create an online API for the newly created Django Bank. The system will expose bank functionality to the external users and will give bank customers better experience with Django bank.
###### The requirements are:
####	Models:
###### o	Customer
###### o	User extensions:
###### 	Person (personal profile)
###### 	Accountant (company profile) – only initiates transfers
###### 	Manager (company profile) – approves or rejects transfers; manager can create accounts
###### o	IBAN Account
###### o	Bank account product – current accounts, deposits, saving accounts, special accounts of mixed type
###### o	Fund Transfer (should have generated OTP and OTP received from user)
###### 	When FT is initiated, a SMS with OTP is sent to the 
###### o	Currencies
#### 	Apps:
###### o	Registrations
###### o	Transfers
###### o	Notifications – SMS (Mail to be added)
###### 	SMS for OTP
###### 	SMS per signed fund transfer
#### 	Other requirements:
###### o	Amount Limits per transfer for managers
###### o	Account balance will be validated when transfer is approved and the amount of transfer will be subtracted, and added, only if credit account is internal for Django bank
###### o	Manager Limit should also be validated, because it must not be exceeded
###### o	When account is created balance will be random 0 -76000 
###### o	Reports :
###### 	Transfers by account, by period, by user
###### 	Account statement – debit and credit operations by account and period
###### o	When adding user to account should check permissions: isSameCustomer (user and acc must be with one and the same customer);  isManagerOrAdmin
