from enum import Enum


class TransferStatusEnum(Enum):
    I = "Initiated"
    A = "Approved"
    R = "Rejected"
    P = "Processed"
    E = "Processed with error"


class PaymentSystemEnum(Enum):
    B = "BISERA"
    T = "TARGET2"
    S = "SWIFT"
    E = "SEPA"
