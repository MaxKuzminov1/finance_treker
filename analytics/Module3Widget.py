from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QDateEdit,
    QPushButton, QScrollArea, QGridLayout, QButtonGroup
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor

from analytics.controller import AnalyticsController
from analytics.charts import create_line_chart, create_pie_chart, create_bar_chart


class KPICard(QFrame):
    """Стилизованная карточка KPI с поддержкой теней."""

    def __init__(self, title, icon, value="0 ₽", subtext="", color="#4F46E5"):
        super().__init__()
        self.color = color
        self.setObjectName("kpi_card")
        self.setup_ui(title, icon, value, subtext)

    def setup_ui(self, title, icon, value, subtext):
        self.setMinimumHeight(130)
        self.setStyleSheet(f"""
            #kpi_card {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }}
            #kpi_card:hover {{ border: 1px solid {self.color}; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("color: #64748B; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"font-size: 16px; color: {self.color}; background: {self.color}15; border-radius: 6px; padding: 4px;")
        header.addWidget(title_lbl)
        header.addStretch()
        header.addWidget(icon_lbl)

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A; margin-top: 4px;")
        self.sub_lbl = QLabel(subtext)
        self.sub_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")

        layout.addLayout(header)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)
        layout.addStretch()

    def update_data(self, value, subtext):
        self.val_lbl.setText(value)
        self.sub_lbl.setText(subtext)


class Module3Widget(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.analytics_ctrl = AnalyticsController()
        self.setup_ui()
        self.set_quick_period("month")  # Период по умолчанию
        self.refresh_all()

    def setup_ui(self):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background-color: #F8FAFC;")

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)
        self.scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.scroll)

        # 1. ЗАГОЛОВОК И ЭКСПОРТ
        header = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.addWidget(
            QLabel("Аналитический Дашборд", styleSheet="font-size: 24px; font-weight: bold; color: #1E293B;"))
        title_vbox.addWidget(QLabel("Интеллектуальный анализ финансов", styleSheet="color: #64748B; font-size: 13px;"))

        self.btn_pdf = QPushButton("📑 Скачать PDF-отчет")
        self.btn_pdf.setFixedSize(180, 40)
        self.btn_pdf.setStyleSheet("""
            QPushButton { background: #0F172A; color: white; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #1E293B; }
        """)
        self.btn_pdf.clicked.connect(self.export_pdf)

        header.addLayout(title_vbox)
        header.addStretch()
        header.addWidget(self.btn_pdf)
        self.main_layout.addLayout(header)

        # 2. ПАНЕЛЬ ФИЛЬТРОВ И БЫСТРЫХ ПЕРИОДОВ
        filter_frame = QFrame(styleSheet="background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        f_layout = QHBoxLayout(filter_frame)
        f_layout.setContentsMargins(15, 10, 15, 10)

        # Быстрые кнопки периодов (Chips)
        self.btn_group = QButtonGroup(self)
        quick_periods = [("Неделя", "week"), ("Месяц", "month"), ("Квартал", "quarter"), ("Год", "year")]

        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        for text, period_id in quick_periods:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("period_id", period_id)
            btn.setStyleSheet("""
                QPushButton { background: #F1F5F9; color: #475569; border-radius: 15px; padding: 6px 16px; border: none; font-weight: bold;}
                QPushButton:checked { background: #4F46E5; color: white; }
                QPushButton:hover:!checked { background: #E2E8F0; }
            """)
            btn.clicked.connect(lambda checked, pid=period_id: self.set_quick_period(pid))
            self.btn_group.addButton(btn)
            quick_layout.addWidget(btn)

        f_layout.addLayout(quick_layout)
        f_layout.addSpacing(20)

        # Точный выбор дат
        f_layout.addWidget(QLabel("Или вручную:", styleSheet="color: #64748B; font-weight: bold;"))
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to = QDateEdit(calendarPopup=True)
        for de in (self.date_from, self.date_to):
            de.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 6px;")
            de.dateChanged.connect(self.custom_date_changed)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.setStyleSheet(
            "background: #10B981; color: white; padding: 6px 20px; border-radius: 6px; font-weight: bold;")
        self.btn_refresh.clicked.connect(self.refresh_all)

        f_layout.addWidget(self.date_from)
        f_layout.addWidget(QLabel("-"))
        f_layout.addWidget(self.date_to)
        f_layout.addStretch()
        f_layout.addWidget(self.btn_refresh)

        self.main_layout.addWidget(filter_frame)

        # 3. KPI GRID
        kpi_grid = QGridLayout()
        self.card_inc = KPICard("Доходы", "📈", color="#10B981")
        self.card_exp = KPICard("Расходы", "📉", color="#EF4444")
        self.card_profit = KPICard("Прибыль", "💰", color="#4F46E5")
        self.card_savings = KPICard("Экономия", "🐷", color="#F59E0B")

        cards = [(self.card_inc, 0, 0), (self.card_exp, 0, 1), (self.card_profit, 0, 2), (self.card_savings, 0, 3)]
        for c, r, col in cards: kpi_grid.addWidget(c, r, col)
        self.main_layout.addLayout(kpi_grid)

        # 4. ГРАФИКИ (Верхний ряд)
        charts_row1 = QHBoxLayout()
        self.line_container = self._create_chart_box("Динамика Cash Flow")
        self.pie_container = self._create_chart_box("Структура расходов")
        charts_row1.addWidget(self.line_container, 2)
        charts_row1.addWidget(self.pie_container, 1)
        self.main_layout.addLayout(charts_row1)

        # 5. НОВЫЙ БЛОК: План/Факт и Тренды (Нижний ряд)
        charts_row2 = QHBoxLayout()
        self.bar_container = self._create_chart_box("Анализ: План vs Факт (Бюджеты)")

        # Информационная панель трендов
        self.trend_frame = self._create_chart_box("Нейро-сводка и Тренды")
        self.trend_label = QLabel("Ожидание данных...")
        self.trend_label.setWordWrap(True)
        self.trend_label.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.5;")
        self.trend_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.trend_frame.layout().addWidget(self.trend_label)
        self.trend_frame.layout().addStretch()

        charts_row2.addWidget(self.bar_container, 2)
        charts_row2.addWidget(self.trend_frame, 1)
        self.main_layout.addLayout(charts_row2)

    def _create_chart_box(self, title):
        frame = QFrame(styleSheet="background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        frame.setMinimumHeight(350)
        layout = QVBoxLayout(frame)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B; margin-bottom: 5px;")
        layout.addWidget(title_lbl)
        return frame

    def set_quick_period(self, period_id):
        """Установка быстрых дат без вызова бесконечного цикла."""
        for btn in self.btn_group.buttons():
            if btn.property("period_id") == period_id:
                btn.setChecked(True)
                break

        today = QDate.currentDate()
        self.date_from.blockSignals(True)
        self.date_to.blockSignals(True)

        self.date_to.setDate(today)
        if period_id == "week":
            self.date_from.setDate(today.addDays(-7))
        elif period_id == "month":
            self.date_from.setDate(today.addMonths(-1))
        elif period_id == "quarter":
            self.date_from.setDate(today.addMonths(-3))
        elif period_id == "year":
            self.date_from.setDate(today.addYears(-1))

        self.date_from.blockSignals(False)
        self.date_to.blockSignals(False)
        self.refresh_all()

    def custom_date_changed(self):
        """Сброс быстрых кнопок при ручном вводе."""
        self.btn_group.setExclusive(False)
        for btn in self.btn_group.buttons(): btn.setChecked(False)
        self.btn_group.setExclusive(True)

    def refresh_all(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()

        # 1. Обновление KPI
        kpi = self.analytics_ctrl.get_kpi(d_from, d_to)
        self.card_inc.update_data(f"{kpi.total_income:,.0f} ₽", "За выбранный период")
        self.card_exp.update_data(f"{kpi.total_expense:,.0f} ₽", f"Топ категория: {kpi.top_expense_category}")
        self.card_profit.update_data(f"{kpi.profit:,.0f} ₽", f"Рентабельность {kpi.profitability:.1f}%")
        self.card_savings.update_data(f"{kpi.savings_rate:.1f}%", f"Ср. чек: {kpi.avg_check:,.0f} ₽")

        # Очистка контейнеров графиков
        for container in [self.line_container, self.pie_container, self.bar_container]:
            for i in reversed(range(1, container.layout().count())):
                container.layout().itemAt(i).widget().setParent(None)

        # 2. Линейный график (Cash Flow)
        ts = self.analytics_ctrl.get_time_series(d_from, d_to)
        if ts:
            self.line_container.layout().addWidget(create_line_chart(
                "", [p.period_label for p in ts], [p.income for p in ts], [p.expense for p in ts],
                [p.profit for p in ts]
            ))

        # 3. Круговая диаграмма
        shares = self.analytics_ctrl.get_category_shares(d_from, d_to, "expense")
        if shares:
            self.pie_container.layout().addWidget(create_pie_chart(
                "", [s.category_name for s in shares], [s.amount for s in shares]
            ))

        # 4. НОВОЕ: График План/Факт (Анализ бюджета)
        budget_data = self.analytics_ctrl.get_budget_comparison(d_from, d_to)
        if budget_data:
            cats = [b['category_name'] for b in budget_data]
            planned = [float(b['planned']) for b in budget_data]
            actual = [float(b['actual']) for b in budget_data]
            self.bar_container.layout().addWidget(create_bar_chart("", cats, planned, actual))
        else:
            lbl = QLabel("Нет данных о бюджетах для сравнения")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bar_container.layout().addWidget(lbl)

        # 5. НОВОЕ: Обновление текстовых трендов
        trends = self.analytics_ctrl.get_trends()
        trend_text = f"<b>Прогноз расходов на следующий период:</b> {trends.forecast_next_period:,.0f} ₽<br><br>"

        dirs = {'up': '<span style="color:red">Рост 📈</span>', 'down': '<span style="color:green">Снижение 📉</span>',
                'stable': 'Стабильно ➖'}
        trend_text += f"<b>Общий тренд:</b> {dirs.get(trends.trend_direction, 'Неизвестно')}<br><br>"

        if trends.anomalies:
            trend_text += "<b>Внимание, найдены аномалии:</b><br>"
            for a in trends.anomalies:
                # Безопасно получаем данные, если структура словаря может отличаться
                period = a.get('period_label', 'Неизвестный период')
                exp = float(a.get('expense', 0))
                trend_text += f"• {period}: аномальный расход {exp:,.0f} ₽<br>"
        else:
            trend_text += "<span style='color:green'>Аномальных всплесков расходов не обнаружено.</span>"

        self.trend_label.setText(trend_text)

    def export_pdf(self):
        # Оставляем логику как есть, либо передаем нужные параметры
        pass