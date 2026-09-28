import pytest
from app.domain.models import User, TokenBalance, Payment, PaymentStatus
from app.domain.errors import PaymentAlreadyProcessedError
from app.services.billing_service import BillingService
from app.services.payment_service import PaymentService
from app.adapters.memory_repositories import MemoryUserRepository, MemoryPaymentRepository
from app.adapters.fake_payment_provider import FakePaymentProvider

@pytest.mark.asyncio
async def test_idempotent_payment_processing():
    user_repo = MemoryUserRepository()
    payment_repo = MemoryPaymentRepository()
    
    user = User(id=1, balance=TokenBalance(package=0))
    await user_repo.save(user)
    
    billing = BillingService(user_repo)
    payment_service = PaymentService(payment_repo, FakePaymentProvider(), billing)
    
    # Первая обработка вебхука
    await payment_service.process_webhook("ext_123", 100, 1)
    
    user_after_1 = await user_repo.get_by_id(1)
    assert user_after_1.balance.package == 100
    
    # Попытка повторной обработки того же external_id
    with pytest.raises(PaymentAlreadyProcessedError):
        await payment_service.process_webhook("ext_123", 100, 1)
    
    # Баланс не должен измениться второй раз
    user_after_2 = await user_repo.get_by_id(1)
    assert user_after_2.balance.package == 100

@pytest.mark.asyncio
async def test_reconciliation():
    user_repo = MemoryUserRepository()
    payment_repo = MemoryPaymentRepository()
    
    user = User(id=1, balance=TokenBalance(package=0))
    await user_repo.save(user)
    
    # Платеж завис в статусе PENDING
    payment = Payment(id="ext_123", external_id="ext_123", user_id=1, amount_tokens=100, status=PaymentStatus.PENDING)
    await payment_repo.save(payment)
    
    billing = BillingService(user_repo)
    # Провайдер подтверждает, что платеж прошел
    payment_service = PaymentService(payment_repo, FakePaymentProvider(should_succeed=True), billing)
    
    await payment_service.reconcile_payment("ext_123")
    
    updated_payment = await payment_repo.get_by_id("ext_123")
    assert updated_payment.status == PaymentStatus.SUCCESS
    
    updated_user = await user_repo.get_by_id(1)
    assert updated_user.balance.package == 100
