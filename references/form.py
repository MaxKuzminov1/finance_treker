from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
    QScrollArea, QWidget
)
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from datetime import datetime


class TransactionForm(QDialog):
    transaction_saved = pyqtSignal()

    def __init__(self, controller, transaction_id=None):
        super().__init__()
        self.controller = controller
        self.transaction_id = transaction_id

        self.setWindowTitle("✏️ Редактирование операции" if transaction_id else "➕ Добавление операции")
        self.setModal(True)
        self.resize(1000, 800)
        self.setMinimumSize(900, 700)

        # Явный цвет текста для всей формы
        self.setStyleSheet("background-color: #F8FAFC; color: #1E293B;")

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.categories = self.controller.get_categories()

        self.init_ui()

        if transaction_id is not None:
            self.load_transaction_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        header = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.addWidget(
            QLabel("✏️ Редактирование операции" if self.transaction_id else "➕ Добавление операции",
                   styleSheet="font-size: 24px; font-weight: bold; color: #1E293B;"))
        title_vbox.addWidget(QLabel("Заполните информацию о транзакции",
                                    styleSheet="color: #64748B; font-size: 13px;"))

        header.addLayout(title_vbox)
        header.addStretch()
        main_layout.addLayout(header)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #F1F5F9; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 5px; min-height: 30px; }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
        """)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(0, 0, 0, 0)

        info_frame = QFrame()
        info_frame.setStyleSheet("QFrame { background: white; border-radius: 12px; border: 1px solid #E2E8F0; }")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(15)

        # --- ОСНОВНЫЕ ПОЛЯ (Уменьшен padding, добавлен min-height) ---
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_label = QLabel("Тип операции")
        type_label.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; min-width: 120px;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["💰 Доход", "💸 Расход"])
        self.type_combo.setStyleSheet("""
            QComboBox { padding: 5px 12px; min-height: 30px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; color: #1E293B; min-width: 200px; font-size: 13px; }
            QComboBox:hover, QComboBox:focus { border-color: #4F46E5; }
        """)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        info_layout.addWidget(type_widget)

        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_label = QLabel("Дата операции")
        date_label.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; min-width: 120px;")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setStyleSheet("""
            QDateEdit { padding: 5px 12px; min-height: 30px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; color: #1E293B; min-width: 200px; font-size: 13px; }
            QDateEdit:hover { border-color: #4F46E5; }
        """)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        info_layout.addWidget(date_widget)

        amount_widget = QWidget()
        amount_layout = QHBoxLayout(amount_widget)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_label = QLabel("Общая сумма")
        amount_label.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; min-width: 120px;")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setStyleSheet("""
            QLineEdit { padding: 5px 12px; min-height: 30px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; color: #1E293B; min-width: 200px; font-size: 13px; }
            QLineEdit:focus { border-color: #4F46E5; }
        """)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        amount_layout.addStretch()
        info_layout.addWidget(amount_widget)

        comment_widget = QWidget()
        comment_layout = QHBoxLayout(comment_widget)
        comment_layout.setContentsMargins(0, 0, 0, 0)
        comment_label = QLabel("Комментарий")
        comment_label.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; min-width: 120px;")
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Введите комментарий (необязательно)...")
        self.comment_input.setStyleSheet("""
            QLineEdit { padding: 5px 12px; min-height: 30px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; color: #1E293B; min-width: 300px; font-size: 13px; }
            QLineEdit:focus { border-color: #4F46E5; }
        """)
        comment_layout.addWidget(comment_label)
        comment_layout.addWidget(self.comment_input)
        comment_layout.addStretch()
        info_layout.addWidget(comment_widget)

        container_layout.addWidget(info_frame)

        # --- ТАБЛИЦА КАТЕГОРИЙ ---
        categories_card = QFrame()
        categories_card.setStyleSheet("QFrame { background: white; border-radius: 12px; border: 1px solid #E2E8F0; }")
        categories_layout = QVBoxLayout(categories_card)
        categories_layout.setContentsMargins(20, 20, 20, 20)
        categories_layout.setSpacing(15)

        categories_header = QHBoxLayout()
        categories_label = QLabel("📂 Распределение по категориям")
        categories_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        categories_header.addWidget(categories_label)
        categories_header.addStretch()
        categories_layout.addLayout(categories_header)

        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels(["Категория", "Сумма (₽)", ""])
        self.setup_table_style(self.categories_table)
        self.categories_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.categories_table.setColumnWidth(1, 150)
        self.categories_table.setColumnWidth(2, 60)
        self.categories_table.setMinimumHeight(150)
        self.categories_table.setMaximumHeight(250)
        categories_layout.addWidget(self.categories_table)

        self.add_category_btn = QPushButton("+ Добавить категорию")
        self.add_category_btn.setStyleSheet("""
            QPushButton { background-color: #4F46E5; color: white; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #6366F1; }
        """)
        self.add_category_btn.clicked.connect(self.add_category_row)
        categories_layout.addWidget(self.add_category_btn)

        container_layout.addWidget(categories_card)

        # --- ТАБЛИЦА ПЛАТЕЖЕЙ ---
        payments_card = QFrame()
        payments_card.setStyleSheet("QFrame { background: white; border-radius: 12px; border: 1px solid #E2E8F0; }")
        payments_layout = QVBoxLayout(payments_card)
        payments_layout.setContentsMargins(20, 20, 20, 20)
        payments_layout.setSpacing(15)

        payments_header = QHBoxLayout()
        payments_label = QLabel("💳 График платежей")
        payments_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        payments_header.addWidget(payments_label)
        payments_header.addStretch()
        payments_layout.addLayout(payments_header)

        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(3)
        self.payments_table.setHorizontalHeaderLabels(["Дата платежа", "Сумма (₽)", ""])
        self.setup_table_style(self.payments_table)
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.payments_table.setColumnWidth(1, 150)
        self.payments_table.setColumnWidth(2, 60)
        self.payments_table.setMinimumHeight(150)
        self.payments_table.setMaximumHeight(250)
        payments_layout.addWidget(self.payments_table)

        self.add_payment_btn = QPushButton("+ Добавить платеж")
        self.add_payment_btn.setStyleSheet("""
            QPushButton { background-color: #4F46E5; color: white; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #6366F1; }
        """)
        self.add_payment_btn.clicked.connect(self.add_payment_row)
        payments_layout.addWidget(self.add_payment_btn)

        container_layout.addWidget(payments_card)

        info_panel = QFrame()
        info_panel.setStyleSheet("QFrame { background: #F1F5F9; border-radius: 12px; border: 1px solid #E2E8F0; }")
        info_panel_layout = QHBoxLayout(info_panel)
        info_panel_layout.setContentsMargins(20, 15, 20, 15)

        self.total_categories_label = QLabel("📊 Сумма по категориям: 0.00 ₽")
        self.total_categories_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 13px;")

        self.total_payments_label = QLabel("💳 Сумма по платежам: 0.00 ₽")
        self.total_payments_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 13px;")

        info_panel_layout.addWidget(self.total_categories_label)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(self.total_payments_label)

        container_layout.addWidget(info_panel)
        container_layout.addStretch()
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

        # --- КНОПКИ ВНИЗУ ---
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.save_btn = QPushButton("✓ Сохранить")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: rgb(15, 23, 42);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgb(30, 41, 59);
            }
        """)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.clicked.connect(self.save)

        self.cancel_btn = QPushButton("✗ Отмена")
        self.cancel_btn.setStyleSheet("""
            QPushButton { background: white; color: #475569; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 30px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background: #F1F5F9; border-color: #94A3B8; }
        """)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setMinimumWidth(150)
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        self.add_category_row()
        self.add_payment_row()
        self.update_totals()

    def setup_table_style(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            QTableWidget::item { padding: 10px; color: #1E293B; }
            QTableWidget::item:selected { background-color: #EEF2FF; color: #4F46E5; }
            QHeaderView::section {
                background: #F8FAFC;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: bold;
                color: #475569;
                font-size: 12px;
            }
        """)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def on_type_changed(self):
        self.update_totals()

    def add_category_row(self):
        row = self.categories_table.rowCount()
        self.categories_table.insertRow(row)

        cat_combo = QComboBox()
        for cat in self.categories:
            cat_combo.addItem(f"{cat['name']}", cat['id'])
        # ИСПРАВЛЕНИЕ: Уменьшен padding, добавлен min-height
        cat_combo.setStyleSheet("""
            QComboBox { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; }
        """)
        self.categories_table.setCellWidget(row, 0, cat_combo)

        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        # ИСПРАВЛЕНИЕ: Уменьшен padding, добавлен min-height
        amount_input.setStyleSheet("""
            QLineEdit { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; }
            QLineEdit:focus { border-color: #4F46E5; }
        """)
        amount_input.textChanged.connect(self.update_totals)
        self.categories_table.setCellWidget(row, 1, amount_input)

        delete_btn = QPushButton("✗")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton { background-color: #EF4444; color: white; border: none; border-radius: 6px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #DC2626; }
        """)
        delete_btn.clicked.connect(lambda: self.delete_category_row(row))
        self.categories_table.setCellWidget(row, 2, delete_btn)

        self.categories_table.setRowHeight(row, 45)

    def delete_category_row(self, row):
        self.categories_table.removeRow(row)
        self.update_totals()

    def add_payment_row(self):
        row = self.payments_table.rowCount()
        self.payments_table.insertRow(row)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        date_edit.setDisplayFormat("dd.MM.yyyy")
        # ИСПРАВЛЕНИЕ: Уменьшен padding, добавлен min-height
        date_edit.setStyleSheet("""
            QDateEdit { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; }
        """)
        self.payments_table.setCellWidget(row, 0, date_edit)

        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        # ИСПРАВЛЕНИЕ: Уменьшен padding, добавлен min-height
        amount_input.setStyleSheet("""
            QLineEdit { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; }
            QLineEdit:focus { border-color: #4F46E5; }
        """)
        amount_input.textChanged.connect(self.update_totals)
        self.payments_table.setCellWidget(row, 1, amount_input)

        delete_btn = QPushButton("✗")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton { background-color: #EF4444; color: white; border: none; border-radius: 6px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #DC2626; }
        """)
        delete_btn.clicked.connect(lambda: self.delete_payment_row(row))
        self.payments_table.setCellWidget(row, 2, delete_btn)

        self.payments_table.setRowHeight(row, 45)

    def delete_payment_row(self, row):
        self.payments_table.removeRow(row)
        self.update_totals()

    def update_totals(self):
        total_categories = 0
        total_payments = 0

        for row in range(self.categories_table.rowCount()):
            amount_input = self.categories_table.cellWidget(row, 1)
            if amount_input:
                try:
                    amount = float(amount_input.text().replace(",", "."))
                    total_categories += amount
                except:
                    pass

        for row in range(self.payments_table.rowCount()):
            amount_input = self.payments_table.cellWidget(row, 1)
            if amount_input:
                try:
                    amount = float(amount_input.text().replace(",", "."))
                    total_payments += amount
                except:
                    pass

        type_color = "#10B981" if self.type_combo.currentIndex() == 0 else "#EF4444"

        self.total_categories_label.setText(f"📊 Сумма по категориям: {total_categories:,.2f} ₽")
        self.total_categories_label.setStyleSheet(f"font-weight: bold; color: {type_color}; font-size: 13px;")

        self.total_payments_label.setText(f"💳 Сумма по платежам: {total_payments:,.2f} ₽")
        self.total_payments_label.setStyleSheet(f"font-weight: bold; color: {type_color}; font-size: 13px;")

    def load_transaction_data(self):
        transaction = self.controller.get_by_id(self.transaction_id)
        if not transaction:
            QMessageBox.warning(self, "Ошибка", "Транзакция не найдена")
            self.reject()
            return

        if transaction["type"] == "income":
            self.type_combo.setCurrentIndex(0)
        else:
            self.type_combo.setCurrentIndex(1)

        date_value = transaction["date"]
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, "%Y-%m-%d").date()
        elif isinstance(date_value, datetime):
            date_obj = date_value.date()
        else:
            date_obj = date_value
        self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))

        self.amount_input.setText(str(transaction["total_amount"]))

        if transaction.get("comment"):
            self.comment_input.setText(transaction["comment"])

        self.categories_table.setRowCount(0)
        for cat in transaction.get("categories", []):
            row = self.categories_table.rowCount()
            self.categories_table.insertRow(row)

            cat_combo = QComboBox()
            for c in self.categories:
                cat_combo.addItem(f"{c['name']}", c['id'])
                if c["id"] == cat["category_id"]:
                    cat_combo.setCurrentIndex(cat_combo.count() - 1)
            cat_combo.setStyleSheet(
                "QComboBox { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; }")
            self.categories_table.setCellWidget(row, 0, cat_combo)

            amount_input = QLineEdit()
            amount_input.setText(str(cat["amount"]))
            amount_input.setStyleSheet(
                "QLineEdit { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; } QLineEdit:focus { border-color: #4F46E5; }")
            amount_input.textChanged.connect(self.update_totals)
            self.categories_table.setCellWidget(row, 1, amount_input)

            delete_btn = QPushButton("✗")
            delete_btn.setFixedSize(28, 28)
            delete_btn.setStyleSheet(
                "QPushButton { background-color: #EF4444; color: white; border: none; border-radius: 6px; font-size: 12px; font-weight: bold; } QPushButton:hover { background-color: #DC2626; }")
            delete_btn.clicked.connect(lambda: self.delete_category_row(row))
            self.categories_table.setCellWidget(row, 2, delete_btn)
            self.categories_table.setRowHeight(row, 45)

        self.payments_table.setRowCount(0)
        for payment in transaction.get("payments", []):
            row = self.payments_table.rowCount()
            self.payments_table.insertRow(row)

            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)

            payment_date_value = payment["date"]
            if isinstance(payment_date_value, str):
                payment_date = datetime.strptime(payment_date_value, "%Y-%m-%d").date()
            elif isinstance(payment_date_value, datetime):
                payment_date = payment_date_value.date()
            else:
                payment_date = payment_date_value

            date_edit.setDate(QDate(payment_date.year, payment_date.month, payment_date.day))
            date_edit.setDisplayFormat("dd.MM.yyyy")
            date_edit.setStyleSheet(
                "QDateEdit { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; }")
            self.payments_table.setCellWidget(row, 0, date_edit)

            amount_input = QLineEdit()
            amount_input.setText(str(payment["amount"]))
            amount_input.setStyleSheet(
                "QLineEdit { padding: 4px 8px; min-height: 28px; border: 1px solid #CBD5E1; border-radius: 6px; background: white; color: #1E293B; font-size: 12px; } QLineEdit:focus { border-color: #4F46E5; }")
            amount_input.textChanged.connect(self.update_totals)
            self.payments_table.setCellWidget(row, 1, amount_input)

            delete_btn = QPushButton("✗")
            delete_btn.setFixedSize(28, 28)
            delete_btn.setStyleSheet(
                "QPushButton { background-color: #EF4444; color: white; border: none; border-radius: 6px; font-size: 12px; font-weight: bold; } QPushButton:hover { background-color: #DC2626; }")
            delete_btn.clicked.connect(lambda: self.delete_payment_row(row))
            self.payments_table.setCellWidget(row, 2, delete_btn)
            self.payments_table.setRowHeight(row, 45)

    def save(self):
        try:
            data = {}
            data["type"] = "income" if self.type_combo.currentIndex() == 0 else "expense"

            qdate = self.date_edit.date()
            data["date"] = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"

            try:
                data["total_amount"] = float(self.amount_input.text().replace(",", "."))
            except:
                QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
                return

            data["comment"] = self.comment_input.text()
            data["user_id"] = 1

            data["categories"] = []
            total_categories = 0

            for row in range(self.categories_table.rowCount()):
                cat_combo = self.categories_table.cellWidget(row, 0)
                amount_input = self.categories_table.cellWidget(row, 1)

                if cat_combo and amount_input:
                    try:
                        amount = float(amount_input.text().replace(",", "."))
                        if amount > 0:
                            data["categories"].append({
                                "category_id": cat_combo.currentData(),
                                "amount": amount
                            })
                            total_categories += amount
                    except:
                        pass

            data["payments"] = []
            total_payments = 0

            for row in range(self.payments_table.rowCount()):
                date_edit = self.payments_table.cellWidget(row, 0)
                amount_input = self.payments_table.cellWidget(row, 1)

                if date_edit and amount_input:
                    try:
                        amount = float(amount_input.text().replace(",", "."))
                        if amount > 0:
                            qdate_pay = date_edit.date()
                            pay_date = f"{qdate_pay.year()}-{qdate_pay.month():02d}-{qdate_pay.day():02d}"
                            data["payments"].append({
                                "date": pay_date,
                                "amount": amount
                            })
                            total_payments += amount
                    except:
                        pass

            if not data["categories"]:
                QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одну категорию")
                return

            if abs(total_categories - data["total_amount"]) > 0.01:
                reply = QMessageBox.question(
                    self,
                    "Предупреждение",
                    f"Сумма по категориям ({total_categories:,.2f} ₽) не совпадает с общей суммой ({data['total_amount']:,.2f} ₽).\n\nСохранить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            if self.transaction_id:
                self.controller.update(self.transaction_id, data)
                success_msg = "Операция успешно обновлена!"
            else:
                self.controller.create(data)
                success_msg = "Операция успешно добавлена!"

            QMessageBox.information(self, "Успех", f"✅ {success_msg}")
            self.transaction_saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Ошибка при сохранении: {str(e)}")