from dataclasses import dataclass, field
from typing import List, Optional, Dict
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
    profitability: float = 0.0
    avg_income_day: float = 0.0
    avg_expense_day: float = 0.0
    savings_rate: float = 0.0
    avg_check: float = 0.0
    transaction_count: int = 0
    top_expense_category: str = "Н/Д"
    top_income_source: str = "Н/Д"
    financial_stability_ratio: float = 0.0

@dataclass
class AnalyticsTrend:
    forecast_next_period: float
    trend_direction: str  # 'up', 'down', 'stable'
    anomalies: List[Dict] = field(default_factory=list)

@dataclass
class TimeSeriesPoint:
    period_label: str
    begin_date: date
    income: float = 0.0
    expense: float = 0.0
    profit: float = 0.0
    balance_running_total: float = 0.0

@dataclass
class CategoryShare:
    category_name: str
    amount: float
    percentage: float = 0.0

@dataclass
class PeriodComparison:
    current_period_label: str
    previous_period_label: str
    income_change: float
    expense_change: float
    profit_change: float
    income_change_pct: float
    expense_change_pct: float
    profit_change_pct: float

@dataclass
class ReportRow:
    period_label: str
    income: float
    expense: float
    profit: float
    change_pct: Optional[float] = None