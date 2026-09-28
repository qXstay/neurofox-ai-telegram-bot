from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    @abstractmethod
    async def verify_payment(self, external_id: str) -> bool: pass
