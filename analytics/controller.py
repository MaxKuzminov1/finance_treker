from typing import List, Optional
from datetime import date
from analytics.repository import AnalyticsRepository
from analytics.service import AnalyticsService
from analytics.models import (
    KPIData, TimeSeriesPoint, CategoryShare, PeriodComparison, ReportRow, GroupBy
)

class AnalyticsController:
    def __init__(self):
        self.repo = AnalyticsRepository()
        self.service = AnalyticsService(self.repo)

    # Показатели KPI
    def get_kpi(self, date_from: date, date_to: date) -> KPIData:
        return self.service.calculate_kpi(date_from, date_to)

    # Временной ряд
    def get_time_series(self, date_from: date, date_to: date,
                        group_by: GroupBy = GroupBy.MONTH) -> List[TimeSeriesPoint]:
        return self.service.build_time_series(date_from, date_to, group_by)

    # Доли категорий (для круговой диаграммы)
    def get_category_shares(self, date_from: date, date_to: date,
                            type_filter: str = 'expense') -> List[CategoryShare]:
        return self.service.get_category_shares(date_from, date_to, type_filter)

    # Сравнение периодов
    def compare_periods(self, current_start: date, current_end: date,
                        previous_start: date, previous_end: date) -> PeriodComparison:
        return self.service.compare_periods(current_start, current_end,
                                            previous_start, previous_end)

    # Отчёт (таблица)
    def build_report(self, date_from: date, date_to: date) -> List[ReportRow]:
        return self.service.build_report(date_from, date_to)

    # Бюджет: план/факт
    def get_budget_comparison(self, date_from: date, date_to: date) -> List[dict]:
        return self.service.get_budget_vs_actual(date_from, date_to)

    # Экспорт данных (возвращает подготовленные структуры; реальный экспорт в UI)
    def export_data(self, date_from: date, date_to: date, fmt: str):
        # Можно вернуть словарь с отчётами для последующего сохранения
        pass