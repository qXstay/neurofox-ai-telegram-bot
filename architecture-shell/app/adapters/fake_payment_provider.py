from app.ports.payment_provider import PaymentProvider

class FakePaymentProvider(PaymentProvider):
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed

    async def verify_payment(self, external_id: str) -> bool:
        return self.should_succeed
