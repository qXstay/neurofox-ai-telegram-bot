"""
Пример асинхронного управления жизненным циклом AI-задачи.
Демонстрирует паттерн "Polling" с обработкой состояний и возвратом ресурсов.
"""

import asyncio
import uuid
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AIServiceProvider:
    """Имитация клиента внешнего AI API."""
    
    async def submit_generation_task(self, model_id: str, prompt: str) -> str:
        """
        Отправляет запрос на генерацию.
        Возвращает уникальный идентификатор задачи (Task ID).
        """
        logger.info(f"API [Request]: Model={model_id}, Prompt='{prompt}'")
        # Имитация сетевой задержки
        await asyncio.sleep(1)
        return f"task_{uuid.uuid4().hex[:8]}"

    async def get_task_status(self, task_id: str) -> dict:
        """
        Запрашивает текущий статус задачи.
        В реальности возвращает JSON с полями status, result_url, error и т.д.
        """
        # Для демонстрации имитируем прогресс
        return {
            "task_id": task_id,
            "status": "completed", 
            "result_url": "https://storage.neurofox.art/v/8f2k9l.mp4"
        }

async def execute_generation_workflow(user_id: int, prompt: str):
    """
    Основной бизнес-процесс генерации контента.
    """
    ai_api = AIServiceProvider()
    
    # 1. Постановка в очередь
    logger.info(f"User {user_id}: Initiating video generation...")
    task_id = await ai_api.submit_generation_task(model_id="sora-v2", prompt=prompt)
    
    # 2. Ожидание результата (Polling Loop)
    max_retries = 12  # Максимум 1 минута (12 * 5 сек)
    for attempt in range(1, max_retries + 1):
        logger.info(f"Task {task_id}: Polling status (Attempt {attempt})...")
        await asyncio.sleep(5)
        
        result = await ai_api.get_task_status(task_id)
        status = result.get("status")
        
        if status == "completed":
            logger.info(f"Task {task_id} SUCCESS: {result['result_url']}")
            return result['result_url']
            
        if status == "failed":
            logger.error(f"Task {task_id} FAILED: {result.get('error_msg', 'Unknown error')}")
            # Здесь вызывается логика возврата (refund) токенов пользователю
            return None
            
    logger.warning(f"Task {task_id}: Timeout reached. Task is still in progress.")
    return None

if __name__ == "__main__":
    asyncio.run(execute_generation_workflow(user_id=42, prompt="Neon fox in a futuristic city, cinematic style"))
