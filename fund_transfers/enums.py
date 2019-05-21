from enum import Enum


class TransferStatusEnum(Enum):
    I = "Initiated"
    A = "Approved"
    R = "Rejected"
    P = "Processed"
    E = "Processed with error"
