from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QFrame, QScrollArea,
    QSizePolicy, QProgressBar, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MetricCard(QFrame):
    """Кастомный виджет для отображения метрик."""

    def __init__(self, title, value="0 ₽", color="#4F46E5"):
        super().__init__()
        self.setStyleSheet(f"""
            MetricCard {{
                background: white;
                border-radius: 12px;
                border-left: 4px solid {color};
                border-top: 1px solid #E2E8F0;
                border-right: 1px solid #E2E8F0;
                border-bottom: 1px solid #E2E8F0;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-weight: bold;")

        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)


class PlanFactTab(QWidget):
    """Вкладка План vs Факт"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: transparent; width: 8px; }
            QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }
        """)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 20)

        # Дашборд метрик
        metrics_layout = QHBoxLayout()
        self.plan_card = MetricCard("ОБЩИЙ ПЛАН", "0 ₽", "#3B82F6")
        self.fact_card = MetricCard("ОБЩИЙ ФАКТ", "0 ₽", "#8B5CF6")
        self.diff_card = MetricCard("ОТКЛОНЕНИЕ", "0 ₽", "#10B981")

        metrics_layout.addWidget(self.plan_card)
        metrics_layout.addWidget(self.fact_card)
        metrics_layout.addWidget(self.diff_card)
        layout.addLayout(metrics_layout)

        # Таблица
        self.plan_fact_table = QTableWidget()
        self.plan_fact_table.setColumnCount(7)
        self.plan_fact_table.setHorizontalHeaderLabels([
            "Категория", "Тип", "План (₽)", "Факт (₽)", "Отклонение", "Выполнение", "Статус"
        ])

        self.plan_fact_table.setStyleSheet("""
            QTableWidget {
                background: white; border: 1px solid #E2E8F0; border-radius: 12px; gridline-color: #F1F5F9;
            }
            QHeaderView::section {
                background: #F8FAFC; padding: 12px; border: none;
                border-bottom: 2px solid #E2E8F0; font-weight: bold; color: #475569;
            }
            QTableWidget::item { padding: 8px; }
        """)
        self.plan_fact_table.setAlternatingRowColors(True)
        self.plan_fact_table.verticalHeader().setVisible(False)
        self.plan_fact_table.verticalHeader().setDefaultSectionSize(55)
        self.plan_fact_table.setMinimumHeight(350)

        header = self.plan_fact_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.plan_fact_table.setColumnWidth(5, 140)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.plan_fact_table)

        # График
        chart_card = QFrame()
        chart_card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        chart_card.setMinimumHeight(450)

        chart_layout = QVBoxLayout(chart_card)
        chart_title = QLabel("📊 Выполнение по категориям")
        chart_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1E293B; padding: 10px;")
        chart_layout.addWidget(chart_title)

        self.figure = Figure(figsize=(10, 5), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)

        layout.addWidget(chart_card)
        layout.addStretch()

        scroll_area.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def _create_progress_bar(self, fact, plan, cat_type):
        bar = QProgressBar()
        bar.setFixedHeight(24)
        bar.setTextVisible(True)

        if plan == 0:
            percent = 100 if fact > 0 else 0
        else:
            percent = int((fact / plan) * 100)

        bar.setValue(min(percent, 100))
        bar.setFormat(f"{percent}%")

        color = "#10B981"
        if cat_type == 'expense' and percent > 100:
            color = "#EF4444"
        elif cat_type == 'income' and percent < 100:
            color = "#F59E0B"

        bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                background-color: #F8FAFC;
                text-align: center;
                color: #1E293B;
                font-weight: bold;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

        container = QWidget()
        l = QVBoxLayout(container)
        l.setContentsMargins(8, 8, 8, 8)
        l.addWidget(bar)
        return container

    def load_data(self, dates):
        try:
            # УМНЫЙ SQL ДЛЯ АНАЛИТИКИ: Собирает суммы планов, входящих в границы периода
            rows = self.controller.execute("""
                SELECT 
                    c.id, c.name, c.type,
                    COALESCE((SELECT SUM(b.planned_amount) FROM budgets b WHERE b.category_id = c.id AND b.period_start >= %s AND b.period_end <= %s), 0) as plan,
                    COALESCE((SELECT SUM(ti.amount) FROM transaction_items ti JOIN transactions t ON t.id = ti.transaction_id WHERE ti.category_id = c.id AND t.date >= %s AND t.date <= %s), 0) as fact
                FROM categories c
                WHERE 
                    COALESCE((SELECT SUM(b.planned_amount) FROM budgets b WHERE b.category_id = c.id AND b.period_start >= %s AND b.period_end <= %s), 0) > 0 
                    OR 
                    COALESCE((SELECT SUM(ti.amount) FROM transaction_items ti JOIN transactions t ON t.id = ti.transaction_id WHERE ti.category_id = c.id AND t.date >= %s AND t.date <= %s), 0) > 0
                ORDER BY c.type DESC, c.name
            """, (dates['start'], dates['end'], dates['start'], dates['end'], dates['start'], dates['end'], dates['start'], dates['end']), fetch=True)

            self.plan_fact_table.setRowCount(len(rows))
            total_plan, total_fact = 0, 0
            data_for_chart = []

            for i, (cat_id, cat_name, cat_type, plan, fact) in enumerate(rows):
                plan_val, fact_val = float(plan), float(fact)
                diff_val = fact_val - plan_val

                modifier = 1 if cat_type == 'income' else -1
                total_plan += plan_val * modifier
                total_fact += fact_val * modifier

                if cat_type == 'income':
                    status = "✅ Выполнено" if diff_val >= 0 else "📉 Отставание"
                    status_color = "#10B981" if diff_val >= 0 else "#F59E0B"
                else:
                    status = "✅ В норме" if diff_val <= 0 else "⚠️ Перерасход"
                    status_color = "#10B981" if diff_val <= 0 else "#EF4444"

                self.plan_fact_table.setItem(i, 0,
                                             QTableWidgetItem(f"{'💰' if cat_type == 'income' else '💸'} {cat_name}"))

                type_item = QTableWidgetItem("Доход" if cat_type == 'income' else "Расход")
                type_item.setForeground(QColor("#10B981" if cat_type == 'income' else "#EF4444"))
                self.plan_fact_table.setItem(i, 1, type_item)

                plan_item = QTableWidgetItem(f"{plan_val:,.2f} ₽")
                plan_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.plan_fact_table.setItem(i, 2, plan_item)

                fact_item = QTableWidgetItem(f"{fact_val:,.2f} ₽")
                fact_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.plan_fact_table.setItem(i, 3, fact_item)

                diff_item = QTableWidgetItem(f"{diff_val:+,.2f} ₽")
                diff_color = "#EF4444" if (cat_type == 'expense' and diff_val > 0) or (
                            cat_type == 'income' and diff_val < 0) else "#10B981"
                diff_item.setForeground(QColor(diff_color))
                diff_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.plan_fact_table.setItem(i, 4, diff_item)

                self.plan_fact_table.setCellWidget(i, 5, self._create_progress_bar(fact_val, plan_val, cat_type))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                font = status_item.font()
                font.setBold(True)
                status_item.setFont(font)
                self.plan_fact_table.setItem(i, 6, status_item)

                data_for_chart.append((cat_name, plan_val, fact_val))

            self.plan_card.value_lbl.setText(f"{total_plan:,.2f} ₽")
            self.fact_card.value_lbl.setText(f"{total_fact:,.2f} ₽")

            total_diff = total_fact - total_plan
            diff_color = "#10B981" if total_diff >= 0 else "#EF4444"
            self.diff_card.value_lbl.setText(f"{total_diff:+,.2f} ₽")
            self.diff_card.value_lbl.setStyleSheet(f"color: {diff_color}; font-size: 18px; font-weight: 800;")
            self.diff_card.setStyleSheet(
                f"background: white; border-radius: 12px; border-left: 4px solid {diff_color}; border: 1px solid #E2E8F0;")

            self.draw_chart(data_for_chart)

        except Exception as e:
            print(f"Ошибка загрузки план/факт: {e}")

    def draw_chart(self, data):
        self.figure.clear()
        if not data:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', color='#94A3B8')
            ax.axis('off')
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        data_sorted = sorted(data, key=lambda x: x[1] + x[2], reverse=True)[:10]

        categories = [item[0][:12] + ".." if len(item[0]) > 12 else item[0] for item in data_sorted]
        plans = [item[1] for item in data_sorted]
        facts = [item[2] for item in data_sorted]
        x = range(len(categories))
        width = 0.35

        ax.bar([i - width / 2 for i in x], plans, width, label='План', color='#CBD5E1', edgecolor='none')
        ax.bar([i + width / 2 for i in x], facts, width, label='Факт', color='#4F46E5', edgecolor='none')

        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=30, ha='right', fontsize=9, color='#475569')
        ax.tick_params(axis='y', colors='#475569')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E2E8F0')
        ax.spines['bottom'].set_color('#E2E8F0')

        ax.legend(frameon=False)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')
        self.figure.tight_layout()
        self.canvas.draw()