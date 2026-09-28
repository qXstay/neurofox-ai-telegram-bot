"""
Пример реализации гибридной системы биллинга.
Демонстрирует логику приоритетного списания токенов:
1. Сначала используются временные (подписочные) токены.
2. Затем используются вечные (пакетные) токены.
"""

import logging
from dataclasses import dataclass
from typing import Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserEntitlements:
    """Модель прав пользователя на использование AI-ресурсов."""
    user_id: int
    subscription_balance: int  # Токены, входящие в тариф (срок действия ограничен)
    package_balance: int       # Купленные токены (без срока действия)

class BillingService:
    """Сервис управления балансами и транзакциями."""
    
    async def get_user_balances(self, user_id: int) -> UserEntitlements:
        """
        Получение актуальных остатков из базы данных.
        В реальности здесь выполняется SQL-запрос к таблице entitlements.
        """
        # Имитация данных из БД
        return UserEntitlements(
            user_id=user_id, 
            subscription_balance=100, 
            package_balance=250
        )

    async def consume_tokens(self, user_id: int, amount: int) -> bool:
        """
        Атомарная операция списания токенов.
        Возвращает True при успешном списании, False — при недостатке средств.
        """
        balances = await self.get_user_balances(user_id)
        total_available = balances.subscription_balance + balances.package_balance
        
        if total_available < amount:
            logger.warning(f"User {user_id}: Insufficient funds. Needed {amount}, has {total_available}")
            return False
            
        # Логика приоритета: сначала тратим то, что может сгореть (подписочные)
        sub_to_deduct = min(balances.subscription_balance, amount)
        pkg_to_deduct = amount - sub_to_deduct
        
        # В продакшн-версии здесь выполняется SQL-транзакция:
        # UPDATE user_balances 
        # SET sub_balance = sub_balance - :sub, pkg_balance = pkg_balance - :pkg 
        # WHERE user_id = :uid AND (sub_balance + pkg_balance) >= :amount
        
        logger.info(
            f"Transaction Successful [User {user_id}]: "
            f"Spent {sub_to_deduct} sub-tokens, {pkg_to_deduct} pkg-tokens. "
            f"Total deducted: {amount}"
        )
        return True

# Пример использования
async def demonstration():
    service = BillingService()
    
    # Сценарий 1: Простая генерация (хватает подписочных токенов)
    logger.info("--- Scenario 1: Basic Generation ---")
    await service.consume_tokens(user_id=777, amount=30)
    
    # Сценарий 2: Тяжелая генерация видео (тратим все подписочные и часть пакетных)
    logger.info("--- Scenario 2: High-cost Video Generation ---")
    await service.consume_tokens(user_id=777, amount=150)

if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstration())
