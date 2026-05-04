from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QWidget, QSpinBox
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QFont
from datetime import datetime


class TransactionForm(QDialog):
    def __init__(self, controller, transaction_id=None):
        super().__init__()
        self.controller = controller
        self.transaction_id = transaction_id

        self.setWindowTitle("Редактирование операции" if transaction_id else "Добавление операции")
        self.setModal(True)
        self.resize(750, 600)
        self.setMinimumSize(600, 500)

        self.categories = self.controller.get_categories()

        self.init_ui()

        # Если передан ID, загружаем данные для редактирования
        if transaction_id is not None:
            self.load_transaction_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Вкладки
        tabs = QTabWidget()

        # Вкладка "Основное"
        main_tab = QWidget()
        main_layout = QVBoxLayout()

        # Тип операции
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип операции:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["💰 Доход", "💸 Расход"])
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        main_layout.addLayout(type_layout)

        # Дата
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        main_layout.addLayout(date_layout)

        # Сумма
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Сумма:"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_layout.addWidget(self.amount_input)
        amount_layout.addStretch()
        main_layout.addLayout(amount_layout)

        # Комментарий
        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel("Комментарий:"))
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Введите комментарий...")
        comment_layout.addWidget(self.comment_input)
        comment_layout.addStretch()
        main_layout.addLayout(comment_layout)

        main_layout.addStretch()
        main_tab.setLayout(main_layout)

        # Вкладка "Категории"
        categories_tab = QWidget()
        categories_layout = QVBoxLayout()

        categories_layout.addWidget(QLabel("Распределение по категориям:"))

        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["Категория", "Сумма"])
        self.categories_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.categories_table.setAlternatingRowColors(True)
        categories_layout.addWidget(self.categories_table)

        btn_layout = QHBoxLayout()
        self.add_category_btn = QPushButton("➕ Добавить категорию")
        self.add_category_btn.clicked.connect(self.add_category_row)
        btn_layout.addWidget(self.add_category_btn)
        btn_layout.addStretch()
        categories_layout.addLayout(btn_layout)

        categories_tab.setLayout(categories_layout)

        # Вкладка "Платежи"
        payments_tab = QWidget()
        payments_layout = QVBoxLayout()

        payments_layout.addWidget(QLabel("График платежей:"))

        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(2)
        self.payments_table.setHorizontalHeaderLabels(["Дата платежа", "Сумма"])
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.payments_table.setAlternatingRowColors(True)
        payments_layout.addWidget(self.payments_table)

        btn_layout2 = QHBoxLayout()
        self.add_payment_btn = QPushButton("➕ Добавить платеж")
        self.add_payment_btn.clicked.connect(self.add_payment_row)
        btn_layout2.addWidget(self.add_payment_btn)
        btn_layout2.addStretch()
        payments_layout.addLayout(btn_layout2)

        payments_tab.setLayout(payments_layout)

        tabs.addTab(main_tab, "Основное")
        tabs.addTab(categories_tab, "Категории")
        tabs.addTab(payments_tab, "Платежи")

        layout.addWidget(tabs)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("✓ Сохранить")
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 8px;")
        self.save_btn.clicked.connect(self.save)

        self.cancel_btn = QPushButton("✗ Отмена")
        self.cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px; border-radius: 8px;")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Добавляем одну пустую строку по умолчанию
        self.add_category_row()
        self.add_payment_row()

    def add_category_row(self):
        row = self.categories_table.rowCount()
        self.categories_table.insertRow(row)

        # Выбор категории
        cat_combo = QComboBox()
        for cat in self.categories:
            cat_combo.addItem(cat["name"], cat["id"])
        self.categories_table.setCellWidget(row, 0, cat_combo)

        # Поле для суммы
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        self.categories_table.setCellWidget(row, 1, amount_input)

    def add_payment_row(self):
        row = self.payments_table.rowCount()
        self.payments_table.insertRow(row)

        # Дата платежа
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        date_edit.setDisplayFormat("dd.MM.yyyy")
        self.payments_table.setCellWidget(row, 0, date_edit)

        # Сумма
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        self.payments_table.setCellWidget(row, 1, amount_input)

    def load_transaction_data(self):
        """Загрузка данных транзакции для редактирования"""
        transaction = self.controller.get_by_id(self.transaction_id)

        if not transaction:
            QMessageBox.warning(self, "Ошибка", "Транзакция не найдена")
            self.reject()
            return

        # Заполняем основные поля
        if transaction["type"] == "income":
            self.type_combo.setCurrentIndex(0)
        else:
            self.type_combo.setCurrentIndex(1)

        # Дата - исправлено
        date_value = transaction["date"]
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, "%Y-%m-%d").date()
        elif isinstance(date_value, datetime):
            date_obj = date_value.date()
        else:
            date_obj = date_value
        self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))

        # Сумма
        self.amount_input.setText(str(transaction["total_amount"]))

        # Комментарий
        if transaction.get("comment"):
            self.comment_input.setText(transaction["comment"])

        # Загружаем категории
        self.categories_table.setRowCount(0)
        for cat in transaction.get("categories", []):
            row = self.categories_table.rowCount()
            self.categories_table.insertRow(row)

            cat_combo = QComboBox()
            for c in self.categories:
                cat_combo.addItem(c["name"], c["id"])
                if c["id"] == cat["category_id"]:
                    cat_combo.setCurrentIndex(cat_combo.count() - 1)
            self.categories_table.setCellWidget(row, 0, cat_combo)

            amount_input = QLineEdit()
            amount_input.setText(str(cat["amount"]))
            self.categories_table.setCellWidget(row, 1, amount_input)

        # Загружаем платежи - исправлено
        self.payments_table.setRowCount(0)
        for payment in transaction.get("payments", []):
            row = self.payments_table.rowCount()
            self.payments_table.insertRow(row)

            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)

            # Проверяем тип данных для даты платежа
            payment_date_value = payment["date"]
            if isinstance(payment_date_value, str):
                payment_date = datetime.strptime(payment_date_value, "%Y-%m-%d").date()
            elif isinstance(payment_date_value, datetime):
                payment_date = payment_date_value.date()
            else:
                payment_date = payment_date_value

            date_edit.setDate(QDate(payment_date.year, payment_date.month, payment_date.day))
            date_edit.setDisplayFormat("dd.MM.yyyy")
            self.payments_table.setCellWidget(row, 0, date_edit)

            amount_input = QLineEdit()
            amount_input.setText(str(payment["amount"]))
            self.payments_table.setCellWidget(row, 1, amount_input)

    def save(self):
        try:
            # Собираем данные
            data = {}

            # Тип
            data["type"] = "income" if self.type_combo.currentIndex() == 0 else "expense"

            # Дата
            qdate = self.date_edit.date()
            data["date"] = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"

            # Сумма
            try:
                data["total_amount"] = float(self.amount_input.text().replace(",", "."))
            except:
                QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
                return

            # Комментарий
            data["comment"] = self.comment_input.text()
            data["user_id"] = 1

            # Категории
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

            # Платежи
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

            # Проверка сумм
            if abs(total_categories - data["total_amount"]) > 0.01:
                reply = QMessageBox.question(
                    self,
                    "Предупреждение",
                    f"Сумма по категориям ({total_categories:.2f}) не совпадает с общей суммой ({data['total_amount']:.2f}).\nСохранить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            if self.transaction_id:
                # Обновление
                self.controller.update(self.transaction_id, data)
                QMessageBox.information(self, "Успех", "Операция успешно обновлена!")
            else:
                # Создание
                self.controller.create(data)
                QMessageBox.information(self, "Успех", "Операция успешно добавлена!")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")