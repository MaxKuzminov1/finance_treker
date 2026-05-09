import MySQLdb
from MySQLdb.cursors import DictCursor
from references.config import DB_CONFIG
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from analytics.models import GroupBy

class AnalyticsRepository:
    def __init__(self):
        self.conn = MySQLdb.connect(
            cursorclass=DictCursor,
            autocommit=True,
            **DB_CONFIG
        )

    # --- внутренние хелперы ---

    def _execute(self, query: str, params: tuple = ()) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(query, params)
            return cur.fetchall()
        finally:
            cur.close()

    # --- доходы / расходы / прибыль ---

    def get_total_amount(self, date_from: Optional[date] = None,
                         date_to: Optional[date] = None,
                         type_filter: Optional[str] = None,
                         category_ids: Optional[List[int]] = None) -> float:
        """type_filter: 'income' / 'expense' / None (все)"""
        params = []
        where = []

        if date_from:
            where.append("t.date >= %s")
            params.append(date_from)
        if date_to:
            where.append("t.date <= %s")
            params.append(date_to)
        if type_filter:
            where.append("t.type = %s")
            params.append(type_filter)

        cat_join = ""
        if category_ids:
            cat_join = "JOIN transaction_items ti ON t.id = ti.transaction_id"
            where.append("ti.category_id IN (%s)" % ",".join(["%s"] * len(category_ids)))
            params.extend(category_ids)

        where_clause = "WHERE " + " AND ".join(where) if where else ""
        sql = f"""
            SELECT COALESCE(SUM(t.total_amount), 0) as total
            FROM transactions t
            {cat_join}
            {where_clause}
        """
        rows = self._execute(sql, tuple(params))
        return float(rows[0]['total']) if rows else 0.0

    def get_time_series(self, date_from: date, date_to: date,
                        group_by: GroupBy = GroupBy.MONTH) -> List[Dict]:
        """Возвращает строки с period_label, income, expense"""
        group_formats = {
            GroupBy.DAY: "%%Y-%%m-%%d",
            GroupBy.WEEK: "%%Y-%%u",  # год-неделя
            GroupBy.MONTH: "%%Y-%%m",
            GroupBy.YEAR: "%%Y",
        }

        if group_by == GroupBy.QUARTER:
            group_expr = "CONCAT(YEAR(t.date), '-Q', QUARTER(t.date))"
        else:
            fmt = group_formats[group_by]
            group_expr = f"DATE_FORMAT(t.date, '{fmt}')"

        sql = f"""
            SELECT
                {group_expr} AS period_label,
                MIN(t.date) AS begin_date,
                SUM(CASE WHEN t.type = 'income' THEN t.total_amount ELSE 0 END) AS income,
                SUM(CASE WHEN t.type = 'expense' THEN t.total_amount ELSE 0 END) AS expense
            FROM transactions t
            WHERE t.date BETWEEN %s AND %s
            GROUP BY period_label
            ORDER BY begin_date
        """
        return self._execute(sql, (date_from, date_to))
    def get_category_breakdown(self, date_from: date, date_to: date,
                               type_filter: str = 'expense') -> List[Dict]:
        """Сумма по категориям для указанного типа (доход / расход)"""
        sql = """
            SELECT c.name AS category_name, SUM(ti.amount) AS amount
            FROM transaction_items ti
            JOIN categories c ON ti.category_id = c.id
            JOIN transactions t ON ti.transaction_id = t.id
            WHERE t.date BETWEEN %s AND %s
              AND t.type = %s
            GROUP BY c.id, c.name
            ORDER BY amount DESC
        """
        return self._execute(sql, (date_from, date_to, type_filter))

    def get_budget_comparison(self, date_from: date, date_to: date) -> List[Dict]:
        """Сравнение бюджета (план/факт) по категориям"""
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