import pytest
from app.domain.models import User, TokenBalance, GenerationStatus
from app.services.billing_service import BillingService
from app.services.generation_service import GenerationService
from app.adapters.memory_repositories import MemoryUserRepository, MemoryTaskRepository
from app.adapters.fake_ai_provider import FakeAIProvider

@pytest.mark.asyncio
async def test_successful_generation_flow():
    user_repo = MemoryUserRepository()
    task_repo = MemoryTaskRepository()
    ai_provider = FakeAIProvider()
    
    user = User(id=1, balance=TokenBalance(package=100))
    await user_repo.save(user)
    
    billing = BillingService(user_repo)
    gen_service = GenerationService(task_repo, ai_provider, billing)
    
    task = await gen_service.start_generation(1, "sora-v2", "Cyberpunk cat", cost=50)
    
    assert task.status == GenerationStatus.PROCESSING
    
    updated_user = await user_repo.get_by_id(1)
    assert updated_user.balance.package == 50
    
    saved_task = await task_repo.get_by_id(task.id)
    assert saved_task is not None
