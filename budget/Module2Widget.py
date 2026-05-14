from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel,
    QComboBox, QFrame, QTabWidget, QHeaderView,
    QDateEdit, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

import calendar

from .dialogs import BudgetAddDialog, BudgetEditDialog
from .plan_fact import PlanFactTab


class Module2Widget(QWidget):
    """Модуль 2. Управление бюджетом"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.budget_ids = []
        self.categories = []
        self.setStyleSheet("background-color: #F8FAFC;")

        self.init_ui()
        self.load_categories()
        self.load_budgets()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # ЗАГОЛОВОК
        header = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.addWidget(
            QLabel("Модуль 2. Управление бюджетом",
                   styleSheet="font-size: 24px; font-weight: bold; color: #1E293B;"))
        title_vbox.addWidget(QLabel("Планирование бюджета и контроль отклонений | План vs Факт",
                                    styleSheet="color: #64748B; font-size: 13px;"))

        header.addLayout(title_vbox)
        header.addStretch()
        main_layout.addLayout(header)

        # КАРТОЧКА ФИЛЬТРОВ
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        filter_layout.setContentsMargins(20, 15, 20, 15)

        # Тип периода
        period_label = QLabel("Период:")
        period_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")

        self.period_type_combo = QComboBox()
        self.period_type_combo.addItems(["Месяц", "Квартал", "Год", "Произвольный"])
        self.period_type_combo.setMinimumWidth(140)
        self.period_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #4F46E5;
            }
        """)
        self.period_type_combo.currentTextChanged.connect(self.on_period_type_changed)

        filter_layout.addWidget(period_label)
        filter_layout.addWidget(self.period_type_combo)

        # МЕСЯЦ
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

        for combo in [self.month_combo, self.year_for_month]:
            combo.setStyleSheet("""
                QComboBox {
                    padding: 8px 12px;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    background: white;
                    font-size: 13px;
                }
            """)

        month_layout.addWidget(QLabel("Месяц:"))
        month_layout.addWidget(self.month_combo)
        month_layout.addWidget(QLabel("Год:"))
        month_layout.addWidget(self.year_for_month)

        # КВАРТАЛ
        self.quarter_container = QWidget()
        quarter_layout = QHBoxLayout(self.quarter_container)
        quarter_layout.setContentsMargins(0, 0, 0, 0)
        quarter_layout.setSpacing(8)

        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems(["1-й квартал", "2-й квартал", "3-й квартал", "4-й квартал"])
        self.quarter_combo.setMinimumWidth(140)

        self.year_for_quarter = QComboBox()
        for y in range(2020, 2031):
            self.year_for_quarter.addItem(str(y))

        for combo in [self.quarter_combo, self.year_for_quarter]:
            combo.setStyleSheet("""
                QComboBox {
                    padding: 8px 12px;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    background: white;
                    font-size: 13px;
                }
            """)

        quarter_layout.addWidget(QLabel("Квартал:"))
        quarter_layout.addWidget(self.quarter_combo)
        quarter_layout.addWidget(QLabel("Год:"))
        quarter_layout.addWidget(self.year_for_quarter)

        # ГОД
        self.year_container = QWidget()
        year_layout = QHBoxLayout(self.year_container)
        year_layout.setContentsMargins(0, 0, 0, 0)
        year_layout.setSpacing(8)

        self.year_only = QComboBox()
        for y in range(2020, 2031):
            self.year_only.addItem(str(y))
        self.year_only.setMinimumWidth(100)
        self.year_only.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
        """)

        year_layout.addWidget(QLabel("Год:"))
        year_layout.addWidget(self.year_only)

        # ПРОИЗВОЛЬНЫЙ
        self.custom_container = QWidget()
        custom_layout = QHBoxLayout(self.custom_container)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(8)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("dd.MM.yyyy")

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("dd.MM.yyyy")

        for date_edit in [self.start_date, self.end_date]:
            date_edit.setStyleSheet("""
                QDateEdit {
                    padding: 8px 12px;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    background: white;
                    font-size: 13px;
                }
            """)

        custom_layout.addWidget(QLabel("С:"))
        custom_layout.addWidget(self.start_date)
        custom_layout.addWidget(QLabel("По:"))
        custom_layout.addWidget(self.end_date)

        # Добавляем контейнеры в layout
        filter_layout.addWidget(self.month_container)
        filter_layout.addWidget(self.quarter_container)
        filter_layout.addWidget(self.year_container)
        filter_layout.addWidget(self.custom_container)
        filter_layout.addStretch()

        # Кнопка обновления
        refresh_btn = QPushButton("🔄 Применить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6366F1;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_all)
        filter_layout.addWidget(refresh_btn)

        filter_card.setLayout(filter_layout)
        main_layout.addWidget(filter_card)

        # Скрываем все кроме месяца по умолчанию
        self.quarter_container.hide()
        self.year_container.hide()
        self.custom_container.hide()

        # TAB WIDGET
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: transparent;
                border: none;
            }
            QTabBar::tab {
                background: #F1F5F9;
                color: #475569;
                padding: 10px 20px;
                border-radius: 8px 8px 0 0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #4F46E5;
            }
            QTabBar::tab:hover {
                background: #E2E8F0;
            }
        """)

        # Вкладка "Бюджеты"
        self.budget_tab = QWidget()
        self.setup_budget_tab()
        self.tab_widget.addTab(self.budget_tab, "📋 Бюджеты")

        # Вкладка "План vs Факт"
        self.plan_fact_tab = PlanFactTab(self.controller, self)
        self.tab_widget.addTab(self.plan_fact_tab, "📊 План vs Факт")

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

    def setup_budget_tab(self):
        """Настройка вкладки Бюджеты"""
        layout = QVBoxLayout(self.budget_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)

        # Таблица бюджетов
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels([
            "Категория", "Тип", "Плановая сумма (₽)", ""
        ])

        self.budget_table.setStyleSheet("""
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

        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.verticalHeader().setVisible(False)
        self.budget_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.budget_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Настройка ширины колонок
        self.budget_table.setColumnWidth(0, 250)
        self.budget_table.setColumnWidth(1, 100)
        self.budget_table.setColumnWidth(2, 180)
        self.budget_table.setColumnWidth(3, 100)

        self.budget_table.horizontalHeader().setStretchLastSection(False)

        layout.addWidget(self.budget_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        add_btn = QPushButton("➕ Добавить бюджет")
        edit_btn = QPushButton("✏️ Редактировать")
        delete_btn = QPushButton("🗑 Удалить")

        button_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
        """

        add_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #4F46E5;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #6366F1;
            }
        """)

        edit_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #F59E0B;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)

        delete_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)

        add_btn.clicked.connect(self.show_add_dialog)
        edit_btn.clicked.connect(self.edit_budget)
        delete_btn.clicked.connect(self.delete_budget)

        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Информационная строка
        info_label = QLabel("💡 Подсказка: Дважды кликните на строке для быстрого редактирования")
        info_label.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 11px;
                padding: 8px;
                background: #F1F5F9;
                border-radius: 6px;
            }
        """)
        layout.addWidget(info_label)

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
        else:
            self.custom_container.show()

    def get_period_dates(self):
        """Получение дат начала и конца периода"""
        period_type = self.period_type_combo.currentText()

        if period_type == "Месяц":
            year = int(self.year_for_month.currentText())
            month = self.month_combo.currentIndex() + 1
            last_day = calendar.monthrange(year, month)[1]

            return {
                'start': f"{year}-{month:02d}-01",
                'end': f"{year}-{month:02d}-{last_day}",
                'display': f"{self.month_combo.currentText()} {year}"
            }

        elif period_type == "Квартал":
            year = int(self.year_for_quarter.currentText())
            quarter = self.quarter_combo.currentIndex() + 1

            if quarter == 1:
                start, end = f"{year}-01-01", f"{year}-03-31"
            elif quarter == 2:
                start, end = f"{year}-04-01", f"{year}-06-30"
            elif quarter == 3:
                start, end = f"{year}-07-01", f"{year}-09-30"
            else:
                start, end = f"{year}-10-01", f"{year}-12-31"

            return {
                'start': start,
                'end': end,
                'display': f"{self.quarter_combo.currentText()} {year}"
            }

        elif period_type == "Год":
            year = int(self.year_only.currentText())
            return {
                'start': f"{year}-01-01",
                'end': f"{year}-12-31",
                'display': f"{year} год"
            }

        else:
            start = self.start_date.date()
            end = self.end_date.date()
            return {
                'start': f"{start.year()}-{start.month():02d}-{start.day():02d}",
                'end': f"{end.year()}-{end.month():02d}-{end.day():02d}",
                'display': f"{start.toString('dd.MM.yyyy')} – {end.toString('dd.MM.yyyy')}"
            }

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
                type_color = "#10B981" if cat_type == 'income' else "#EF4444"
                type_icon = "💰" if cat_type == 'income' else "💸"

                # Категория
                category_item = QTableWidgetItem(f"{type_icon} {cat_name}")

                # Тип
                type_item = QTableWidgetItem(type_label)
                type_item.setForeground(QColor(type_color))
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Сумма
                plan_val = float(plan) if plan else 0
                plan_item = QTableWidgetItem(f"{plan_val:,.2f} ₽")
                plan_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)

                font = plan_item.font()
                font.setBold(True)
                plan_item.setFont(font)

                self.budget_table.setItem(i, 0, category_item)
                self.budget_table.setItem(i, 1, type_item)
                self.budget_table.setItem(i, 2, plan_item)

                # Кнопки
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 5, 5, 5)
                btn_layout.setSpacing(8)

                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(20, 20)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F59E0B;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #D97706;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=i: self.edit_budget(r))

                delete_btn = QPushButton("🗑")
                delete_btn.setFixedSize(20, 20)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #EF4444;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #DC2626;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=i: self.delete_budget(r))

                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.addStretch()

                self.budget_table.setCellWidget(i, 3, btn_widget)
                self.budget_table.setRowHeight(i, 50)

        except Exception as e:
            print(f"Ошибка загрузки бюджетов: {e}")

    def show_add_dialog(self):
        """Показать диалог добавления бюджета"""
        dialog = BudgetAddDialog(self.categories, self.get_period_dates(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                dates = self.get_period_dates()

                # Проверка существования
                existing = self.controller.execute("""
                    SELECT id FROM budgets 
                    WHERE category_id = %s AND period_start = %s AND period_end = %s
                """, (dialog.category_id, dates['start'], dates['end']), fetch=True)

                if existing:
                    QMessageBox.warning(self, "Ошибка", "Бюджет для этой категории уже существует на выбранный период")
                    return

                self.controller.execute("""
                    INSERT INTO budgets (category_id, period_start, period_end, planned_amount)
                    VALUES (%s, %s, %s, %s)
                """, (dialog.category_id, dates['start'], dates['end'], dialog.amount))

                self.refresh_all()
                QMessageBox.information(self, "Успех", f"✅ Бюджет успешно добавлен!\nСумма: {dialog.amount:,.2f} ₽")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить бюджет: {e}")

    def edit_budget(self, row=None):
        """Редактирование бюджета"""
        if row is None:
            row = self.budget_table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите бюджет для редактирования")
            return

        bid = self.budget_ids[row]
        category_name = self.budget_table.item(row, 0).text()
        current_amount_text = self.budget_table.item(row, 2).text().replace(" ₽", "").replace(",", "")
        current_amount = float(current_amount_text) if current_amount_text else 0

        dialog = BudgetEditDialog(category_name, current_amount, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.controller.execute(
                    "UPDATE budgets SET planned_amount=%s WHERE id=%s",
                    (dialog.amount, bid)
                )
                self.refresh_all()
                QMessageBox.information(self, "Успех",
                                        f"✅ Бюджет успешно обновлён!\nНовая сумма: {dialog.amount:,.2f} ₽")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить: {e}")

    def delete_budget(self, row=None):
        """Удаление бюджета"""
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
                QMessageBox.information(self, "Успех", "✅ Бюджет удалён!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")

    def refresh_all(self):
        """Обновление всех данных"""
        self.load_budgets()
        self.plan_fact_tab.load_data(self.get_period_dates())