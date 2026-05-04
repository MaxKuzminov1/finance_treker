
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"

@dataclass
class Category:
    id: Optional[int] = None
    name: str = ""
    type: CategoryType = CategoryType.EXPENSE
    parent_id: Optional[int] = None
    children: List['Category'] = field(default_factory=list)

@dataclass
class Counterparty:
    id: Optional[int] = None
    name: str = ""
    type: str = ""
    contact_info: str = ""
    address: str = ""
    requisites: str = ""
    comment: str = ""

@dataclass
class User:
    id: Optional[int] = None
    login: str = ""
    password_hash: str = ""
    role_id: int = 0
    status: UserStatus = UserStatus.ACTIVE
    role_name: str = ""  # для отображения

@dataclass
class Role:
    id: int
    name: str

@dataclass
class AppSettings:
    theme: str = "light"
    date_format: str = "dd.MM.yyyy"
    auto_refresh: bool = False
    recurring_enabled: bool = False
    logging_enabled: bool = True