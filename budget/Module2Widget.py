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
        self.budget_counts = []
        self.budget_cat_ids = []
        self.categories = []

        # Секретный период для хранения шаблона "По умолчанию"
        self.TEMPLATE_START = '1999-01-01'
        self.TEMPLATE_END = '1999-12-31'

        self.setStyleSheet("background-color: #F3F4F6;")

        self.init_ui()
        self.load_categories()
        self.load_budgets()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ЗАГОЛОВОК
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        title = QLabel("Управление бюджетом")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px;")
        subtitle = QLabel("Планирование лимитов и анализ исполнения")
        subtitle.setStyleSheet("color: #64748B; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # КАРТОЧКА ФИЛЬТРОВ
        filter_card = QFrame()
        filter_card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(16)

        filter_layout.addWidget(QLabel("🗓️ Период:", styleSheet="font-weight: bold; color: #475569;"))

        combo_style = "QComboBox { padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px; background: #F8FAFC; }"
        self.period_type_combo = QComboBox()
        self.period_type_combo.addItems(["Месяц", "Квартал", "Год", "Произвольный"])
        self.period_type_combo.setStyleSheet(combo_style)
        self.period_type_combo.currentTextChanged.connect(self.on_period_type_changed)
        filter_layout.addWidget(self.period_type_combo)

        # Контейнер для динамических фильтров
        self.dynamic_filters = QWidget()
        self.dynamic_layout = QHBoxLayout(self.dynamic_filters)
        self.dynamic_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_layout.setSpacing(8)

        # Месяц (по умолчанию)
        self.month_combo = QComboBox()
        self.month_combo.addItems(
            ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
             "Декабрь"])
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.month_combo.setStyleSheet(combo_style)

        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(y) for y in range(current_year - 3, current_year + 4)])
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.setStyleSheet(combo_style)

        self.dynamic_layout.addWidget(self.month_combo)
        self.dynamic_layout.addWidget(self.year_combo)

        filter_layout.addWidget(self.dynamic_filters)

        # ВИЗУАЛЬНАЯ ПОДСКАЗКА (Опция 2)
        self.period_hint_lbl = QLabel("")
        self.period_hint_lbl.setStyleSheet("color: #D97706; font-size: 12px; font-weight: bold;")
        filter_layout.addWidget(self.period_hint_lbl)

        filter_layout.addStretch()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton { background: #4F46E5; color: white; border-radius: 6px; padding: 8px 20px; font-weight: bold; }
            QPushButton:hover { background: #4338CA; }
        """)
        refresh_btn.clicked.connect(self.refresh_all)
        filter_layout.addWidget(refresh_btn)

        main_layout.addWidget(filter_card)

        # TAB WIDGET
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { background: transparent; border: none; }
            QTabBar::tab { background: #E2E8F0; color: #64748B; padding: 10px 24px; margin-right: 4px; border-radius: 8px 8px 0 0; font-weight: bold; }
            QTabBar::tab:selected { background: white; color: #4F46E5; border-bottom: 3px solid #4F46E5; }
        """)

        self.budget_tab = QWidget()
        self.setup_budget_tab()
        self.tab_widget.addTab(self.budget_tab, "📋 Планирование")

        self.plan_fact_tab = PlanFactTab(self.controller, self)
        self.tab_widget.addTab(self.plan_fact_tab, "📊 Исполнение (План/Факт)")

        main_layout.addWidget(self.tab_widget)

    def setup_budget_tab(self):
        layout = QVBoxLayout(self.budget_tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        add_btn = QPushButton("➕ Добавить лимит")
        add_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; } QPushButton:hover { background: #059669; }")
        add_btn.clicked.connect(self.show_add_dialog)

        sec_btn_style = """
            QPushButton { background: white; color: #475569; border: 1px solid #CBD5E1; padding: 10px 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #F8FAFC; border-color: #94A3B8; }
        """

        copy_prev_btn = QPushButton("🔄 Из прошлого месяца")
        copy_prev_btn.setStyleSheet(sec_btn_style)
        copy_prev_btn.clicked.connect(self.copy_from_previous)
        copy_prev_btn.setToolTip("Работает только если выбран период 'Месяц'")

        save_def_btn = QPushButton("⭐ Сохранить как шаблон")
        save_def_btn.setStyleSheet(sec_btn_style)
        save_def_btn.clicked.connect(self.save_as_default)
        save_def_btn.setToolTip("Сохранить текущие суммы как базовый шаблон")

        load_def_btn = QPushButton("📥 Загрузить шаблон")
        load_def_btn.setStyleSheet(sec_btn_style)
        load_def_btn.clicked.connect(self.load_from_default)

        toolbar.addWidget(add_btn)
        toolbar.addWidget(copy_prev_btn)
        toolbar.addWidget(save_def_btn)
        toolbar.addWidget(load_def_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Таблица бюджетов
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels(["Категория", "Тип", "Плановая сумма (₽)", "Действия"])
        self.budget_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E2E8F0; border-radius: 12px; gridline-color: #F1F5F9; }
            QHeaderView::section { background: #F8FAFC; padding: 12px; border: none; border-bottom: 2px solid #E2E8F0; font-weight: bold; color: #475569; }
            QTableWidget::item { padding: 8px; }
        """)
        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.verticalHeader().setVisible(False)
        self.budget_table.verticalHeader().setDefaultSectionSize(55)
        self.budget_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.budget_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.budget_table.setColumnWidth(3, 100)

        layout.addWidget(self.budget_table)

    def _transfer_budgets(self, source_start, source_end, target_start, target_end):
        try:
            # Умный перенос: берем агрегированную сумму из источника
            source_budgets = self.controller.execute("""
                SELECT category_id, SUM(planned_amount) 
                FROM budgets 
                WHERE period_start >= %s AND period_end <= %s
                GROUP BY category_id
            """, (source_start, source_end), fetch=True)

            if not source_budgets:
                QMessageBox.information(self, "Инфо", "Нет данных для переноса.")
                return

            target_existing = self.controller.execute("""
                SELECT category_id FROM budgets 
                WHERE period_start >= %s AND period_end <= %s
            """, (target_start, target_end), fetch=True)
            existing_ids = {row[0] for row in target_existing}

            added_count = 0
            for cat_id, amount in source_budgets:
                if cat_id not in existing_ids:
                    self.controller.execute(
                        "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                        (cat_id, target_start, target_end, amount)
                    )
                    added_count += 1

            if added_count > 0:
                self.refresh_all()
                QMessageBox.information(self, "Успех", f"Успешно перенесено лимитов: {added_count}.")
            else:
                QMessageBox.information(self, "Инфо", "В текущем периоде уже установлены лимиты (дубликаты пропущены).")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при переносе: {e}")

    def copy_from_previous(self):
        if self.period_type_combo.currentText() != "Месяц":
            QMessageBox.warning(self, "Внимание", "Авто-перенос работает только когда в фильтре выбран 'Месяц'.")
            return
        dates = self.get_period_dates()
        current_start = QDate.fromString(dates['start'], "yyyy-MM-dd")
        prev_start_date = current_start.addMonths(-1)
        prev_year = prev_start_date.year()
        prev_month = prev_start_date.month()
        last_day = calendar.monthrange(prev_year, prev_month)[1]

        self._transfer_budgets(f"{prev_year}-{prev_month:02d}-01", f"{prev_year}-{prev_month:02d}-{last_day}",
                               dates['start'], dates['end'])

    def save_as_default(self):
        if self.budget_table.rowCount() == 0:
            QMessageBox.warning(self, "Внимание", "Добавьте лимиты, чтобы сохранить шаблон.")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Сделать текущие лимиты стандартными?\n\nЭто перезапишет старый шаблон.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                dates = self.get_period_dates()
                self.controller.execute("DELETE FROM budgets WHERE period_start = %s AND period_end = %s",
                                        (self.TEMPLATE_START, self.TEMPLATE_END))

                current = self.controller.execute("""
                    SELECT category_id, SUM(planned_amount) 
                    FROM budgets 
                    WHERE period_start >= %s AND period_end <= %s
                    GROUP BY category_id
                """, (dates['start'], dates['end']), fetch=True)

                for cat_id, amount in current:
                    self.controller.execute(
                        "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                        (cat_id, self.TEMPLATE_START, self.TEMPLATE_END, amount)
                    )
                QMessageBox.information(self, "Успех", "Шаблон успешно обновлен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")

    def load_from_default(self):
        dates = self.get_period_dates()
        self._transfer_budgets(self.TEMPLATE_START, self.TEMPLATE_END, dates['start'], dates['end'])

    def on_period_type_changed(self):
        for i in reversed(range(self.dynamic_layout.count())):
            self.dynamic_layout.itemAt(i).widget().setParent(None)

        period_type = self.period_type_combo.currentText()
        combo_style = "QComboBox { padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px; background: #F8FAFC; }"

        if period_type == "Месяц":
            self.month_combo = QComboBox()
            self.month_combo.addItems(
                ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
                 "Ноябрь", "Декабрь"])
            self.month_combo.setStyleSheet(combo_style)
            self.dynamic_layout.addWidget(self.month_combo)
            self.dynamic_layout.addWidget(self.year_combo)
            self.period_hint_lbl.setText("")

        elif period_type == "Квартал":
            self.quarter_combo = QComboBox()
            self.quarter_combo.addItems(["1-й квартал", "2-й квартал", "3-й квартал", "4-й квартал"])
            self.quarter_combo.setStyleSheet(combo_style)
            self.dynamic_layout.addWidget(self.quarter_combo)
            self.dynamic_layout.addWidget(self.year_combo)
            self.period_hint_lbl.setText("💡 Показана сумма всех лимитов внутри квартала")

        elif period_type == "Год":
            self.dynamic_layout.addWidget(self.year_combo)
            self.period_hint_lbl.setText("💡 Показана сумма всех лимитов внутри года")

        else:
            self.start_date = QDateEdit()
            self.end_date = QDateEdit()
            for de in [self.start_date, self.end_date]:
                de.setCalendarPopup(True)
                de.setDate(QDate.currentDate())
                de.setStyleSheet(combo_style.replace("QComboBox", "QDateEdit"))
            self.dynamic_layout.addWidget(QLabel("С:"))
            self.dynamic_layout.addWidget(self.start_date)
            self.dynamic_layout.addWidget(QLabel("По:"))
            self.dynamic_layout.addWidget(self.end_date)
            self.period_hint_lbl.setText("")

    def get_period_dates(self):
        period_type = self.period_type_combo.currentText()
        if period_type == "Месяц":
            year = int(self.year_combo.currentText())
            month = self.month_combo.currentIndex() + 1
            last_day = calendar.monthrange(year, month)[1]
            return {'start': f"{year}-{month:02d}-01", 'end': f"{year}-{month:02d}-{last_day}",
                    'display': f"{self.month_combo.currentText()} {year}"}
        elif period_type == "Квартал":
            year = int(self.year_combo.currentText())
            q = self.quarter_combo.currentIndex() + 1
            starts = [f"{year}-01-01", f"{year}-04-01", f"{year}-07-01", f"{year}-10-01"]
            ends = [f"{year}-03-31", f"{year}-06-30", f"{year}-09-30", f"{year}-12-31"]
            return {'start': starts[q - 1], 'end': ends[q - 1], 'display': f"{q}-й квартал {year}"}
        elif period_type == "Год":
            year = int(self.year_combo.currentText())
            return {'start': f"{year}-01-01", 'end': f"{year}-12-31", 'display': f"{year} год"}
        else:
            s, e = self.start_date.date(), self.end_date.date()
            return {'start': s.toString("yyyy-MM-dd"), 'end': e.toString("yyyy-MM-dd"),
                    'display': f"{s.toString('dd.MM.yyyy')} - {e.toString('dd.MM.yyyy')}"}

    def load_categories(self):
        try:
            rows = self.controller.execute("SELECT id, name, type FROM categories", fetch=True)
            self.categories = [
                {'id': r[0], 'name': r[1], 'type': 'Доход' if r[2] == 'income' else 'Расход', 'type_en': r[2]} for r in
                rows]
        except Exception as e:
            print(e)

    def load_budgets(self):
        try:
            dates = self.get_period_dates()
            # НОВЫЙ SQL: Суммирует все бюджеты, которые входят в выбранный период
            rows = self.controller.execute("""
                SELECT 
                    MIN(b.id), c.id, c.name, c.type, SUM(b.planned_amount), COUNT(b.id)
                FROM budgets b JOIN categories c ON c.id = b.category_id
                WHERE b.period_start >= %s AND b.period_end <= %s 
                GROUP BY c.id, c.name, c.type
                ORDER BY c.type DESC, c.name
            """, (dates['start'], dates['end']), fetch=True)

            self.budget_table.setRowCount(len(rows))
            self.budget_ids = []
            self.budget_counts = []
            self.budget_cat_ids = []

            for i, (bid, cat_id, cat_name, cat_type, plan, count) in enumerate(rows):
                self.budget_ids.append(bid)
                self.budget_counts.append(count)
                self.budget_cat_ids.append(cat_id)

                plan_val = float(plan) if plan else 0

                self.budget_table.setItem(i, 0, QTableWidgetItem(f"{'💰' if cat_type == 'income' else '💸'} {cat_name}"))
                type_item = QTableWidgetItem("Доход" if cat_type == 'income' else "Расход")
                type_item.setForeground(QColor("#10B981" if cat_type == 'income' else "#EF4444"))
                self.budget_table.setItem(i, 1, type_item)

                plan_item = QTableWidgetItem(f"{plan_val:,.2f} ₽")
                font = plan_item.font()
                font.setBold(True)
                plan_item.setFont(font)
                self.budget_table.setItem(i, 2, plan_item)

                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(8)
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)

                # Если сумма состоит из нескольких месяцев, блокируем простое редактирование
                if count > 1:
                    edit_btn.setDisabled(True)
                    edit_btn.setToolTip("Составной бюджет. Для редактирования переключитесь на период 'Месяц'.")
                    edit_btn.setStyleSheet(
                        "QPushButton { background: #F1F5F9; border-radius: 6px; color: transparent; }")
                else:
                    edit_btn.setStyleSheet(
                        "QPushButton { background: #F1F5F9; border-radius: 6px; } QPushButton:hover { background: #E2E8F0; }")
                    edit_btn.clicked.connect(lambda checked, r=i: self.edit_budget(r))

                delete_btn = QPushButton("🗑")
                delete_btn.setFixedSize(30, 30)
                delete_btn.setStyleSheet(
                    "QPushButton { background: #FEE2E2; color: #EF4444; border-radius: 6px; } QPushButton:hover { background: #FECACA; }")
                delete_btn.clicked.connect(lambda checked, r=i: self.delete_budget(r))

                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                self.budget_table.setCellWidget(i, 3, btn_widget)

        except Exception as e:
            print(f"Ошибка загрузки бюджетов: {e}")

    def show_add_dialog(self):
        period_type = self.period_type_combo.currentText()
        dialog = BudgetAddDialog(self.categories, self.get_period_dates(), period_type, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                dates = self.get_period_dates()

                # ЛОГИКА УМНОГО РАСПРЕДЕЛЕНИЯ (Опция 3)
                if dialog.allocation_method == 'divide':
                    year = int(self.year_combo.currentText())
                    if period_type == "Год":
                        months = list(range(1, 13))
                    elif period_type == "Квартал":
                        q = self.quarter_combo.currentIndex() + 1
                        start_m = (q - 1) * 3 + 1
                        months = [start_m, start_m + 1, start_m + 2]

                    div_amount = dialog.amount / len(months)
                    added = 0
                    for m in months:
                        last_day = calendar.monthrange(year, m)[1]
                        m_start = f"{year}-{m:02d}-01"
                        m_end = f"{year}-{m:02d}-{last_day}"

                        existing = self.controller.execute(
                            "SELECT id FROM budgets WHERE category_id = %s AND period_start = %s AND period_end = %s",
                            (dialog.category_id, m_start, m_end), fetch=True)
                        if not existing:
                            self.controller.execute(
                                "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                                (dialog.category_id, m_start, m_end, div_amount))
                            added += 1

                    QMessageBox.information(self, "Успех", f"Сумма разбита на {added} мес. (по {div_amount:,.2f} ₽)")
                else:
                    # Стандартное добавление
                    existing = self.controller.execute(
                        "SELECT id FROM budgets WHERE category_id = %s AND period_start = %s AND period_end = %s",
                        (dialog.category_id, dates['start'], dates['end']), fetch=True)
                    if existing:
                        QMessageBox.warning(self, "Ошибка",
                                            "Бюджет для этой категории на выбранный период уже существует")
                        return
                    self.controller.execute(
                        "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                        (dialog.category_id, dates['start'], dates['end'], dialog.amount))
                self.refresh_all()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_budget(self, row):
        bid = self.budget_ids[row]
        category_name = self.budget_table.item(row, 0).text()
        current_amount = float(self.budget_table.item(row, 2).text().replace(" ₽", "").replace(",", ""))

        dialog = BudgetEditDialog(category_name, current_amount, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.controller.execute("UPDATE budgets SET planned_amount=%s WHERE id=%s", (dialog.amount, bid))
            self.refresh_all()

    def delete_budget(self, row):
        category = self.budget_table.item(row, 0).text()
        count = self.budget_counts[row]
        cat_id = self.budget_cat_ids[row]

        msg = f"Удалить лимит '{category}'?"
        if count > 1:
            msg = f"Внимание! Внутри этого периода есть {count} отдельных записей для '{category}'.\nУдалить их все?"

        if QMessageBox.question(self, "Удаление", msg) == QMessageBox.StandardButton.Yes:
            dates = self.get_period_dates()
            # Умное удаление: сносим всё, что входит в текущий фильтр
            self.controller.execute("""
                DELETE FROM budgets 
                WHERE category_id = %s AND period_start >= %s AND period_end <= %s
            """, (cat_id, dates['start'], dates['end']))
            self.refresh_all()

    def refresh_all(self):
        self.load_budgets()
        self.plan_fact_tab.load_data(self.get_period_dates())