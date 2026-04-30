from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class CategorySplit:
    category: str
    amount: float


@dataclass
class Payment:
    payment_date: date
    amount: float


@dataclass
class Attachment:
    file_path: str


@dataclass
class Transaction:
    id: int
    date: date
    type: str  # "income" or "expense"
    amount: float
    counterparty: str
    comment: str = ""

    categories: List[CategorySplit] = field(default_factory=list)
    payments: List[Payment] = field(default_factory=list)
    attachments: List[Attachment] = field(default_factory=list)

    is_deleted: bool = False

    def paid_amount(self):
        return sum(p.amount for p in self.payments)

    def status(self):
        if self.paid_amount() >= self.amount:
            return "Оплачено"
        elif self.paid_amount() > 0:
            return "Частично"
        return "Создана"