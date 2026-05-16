from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFrame, QMessageBox,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator


class BudgetAddDialog(QDialog):
    """Диалог добавления бюджета с умным распределением"""

    def __init__(self, categories, period_dates, period_type, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.period_dates = period_dates
        self.period_type = period_type  # Передаем тип периода (Месяц, Год и т.д.)
        self.category_id = None
        self.amount = 0
        self.allocation_method = 'lump_sum'  # По умолчанию единая сумма

        self.setWindowTitle("➕ Добавление бюджета")
        # Если период большой, увеличиваем окно под меню распределения
        self.setFixedSize(450, 500 if period_type in ['Год', 'Квартал'] else 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #F8FAFC;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        title = QLabel("Новый бюджет")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1E293B;")
        layout.addWidget(title)

        # Информация о периоде
        period_frame = QFrame()
        period_frame.setStyleSheet("background: #F1F5F9; border-radius: 8px;")
        period_layout = QVBoxLayout(period_frame)
        period_label = QLabel(f"📅 Период: <b>{self.period_dates['display']}</b>")
        period_label.setStyleSheet("color: #475569; font-size: 13px;")
        period_layout.addWidget(period_label)
        layout.addWidget(period_frame)

        # Категория
        layout.addWidget(self._create_label("📁 Категория"))
        self.category_combo = QComboBox()
        for cat in self.categories:
            icon = "💰" if cat['type_en'] == 'income' else "💸"
            self.category_combo.addItem(f"{icon} {cat['name']} ({cat['type']})", cat['id'])
        self.category_combo.setStyleSheet(self._input_style())
        layout.addWidget(self.category_combo)

        # Сумма
        layout.addWidget(self._create_label("💰 Плановая сумма (₽)"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        validator = QDoubleValidator(0.00, 999999999.99, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount_input.setValidator(validator)
        self.amount_input.setStyleSheet(self._input_style())
        layout.addWidget(self.amount_input)

        # === УМНЫЙ РАСПРЕДЕЛИТЕЛЬ (Появляется только для Года и Квартала) ===
        if self.period_type in ['Год', 'Квартал']:
            alloc_frame = QFrame()
            alloc_frame.setStyleSheet("background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px;")
            alloc_layout = QVBoxLayout(alloc_frame)

            hint = QLabel("💡 Как распределить эту сумму?")
            hint.setStyleSheet("color: #D97706; font-weight: bold; font-size: 13px;")
            alloc_layout.addWidget(hint)

            self.radio_lump = QRadioButton(f"Единым лимитом на {self.period_type.lower()}")
            self.radio_divide = QRadioButton("Разбить поровну по месяцам")
            self.radio_lump.setChecked(True)  # По умолчанию ставим единый лимит

            radio_style = "QRadioButton { color: #475569; font-size: 13px; font-weight: bold; padding: 4px; }"
            self.radio_lump.setStyleSheet(radio_style)
            self.radio_divide.setStyleSheet(radio_style)

            self.alloc_group = QButtonGroup(self)
            self.alloc_group.addButton(self.radio_lump)
            self.alloc_group.addButton(self.radio_divide)

            alloc_layout.addWidget(self.radio_lump)
            alloc_layout.addWidget(self.radio_divide)
            layout.addWidget(alloc_frame)

        layout.addStretch()

        # Кнопки
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(self._btn_style(is_primary=False))
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet(self._btn_style(is_primary=True))
        save_btn.clicked.connect(self.save)

        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #475569; font-weight: 700; font-size: 13px; margin-top: 8px;")
        return lbl

    def _input_style(self):
        return """
            QWidget { padding: 10px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; font-size: 14px; }
            QWidget:focus { border-color: #4F46E5; }
        """

    def _btn_style(self, is_primary):
        if is_primary:
            return """
                QPushButton { background: #4F46E5; color: white; border: none; border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px; }
                QPushButton:hover { background: #4338CA; }
            """
        return """
            QPushButton { background: white; color: #475569; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background: #F1F5F9; }
        """

    def save(self):
        amount_text = self.amount_input.text().strip().replace(',', '.')
        if not amount_text:
            QMessageBox.warning(self, "Ошибка", "Введите сумму")
            return

        self.category_id = self.category_combo.currentData()
        self.amount = float(amount_text)

        # Сохраняем выбор пользователя для передачи в основной модуль
        if hasattr(self, 'radio_divide') and self.radio_divide.isChecked():
            self.allocation_method = 'divide'

        self.accept()


class BudgetEditDialog(QDialog):
    """Диалог редактирования бюджета (оставлен без изменений)"""

    def __init__(self, category_name, current_amount, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.current_amount = current_amount
        self.amount = 0
        self.setWindowTitle("✏️ Редактирование бюджета")
        self.setFixedSize(450, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #F8FAFC;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        title = QLabel("Редактирование бюджета")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1E293B;")
        layout.addWidget(title)
        info_frame = QFrame()
        info_frame.setStyleSheet("background: #F1F5F9; border-radius: 8px;")
        info_layout = QVBoxLayout(info_frame)
        cat_label = QLabel(f"📁 Категория: <b>{self.category_name}</b>")
        cat_label.setStyleSheet("color: #475569; font-size: 13px;")
        info_layout.addWidget(cat_label)
        layout.addWidget(info_frame)
        lbl = QLabel("💰 Плановая сумма (₽)")
        lbl.setStyleSheet("color: #475569; font-weight: 700; font-size: 13px; margin-top: 8px;")
        layout.addWidget(lbl)
        self.amount_input = QLineEdit()
        self.amount_input.setText(f"{self.current_amount:.2f}")
        validator = QDoubleValidator(0.00, 999999999.99, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount_input.setValidator(validator)
        self.amount_input.setStyleSheet("""
            QLineEdit { padding: 10px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; font-size: 14px; }
            QLineEdit:focus { border-color: #4F46E5; }
        """)
        layout.addWidget(self.amount_input)
        layout.addStretch()
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        save_btn = QPushButton("Сохранить")
        cancel_btn.setStyleSheet("""
            QPushButton { background: white; color: #475569; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 24px; font-weight: bold; }
            QPushButton:hover { background: #F1F5F9; }
        """)
        save_btn.setStyleSheet("""
            QPushButton { background: #4F46E5; color: white; border: none; border-radius: 8px; padding: 10px 24px; font-weight: bold; }
            QPushButton:hover { background: #4338CA; }
        """)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def save(self):
        amount_text = self.amount_input.text().strip().replace(',', '.')
        if not amount_text:
            QMessageBox.warning(self, "Ошибка", "Введите сумму")
            return
        self.amount = float(amount_text)
        self.accept()