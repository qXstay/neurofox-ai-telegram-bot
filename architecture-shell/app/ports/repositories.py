from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.domain.models import User, GenerationTask, Payment

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]: pass
    
    @abstractmethod
    async def save(self, user: User) -> None: pass

class TaskRepository(ABC):
    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[GenerationTask]: pass
    
    @abstractmethod
    async def save(self, task: GenerationTask) -> None: pass

class PaymentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, payment_id: str) -> Optional[Payment]: pass
    
    @abstractmethod
    async def get_by_external_id(self, external_id: str) -> Optional[Payment]: pass
    
    @abstractmethod
    async def save(self, payment: Payment) -> None: pass

class AIProvider(ABC):
    @abstractmethod
    async def create_task(self, model_id: str, params: dict) -> str: pass
    
    @abstractmethod
    async def get_status(self, external_task_id: str) -> dict: pass

class PaymentProvider(ABC):
    @abstractmethod
    async def verify_payment(self, external_id: str) -> bool: pass
