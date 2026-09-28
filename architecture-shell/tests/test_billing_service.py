import pytest
from app.domain.models import User, TokenBalance
from app.domain.errors import InsufficientTokensError
from app.services.billing_service import BillingService
from app.adapters.memory_repositories import MemoryUserRepository

@pytest.mark.asyncio
async def test_consume_priority():
    repo = MemoryUserRepository()
    user = User(id=1, balance=TokenBalance(subscription=100, package=100))
    await repo.save(user)
    
    service = BillingService(repo)
    
    # Списание 120 токенов: 100 из подписки, 20 из пакета
    await service.consume_tokens(1, 120)
    
    updated_user = await repo.get_by_id(1)
    assert updated_user.balance.subscription == 0
    assert updated_user.balance.package == 80

@pytest.mark.asyncio
async def test_insufficient_tokens():
    repo = MemoryUserRepository()
    user = User(id=1, balance=TokenBalance(subscription=10, package=10))
    await repo.save(user)
    
    service = BillingService(repo)
    
    with pytest.raises(InsufficientTokensError):
        await service.consume_tokens(1, 30)
