from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QFrame, QScrollArea,
    QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlanFactTab(QWidget):
    """Вкладка План vs Факт"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent_widget = parent
        self.init_ui()

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 20)

        # Информационная панель
        info_widget = QFrame()
        info_widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 15px;
            }
        """)

        info_layout = QHBoxLayout()

        self.plan_fact_records = QLabel("📊 Всего записей: 0")
        self.plan_fact_records.setStyleSheet("color: #475569; font-size: 13px; font-weight: bold;")

        self.total_plan_label = QLabel("Общий план: 0 ₽")
        self.total_plan_label.setStyleSheet("color: #4F46E5; font-size: 13px; font-weight: bold;")

        self.total_fact_label = QLabel("Общий факт: 0 ₽")
        self.total_fact_label.setStyleSheet("color: #10B981; font-size: 13px; font-weight: bold;")

        self.total_diff_label = QLabel("Отклонение: 0 ₽")
        self.total_diff_label.setStyleSheet("color: #10B981; font-size: 13px; font-weight: bold;")

        info_layout.addWidget(self.plan_fact_records)
        info_layout.addStretch()
        info_layout.addWidget(self.total_plan_label)
        info_layout.addStretch()
        info_layout.addWidget(self.total_fact_label)
        info_layout.addStretch()
        info_layout.addWidget(self.total_diff_label)

        info_widget.setLayout(info_layout)
        layout.addWidget(info_widget)

        # Таблица
        self.plan_fact_table = QTableWidget()
        self.plan_fact_table.setColumnCount(7)
        self.plan_fact_table.setHorizontalHeaderLabels([
            "Категория", "Тип", "План (₽)", "Факт (₽)", "Отклонение", "%", "Статус"
        ])

        self.plan_fact_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QHeaderView::section {
                background: #F8FAFC;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: bold;
                color: #475569;
                font-size: 12px;
            }
        """)

        self.plan_fact_table.setAlternatingRowColors(True)
        self.plan_fact_table.verticalHeader().setVisible(False)

        # Настройка ширины колонок
        self.plan_fact_table.setColumnWidth(0, 200)
        self.plan_fact_table.setColumnWidth(1, 80)
        self.plan_fact_table.setColumnWidth(2, 120)
        self.plan_fact_table.setColumnWidth(3, 120)
        self.plan_fact_table.setColumnWidth(4, 140)
        self.plan_fact_table.setColumnWidth(5, 100)
        self.plan_fact_table.setColumnWidth(6, 120)

        self.plan_fact_table.horizontalHeader().setStretchLastSection(True)
        self.plan_fact_table.setMinimumHeight(350)
        self.plan_fact_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(self.plan_fact_table)

        # График
        chart_card = QFrame()
        chart_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 15px;
            }
        """)
        chart_card.setMinimumHeight(450)

        chart_layout = QVBoxLayout()
        chart_title = QLabel("📊 План vs Факт по категориям")
        chart_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B; padding-bottom: 10px;")
        chart_layout.addWidget(chart_title)

        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)

        chart_layout.addWidget(self.canvas)
        chart_card.setLayout(chart_layout)
        layout.addWidget(chart_card)

        layout.addStretch()

        scroll_area.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def load_data(self, dates):
        """Загрузка данных план/факт"""
        try:
            rows = self.controller.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.type,
                    COALESCE(b.planned_amount, 0) as plan,
                    COALESCE((
                        SELECT SUM(ti.amount)
                        FROM transaction_items ti
                        JOIN transactions t ON t.id = ti.transaction_id
                        WHERE ti.category_id = c.id
                        AND t.date >= %s 
                        AND t.date <= %s
                    ), 0) as fact
                FROM categories c
                LEFT JOIN budgets b ON b.category_id = c.id 
                    AND b.period_start = %s
                    AND b.period_end = %s
                ORDER BY c.type DESC, c.name
            """, (dates['start'], dates['end'], dates['start'], dates['end']), fetch=True)

            self.plan_fact_table.setRowCount(len(rows))

            total_plan = 0
            total_fact = 0
            data_for_chart = []

            for i, (cat_id, cat_name, cat_type, plan, fact) in enumerate(rows):
                plan_val = float(plan) if plan else 0
                fact_val = float(fact) if fact else 0
                diff_val = fact_val - plan_val
                diff_percent = (diff_val / plan_val * 100) if plan_val > 0 else (0 if fact_val == 0 else float('inf'))

                type_label = "Доход" if cat_type == 'income' else "Расход"
                type_icon = "💰" if cat_type == 'income' else "💸"
                type_color = "#10B981" if cat_type == 'income' else "#EF4444"

                if cat_type == 'income':
                    if diff_val >= 0:
                        status = "✅ Выполнено"
                        status_color = "#10B981"
                    else:
                        status = "❌ Не выполнено"
                        status_color = "#EF4444"
                    total_plan += plan_val
                    total_fact += fact_val
                else:
                    if diff_val <= 0:
                        status = "✅ В норме"
                        status_color = "#10B981"
                    else:
                        status = "⚠️ Превышение"
                        status_color = "#EF4444"
                    total_plan += plan_val
                    total_fact += fact_val

                # Категория
                cat_item = QTableWidgetItem(f"{type_icon} {cat_name}")
                self.plan_fact_table.setItem(i, 0, cat_item)

                # Тип
                type_item = QTableWidgetItem(type_label)
                type_item.setForeground(QColor(type_color))
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_fact_table.setItem(i, 1, type_item)

                # План и Факт
                plan_item = QTableWidgetItem(f"{plan_val:,.2f} ₽")
                plan_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.plan_fact_table.setItem(i, 2, plan_item)

                fact_item = QTableWidgetItem(f"{fact_val:,.2f} ₽")
                fact_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.plan_fact_table.setItem(i, 3, fact_item)

                # Отклонение
                diff_item = QTableWidgetItem(f"{diff_val:+,.2f} ₽")
                if diff_val > 0:
                    diff_item.setForeground(QColor("#EF4444") if cat_type == 'expense' else QColor("#10B981"))
                else:
                    diff_item.setForeground(QColor("#10B981") if cat_type == 'expense' else QColor("#EF4444"))
                diff_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.plan_fact_table.setItem(i, 4, diff_item)

                # Процент
                percent_text = f"{diff_percent:+,.1f}%" if diff_percent != float('inf') else "∞%"
                percent_item = QTableWidgetItem(percent_text)
                if diff_percent > 0 and diff_percent != float('inf'):
                    percent_item.setForeground(QColor("#EF4444") if cat_type == 'expense' else QColor("#10B981"))
                elif diff_percent < 0:
                    percent_item.setForeground(QColor("#10B981") if cat_type == 'expense' else QColor("#EF4444"))
                percent_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.plan_fact_table.setItem(i, 5, percent_item)

                # Статус
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                font = status_item.font()
                font.setBold(True)
                status_item.setFont(font)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_fact_table.setItem(i, 6, status_item)

                data_for_chart.append((cat_name, plan_val, fact_val))

            total_diff = total_fact - total_plan

            self.plan_fact_records.setText(f"📊 Всего записей: {len(rows)}")
            self.total_plan_label.setText(f"Общий план: {total_plan:,.2f} ₽")
            self.total_fact_label.setText(f"Общий факт: {total_fact:,.2f} ₽")

            diff_color = "#10B981" if total_diff >= 0 else "#EF4444"
            self.total_diff_label.setText(f"Отклонение: {total_diff:+,.2f} ₽")
            self.total_diff_label.setStyleSheet(f"color: {diff_color}; font-size: 13px; font-weight: bold;")

            self.draw_chart(data_for_chart)

        except Exception as e:
            print(f"Ошибка загрузки план/факт: {e}")

    def draw_chart(self, data):
        """Рисование графика"""
        self.figure.clear()

        if not data:
            ax = self.figure.add_subplot(111)
            ax.clear()
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', fontsize=14, color='#94A3B8')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)

        # Сортировка и ограничение количества категорий
        data_sorted = sorted(data, key=lambda x: x[1] + x[2], reverse=True)[:15]

        categories = [item[0][:15] + ".." if len(item[0]) > 15 else item[0] for item in data_sorted]
        plans = [item[1] for item in data_sorted]
        facts = [item[2] for item in data_sorted]

        x = range(len(categories))
        width = 0.35

        ax.bar([i - width / 2 for i in x], plans, width,
               label='План', color='#4F46E5', alpha=0.8)
        ax.bar([i + width / 2 for i in x], facts, width,
               label='Факт', color='#10B981', alpha=0.8)

        ax.set_ylabel('Сумма (₽)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Категории', fontsize=11, fontweight='bold')
        ax.set_title('План vs Факт по категориям', fontsize=12, fontweight='bold', pad=15)

        # Поворот подписей при большом количестве
        if len(categories) > 8:
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)
            self.figure.subplots_adjust(bottom=0.25)
        else:
            ax.set_xticks(x)
            ax.set_xticklabels(categories, fontsize=10)

        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.set_facecolor('#F8FAFC')

        self.figure.tight_layout()
        self.canvas.draw()