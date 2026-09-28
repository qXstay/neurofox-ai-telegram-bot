from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def create_task(self, model_id: str, params: dict) -> str: pass
    
    @abstractmethod
    async def get_status(self, external_task_id: str) -> dict: pass
