import logging
from app.domain.models import User
from app.domain.errors import InsufficientTokensError
from app.ports.repositories import UserRepository

logger = logging.getLogger(__name__)

class BillingService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def consume_tokens(self, user_id: int, amount: int) -> None:
        """
        Consumes tokens with priority:
        1. Subscription tokens (expire)
        2. Package tokens (eternal)
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if user.balance.total < amount:
            raise InsufficientTokensError(amount, user.balance.total)

        sub_spent = min(user.balance.subscription, amount)
        pkg_spent = amount - sub_spent

        user.balance.subscription -= sub_spent
        user.balance.package -= pkg_spent

        await self.user_repo.save(user)
        logger.info(f"User {user_id} spent {amount} tokens (Sub: {sub_spent}, Pkg: {pkg_spent})")

    async def add_tokens(self, user_id: int, amount: int, is_subscription: bool = False) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            user = User(id=user_id)

        if is_subscription:
            user.balance.subscription += amount
        else:
            user.balance.package += amount

        await self.user_repo.save(user)
        logger.info(f"Added {amount} {'subscription' if is_subscription else 'package'} tokens to user {user_id}")
