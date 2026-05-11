from typing import List, Optional, Dict
from datetime import date
from analytics.repository import AnalyticsRepository
from analytics.service import AnalyticsService
from analytics.models import (
    KPIData, TimeSeriesPoint, CategoryShare, PeriodComparison,
    ReportRow, GroupBy, AnalyticsTrend
)

class AnalyticsController:
    def __init__(self):
        self.repo = AnalyticsRepository()
        self.service = AnalyticsService(self.repo)

    def get_kpi(self, date_from: date, date_to: date) -> KPIData:
        """Возвращает расширенный набор ключевых показателей."""
        return self.service.calculate_kpi(date_from, date_to)

    def get_trends(self) -> AnalyticsTrend:
        """Возвращает прогноз и анализ аномалий."""
        return self.service.get_trends_and_forecast()

    def get_time_series(self, date_from: date, date_to: date,
                        group_by: GroupBy = GroupBy.MONTH) -> List[TimeSeriesPoint]:
        """Возвращает данные для линейных графиков."""
        # Используем метод репозитория напрямую или через сервис
        rows = self.repo.get_time_series(date_from, date_to, group_by)
        points = []
        for r in rows:
            points.append(TimeSeriesPoint(
                period_label=r['period_label'],
                begin_date=r['begin_date'],
                income=float(r['income']),
                expense=float(r['expense']),
                profit=float(r['income']) - float(r['expense'])
            ))
        return points

    def get_category_shares(self, date_from: date, date_to: date,
                            type_filter: str = 'expense') -> List[CategoryShare]:
        """Данные для круговой диаграммы (расходы или доходы)."""
        return self.service.get_category_shares(date_from, date_to, type_filter)

    def compare_periods(self, current_start: date, current_end: date,
                        previous_start: date, previous_end: date) -> PeriodComparison:
        """Сравнение двух произвольных периодов."""
        return self.service.compare_periods(current_start, current_end,
                                            previous_start, previous_end)

    def build_report(self, date_from: date, date_to: date) -> List[ReportRow]:
        """Данные для сводной таблицы отчета."""
        return self.service.build_report_data(date_from, date_to)

    def get_budget_comparison(self, date_from: date, date_to: date) -> List[dict]:
        """Сравнение плана и факта."""
        return self.service.get_budget_vs_actual(date_from, date_to)