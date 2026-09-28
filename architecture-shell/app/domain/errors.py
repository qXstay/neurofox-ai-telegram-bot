class DomainError(Exception):
    """Base domain error"""

class InsufficientTokensError(DomainError):
    def __init__(self, required: int, available: int):
        super().__init__(f"Insufficient tokens: required {required}, available {available}")

class TaskNotFoundError(DomainError):
    pass

class PaymentAlreadyProcessedError(DomainError):
    pass
