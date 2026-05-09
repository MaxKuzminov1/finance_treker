from dataclasses import dataclass
from typing import List, Optional
from datetime import date
from enum import Enum

class GroupBy(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class KPIData:
    total_income: float = 0.0
    total_expense: float = 0.0
    profit: float = 0.0
    profitability: float = 0.0  # в процентах

@dataclass
class TimeSeriesPoint:
    period_label: str          # например "2025-05"
    begin_date: date
    income: float = 0.0
    expense: float = 0.0
    profit: float = 0.0

@dataclass
class CategoryShare:
    category_name: str
    amount: float
    percentage: float = 0.0

@dataclass
class PeriodComparison:
    current_period_label: str
    previous_period_label: str
    income_change: float       # абсолютное изменение
    expense_change: float
    profit_change: float
    income_change_pct: float   # процентное изменение
    expense_change_pct: float
    profit_change_pct: float

@dataclass
class ReportRow:
    period_label: str
    income: float
    expense: float
    profit: float
    change_pct: Optional[float] = None  # изменение прибыли к предыдущему периоду