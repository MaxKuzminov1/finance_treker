from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QWidget, QSpinBox, QFrame, QScrollArea
)
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon

from datetime import datetime


class TransactionForm(QDialog):
    transaction_saved = pyqtSignal()

    def __init__(self, controller, transaction_id=None):
        super().__init__()
        self.controller = controller
        self.transaction_id = transaction_id

        self.setWindowTitle("✏️ Редактирование операции" if transaction_id else "➕ Добавление операции")
        self.setModal(True)
        self.resize(900, 750)
        self.setMinimumSize(800, 650)

        # Убираем кнопку помощи
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.categories = self.controller.get_categories()

        self.init_ui()

        # Если передан ID, загружаем данные для редактирования
        if transaction_id is not None:
            self.load_transaction_data()

    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel(self.get_window_title())
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 15px;
        """)
        main_layout.addWidget(title_label)

        # Создаем область прокрутки
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Контейнер для содержимого
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Основная информация
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)

        # Тип операции
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_label = QLabel("📊 Тип операции:")
        type_label.setStyleSheet("font-weight: bold; color: #2c3e50; min-width: 120px;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["💰 Доход", "💸 Расход"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                background: white;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
        """)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        info_layout.addWidget(type_widget)

        # Дата
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_label = QLabel("📅 Дата операции:")
        date_label.setStyleSheet("font-weight: bold; color: #2c3e50; min-width: 120px;")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                background: white;
                min-width: 200px;
            }
            QDateEdit:hover {
                border-color: #3498db;
            }
        """)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        info_layout.addWidget(date_widget)

        # Сумма
        amount_widget = QWidget()
        amount_layout = QHBoxLayout(amount_widget)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_label = QLabel("💰 Общая сумма:")
        amount_label.setStyleSheet("font-weight: bold; color: #2c3e50; min-width: 120px;")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                background: white;
                min-width: 200px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        amount_layout.addStretch()
        info_layout.addWidget(amount_widget)

        # Комментарий
        comment_widget = QWidget()
        comment_layout = QHBoxLayout(comment_widget)
        comment_layout.setContentsMargins(0, 0, 0, 0)
        comment_label = QLabel("💬 Комментарий:")
        comment_label.setStyleSheet("font-weight: bold; color: #2c3e50; min-width: 120px;")
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Введите комментарий (необязательно)...")
        self.comment_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                background: white;
                min-width: 300px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        comment_layout.addWidget(comment_label)
        comment_layout.addWidget(self.comment_input)
        comment_layout.addStretch()
        info_layout.addWidget(comment_widget)

        container_layout.addWidget(info_frame)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e1e8ed; max-height: 2px; margin: 10px 0;")
        container_layout.addWidget(separator)

        # Категории
        categories_label = QLabel("📂 Распределение по категориям")
        categories_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 10px 0;")
        container_layout.addWidget(categories_label)

        # Таблица категорий с фиксированной высотой
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels(["Категория", "Сумма (₽)", "Действия"])
        self.setup_table_style(self.categories_table)
        self.categories_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.categories_table.setColumnWidth(1, 150)
        self.categories_table.setColumnWidth(2, 100)
        self.categories_table.setMinimumHeight(200)
        self.categories_table.setMaximumHeight(300)
        container_layout.addWidget(self.categories_table)

        # Кнопки для категорий
        cat_buttons_layout = QHBoxLayout()
        self.add_category_btn = QPushButton("➕ Добавить категорию")
        self.add_category_btn.setStyleSheet(self.get_button_style("#27ae60", "#229954"))
        self.add_category_btn.clicked.connect(self.add_category_row)
        cat_buttons_layout.addWidget(self.add_category_btn)
        cat_buttons_layout.addStretch()
        container_layout.addLayout(cat_buttons_layout)

        # Разделитель
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background-color: #e1e8ed; max-height: 2px; margin: 20px 0 10px 0;")
        container_layout.addWidget(separator2)

        # Платежи
        payments_label = QLabel("💳 График платежей")
        payments_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 10px 0;")
        container_layout.addWidget(payments_label)

        # Таблица платежей с фиксированной высотой
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(3)
        self.payments_table.setHorizontalHeaderLabels(["Дата платежа", "Сумма (₽)", "Действия"])
        self.setup_table_style(self.payments_table)
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.payments_table.setColumnWidth(1, 150)
        self.payments_table.setColumnWidth(2, 100)
        self.payments_table.setMinimumHeight(200)
        self.payments_table.setMaximumHeight(300)
        container_layout.addWidget(self.payments_table)

        # Кнопки для платежей
        payment_buttons_layout = QHBoxLayout()
        self.add_payment_btn = QPushButton("➕ Добавить платеж")
        self.add_payment_btn.setStyleSheet(self.get_button_style("#27ae60", "#229954"))
        self.add_payment_btn.clicked.connect(self.add_payment_row)
        payment_buttons_layout.addWidget(self.add_payment_btn)
        payment_buttons_layout.addStretch()
        container_layout.addLayout(payment_buttons_layout)

        # Итоговая информация
        info_panel = QFrame()
        info_panel.setStyleSheet("""
            QFrame {
                background: #ecf0f1;
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
            }
        """)
        info_panel_layout = QHBoxLayout(info_panel)

        self.total_categories_label = QLabel("📊 Сумма по категориям: 0.00 ₽")
        self.total_categories_label.setStyleSheet("font-weight: bold; color: #2c3e50;")

        self.total_payments_label = QLabel("💳 Сумма по платежам: 0.00 ₽")
        self.total_payments_label.setStyleSheet("font-weight: bold; color: #2c3e50;")

        info_panel_layout.addWidget(self.total_categories_label)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(self.total_payments_label)

        container_layout.addWidget(info_panel)

        # Добавляем растяжку в конце контейнера
        container_layout.addStretch()

        # Устанавливаем контейнер в scroll area
        scroll_area.setWidget(container)

        # Добавляем scroll area в основной layout
        main_layout.addWidget(scroll_area)

        # Кнопки внизу (вне скролла)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.save_btn = QPushButton("✓ Сохранить")
        self.save_btn.setStyleSheet(self.get_button_style("#27ae60", "#229954", True))
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.clicked.connect(self.save)

        self.cancel_btn = QPushButton("✗ Отмена")
        self.cancel_btn.setStyleSheet(self.get_button_style("#95a5a6", "#7f8c8d", True))
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setMinimumWidth(150)
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Добавляем одну пустую строку по умолчанию
        self.add_category_row()
        self.add_payment_row()

        # Подключаем обновление итогов
        self.update_totals()

    def get_window_title(self):
        return "✏️ Редактирование операции" if self.transaction_id else "➕ Добавление операции"

    def get_button_style(self, color, hover_color, large=False):
        if large:
            padding = "12px 30px"
            font_size = "14px"
        else:
            padding = "8px 20px"
            font_size = "12px"

        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {hover_color});
                color: white;
                border: none;
                border-radius: 8px;
                padding: {padding};
                font-weight: bold;
                font-size: {font_size};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {hover_color}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: {hover_color};
            }}
        """

    def setup_table_style(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 10px;
                gridline-color: #e1e8ed;
                alternate-background-color: #f8f9fc;
                border: 1px solid #e1e8ed;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background: #f8f9fc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #3498db;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def on_type_changed(self):
        """При изменении типа операции обновляем заголовки"""
        self.update_totals()

    def add_category_row(self):
        row = self.categories_table.rowCount()
        self.categories_table.insertRow(row)

        # Выбор категории
        cat_combo = QComboBox()
        for cat in self.categories:
            cat_combo.addItem(f"{cat['name']}", cat['id'])
        cat_combo.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
        self.categories_table.setCellWidget(row, 0, cat_combo)

        # Поле для суммы
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        amount_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
        amount_input.textChanged.connect(self.update_totals)
        self.categories_table.setCellWidget(row, 1, amount_input)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_category_row(row))
        self.categories_table.setCellWidget(row, 2, delete_btn)

        self.categories_table.setRowHeight(row, 50)

    def delete_category_row(self, row):
        self.categories_table.removeRow(row)
        self.update_totals()

    def add_payment_row(self):
        row = self.payments_table.rowCount()
        self.payments_table.insertRow(row)

        # Дата платежа
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        date_edit.setDisplayFormat("dd.MM.yyyy")
        date_edit.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
        self.payments_table.setCellWidget(row, 0, date_edit)

        # Сумма
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        amount_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
        amount_input.textChanged.connect(self.update_totals)
        self.payments_table.setCellWidget(row, 1, amount_input)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_payment_row(row))
        self.payments_table.setCellWidget(row, 2, delete_btn)

        self.payments_table.setRowHeight(row, 50)

    def delete_payment_row(self, row):
        self.payments_table.removeRow(row)
        self.update_totals()

    def update_totals(self):
        """Обновление итоговых сумм"""
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

        # Обновляем цвет в зависимости от типа операции
        type_color = "#27ae60" if self.type_combo.currentIndex() == 0 else "#e74c3c"

        self.total_categories_label.setText(f"📊 Сумма по категориям: {total_categories:,.2f} ₽")
        self.total_categories_label.setStyleSheet(f"font-weight: bold; color: {type_color};")

        self.total_payments_label.setText(f"💳 Сумма по платежам: {total_payments:,.2f} ₽")
        self.total_payments_label.setStyleSheet(f"font-weight: bold; color: {type_color};")

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

        # Дата
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
                cat_combo.addItem(f"{c['name']}", c['id'])
                if c["id"] == cat["category_id"]:
                    cat_combo.setCurrentIndex(cat_combo.count() - 1)
            cat_combo.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
            self.categories_table.setCellWidget(row, 0, cat_combo)

            amount_input = QLineEdit()
            amount_input.setText(str(cat["amount"]))
            amount_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
            amount_input.textChanged.connect(self.update_totals)
            self.categories_table.setCellWidget(row, 1, amount_input)

            delete_btn = QPushButton("🗑")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_category_row(row))
            self.categories_table.setCellWidget(row, 2, delete_btn)

            self.categories_table.setRowHeight(row, 50)

        # Загружаем платежи
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
            date_edit.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
            self.payments_table.setCellWidget(row, 0, date_edit)

            amount_input = QLineEdit()
            amount_input.setText(str(payment["amount"]))
            amount_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 6px;")
            amount_input.textChanged.connect(self.update_totals)
            self.payments_table.setCellWidget(row, 1, amount_input)

            delete_btn = QPushButton("🗑")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_payment_row(row))
            self.payments_table.setCellWidget(row, 2, delete_btn)

            self.payments_table.setRowHeight(row, 50)

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

            # Проверка категорий
            if not data["categories"]:
                QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одну категорию")
                return

            # Проверка сумм
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
                # Обновление
                self.controller.update(self.transaction_id, data)
                success_msg = "Операция успешно обновлена!"
            else:
                # Создание
                self.controller.create(data)
                success_msg = "Операция успешно добавлена!"

            QMessageBox.information(self, "Успех", f"✅ {success_msg}")
            self.transaction_saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Ошибка при сохранении: {str(e)}")