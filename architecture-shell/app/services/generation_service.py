import logging
from uuid import UUID
from app.domain.models import GenerationTask, GenerationStatus
from app.ports.repositories import TaskRepository
from app.ports.ai_provider import AIProvider
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(
        self, 
        task_repo: TaskRepository, 
        ai_provider: AIProvider,
        billing: BillingService
    ):
        self.task_repo = task_repo
        self.ai_provider = ai_provider
        self.billing = billing

    async def start_generation(self, user_id: int, model_id: str, prompt: str, cost: int) -> GenerationTask:
        # 1. Списание токенов (Hold)
        await self.billing.consume_tokens(user_id, cost)

        # 2. Создание задачи в БД
        task = GenerationTask(user_id=user_id, model_id=model_id, cost=cost)
        await self.task_repo.save(task)

        # 3. Отправка во внешний API
        try:
            external_id = await self.ai_provider.create_task(model_id, {"prompt": prompt})
            task.status = GenerationStatus.PROCESSING
            await self.task_repo.save(task)
        except Exception as e:
            logger.error(f"Failed to start generation: {e}")
            task.status = GenerationStatus.FAILED
            # Возврат токенов при сбое
            await self.billing.add_tokens(user_id, cost, is_subscription=False) 
            await self.task_repo.save(task)
            raise

        return task
