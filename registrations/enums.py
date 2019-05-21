from enum import Enum


class CustomerTypeEnum(Enum):
    P = "Person"
    C = "Company"


class AccountProductTypeEnum(Enum):
    D = "Deposit"
    C = "Current account"
    S = "Saving account"


class AccountStatusEnum(Enum):
    A = "Active"
    C = "Closed"

