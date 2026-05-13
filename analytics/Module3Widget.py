import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QDateEdit,
    QPushButton, QScrollArea, QGridLayout, QButtonGroup, QFileDialog, QMessageBox,
    QSizePolicy, QSlider, QComboBox, QSpinBox
)
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from analytics.controller import AnalyticsController
from analytics.charts import create_line_chart, create_pie_chart, create_bar_chart
from analytics.pdf_generator import PDFReportGenerator


class KPICard(QFrame):
    # ... (код KPICard остается без изменений, он у нас уже идеален)
    def __init__(self, title, icon, value="0 ₽", subtext="", color="#4F46E5"):
        super().__init__()
        self.color = color
        self.setObjectName("kpi_card")
        self.setup_ui(title, icon, value, subtext)

    def setup_ui(self, title, icon, value, subtext):
        self.setMinimumHeight(140)
        self.setStyleSheet(
            f"#kpi_card {{ background-color: white; border-radius: 12px; border: 1px solid #E2E8F0; }} #kpi_card:hover {{ border: 1px solid {self.color}; }}")
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
        self.trend_lbl = QLabel("")
        self.trend_lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.trend_lbl.setVisible(False)
        layout.addLayout(header)
        layout.addWidget(self.val_lbl)
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.sub_lbl)
        sub_layout.addStretch()
        sub_layout.addWidget(self.trend_lbl)
        layout.addLayout(sub_layout)
        layout.addStretch()

    def update_data(self, value, subtext, trend_pct=None):
        self.val_lbl.setText(value)
        self.sub_lbl.setText(subtext)
        if trend_pct is not None:
            self.trend_lbl.setVisible(True)
            if trend_pct > 0:
                self.trend_lbl.setText(f"▲ +{trend_pct:.1f}%")
                self.trend_lbl.setStyleSheet("color: #10B981; font-size: 11px; font-weight: bold;")
            elif trend_pct < 0:
                self.trend_lbl.setText(f"▼ {trend_pct:.1f}%")
                self.trend_lbl.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")
            else:
                self.trend_lbl.setText(f"▬ 0%")
                self.trend_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: bold;")
        else:
            self.trend_lbl.setVisible(False)


