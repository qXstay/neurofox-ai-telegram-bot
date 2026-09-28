from typing import Optional, Dict
from uuid import UUID
from app.domain.models import User, GenerationTask, Payment
from app.ports.repositories import UserRepository, TaskRepository, PaymentRepository

class MemoryUserRepository(UserRepository):
    def __init__(self):
        self.users: Dict[int, User] = {}

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    async def save(self, user: User) -> None:
        self.users[user.id] = user

class MemoryTaskRepository(TaskRepository):
    def __init__(self):
        self.tasks: Dict[UUID, GenerationTask] = {}

    async def get_by_id(self, task_id: UUID) -> Optional[GenerationTask]:
        return self.tasks.get(task_id)

    async def save(self, task: GenerationTask) -> None:
        self.tasks[task.id] = task

class MemoryPaymentRepository(PaymentRepository):
    def __init__(self):
        self.payments: Dict[str, Payment] = {}

    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        return self.payments.get(payment_id)

    async def get_by_external_id(self, external_id: str) -> Optional[Payment]:
        for p in self.payments.values():
            if p.external_id == external_id:
                return p
        return None

    async def save(self, payment: Payment) -> None:
        self.payments[payment.id] = payment
