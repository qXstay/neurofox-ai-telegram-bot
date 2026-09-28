import logging
from app.domain.models import Payment, PaymentStatus
from app.domain.errors import PaymentAlreadyProcessedError
from app.ports.repositories import PaymentRepository
from app.ports.payment_provider import PaymentProvider
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(
        self, 
        payment_repo: PaymentRepository, 
        payment_provider: PaymentProvider,
        billing: BillingService
    ):
        self.payment_repo = payment_repo
        self.payment_provider = payment_provider
        self.billing = billing

    async def process_webhook(self, external_id: str, amount_tokens: int, user_id: int):
        # 1. Проверка на дубликаты
        existing = await self.payment_repo.get_by_external_id(external_id)
        if existing and existing.status == PaymentStatus.SUCCESS:
            raise PaymentAlreadyProcessedError(f"Payment {external_id} already processed")

        # 2. Сохранение/Обновление статуса
        payment = existing or Payment(id=external_id, user_id=user_id, amount_tokens=amount_tokens, external_id=external_id)
        payment.status = PaymentStatus.SUCCESS
        await self.payment_repo.save(payment)

        # 3. Начисление токенов
        await self.billing.add_tokens(user_id, amount_tokens, is_subscription=False)
        logger.info(f"Payment {external_id} processed for user {user_id}")

    async def reconcile_payment(self, payment_id: str):
        """Проверка статуса зависшего платежа"""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment or payment.status == PaymentStatus.SUCCESS:
            return

        is_success = await self.payment_provider.verify_payment(payment.external_id)
        if is_success:
            await self.process_webhook(payment.external_id, payment.amount_tokens, payment.user_id)
