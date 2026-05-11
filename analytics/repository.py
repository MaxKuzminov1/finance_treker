import MySQLdb
from MySQLdb.cursors import DictCursor
from references.config import DB_CONFIG
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from analytics.models import GroupBy


class AnalyticsRepository:
    def __init__(self):
        self.conn = MySQLdb.connect(
            cursorclass=DictCursor,
            autocommit=True,
            **DB_CONFIG
        )

    def _execute(self, query: str, params: tuple = ()) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(query, params)
            return cur.fetchall()
        finally:
            cur.close()

    def get_detailed_stats(self, date_from: date, date_to: date) -> Dict:
        sql = """
            SELECT 
                COUNT(*) as tx_count,
                AVG(total_amount) as avg_check,
                SUM(CASE WHEN type = 'income' THEN total_amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN total_amount ELSE 0 END) as total_expense
            FROM transactions
            WHERE date BETWEEN %s AND %s
        """
        rows = self._execute(sql, (date_from, date_to))
        return rows[0] if rows else {}

    def get_top_category(self, date_from: date, date_to: date, tx_type: str) -> str:
        sql = """
            SELECT c.name, SUM(ti.amount) as total
            FROM transaction_items ti
            JOIN categories c ON ti.category_id = c.id
            JOIN transactions t ON ti.transaction_id = t.id
            WHERE t.date BETWEEN %s AND %s AND t.type = %s
            GROUP BY c.id
            ORDER BY total DESC LIMIT 1
        """
        rows = self._execute(sql, (date_from, date_to, tx_type))
        return rows[0]['name'] if rows else "Нет данных"

    def get_time_series(self, date_from: date, date_to: date, group_by: GroupBy = GroupBy.MONTH) -> List[Dict]:
        # ВНИМАНИЕ: Используем двойной процент %%, чтобы Python не пытался
        # интерпретировать его как форматную строку.
        group_formats = {
            GroupBy.DAY: "%%Y-%%m-%%d",
            GroupBy.WEEK: "%%Y-%%u",
            GroupBy.MONTH: "%%Y-%%m",
            GroupBy.YEAR: "%%Y",
        }
        fmt = group_formats.get(group_by, "%%Y-%%m")

        sql = f"""
            SELECT 
                DATE_FORMAT(date, '{fmt}') as period_label,
                MIN(date) as begin_date,
                SUM(CASE WHEN type = 'income' THEN total_amount ELSE 0 END) as income,
                SUM(CASE WHEN type = 'expense' THEN total_amount ELSE 0 END) as expense
            FROM transactions
            WHERE date BETWEEN %s AND %s
            GROUP BY period_label
            ORDER BY begin_date
        """
        return self._execute(sql, (date_from, date_to))

    def get_historical_data_for_forecast(self, months: int = 12) -> List[Dict]:
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        return self.get_time_series(start_date, end_date, GroupBy.MONTH)

    def get_category_breakdown(self, date_from: date, date_to: date, type_filter: str) -> List[Dict]:
        sql = """
            SELECT c.name as category_name, SUM(ti.amount) as amount
            FROM transaction_items ti
            JOIN categories c ON ti.category_id = c.id
            JOIN transactions t ON ti.transaction_id = t.id
            WHERE t.date BETWEEN %s AND %s AND t.type = %s
            GROUP BY c.id
            ORDER BY amount DESC
        """
        return self._execute(sql, (date_from, date_to, type_filter))

    def get_budget_comparison(self, date_from: date, date_to: date) -> List[Dict]:
        sql = """
            SELECT
                c.name AS category_name,
                COALESCE(b.planned_amount, 0) AS planned,
                COALESCE(SUM(ti.amount), 0) AS actual
            FROM categories c
            LEFT JOIN budgets b ON c.id = b.category_id
                AND b.period_start <= %s AND b.period_end >= %s
            LEFT JOIN transaction_items ti ON c.id = ti.category_id
            LEFT JOIN transactions t ON ti.transaction_id = t.id AND t.date BETWEEN %s AND %s
            GROUP BY c.id, c.name, b.planned_amount
            HAVING planned > 0 OR actual > 0
            ORDER BY c.name
        """
        return self._execute(sql, (date_to, date_from, date_from, date_to))