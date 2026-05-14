from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt


class BudgetAddDialog(QDialog):
    """Диалог добавления бюджета"""

    def __init__(self, categories, period_dates, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.period_dates = period_dates
        self.category_id = None
        self.amount = 0

        self.setWindowTitle("➕ Добавление бюджета")
        self.setFixedSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #F8FAFC;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title = QLabel("📊 Новый бюджет")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title)

        # Информация о периоде
        period_frame = QFrame()
        period_frame.setStyleSheet("""
            QFrame {
                background: #F1F5F9;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        period_layout = QVBoxLayout(period_frame)
        period_label = QLabel(f"📅 Период: {self.period_dates['display']}")
        period_label.setStyleSheet("color: #475569; font-size: 13px;")
        period_layout.addWidget(period_label)
        layout.addWidget(period_frame)

        # Категория
        cat_label = QLabel("📁 Категория")
        cat_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(cat_label)

        self.category_combo = QComboBox()
        for cat in self.categories:
            icon = "💰" if cat['type_en'] == 'income' else "💸"
            self.category_combo.addItem(f"{icon} {cat['name']} ({cat['type']})", cat['id'])
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #4F46E5;
            }
        """)
        layout.addWidget(self.category_combo)

        # Сумма
        amount_label = QLabel("💰 Плановая сумма")
        amount_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(amount_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4F46E5;
            }
        """)
        layout.addWidget(self.amount_input)

        # Подсказка
        hint = QLabel("💡 Введите сумму в рублях. Например: 15000 или 15000.50")
        hint.setStyleSheet("color: #94A3B8; font-size: 11px; font-style: italic;")
        layout.addWidget(hint)

        layout.addStretch()

        # Кнопки
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: white;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F1F5F9;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4F46E5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #6366F1;
            }
        """)
        save_btn.clicked.connect(self.save)

        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def save(self):
        try:
            amount_text = self.amount_input.text().strip().replace(',', '.')
            if not amount_text:
                QMessageBox.warning(self, "Ошибка", "Введите сумму")
                return

            amount = float(amount_text)
            if amount < 0:
                QMessageBox.warning(self, "Ошибка", "Сумма не может быть отрицательной")
                return

            self.category_id = self.category_combo.currentData()
            self.amount = amount
            self.accept()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")


class BudgetEditDialog(QDialog):
    """Диалог редактирования бюджета"""

    def __init__(self, category_name, current_amount, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.current_amount = current_amount
        self.amount = 0

        self.setWindowTitle("✏️ Редактирование бюджета")
        self.setFixedSize(500, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #F8FAFC;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title = QLabel("✏️ Редактирование бюджета")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title)

        # Информация о категории
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #F1F5F9;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        cat_label = QLabel(f"📁 Категория: {self.category_name}")
        cat_label.setStyleSheet("color: #475569; font-size: 13px; font-weight: bold;")
        info_layout.addWidget(cat_label)
        layout.addWidget(info_frame)

        # Сумма
        amount_label = QLabel("💰 Плановая сумма")
        amount_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(amount_label)

        self.amount_input = QLineEdit()
        self.amount_input.setText(f"{self.current_amount:,.2f}")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4F46E5;
            }
        """)
        layout.addWidget(self.amount_input)

        # Подсказка
        hint = QLabel("💡 Введите новую сумму в рублях")
        hint.setStyleSheet("color: #94A3B8; font-size: 11px; font-style: italic;")
        layout.addWidget(hint)

        layout.addStretch()

        # Кнопки
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: white;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F1F5F9;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4F46E5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #6366F1;
            }
        """)
        save_btn.clicked.connect(self.save)

        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def save(self):
        try:
            amount_text = self.amount_input.text().strip().replace(',', '.').replace(' ', '')
            if not amount_text:
                QMessageBox.warning(self, "Ошибка", "Введите сумму")
                return

            amount = float(amount_text)
            if amount < 0:
                QMessageBox.warning(self, "Ошибка", "Сумма не может быть отрицательной")
                return

            self.amount = amount
            self.accept()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")