class Module3Widget(QWidget):
    # === 1. ОБЪЯВЛЯЕМ СИГНАЛ ДЛЯ DRILL-DOWN ===
    drill_down_requested = pyqtSignal(str)

    def __init__(self, controller=None):
        super().__init__()
        self.analytics_ctrl = AnalyticsController()

        # Переменные состояния для симулятора
        self.base_income = 0
        self.base_expense = 0
        self.current_shares = []

        self.setup_ui()
        self.set_quick_period("month")
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

        self.btn_excel = QPushButton("📊 P&L Excel")
        self.btn_excel.setFixedSize(140, 40)
        self.btn_excel.setStyleSheet(
            "QPushButton { background: #10B981; color: white; border-radius: 8px; font-weight: bold; } QPushButton:hover { background: #059669; }")
        self.btn_excel.clicked.connect(self.export_excel)

        self.btn_pdf = QPushButton("📑 Отчет PDF")
        self.btn_pdf.setFixedSize(140, 40)
        self.btn_pdf.setStyleSheet(
            "QPushButton { background: #0F172A; color: white; border-radius: 8px; font-weight: bold; } QPushButton:hover { background: #1E293B; }")
        self.btn_pdf.clicked.connect(self.export_pdf)

        header.addLayout(title_vbox)
        header.addStretch()
        header.addWidget(self.btn_excel)
        header.addWidget(self.btn_pdf)
        self.main_layout.addLayout(header)

        # 2. ПАНЕЛЬ ФИЛЬТРОВ И БЫСТРЫХ ПЕРИОДОВ
        filter_frame = QFrame(objectName="filter_frame")
        filter_frame.setStyleSheet(
            "QFrame#filter_frame { background: white; border-radius: 12px; border: 1px solid #E2E8F0; }")
        f_layout = QHBoxLayout(filter_frame)
        f_layout.setContentsMargins(15, 10, 15, 10)

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

        f_layout.addWidget(QLabel("Вручную:", styleSheet="color: #64748B; font-weight: bold;"))
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to = QDateEdit(calendarPopup=True)
        for de in (self.date_from, self.date_to):
            de.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 6px;")
            de.dateChanged.connect(self.custom_date_changed)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.setStyleSheet(
            "background: #4F46E5; color: white; padding: 6px 20px; border-radius: 6px; font-weight: bold;")
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
        self.card_savings = KPICard("Рентабельность", "📊", color="#F59E0B")
        cards = [(self.card_inc, 0, 0), (self.card_exp, 0, 1), (self.card_profit, 0, 2), (self.card_savings, 0, 3)]
        for c, r, col in cards: kpi_grid.addWidget(c, r, col)
        self.main_layout.addLayout(kpi_grid)

        # 4. ГРАФИКИ
        charts_row1 = QHBoxLayout()
        self.line_container = self._create_chart_box("Динамика Cash Flow")
        self.pie_container = self._create_chart_box("Структура расходов (Кликабельно)")
        charts_row1.addWidget(self.line_container, 2)
        charts_row1.addWidget(self.pie_container, 1)
        self.main_layout.addLayout(charts_row1)

        charts_row2 = QHBoxLayout()
        self.bar_container = self._create_chart_box("Анализ: План vs Факт (Бюджеты)")
        self.trend_frame = self._create_chart_box("Нейро-сводка")
        self.trend_label = QLabel("Ожидание данных...")
        self.trend_label.setWordWrap(True)
        self.trend_label.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.5;")
        self.trend_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.trend_frame.layout().addWidget(self.trend_label)
        self.trend_frame.layout().addStretch()
        charts_row2.addWidget(self.bar_container, 2)
        charts_row2.addWidget(self.trend_frame, 1)
        self.main_layout.addLayout(charts_row2)

        # === 5. ПЕРЕРАБОТАННЫЙ КАЛЬКУЛЯТОР "ЧТО-ЕСЛИ" И НАЛОГИ ===
        tools_row = QHBoxLayout()

        self.tax_frame = self._create_chart_box("🏦 Налоговый радар")
        self.tax_label = QLabel("Расчет...")
        self.tax_label.setWordWrap(True)
        self.tax_label.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.5;")
        self.tax_frame.layout().addWidget(self.tax_label)
        self.tax_frame.layout().addStretch()

        self.whatif_frame = self._create_chart_box("🧪 Продвинутый P&L Симулятор")
        wi_layout = QGridLayout()
        wi_layout.setSpacing(15)

        # Селектор категории
        wi_layout.addWidget(QLabel("Моделируемая статья расходов:", styleSheet="color: #64748B;"), 0, 0)
        self.wi_combo = QComboBox()
        self.wi_combo.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.wi_combo.currentIndexChanged.connect(self.calculate_whatif)
        wi_layout.addWidget(self.wi_combo, 0, 1)

        # SpinBox расходов (можно урезать расходы -50%, а можно увеличить цены на сырье +50%)
        wi_layout.addWidget(QLabel("Изменение стоимости статьи:", styleSheet="color: #64748B;"), 1, 0)
        self.wi_exp_spin = QSpinBox()
        self.wi_exp_spin.setRange(-100, 500)
        self.wi_exp_spin.setSuffix(" %")
        self.wi_exp_spin.setValue(-10)  # По умолчанию имитируем оптимизацию на 10%
        self.wi_exp_spin.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.wi_exp_spin.valueChanged.connect(self.calculate_whatif)
        wi_layout.addWidget(self.wi_exp_spin, 1, 1)

        # Рост доходов
        wi_layout.addWidget(QLabel("Прогноз роста общих доходов:", styleSheet="color: #64748B;"), 2, 0)
        self.wi_inc_spin = QSpinBox()
        self.wi_inc_spin.setRange(-100, 1000)
        self.wi_inc_spin.setSuffix(" %")
        self.wi_inc_spin.setValue(0)
        self.wi_inc_spin.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.wi_inc_spin.valueChanged.connect(self.calculate_whatif)
        wi_layout.addWidget(self.wi_inc_spin, 2, 1)

        # Результат
        self.wi_result_profit = QLabel("Прогноз прибыли: 0 ₽")
        self.wi_result_profit.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")
        self.wi_result_margin = QLabel("Прогноз рентабельности: 0%")
        self.wi_result_margin.setStyleSheet("font-size: 14px; font-weight: bold; color: #4F46E5;")

        wi_layout.addWidget(self.wi_result_profit, 3, 0, 1, 2)
        wi_layout.addWidget(self.wi_result_margin, 4, 0, 1, 2)

        self.whatif_frame.layout().addLayout(wi_layout)
        self.whatif_frame.layout().addStretch()

        tools_row.addWidget(self.tax_frame, 1)
        tools_row.addWidget(self.whatif_frame, 2)
        self.main_layout.addLayout(tools_row)

    def _create_chart_box(self, title):
        frame = QFrame(objectName="chart_box")
        frame.setStyleSheet("QFrame#chart_box { background: white; border-radius: 12px; border: 1px solid #E2E8F0; }")
        frame.setMinimumHeight(220)
        layout = QVBoxLayout(frame)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B; margin-bottom: 5px;")
        layout.addWidget(title_lbl)
        return frame

    def set_quick_period(self, period_id):
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
        self.btn_group.setExclusive(False)
        for btn in self.btn_group.buttons(): btn.setChecked(False)
        self.btn_group.setExclusive(True)

    def _add_empty_label(self, container, text="Данные за период отсутствуют"):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #94A3B8; font-style: italic; font-size: 14px;")
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        container.layout().addWidget(lbl)

    # === 2. МЕТОД, КОТОРЫЙ ИСПУСКАЕТ СИГНАЛ ПРИ КЛИКЕ НА ПИРОГ ===
    def handle_drill_down(self, category_name):
        """Передает управление главному окну для переключения вкладки и фильтрации"""
        self.drill_down_requested.emit(category_name)

    # === 3. ЛОГИКА ПРОДВИНУТОГО СИМУЛЯТОРА ===
    def calculate_whatif(self):
        if not self.current_shares or self.base_income == 0:
            return

        cat_name = self.wi_combo.currentText()
        cat_amount = 0
        for s in self.current_shares:
            if s.category_name == cat_name:
                cat_amount = s.amount
                break

        # Рассчитываем изменения
        exp_modifier = self.wi_exp_spin.value() / 100.0  # например, -0.1 для -10%
        inc_modifier = self.wi_inc_spin.value() / 100.0

        # Новая сумма именно этой категории
        new_cat_amount = cat_amount * (1 + exp_modifier)

        # Общий новый расход = Старый расход - Старая сумма категории + Новая сумма категории
        new_total_expense = self.base_expense - cat_amount + new_cat_amount

        # Общий новый доход
        new_total_income = self.base_income * (1 + inc_modifier)

        # Итоги
        new_profit = new_total_income - new_total_expense
        new_margin = (new_profit / new_total_income * 100) if new_total_income > 0 else 0
        profit_diff = new_profit - (self.base_income - self.base_expense)

        diff_str = f"+{profit_diff:,.0f}" if profit_diff > 0 else f"{profit_diff:,.0f}"
        color = "#10B981" if profit_diff >= 0 else "#EF4444"

        self.wi_result_profit.setText(
            f"Прогноз прибыли: {new_profit:,.0f} ₽ (<span style='color:{color}'>{diff_str} ₽</span>)")
        self.wi_result_margin.setText(f"Прогноз рентабельности: {new_margin:.1f}%")

    def refresh_all(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()

        kpi = self.analytics_ctrl.get_kpi(d_from, d_to)

        # Сохраняем базу для симулятора
        self.base_income = kpi.total_income
        self.base_expense = kpi.total_expense

        import datetime
        prev_from = d_from - datetime.timedelta(days=(d_to - d_from).days)
        comp = self.analytics_ctrl.compare_periods(d_from, d_to, prev_from, d_from)

        self.card_inc.update_data(f"{kpi.total_income:,.0f} ₽", "К прошлому периоду:", comp.income_change_pct)
        self.card_exp.update_data(f"{kpi.total_expense:,.0f} ₽", f"Топ: {kpi.top_expense_category}",
                                  comp.expense_change_pct)
        self.card_profit.update_data(f"{kpi.profit:,.0f} ₽", "Чистый денежный поток", comp.profit_change_pct)
        self.card_savings.update_data(f"{kpi.profitability:.1f}%", f"Маржинальность бизнеса")

        tax_usn6 = kpi.total_income * 0.06
        tax_usn15 = max(0, kpi.profit * 0.15)
        self.tax_label.setText(
            f"<b>Оценочный налог за выбранный период:</b><br><br>"
            f"• <b>УСН 6% (Доходы):</b> <span style='color:#EF4444'>{tax_usn6:,.0f} ₽</span><br>"
            f"• <b>УСН 15% (Доходы-Расходы):</b> <span style='color:#EF4444'>{tax_usn15:,.0f} ₽</span><br><br>"
            f"<i>💡 Напоминание:</i> Авансовые платежи уплачиваются до 28 числа."
        )

        for container in [self.line_container, self.pie_container, self.bar_container]:
            for i in reversed(range(1, container.layout().count())):
                w = container.layout().itemAt(i).widget()
                if w: w.setParent(None); w.deleteLater()

        ts = self.analytics_ctrl.get_time_series(d_from, d_to)
        if ts and any(p.income > 0 or p.expense > 0 for p in ts):
            self.line_container.layout().addWidget(
                create_line_chart("", [p.period_label for p in ts], [p.income for p in ts], [p.expense for p in ts],
                                  [p.profit for p in ts]))
        else:
            self._add_empty_label(self.line_container)

        shares = self.analytics_ctrl.get_category_shares(d_from, d_to, "expense")
        self.current_shares = shares

        # Обновляем комбобокс в симуляторе
        self.wi_combo.blockSignals(True)
        self.wi_combo.clear()
        if shares:
            for s in shares:
                self.wi_combo.addItem(s.category_name)
            self.wi_combo.setCurrentIndex(0)
            self.calculate_whatif()

            self.pie_container.layout().addWidget(create_pie_chart(
                "", [s.category_name for s in shares], [s.amount for s in shares],
                on_click_callback=self.handle_drill_down
            ))
        else:
            self.wi_combo.addItem("Нет данных")
            self._add_empty_label(self.pie_container, "Нет данных о расходах")

        self.wi_combo.blockSignals(False)

        budget_data = self.analytics_ctrl.get_budget_comparison(d_from, d_to)
        if budget_data:
            cats = [b['category_name'] for b in budget_data]
            planned = [float(b['planned']) for b in budget_data]
            actual = [float(b['actual']) for b in budget_data]
            self.bar_container.layout().addWidget(create_bar_chart("", cats, planned, actual))
        else:
            self._add_empty_label(self.bar_container, "Нет бюджетов для сравнения")

        trends = self.analytics_ctrl.get_trends()
        trend_text = f"<b>🔮 AI Прогноз расходов:</b> {trends.forecast_next_period:,.0f} ₽<br><br>"
        dirs = {'up': '<span style="color:#EF4444">Восходящий 📈</span>',
                'down': '<span style="color:#10B981">Нисходящий 📉</span>',
                'stable': '<span style="color:#F59E0B">Боковой ➖</span>'}
        trend_text += f"<b>Вектор тренда:</b> {dirs.get(trends.trend_direction, 'Неизвестно')}<br><br>"
        if trends.anomalies:
            trend_text += "<b>⚠️ Аномалии:</b><br>"
            for a in trends.anomalies:
                trend_text += f"• <span style='color:#EF4444'>{a.get('period_label', '')}</span>: {float(a.get('expense', 0)):,.0f} ₽<br>"
        else:
            trend_text += "<b>✅ Паттерны:</b> Финансовое поведение в норме."
        self.trend_label.setText(trend_text)

    def export_excel(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить P&L отчет", f"PNL_{d_from}_{d_to}.xlsx",
                                                   "Excel Files (*.xlsx)")
        if not file_path: return
        try:
            self.analytics_ctrl.service.export_pl_excel(d_from, d_to, file_path)
            QMessageBox.information(self, "Успех", f"P&L Отчет сохранен в:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта:\n{str(e)}")

    def export_pdf(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF-отчет", f"Аналитика_{d_from}_по_{d_to}.pdf",
                                                   "PDF Files (*.pdf)")
        if not file_path: return
        try:
            kpi = self.analytics_ctrl.get_kpi(d_from, d_to)
            report_rows = self.analytics_ctrl.build_report(d_from, d_to)
            shares = self.analytics_ctrl.get_category_shares(d_from, d_to, "expense")
            trend_text = self.trend_label.text()
            period_str = f"{d_from.strftime('%d.%m.%Y')} - {d_to.strftime('%d.%m.%Y')}"
            pdf_gen = PDFReportGenerator(file_path)
            pdf_gen.generate(kpi, report_rows, period_str, shares, trend_text)
            QMessageBox.information(self, "Успех", f"PDF Отчет сохранен в:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Произошла ошибка при создании PDF:\n{str(e)}")