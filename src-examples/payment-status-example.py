"""
Пример обработки платежных вебхуков и асинхронного зачисления токенов.
Демонстрирует интеграцию с платежными шлюзами (YooKassa/Prodamus/Stars).
"""

import logging
import hmac
import hashlib
from enum import Enum
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"

class PaymentProcessor:
    """Сервис обработки входящих уведомлений об оплате."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Проверка подлинности уведомления от платежной системы.
        Исключает возможность имитации оплаты злоумышленниками.
        """
        expected_sig = hmac.new(
            self.secret_key.encode(), 
            payload.encode(), 
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Запрос статуса у эквайера (YooKassa/Prodamus)"""
        # Имитация вызова API
        return PaymentStatus.SUCCEEDED

    async def finalize_order(self, order_id: str, amount_paid: float, user_id: int):
        """
        Зачисление ресурсов пользователю после подтверждения оплаты.
        """
        logger.info(f"Payment Verified [Order {order_id}]: User {user_id} paid {amount_paid} RUB")
        
        # 1. Запись транзакции в базу данных
        # 2. Начисление токенов (биллинг-сервис)
        # 3. Отправка уведомления пользователю в Telegram
        
        logger.info(f"Tokens Credited [Order {order_id}]: User {user_id} received his assets.")

async def handle_incoming_webhook(request_body: Dict[str, Any], headers: Dict[str, str]):
    """
    Эндпоинт (обработчик), вызываемый платежной системой.
    """
    payment_service = PaymentProcessor(secret_key="demo-payment-signing-key")
    
    # В реальности данные берутся из HTTP-запроса
    order_id = request_body.get("order_id")
    user_id = request_body.get("user_id")
    amount = request_body.get("amount")
    
    # Проверка подписи (Sanitization)
    is_valid = payment_service.verify_webhook_signature(
        str(request_body), 
        headers.get("X-Payment-Signature", "")
    )
    
    if not is_valid:
        logger.error(f"Security Alert: Invalid webhook signature for order {order_id}")
        return {"status": "error", "message": "Invalid signature"}

    # Завершение заказа
    await payment_service.finalize_order(order_id, amount, user_id)
    return {"status": "ok"}

async def reconcile_pending_payments():
    """Фоновая задача для проверки 'зависших' платежей"""
    processor = PaymentProcessor(secret_key="demo-payment-signing-key")
    
    # Имитация получения списка платежей со статусом 'pending' из БД
    pending_orders = [
        {"id": "pay_001", "external_id": "yookassa_id_1"},
        {"id": "pay_002", "external_id": "yookassa_id_2"},
    ]
    
    for order in pending_orders:
        status = await processor.get_payment_status(order["external_id"])
        
        if status == PaymentStatus.SUCCEEDED:
            await processor.finalize_order(order["id"], 0.0, 0)
        elif status == PaymentStatus.CANCELED:
            print(f"Order {order['id']} was canceled by user.")

# Пример использования в Webhook-хендлере
async def on_payment_webhook(payload: dict):
    """Вызывается при получении уведомления от платежной системы"""
    payment_id = payload.get("object", {}).get("id")
    event = payload.get("event")
    
    if event == "payment.succeeded":
        processor = PaymentProcessor()
        # В реальности здесь поиск заказа по payment_id
        await processor.finalize_order("local_order_id")
