from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

class TokenType(Enum):
    SUBSCRIPTION = "subscription"
    PACKAGE = "package"

@dataclass
class TokenBalance:
    subscription: int = 0
    package: int = 0

    @property
    def total(self) -> int:
        return self.subscription + self.package

@dataclass
class User:
    id: int
    balance: TokenBalance = field(default_factory=TokenBalance)
    referred_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

class GenerationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class GenerationTask:
    id: UUID = field(default_factory=uuid4)
    user_id: int = 0
    model_id: str = ""
    status: GenerationStatus = GenerationStatus.PENDING
    result_url: Optional[str] = None
    cost: int = 0

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class Payment:
    id: str
    user_id: int
    amount_tokens: int
    status: PaymentStatus = PaymentStatus.PENDING
    external_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
