from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QMessageBox,
    QFrame, QInputDialog, QTabWidget,
    QDialog, QDialogButtonBox, QHeaderView,
    QScrollArea, QSizePolicy, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from datetime import datetime, timedelta
import calendar


class Module2Widget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.budget_ids = []
        self.categories = []

        self.init_ui()
        self.load_categories()
        self.load_budgets()
        self.load_plan_fact()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # =========================
        # HEADER
        # =========================
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
                border-radius: 15px;
                padding: 15px;
            }
        """)

        header_layout = QVBoxLayout()

        title = QLabel("📊 Модуль 2. Управление бюджетом")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        subtitle = QLabel("Планирование бюджета и контроль отклонений | План vs Факт | Настройки бюджета")
        subtitle.setStyleSheet("color: #a8b2c9; font-size: 13px;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header.setLayout(header_layout)

        main_layout.addWidget(header)

        # =========================
        # TOP PANEL
        # =========================
        top_panel = QFrame()
        top_panel.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        # ---- Тип периода ----
        period_type_label = QLabel("Период:")
        period_type_label.setStyleSheet("font-weight: bold; color: #2c3e50;")

        self.period_type_combo = QComboBox()
        self.period_type_combo.addItems(["Месяц", "Квартал", "Год", "Произвольный"])
        self.period_type_combo.setMinimumWidth(140)
        self.period_type_combo.setStyleSheet("padding: 6px; border-radius: 8px;")
        self.period_type_combo.currentTextChanged.connect(self.on_period_type_changed)

        # =========================
        # МЕСЯЦ
        # =========================
        self.month_container = QWidget()
        month_layout = QHBoxLayout(self.month_container)
        month_layout.setContentsMargins(0, 0, 0, 0)
        month_layout.setSpacing(8)

        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "Январь", "Февраль", "Март", "Апрель",
            "Май", "Июнь", "Июль", "Август",
            "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ])
        self.month_combo.setMinimumWidth(120)

        self.year_for_month = QComboBox()
        for y in range(2020, 2031):
            self.year_for_month.addItem(str(y))
        self.year_for_month.setMinimumWidth(80)

        month_layout.addWidget(QLabel("Месяц:"))
        month_layout.addWidget(self.month_combo)
        month_layout.addWidget(QLabel("Год:"))
        month_layout.addWidget(self.year_for_month)

        # =========================
        # КВАРТАЛ
        # =========================
        self.quarter_container = QWidget()
        quarter_layout = QHBoxLayout(self.quarter_container)
        quarter_layout.setContentsMargins(0, 0, 0, 0)
        quarter_layout.setSpacing(8)

        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems([
            "1-й квартал", "2-й квартал",
            "3-й квартал", "4-й квартал"
        ])
        self.quarter_combo.setMinimumWidth(140)

        self.year_for_quarter = QComboBox()
        for y in range(2020, 2031):
            self.year_for_quarter.addItem(str(y))
        self.year_for_quarter.setMinimumWidth(80)

        quarter_layout.addWidget(QLabel("Квартал:"))
        quarter_layout.addWidget(self.quarter_combo)
        quarter_layout.addWidget(QLabel("Год:"))
        quarter_layout.addWidget(self.year_for_quarter)

        # =========================
        # ГОД
        # =========================
        self.year_container = QWidget()
        year_layout = QHBoxLayout(self.year_container)
        year_layout.setContentsMargins(0, 0, 0, 0)
        year_layout.setSpacing(8)

        self.year_only = QComboBox()
        for y in range(2020, 2031):
            self.year_only.addItem(str(y))
        self.year_only.setMinimumWidth(100)

        year_layout.addWidget(QLabel("Год:"))
        year_layout.addWidget(self.year_only)

        # =========================
        # CUSTOM
        # =========================
        self.custom_container = QWidget()
        custom_layout = QHBoxLayout(self.custom_container)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(8)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)

        custom_layout.addWidget(QLabel("С:"))
        custom_layout.addWidget(self.start_date)
        custom_layout.addWidget(QLabel("По:"))
        custom_layout.addWidget(self.end_date)

        # =========================
        # СКРЫВАЕМ ВСЁ КРОМЕ МЕСЯЦА
        # =========================
        self.quarter_container.hide()
        self.year_container.hide()
        self.custom_container.hide()

        # =========================
        # КНОПКА
        # =========================
        refresh_btn = QPushButton("🔄 Применить")
        refresh_btn.setMinimumWidth(120)
        refresh_btn.clicked.connect(self.refresh_all)

        # =========================
        # LAYOUT С ФИКСОМ РАСТЯЖЕНИЯ
        # =========================
        top_layout.addWidget(period_type_label)
        top_layout.addWidget(self.period_type_combo)

        top_layout.addWidget(self.month_container)
        top_layout.addWidget(self.quarter_container)
        top_layout.addWidget(self.year_container)
        top_layout.addWidget(self.custom_container)

        top_layout.addStretch()
        top_layout.addWidget(refresh_btn)

        top_panel.setLayout(top_layout)
        main_layout.addWidget(top_panel)

        # =========================
        # TAB WIDGET
        # =========================
        self.tab_widget = QTabWidget()

        self.budget_tab = QWidget()
        self.setup_budget_tab()
        self.tab_widget.addTab(self.budget_tab, "📋 Бюджеты")

        self.plan_fact_tab = QWidget()
        self.setup_plan_fact_tab()
        self.tab_widget.addTab(self.plan_fact_tab, "📊 План vs Факт")

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)
    def on_period_type_changed(self):
        """При изменении типа периода показываем соответствующий контейнер"""
        period_type = self.period_type_combo.currentText()

        self.month_container.hide()
        self.quarter_container.hide()
        self.year_container.hide()
        self.custom_container.hide()

        if period_type == "Месяц":
            self.month_container.show()
        elif period_type == "Квартал":
            self.quarter_container.show()
        elif period_type == "Год":
            self.year_container.show()
        else:  # Произвольный
            self.custom_container.show()

    def get_period_dates(self):
        """Получение дат начала и конца периода"""
        period_type = self.period_type_combo.currentText()

        if period_type == "Месяц":
            year = int(self.year_for_month.currentText())
            month = self.month_combo.currentIndex() + 1

            # Первый день месяца
            start_date = f"{year}-{month:02d}-01"

            # Последний день месяца
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"

            return {
                'start': start_date,
                'end': end_date,
                'display': f"{self.month_combo.currentText()} {year}"
            }

        elif period_type == "Квартал":
            year = int(self.year_for_quarter.currentText())
            quarter = self.quarter_combo.currentIndex() + 1

            if quarter == 1:
                start_date = f"{year}-01-01"
                end_date = f"{year}-03-31"
            elif quarter == 2:
                start_date = f"{year}-04-01"
                end_date = f"{year}-06-30"
            elif quarter == 3:
                start_date = f"{year}-07-01"
                end_date = f"{year}-09-30"
            else:
                start_date = f"{year}-10-01"
                end_date = f"{year}-12-31"

            return {
                'start': start_date,
                'end': end_date,
                'display': f"{self.quarter_combo.currentText()} {year}"
            }

        elif period_type == "Год":
            year = int(self.year_only.currentText())
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"

            return {
                'start': start_date,
                'end': end_date,
                'display': f"{year} год"
            }

        else:  # Произвольный период
            start_qdate = self.start_date.date()
            end_qdate = self.end_date.date()

            start_date = f"{start_qdate.year()}-{start_qdate.month():02d}-{start_qdate.day():02d}"
            end_date = f"{end_qdate.year()}-{end_qdate.month():02d}-{end_qdate.day():02d}"

            return {
                'start': start_date,
                'end': end_date,
                'display': f"{start_date} – {end_date}"
            }

    def setup_budget_tab(self):
        """Настройка вкладки Бюджеты с красивой таблицей"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Таблица бюджетов
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels([
            "Категория", "Тип", "Плановая сумма (₽)", "Действия"
        ])

        # Стиль таблицы
        self.budget_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 12px;
                gridline-color: #e1e8ed;
                alternate-background-color: #f8f9fc;
                border: 1px solid #e1e8ed;
            }
            QTableWidget::item {
                padding: 16px 12px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fc, stop:1 #f0f2f5);
                padding: 14px 10px;
                border: none;
                border-bottom: 2px solid #3498db;
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
            }
            QHeaderView::section:hover {
                background: #e8ecf1;
            }
        """)

        # Настройка заголовка
        header = self.budget_table.horizontalHeader()
        header.setStretchLastSection(True)  # Последняя колонка растягивается
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Устанавливаем ширину колонок
        self.budget_table.setColumnWidth(0, 250)  # Категория
        self.budget_table.setColumnWidth(1, 100)  # Тип
        self.budget_table.setColumnWidth(2, 180)  # Плановая сумма

        # Настройка высоты строк
        self.budget_table.verticalHeader().setDefaultSectionSize(70)
        self.budget_table.verticalHeader().setMinimumSectionSize(70)
        self.budget_table.verticalHeader().setVisible(False)

        # Настройка выделения
        self.budget_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.budget_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.setWordWrap(False)
        self.budget_table.setSortingEnabled(True)

        # Запрещаем редактирование
        self.budget_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.budget_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        add_btn = QPushButton("➕ Добавить бюджет")
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: #1e8449;
            }
        """)
        add_btn.clicked.connect(self.show_add_dialog)

        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2471a3;
            }
        """)
        edit_btn.clicked.connect(self.edit_budget)

        delete_btn = QPushButton("🗑 Удалить")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ec7063, stop:1 #e74c3c);
            }
            QPushButton:pressed {
                background: #a93226;
            }
        """)
        delete_btn.clicked.connect(self.delete_budget)

        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Добавляем информационную строку
        info_label = QLabel("💡 Подсказка: Дважды кликните на сумме для быстрого редактирования")
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 11px;
                padding: 8px;
                background: #ecf0f1;
                border-radius: 6px;
            }
        """)
        layout.addWidget(info_label)

        self.budget_tab.setLayout(layout)

    def setup_plan_fact_tab(self):
        """Настройка вкладки План vs Факт"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 20)

        # Информационная панель
        info_widget = QFrame()
        info_widget.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 10px; }")

        info_layout = QHBoxLayout()

        self.plan_fact_records = QLabel("📊 Всего записей: 0")
        self.plan_fact_records.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: bold;")

        self.total_plan_label = QLabel("Общий план: 0 ₽")
        self.total_plan_label.setStyleSheet("color: #3498db; font-size: 13px; font-weight: bold;")

        self.total_fact_label = QLabel("Общий факт: 0 ₽")
        self.total_fact_label.setStyleSheet("color: #2ecc71; font-size: 13px; font-weight: bold;")

        self.total_diff_label = QLabel("Отклонение: 0 ₽")
        self.total_diff_label.setStyleSheet("color: #2ecc71; font-size: 13px; font-weight: bold;")

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
                border-radius: 10px;
                gridline-color: #e1e8ed;
                alternate-background-color: #fafbfc;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QHeaderView::section {
                background: #f8f9fc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e1e8ed;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        self.plan_fact_table.setAlternatingRowColors(True)
        self.plan_fact_table.verticalHeader().setVisible(False)

        # Настройка ширины столбцов
        header = self.plan_fact_table.horizontalHeader()
        self.plan_fact_table.setColumnWidth(0, 200)
        self.plan_fact_table.setColumnWidth(1, 80)
        self.plan_fact_table.setColumnWidth(2, 120)
        self.plan_fact_table.setColumnWidth(3, 120)
        self.plan_fact_table.setColumnWidth(4, 140)
        self.plan_fact_table.setColumnWidth(5, 100)
        self.plan_fact_table.setColumnWidth(6, 160)

        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.plan_fact_table.setWordWrap(True)
        self.plan_fact_table.setMinimumHeight(350)
        self.plan_fact_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(self.plan_fact_table)

        # График
        chart_card = QFrame()
        chart_card.setStyleSheet("QFrame { background: white; border-radius: 12px; padding: 15px; }")
        chart_card.setMinimumHeight(450)

        chart_layout = QVBoxLayout()
        chart_title = QLabel("📊 План vs Факт по категориям")
        chart_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;")
        chart_layout.addWidget(chart_title)

        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        chart_layout.addWidget(self.canvas)
        chart_card.setLayout(chart_layout)
        layout.addWidget(chart_card)

        layout.addStretch()

        scroll_area.setWidget(container)

        main_layout = QVBoxLayout(self.plan_fact_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def load_categories(self):
        """Загрузка всех категорий"""
        try:
            rows = self.controller.execute(
                "SELECT id, name, type FROM categories",
                fetch=True
            )

            self.categories = []
            for cid, name, ctype in rows:
                self.categories.append({
                    'id': cid,
                    'name': name,
                    'type': 'Доход' if ctype == 'income' else 'Расход',
                    'type_en': ctype
                })
        except Exception as e:
            print(f"Ошибка загрузки категорий: {e}")

    def load_budgets(self):
        """Загрузка бюджетов (плановых сумм)"""
        try:
            dates = self.get_period_dates()

            rows = self.controller.execute("""
                SELECT 
                    b.id,
                    c.id as cat_id,
                    c.name,
                    c.type,
                    b.planned_amount
                FROM budgets b
                JOIN categories c ON c.id = b.category_id
                WHERE b.period_start = %s AND b.period_end = %s
                ORDER BY c.type DESC, c.name
            """, (dates['start'], dates['end']), fetch=True)

            self.budget_table.setRowCount(len(rows))
            self.budget_ids = []

            for i, (bid, cat_id, cat_name, cat_type, plan) in enumerate(rows):
                self.budget_ids.append(bid)
                type_label = "Доход" if cat_type == 'income' else "Расход"

                # Цвет для типа
                type_color = "#27ae60" if cat_type == 'income' else "#e74c3c"
                type_icon = "💰" if cat_type == 'income' else "💸"

                # Категория с иконкой
                category_item = QTableWidgetItem(f"{type_icon}  {cat_name}")
                category_item.setToolTip(cat_name)

                # Тип с цветом
                type_item = QTableWidgetItem(type_label)
                type_item.setForeground(QColor(type_color))
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Сумма
                plan_item = QTableWidgetItem(f"{float(plan):,.2f} ₽")
                plan_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                plan_item.setToolTip(f"{float(plan):,.2f} рублей")

                # Устанавливаем жирный шрифт для сумм
                font = plan_item.font()
                font.setBold(True)
                plan_item.setFont(font)

                self.budget_table.setItem(i, 0, category_item)
                self.budget_table.setItem(i, 1, type_item)
                self.budget_table.setItem(i, 2, plan_item)

                # Устанавливаем высоту строки
                self.budget_table.setRowHeight(i, 70)

                # Кнопки действий
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 5, 5, 5)
                btn_layout.setSpacing(10)

                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(38, 38)
                edit_btn.setToolTip("Редактировать")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 8px;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #5dade2;
                    }
                    QPushButton:pressed {
                        background-color: #2471a3;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=i: self.edit_budget(r))

                delete_btn = QPushButton("🗑")
                delete_btn.setFixedSize(38, 38)
                delete_btn.setToolTip("Удалить")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 8px;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #ec7063;
                    }
                    QPushButton:pressed {
                        background-color: #a93226;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=i: self.delete_budget(r))

                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_widget.setLayout(btn_layout)

                self.budget_table.setCellWidget(i, 3, btn_widget)

        except Exception as e:
            print(f"Ошибка загрузки бюджетов: {e}")

    def load_plan_fact(self):
        """Загрузка сравнения план/факт"""
        try:
            dates = self.get_period_dates()

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

            for i, (cat_id, cat_name, cat_type, plan, fact) in enumerate(rows):
                plan_val = float(plan) if plan else 0
                fact_val = float(fact) if fact else 0
                diff_val = fact_val - plan_val
                diff_percent = (diff_val / plan_val * 100) if plan_val > 0 else (0 if fact_val == 0 else float('inf'))

                type_label = "Доход" if cat_type == 'income' else "Расход"
                type_icon = "💰" if cat_type == 'income' else "💸"

                if cat_type == 'income':
                    if diff_val >= 0:
                        status = "✅ Выполнено"
                        status_color = QColor("#27ae60")
                    else:
                        status = "❌ Не выполнено"
                        status_color = QColor("#e74c3c")
                    total_plan += plan_val
                    total_fact += fact_val
                else:
                    if diff_val <= 0:
                        status = "✅ В норме"
                        status_color = QColor("#27ae60")
                    else:
                        status = "⚠️ Превышение"
                        status_color = QColor("#e74c3c")
                    total_plan += plan_val
                    total_fact += fact_val

                self.plan_fact_table.setItem(i, 0, QTableWidgetItem(f"{type_icon} {cat_name}"))
                self.plan_fact_table.setItem(i, 1, QTableWidgetItem(type_label))
                self.plan_fact_table.setItem(i, 2, QTableWidgetItem(f"{plan_val:,.2f} ₽"))
                self.plan_fact_table.setItem(i, 3, QTableWidgetItem(f"{fact_val:,.2f} ₽"))

                diff_item = QTableWidgetItem(f"{diff_val:+,.2f} ₽")
                if diff_val > 0:
                    diff_item.setForeground(QColor("#e74c3c") if cat_type == 'expense' else QColor("#27ae60"))
                else:
                    diff_item.setForeground(QColor("#27ae60") if cat_type == 'expense' else QColor("#e74c3c"))
                self.plan_fact_table.setItem(i, 4, diff_item)

                percent_text = f"{diff_percent:+,.1f}%" if diff_percent != float('inf') else "∞%"
                percent_item = QTableWidgetItem(percent_text)
                if diff_percent > 0 and diff_percent != float('inf'):
                    percent_item.setForeground(QColor("#e74c3c") if cat_type == 'expense' else QColor("#27ae60"))
                elif diff_percent < 0:
                    percent_item.setForeground(QColor("#27ae60") if cat_type == 'expense' else QColor("#e74c3c"))
                self.plan_fact_table.setItem(i, 5, percent_item)

                status_item = QTableWidgetItem(status)
                status_item.setForeground(status_color)
                font = status_item.font()
                font.setBold(True)
                status_item.setFont(font)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_fact_table.setItem(i, 6, status_item)

            total_diff = total_fact - total_plan
            self.plan_fact_records.setText(f"📊 Всего записей: {len(rows)}")
            self.total_plan_label.setText(f"Общий план: {total_plan:,.2f} ₽")
            self.total_fact_label.setText(f"Общий факт: {total_fact:,.2f} ₽")

            if total_diff >= 0:
                self.total_diff_label.setText(f"Отклонение: {total_diff:+,.2f} ₽")
                self.total_diff_label.setStyleSheet("color: #2ecc71; font-size: 13px; font-weight: bold;")
            else:
                self.total_diff_label.setText(f"Отклонение: {total_diff:+,.2f} ₽")
                self.total_diff_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold;")

            self.draw_plan_fact_chart(rows)

        except Exception as e:
            print(f"Ошибка загрузки план/факт: {e}")

    def draw_plan_fact_chart(self, data):
        """Рисование графика"""
        self.figure.clear()

        if not data or len(data) == 0:
            ax = self.figure.add_subplot(111)
            ax.clear()
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', fontsize=14, color='gray')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)

        categories = []
        plans = []
        facts = []

        for row in data:
            cat_id, cat_name, cat_type, plan, fact = row
            short_name = cat_name[:12] + ".." if len(cat_name) > 14 else cat_name
            categories.append(short_name)
            plans.append(float(plan) if plan else 0)
            facts.append(float(fact) if fact else 0)

        combined_data = list(zip(categories, plans, facts))
        combined_data.sort(key=lambda x: x[1] + x[2], reverse=True)

        if combined_data:
            categories, plans, facts = zip(*combined_data)
            categories = list(categories)
            plans = list(plans)
            facts = list(facts)

        x = range(len(categories))
        width = 0.35

        ax.bar([i - width / 2 for i in x], plans, width,
               label='План', color='#3498db', alpha=0.8)
        ax.bar([i + width / 2 for i in x], facts, width,
               label='Факт', color='#2ecc71', alpha=0.8)

        max_val = max(max(plans) if plans else 0, max(facts) if facts else 0)

        if max_val == 0:
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', fontsize=12, color='gray',
                    transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return

        ax.set_ylabel('Сумма (₽)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Категории', fontsize=11, fontweight='bold')
        ax.set_title('План vs Факт по категориям', fontsize=12, fontweight='bold', pad=15)

        if len(categories) > 10:
            rotation = 90
            fontsize = 8
        elif len(categories) > 6:
            rotation = 45
            fontsize = 9
        else:
            rotation = 0
            fontsize = 10

        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=rotation, ha='center', fontsize=fontsize)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

        self.figure.tight_layout()

        if rotation == 90:
            self.figure.subplots_adjust(bottom=0.25)
        elif rotation == 45:
            self.figure.subplots_adjust(bottom=0.3)

        self.canvas.draw()

    def show_add_dialog(self):
        """Красивый диалог добавления бюджета"""
        if not self.categories:
            QMessageBox.warning(self, "Ошибка", "Нет доступных категорий")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Добавление бюджета")
        dialog.setFixedSize(600, 450)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fc, stop:1 #eef2f7);
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 13px;
                margin: 5px 0;
            }
            QComboBox, QLineEdit {
                background: white;
                border: 2px solid #e1e8ed;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2471a3;
            }
            QPushButton#cancel {
                background: #95a5a6;
            }
            QPushButton#cancel:hover {
                background: #7f8c8d;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("📊 Новый бюджет")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Категория
        category_layout = QVBoxLayout()
        category_layout.setSpacing(5)
        category_label = QLabel("Выберите категорию")
        category_label.setStyleSheet("color: #2c3e50;")
        category_combo = QComboBox()

        for cat in self.categories:
            icon = "💰" if cat['type_en'] == 'income' else "💸"
            category_combo.addItem(f"{icon}  {cat['name']} ({cat['type']})", cat['id'])

        category_combo.setMinimumHeight(40)
        category_layout.addWidget(category_label)
        category_layout.addWidget(category_combo)
        layout.addLayout(category_layout)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #e1e8ed; max-height: 1px;")
        layout.addWidget(line)

        # Плановая сумма
        amount_layout = QVBoxLayout()
        amount_layout.setSpacing(5)
        amount_label = QLabel("💰 Плановая сумма")
        amount_label.setStyleSheet("color: #2c3e50;")
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        amount_input.setMinimumHeight(40)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(amount_input)
        layout.addLayout(amount_layout)

        # Подсказка
        hint_label = QLabel("💡 Введите сумму в рублях. Например: 15000 или 15000.50")
        hint_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic; margin-top: 5px;")
        layout.addWidget(hint_label)

        layout.addStretch()

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ok_btn = QPushButton("✓ Сохранить")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_btn = QPushButton("✗ Отмена")
        cancel_btn.setObjectName("cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                cid = category_combo.currentData()
                amount_text = amount_input.text().strip().replace(',', '.')

                if not amount_text:
                    QMessageBox.warning(self, "Ошибка", "Введите сумму")
                    return

                amount = float(amount_text)

                if amount < 0:
                    QMessageBox.warning(self, "Ошибка", "Сумма не может быть отрицательной")
                    return

                dates = self.get_period_dates()

                existing = self.controller.execute("""
                    SELECT id FROM budgets 
                    WHERE category_id = %s AND period_start = %s AND period_end = %s
                """, (cid, dates['start'], dates['end']), fetch=True)

                if existing:
                    QMessageBox.warning(self, "Ошибка", "Бюджет для этой категории уже существует на выбранный период")
                    return

                self.controller.execute("""
                    INSERT INTO budgets (category_id, period_start, period_end, planned_amount)
                    VALUES (%s, %s, %s, %s)
                """, (cid, dates['start'], dates['end'], amount))

                self.refresh_all()

                # Красивое сообщение об успехе
                msg = QMessageBox(self)
                msg.setWindowTitle("Успех")
                msg.setText("✅ Бюджет успешно добавлен!")
                msg.setInformativeText(f"Категория: {category_combo.currentText()}\nСумма: {amount:,.2f} ₽")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()

            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную сумму (используйте точку или запятую)")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить бюджет: {e}")

    def edit_budget(self, row=None):
        """Красивый диалог редактирования бюджета"""
        if row is None:
            row = self.budget_table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите бюджет для редактирования")
            return

        bid = self.budget_ids[row]
        category_name = self.budget_table.item(row, 0).text()
        current_amount_text = self.budget_table.item(row, 2).text().replace(" ₽", "").replace(",", "")
        current_amount = float(current_amount_text) if current_amount_text else 0

        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Редактирование бюджета")
        dialog.setFixedSize(600, 450)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fc, stop:1 #eef2f7);
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 13px;
                margin: 5px 0;
            }
            QLineEdit {
                background: white;
                border: 2px solid #e1e8ed;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: #1e8449;
            }
            QPushButton#cancel {
                background: #95a5a6;
            }
            QPushButton#cancel:hover {
                background: #7f8c8d;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("✏️ Редактирование бюджета")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Информация о категории
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #ecf0f1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        category_info = QLabel(f"📁 Категория: {category_name}")
        category_info.setStyleSheet("color: #2c3e50; font-size: 13px;")
        info_layout.addWidget(category_info)

        layout.addWidget(info_frame)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #e1e8ed; max-height: 1px;")
        layout.addWidget(line)

        # Плановая сумма
        amount_layout = QVBoxLayout()
        amount_layout.setSpacing(5)
        amount_label = QLabel("💰 Плановая сумма")
        amount_label.setStyleSheet("color: #2c3e50;")
        amount_input = QLineEdit()
        amount_input.setText(f"{current_amount:,.2f}")
        amount_input.setMinimumHeight(40)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(amount_input)
        layout.addLayout(amount_layout)

        # Подсказка
        hint_label = QLabel("💡 Введите новую сумму в рублях")
        hint_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic; margin-top: 5px;")
        layout.addWidget(hint_label)

        layout.addStretch()

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ok_btn = QPushButton("✓ Сохранить")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_btn = QPushButton("✗ Отмена")
        cancel_btn.setObjectName("cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                amount_text = amount_input.text().strip().replace(',', '.')

                if not amount_text:
                    QMessageBox.warning(self, "Ошибка", "Введите сумму")
                    return

                new_amount = float(amount_text)

                if new_amount < 0:
                    QMessageBox.warning(self, "Ошибка", "Сумма не может быть отрицательной")
                    return

                self.controller.execute(
                    "UPDATE budgets SET planned_amount=%s WHERE id=%s",
                    (new_amount, bid)
                )

                self.refresh_all()

                # Красивое сообщение об успехе
                msg = QMessageBox(self)
                msg.setWindowTitle("Успех")
                msg.setText("✅ Бюджет успешно обновлён!")
                msg.setInformativeText(f"Категория: {category_name}\nНовая сумма: {new_amount:,.2f} ₽")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()

            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить: {e}")

    def delete_budget(self, row=None):
        """Удаление выбранного бюджета"""
        if row is None:
            row = self.budget_table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите бюджет для удаления")
            return

        bid = self.budget_ids[row]
        category = self.budget_table.item(row, 0).text()

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить бюджет для категории '{category}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.execute("DELETE FROM budgets WHERE id=%s", (bid,))
                self.refresh_all()
                QMessageBox.information(self, "Успех", "Бюджет удалён!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")

    def refresh_all(self):
        """Обновление всех данных"""
        self.load_budgets()
        self.load_plan_fact()

    def resizeEvent(self, event):
        """При изменении размера окна перерисовываем график"""
        super().resizeEvent(event)
        if hasattr(self, 'canvas'):
            self.load_plan_fact()