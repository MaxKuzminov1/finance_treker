# Module3Widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QDateEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGraphicsDropShadowEffect, QFileDialog, QMessageBox,
    QSizePolicy, QScrollArea
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor

from analytics.controller import AnalyticsController
from analytics.charts import create_line_chart, create_pie_chart, create_bar_chart
from analytics.models import GroupBy, KPIData
from datetime import date
import csv
import openpyxl


class KPICard(QFrame):
    """Современная карточка KPI с бейджем, крупной цифрой и тенью."""

    def __init__(self, title, icon="📊", value="0", trend="+0%", trend_up=True, color="#4F46E5"):
        super().__init__()
        self.setObjectName("kpi_card")
        self.icon = icon
        self.title = title
        self.value = value
        self.trend = trend
        self.trend_up = trend_up
        self.color = color
        self.setup_ui()
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def setup_ui(self):
        self.setMinimumSize(230, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("""
            #kpi_card {
                background: white;
                border-radius: 18px;
                border: 1px solid #E2E8F0;
            }
            #kpi_card:hover {
                border: 1px solid #C7D2FE;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        icon_lbl = QLabel(self.icon)
        icon_lbl.setStyleSheet("font-size: 22px;")
        trend_lbl = QLabel(self.trend)
        trend_color = "#10B981" if self.trend_up else "#EF4444"
        trend_lbl.setStyleSheet(f"""
            background-color: {trend_color}20;
            color: {trend_color};
            border-radius: 20px;
            padding: 3px 10px;
            font-size: 12px;
            font-weight: 700;
        """)
        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        top_row.addWidget(trend_lbl)
        layout.addLayout(top_row)

        title_lbl = QLabel(self.title)
        title_lbl.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500;")
        layout.addWidget(title_lbl)

        self.value_lbl = QLabel(self.value)
        self.value_lbl.setStyleSheet("font-size: 28px; font-weight: 700; color: #1E293B;")
        layout.addWidget(self.value_lbl)

        line = QFrame()
        line.setFixedHeight(3)
        line.setStyleSheet(f"background-color: {self.color}; border-radius: 2px;")
        layout.addWidget(line)

        self.setLayout(layout)

    def set_value(self, value, trend=None, trend_up=None):
        self.value_lbl.setText(value)
        if trend is not None:
            self.trend = trend
            self.trend_up = trend_up if trend_up is not None else self.trend_up
            top_row = self.layout().itemAt(0).layout()
            trend_widget = top_row.itemAt(2).widget()
            trend_color = "#10B981" if self.trend_up else "#EF4444"
            trend_widget.setText(self.trend)
            trend_widget.setStyleSheet(f"""
                background-color: {trend_color}20;
                color: {trend_color};
                border-radius: 20px;
                padding: 3px 10px;
                font-size: 12px;
                font-weight: 700;
            """)


class Module3Widget(QWidget):
    # Единая современная палитра для диаграммы и легенды
    PIE_COLORS = [
        "#6C5CE7", "#00B894", "#E17055", "#FDCB6E", "#0984E3",
        "#E84393", "#636E72", "#2D3436", "#FF7675", "#74B9FF"
    ]

    def __init__(self, controller=None):
        super().__init__()
        self.analytics_ctrl = AnalyticsController()
        self.setup_ui()
        self.connect_signals()
        self.apply_default_dates()
        self.refresh_all()

    def setup_ui(self):
        # Основной контейнер с прокруткой
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #A5B4FC;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #818CF8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        content_widget = QWidget()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.scroll_area)
        self.scroll_area.setWidget(content_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)
        content_widget.setLayout(main_layout)

        # ---- Header ----
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(100)
        header.setStyleSheet("""
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #6C5CE7, stop:1 #4F46E5);
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 6)
        header.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(24, 16, 24, 16)
        icon_lbl = QLabel("📈")
        icon_lbl.setStyleSheet("font-size: 40px; background: transparent; border: none;")
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        title = QLabel("Аналитика и отчётность")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: white; background: transparent;")
        subtitle = QLabel("Ключевые метрики, динамика и сравнение бюджета")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8); background: transparent;")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        header_layout.addWidget(icon_lbl)
        header_layout.addSpacing(12)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # ---- Фильтры ----
        filter_frame = QFrame()
        filter_frame.setObjectName("filter_card")
        filter_frame.setStyleSheet("""
            #filter_card {
                background: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                padding: 12px 20px;
            }
        """)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: 600; color: #475569;")
            return lbl

        filter_layout.addWidget(create_label("📅 Период"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setFixedHeight(36)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setFixedHeight(36)

        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("–"))
        filter_layout.addWidget(self.date_to)

        filter_layout.addWidget(create_label("📂 Тип"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Все", "Доход", "Расход"])
        self.type_combo.setFixedHeight(36)
        filter_layout.addWidget(self.type_combo)

        filter_layout.addStretch()

        self.apply_btn = QPushButton("🔄 Применить")
        self.apply_btn.setFixedHeight(36)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5;
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #4338CA; }
        """)
        self.reset_btn = QPushButton("↺ Сброс")
        self.reset_btn.setFixedHeight(36)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #475569;
                font-weight: 600;
                border-radius: 12px;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        filter_layout.addWidget(self.apply_btn)
        filter_layout.addWidget(self.reset_btn)

        filter_frame.setLayout(filter_layout)
        main_layout.addWidget(filter_frame)

        # ---- KPI Cards ----
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        self.card_income = KPICard("Общий доход", "💰", "0 ₽", "+12.5%", True, "#10B981")
        self.card_expense = KPICard("Общий расход", "📉", "0 ₽", "+5.2%", False, "#EF4444")
        self.card_profit = KPICard("Чистая прибыль", "📊", "0 ₽", "+18.3%", True, "#4F46E5")
        self.card_profitability = KPICard("Рентабельность", "📈", "0%", "+2.1%", True, "#F59E0B")
        for card in (self.card_income, self.card_expense, self.card_profit, self.card_profitability):
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            kpi_layout.addWidget(card)
        main_layout.addLayout(kpi_layout)

        # ---- Графики (два в ряд) ----
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # График динамики
        dynamics_card = self._create_chart_container("📈 Динамика доходов и расходов")
        self.dynamics_content_layout = QVBoxLayout()
        self.dynamics_content_layout.setContentsMargins(0, 0, 0, 0)
        dynamics_card.layout().addLayout(self.dynamics_content_layout, 1)

        # Donut + легенда
        structure_card = self._create_chart_container("🥧 Структура расходов")
        self.structure_content_layout = QHBoxLayout()
        self.structure_content_layout.setContentsMargins(0, 0, 0, 0)
        structure_card.layout().addLayout(self.structure_content_layout, 1)

        charts_layout.addWidget(dynamics_card, 2)
        charts_layout.addWidget(structure_card, 1)
        main_layout.addLayout(charts_layout)

        # ---- Таблица ----
        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_card.setStyleSheet("""
            #table_card {
                background: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                padding: 16px;
            }
        """)
        shadow_table = QGraphicsDropShadowEffect()
        shadow_table.setBlurRadius(12)
        shadow_table.setColor(QColor(0, 0, 0, 12))
        shadow_table.setOffset(0, 4)
        table_card.setGraphicsEffect(shadow_table)

        table_layout = QVBoxLayout()
        title_row = QHBoxLayout()
        title_tbl = QLabel("📋 Сводный отчёт по периодам")
        title_tbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #1E293B;")
        title_row.addWidget(title_tbl)
        title_row.addStretch()
        self.export_btn = QPushButton("📤 Экспорт")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5;
                color: white;
                font-weight: 600;
                border-radius: 14px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #4338CA; }
        """)
        shadow_export = QGraphicsDropShadowEffect()
        shadow_export.setBlurRadius(8)
        shadow_export.setColor(QColor(79, 70, 229, 80))
        shadow_export.setOffset(0, 2)
        self.export_btn.setGraphicsEffect(shadow_export)
        title_row.addWidget(self.export_btn)
        table_layout.addLayout(title_row)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(
            ["Период", "Доход", "Расход", "Прибыль", "Изменение, %"]
        )
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.report_table.setMinimumHeight(300)
        self.report_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                border: none;
                border-bottom: 1px solid #E2E8F0;
                padding: 12px 8px;
                font-weight: 700;
                color: #475569;
            }
            QTableWidget::item {
                padding: 10px 8px;
            }
            QTableWidget::item:selected {
                background: #EEF2FF;
                color: #1E293B;
            }
        """)
        table_layout.addWidget(self.report_table)
        table_card.setLayout(table_layout)
        main_layout.addWidget(table_card)

        main_layout.addStretch()

    def _create_chart_container(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("chart_container")
        card.setStyleSheet("""
            #chart_container {
                background: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                padding: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 8px;")
        layout.addWidget(title_lbl)
        card.setLayout(layout)
        return card

    def connect_signals(self):
        self.apply_btn.clicked.connect(self.refresh_all)
        self.reset_btn.clicked.connect(self.reset_filters)
        self.export_btn.clicked.connect(self.export_data_dialog)

    def apply_default_dates(self):
        today = QDate.currentDate()
        self.date_from.setDate(today.addDays(-today.day() + 1))
        self.date_to.setDate(today)

    def reset_filters(self):
        self.apply_default_dates()
        self.type_combo.setCurrentIndex(0)
        self.refresh_all()

    def refresh_all(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()
        kpi = self.analytics_ctrl.get_kpi(d_from, d_to)
        self.update_kpi_cards(kpi)
        self.update_dynamics_chart(d_from, d_to)
        self.update_structure_chart(d_from, d_to)
        self.update_report_table(d_from, d_to)

    def update_kpi_cards(self, kpi: KPIData):
        self.card_income.set_value(f"{kpi.total_income:,.0f} ₽", "+12.5%", True)
        self.card_expense.set_value(f"{kpi.total_expense:,.0f} ₽", "+5.2%", False)
        self.card_profit.set_value(f"{kpi.profit:,.0f} ₽", "+18.3%", True)
        self.card_profitability.set_value(f"{kpi.profitability:.1f}%", "+2.1%", True)

    def update_dynamics_chart(self, d_from, d_to):
        self._clear_layout(self.dynamics_content_layout)
        delta = d_to - d_from
        group_by = GroupBy.DAY if delta.days <= 31 else GroupBy.MONTH
        series = self.analytics_ctrl.get_time_series(d_from, d_to, group_by)
        if not series:
            placeholder = QLabel("Нет данных")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #94A3B8; font-size: 15px;")
            self.dynamics_content_layout.addWidget(placeholder)
            return
        labels = [p.period_label for p in series]
        income = [p.income for p in series]
        expense = [p.expense for p in series]
        profit = [p.profit for p in series]
        chart = create_line_chart("", labels, income, expense, profit)
        chart.setMinimumHeight(400)
        self.dynamics_content_layout.addWidget(chart)

    def update_structure_chart(self, d_from, d_to):
        self._clear_layout(self.structure_content_layout)
        type_filter = self.type_combo.currentText()
        cat_type = "expense" if type_filter in ("Все", "Расход") else "income"
        shares = self.analytics_ctrl.get_category_shares(d_from, d_to, cat_type)
        if not shares:
            placeholder = QLabel("Нет данных")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #94A3B8;")
            self.structure_content_layout.addWidget(placeholder)
            return

        labels = [s.category_name for s in shares]
        values = [s.amount for s in shares]
        # Передаём палитру, чтобы цвета легенды и сегментов совпадали
        used_colors = self.PIE_COLORS[:len(values)]

        donut_widget = create_pie_chart("", labels, values, colors=used_colors)
        donut_widget.setMinimumWidth(280)
        donut_widget.setMinimumHeight(400)

        # Легенда с точно такими же цветами
        legend_widget = QWidget()
        legend_layout = QVBoxLayout()
        legend_layout.setSpacing(8)
        for i, s in enumerate(shares):
            color = used_colors[i]
            row = QHBoxLayout()
            color_box = QLabel()
            color_box.setFixedSize(14, 14)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            name_lbl = QLabel(f"{s.category_name} ({s.percentage:.1f}%)")
            name_lbl.setStyleSheet("font-size: 13px; color: #334155;")
            amount_lbl = QLabel(f"{s.amount:,.0f} ₽")
            amount_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #1E293B;")
            row.addWidget(color_box)
            row.addWidget(name_lbl, 1)
            row.addWidget(amount_lbl)
            legend_layout.addLayout(row)
        legend_widget.setLayout(legend_layout)

        self.structure_content_layout.addWidget(donut_widget)
        self.structure_content_layout.addWidget(legend_widget)

    def update_report_table(self, d_from, d_to):
        rows = self.analytics_ctrl.build_report(d_from, d_to)
        self.report_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.report_table.setItem(i, 0, QTableWidgetItem(r.period_label))
            self.report_table.setItem(i, 1, QTableWidgetItem(f"{r.income:,.0f}"))
            self.report_table.setItem(i, 2, QTableWidgetItem(f"{r.expense:,.0f}"))
            self.report_table.setItem(i, 3, QTableWidgetItem(f"{r.profit:,.0f}"))
            change = f"{r.change_pct:+.1f}%" if r.change_pct is not None else "—"
            item_ch = QTableWidgetItem(change)
            if r.change_pct is not None:
                if r.change_pct > 0:
                    item_ch.setForeground(QColor("#10B981"))
                elif r.change_pct < 0:
                    item_ch.setForeground(QColor("#EF4444"))
            self.report_table.setItem(i, 4, item_ch)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def export_data_dialog(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт отчёта", "", "CSV (*.csv);;Excel (*.xlsx)")
        if not path:
            return
        try:
            if path.endswith('.csv'):
                self.export_csv(d_from, d_to, path)
            elif path.endswith('.xlsx'):
                self.export_excel(d_from, d_to, path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def export_csv(self, d_from, d_to, filepath):
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["Период", "Доход", "Расход", "Прибыль", "Изменение %"])
            rows = self.analytics_ctrl.build_report(d_from, d_to)
            for r in rows:
                writer.writerow([
                    r.period_label, r.income, r.expense, r.profit,
                    r.change_pct if r.change_pct is not None else ""
                ])
        QMessageBox.information(self, "Успех", "CSV сохранён")

    def export_excel(self, d_from, d_to, filepath):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Аналитика"
        ws.append(["Период", "Доход", "Расход", "Прибыль", "Изменение %"])
        rows = self.analytics_ctrl.build_report(d_from, d_to)
        for r in rows:
            ws.append([r.period_label, r.income, r.expense, r.profit,
                       r.change_pct if r.change_pct is not None else None])
        wb.save(filepath)
        QMessageBox.information(self, "Успех", "Excel сохранён")