from typing import List, Optional
from datetime import date
from analytics.models import (
    KPIData, TimeSeriesPoint, CategoryShare, PeriodComparison, ReportRow, GroupBy
)
from analytics.repository import AnalyticsRepository

class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def calculate_kpi(self, date_from: date, date_to: date) -> KPIData:
        income = self.repo.get_total_amount(date_from, date_to, 'income')
        expense = self.repo.get_total_amount(date_from, date_to, 'expense')
        profit = income - expense
        profitability = (profit / income * 100) if income != 0 else 0.0
        return KPIData(
            total_income=income,
            total_expense=expense,
            profit=profit,
            profitability=profitability
        )

    def build_time_series(self, date_from: date, date_to: date,
                          group_by: GroupBy = GroupBy.MONTH) -> List[TimeSeriesPoint]:
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
        rows = self.repo.get_category_breakdown(date_from, date_to, type_filter)
        total = sum(float(r['amount']) for r in rows)
        shares = []
        for r in rows:
            amt = float(r['amount'])
            shares.append(CategoryShare(
                category_name=r['category_name'],
                amount=amt,
                percentage=(amt / total * 100) if total != 0 else 0.0
            ))
        return shares

    def compare_periods(self, current_start: date, current_end: date,
                        previous_start: date, previous_end: date) -> PeriodComparison:
        curr_kpi = self.calculate_kpi(current_start, current_end)
        prev_kpi = self.calculate_kpi(previous_start, previous_end)

        def pct_change(cur, prev):
            if prev != 0:
                return (cur - prev) / abs(prev) * 100
            return 0.0 if cur == 0 else 100.0

        return PeriodComparison(
            current_period_label=f"{current_start} – {current_end}",
            previous_period_label=f"{previous_start} – {previous_end}",
            income_change=curr_kpi.total_income - prev_kpi.total_income,
            expense_change=curr_kpi.total_expense - prev_kpi.total_expense,
            profit_change=curr_kpi.profit - prev_kpi.profit,
            income_change_pct=pct_change(curr_kpi.total_income, prev_kpi.total_income),
            expense_change_pct=pct_change(curr_kpi.total_expense, prev_kpi.total_expense),
            profit_change_pct=pct_change(curr_kpi.profit, prev_kpi.profit)
        )

    def build_report(self, date_from: date, date_to: date,
                     group_by: GroupBy = GroupBy.MONTH) -> List[ReportRow]:
        points = self.build_time_series(date_from, date_to, group_by)
        rows = []
        for i, pt in enumerate(points):
            prev_profit = points[i-1].profit if i > 0 else None
            if prev_profit is not None and prev_profit != 0:
                change = (pt.profit - prev_profit) / abs(prev_profit) * 100
            else:
                change = None
            rows.append(ReportRow(
                period_label=pt.period_label,
                income=pt.income,
                expense=pt.expense,
                profit=pt.profit,
                change_pct=round(change, 2) if change is not None else None
            ))
        return rows

    def get_budget_vs_actual(self, date_from: date, date_to: date) -> List[dict]:
        return self.repo.get_budget_comparison(date_from, date_to)