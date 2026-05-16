from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from .models import CategoryType, UserStatus


class CategoryForm(QDialog):
    def __init__(self, controller, cat_data=None, initial_parent_id=None):
        super().__init__()
        self.controller = controller
        self.cat_data = cat_data
        self.initial_parent_id = initial_parent_id
        self.setWindowTitle("Редактирование категории" if cat_data else "Новая категория")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Доход", "Расход"])
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Родительская категория:"))
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("Нет", None)
        for cat in self.controller.get_all_categories():
            if not self.cat_data or cat.id != self.cat_data.id:
                self.parent_combo.addItem(cat.name, cat.id)
        layout.addWidget(self.parent_combo)

        # НОВОЕ: Лимит
        layout.addWidget(QLabel("Месячный бюджет (лимит):"))
        self.limit_spin = QDoubleSpinBox()
        self.limit_spin.setMaximum(1000000000)
        layout.addWidget(self.limit_spin)

        if self.cat_data:
            self.name_edit.setText(self.cat_data.name)
            self.type_combo.setCurrentIndex(0 if self.cat_data.type == CategoryType.INCOME else 1)
            idx = self.parent_combo.findData(self.cat_data.parent_id)
            if idx >= 0: self.parent_combo.setCurrentIndex(idx)
            self.limit_spin.setValue(self.cat_data.monthly_limit or 0.0)
        elif self.initial_parent_id:
            idx = self.parent_combo.findData(self.initial_parent_id)
            if idx >= 0: self.parent_combo.setCurrentIndex(idx)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("✓ Сохранить")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("✗ Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save(self):
        name = self.name_edit.text().strip()
        if not name: return QMessageBox.warning(self, "Ошибка", "Введите название")
        cat_type = CategoryType.INCOME if self.type_combo.currentIndex() == 0 else CategoryType.EXPENSE
        parent_id = self.parent_combo.currentData()

        # ЖЁСТКАЯ НОРМАЛИЗАЦИЯ
        if parent_id in (0, "0", "", False):
            parent_id = None

        # Защита от self-parent
        if self.cat_data and parent_id == self.cat_data.id:
            parent_id = None
        limit = self.limit_spin.value()

        try:
            if self.cat_data:
                self.controller.update_category(self.cat_data.id, name, cat_type, parent_id, limit)
            else:
                self.controller.add_category(name, cat_type, parent_id, limit)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class CounterpartyForm(QDialog):
    def __init__(self, controller, cp_data=None, initial_parent_id=None):
        super().__init__()
        self.controller = controller
        self.cp_data = cp_data
        self.initial_parent_id = initial_parent_id
        self.setWindowTitle("Контрагент")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Клиент", "Поставщик", "Сотрудник", "Прочие"])
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("Нет", None)
        for cp in self.controller.get_counterparties():
            if not self.cp_data or cp.id != self.cp_data.id:
                self.parent_combo.addItem(cp.name, cp.id)

        self.contact_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.req_edit = QLineEdit()
        self.req_edit.setPlaceholderText("Например: ИНН 7700000000")
        self.comment_edit = QLineEdit()

        layout.addRow("Название:", self.name_edit)
        layout.addRow("Группа (Родитель):", self.parent_combo)
        layout.addRow("Тип:", self.type_combo)
        layout.addRow("Контакты:", self.contact_edit)
        layout.addRow("Адрес:", self.address_edit)
        layout.addRow("Реквизиты:", self.req_edit)
        layout.addRow("Комментарий:", self.comment_edit)

        if self.cp_data:
            self.name_edit.setText(self.cp_data.name)
            self.type_combo.setCurrentText(self.cp_data.type)
            idx = self.parent_combo.findData(self.cp_data.parent_id)
            if idx >= 0: self.parent_combo.setCurrentIndex(idx)
            self.contact_edit.setText(self.cp_data.contact_info)
            self.address_edit.setText(self.cp_data.address)
            self.req_edit.setText(self.cp_data.requisites)
            self.comment_edit.setText(self.cp_data.comment)
        elif self.initial_parent_id:
            idx = self.parent_combo.findData(self.initial_parent_id)
            if idx >= 0: self.parent_combo.setCurrentIndex(idx)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save(self):
        data = {
            "name": self.name_edit.text(),
            "type": self.type_combo.currentText(),
            "parent_id": self.parent_combo.currentData(),
            "contact_info": self.contact_edit.text(),
            "address": self.address_edit.text(),
            "requisites": self.req_edit.text(),
            "comment": self.comment_edit.text()
        }
        try:
            if self.cp_data:
                self.controller.update_counterparty(self.cp_data.id, data)
            else:
                self.controller.add_counterparty(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class MergeCategoryDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Слияние категорий")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Внимание! Старая категория будет удалена,\nа все её операции перенесены в новую.",
                                styleSheet="color: #EF4444;"))

        cats = self.controller.get_all_categories()

        layout.addWidget(QLabel("Категория ИСТОЧНИК (будет удалена):"))
        self.source_combo = QComboBox()
        for c in cats: self.source_combo.addItem(c.name, c.id)
        layout.addWidget(self.source_combo)

        layout.addWidget(QLabel("Категория ПРИЕМНИК (останется):"))
        self.target_combo = QComboBox()
        for c in cats: self.target_combo.addItem(c.name, c.id)
        layout.addWidget(self.target_combo)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_data(self):
        return self.source_combo.currentData(), self.target_combo.currentData()