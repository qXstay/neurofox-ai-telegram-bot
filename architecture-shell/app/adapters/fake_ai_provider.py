from app.ports.ai_provider import AIProvider

class FakeAIProvider(AIProvider):
    async def create_task(self, model_id: str, params: dict) -> str:
        return "external_task_123"

    async def get_status(self, external_task_id: str) -> dict:
        return {"status": "completed", "url": "https://example.com/result.mp4"}
