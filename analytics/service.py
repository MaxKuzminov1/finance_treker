import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import date, timedelta
from analytics.models import (
    KPIData, TimeSeriesPoint, CategoryShare, ReportRow, GroupBy, AnalyticsTrend, PeriodComparison
)


class AnalyticsService:
    def __init__(self, repo):
        self.repo = repo

    def calculate_kpi(self, date_from: date, date_to: date) -> KPIData:
        stats = self.repo.get_detailed_stats(date_from, date_to)
        days = max((date_to - date_from).days, 1)

        income = float(stats.get('total_income') or 0)
        expense = float(stats.get('total_expense') or 0)
        profit = income - expense

        return KPIData(
            total_income=income,
            total_expense=expense,
            profit=profit,
            profitability=(profit / income * 100) if income > 0 else 0,
            avg_income_day=income / days,
            avg_expense_day=expense / days,
            savings_rate=((income - expense) / income * 100) if income > 0 else 0,
            avg_check=float(stats.get('avg_check') or 0),
            transaction_count=int(stats.get('tx_count') or 0),
            top_expense_category=self.repo.get_top_category(date_from, date_to, 'expense'),
            top_income_source=self.repo.get_top_category(date_from, date_to, 'income'),
            financial_stability_ratio=(income / expense) if expense > 0 else 0
        )

    def get_trends_and_forecast(self) -> AnalyticsTrend:
        data = self.repo.get_historical_data_for_forecast(6)
        if len(data) < 2:
            return AnalyticsTrend(0, 'stable')

        df = pd.DataFrame(data)
        df['expense'] = df['expense'].astype(float)

        y = df['expense'].values
        x = np.arange(len(y))
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)

        forecast = p(len(y))
        direction = 'up' if z[0] > 0.05 else 'down' if z[0] < -0.05 else 'stable'

        mean_exp = df['expense'].mean()
        std_exp = df['expense'].std() or 1
        anomalies = df[abs(df['expense'] - mean_exp) > (2 * std_exp)].to_dict('records')

        return AnalyticsTrend(forecast_next_period=float(max(0, forecast)),
                              trend_direction=direction,
                              anomalies=anomalies)

    def get_category_shares(self, date_from: date, date_to: date, type_filter: str) -> List[CategoryShare]:
        rows = self.repo.get_category_breakdown(date_from, date_to, type_filter)
        total = sum(float(r['amount']) for r in rows)
        return [CategoryShare(
            category_name=r['category_name'],
            amount=float(r['amount']),
            percentage=(float(r['amount']) / total * 100) if total > 0 else 0
        ) for r in rows]

    def build_report_data(self, date_from: date, date_to: date) -> List[ReportRow]:
        points = self.repo.get_time_series(date_from, date_to, GroupBy.MONTH)
        report = []
        for i, p in enumerate(points):
            inc, exp = float(p['income']), float(p['expense'])
            prof = inc - exp
            change = None
            if i > 0:
                prev_prof = float(points[i - 1]['income']) - float(points[i - 1]['expense'])
                if prev_prof != 0:
                    change = (prof - prev_prof) / abs(prev_prof) * 100
            report.append(ReportRow(p['period_label'], inc, exp, prof, change))
        return report

    def compare_periods(self, current_start: date, current_end: date,
                        previous_start: date, previous_end: date) -> PeriodComparison:
        curr = self.calculate_kpi(current_start, current_end)
        prev = self.calculate_kpi(previous_start, previous_end)

        def get_pct(c, p):
            if p == 0: return 100.0 if c > 0 else 0.0
            return (c - p) / abs(p) * 100

        return PeriodComparison(
            current_period_label=f"{current_start} - {current_end}",
            previous_period_label=f"{previous_start} - {previous_end}",
            income_change=curr.total_income - prev.total_income,
            expense_change=curr.total_expense - prev.total_expense,
            profit_change=curr.profit - prev.profit,
            income_change_pct=get_pct(curr.total_income, prev.total_income),
            expense_change_pct=get_pct(curr.total_expense, prev.total_expense),
            profit_change_pct=get_pct(curr.profit, prev.profit)
        )

    def get_budget_vs_actual(self, date_from: date, date_to: date) -> List[dict]:
        return self.repo.get_budget_comparison(date_from, date_to)