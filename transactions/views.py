from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QPalette, QFont
from .controller import ReferencesController
from .models import CategoryType, UserStatus, AppSettings
from references.AnimatedButton import AnimatedButton

class CategoryForm(QDialog):
    def __init__(self, controller, parent_item=None, cat_data=None):
        super().__init__()
        self.controller = controller
        self.parent_item = parent_item
        self.cat_data = cat_data
        self.setWindowTitle("Редактирование категории" if cat_data else "Новая категория")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
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
        # Заполним категории, исключая текущую
        all_cats = self.controller.repo.get_all_categories()
        for cat in all_cats:
            if not self.cat_data or cat.id != self.cat_data.id:
                self.parent_combo.addItem(cat.name, cat.id)
        layout.addWidget(self.parent_combo)

        if self.cat_data:
            self.name_edit.setText(self.cat_data.name)
            self.type_combo.setCurrentIndex(0 if self.cat_data.type == CategoryType.INCOME else 1)
            idx = self.parent_combo.findData(self.cat_data.parent_id)
            if idx >= 0:
                self.parent_combo.setCurrentIndex(idx)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("✓ Сохранить")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 8px;")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("✗ Отмена")
        cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название")
            return
        cat_type = CategoryType.INCOME if self.type_combo.currentIndex() == 0 else CategoryType.EXPENSE
        parent_id = self.parent_combo.currentData()
        try:
            if self.cat_data:
                self.controller.update_category(self.cat_data.id, name, cat_type, parent_id)
            else:
                self.controller.add_category(name, cat_type, parent_id)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class CounterpartyForm(QDialog):
    FIELDS = [
        ("name", "Название", QLineEdit),
        ("type", "Тип", QComboBox),
        ("contact_info", "Контакты", QLineEdit),
        ("address", "Адрес", QLineEdit),
        ("requisites", "Реквизиты", QLineEdit),
        ("comment", "Комментарий", QLineEdit),
    ]
    def __init__(self, controller, cp_data=None):
        super().__init__()
        self.controller = controller
        self.cp_data = cp_data
        self.setWindowTitle("Редактирование контрагента" if cp_data else "Новый контрагент")
        self.setModal(True)
        self.inputs = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        for field, label, widget_cls in self.FIELDS:
            layout.addWidget(QLabel(label))
            if widget_cls == QComboBox:
                widget = QComboBox()
                widget.addItems(["Клиент", "Поставщик", "Прочие"])
                self.inputs[field] = widget
            else:
                widget = QLineEdit()
                self.inputs[field] = widget
            layout.addWidget(widget)

        if self.cp_data:
            self.inputs["name"].setText(self.cp_data.name)
            self.inputs["type"].setCurrentText(self.cp_data.type)
            self.inputs["contact_info"].setText(self.cp_data.contact_info)
            self.inputs["address"].setText(self.cp_data.address)
            self.inputs["requisites"].setText(self.cp_data.requisites)
            self.inputs["comment"].setText(self.cp_data.comment)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("✓ Сохранить")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 8px;")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("✗ Отмена")
        cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save(self):
        data = {f: self.inputs[f].text() if isinstance(self.inputs[f], QLineEdit) else self.inputs[f].currentText()
                for f, _, _ in self.FIELDS}
        try:
            if self.cp_data:
                self.controller.update_counterparty(self.cp_data.id, data)
            else:
                self.controller.add_counterparty(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class UserForm(QDialog):
    def __init__(self, controller, user_data=None):
        super().__init__()
        self.controller = controller
        self.user_data = user_data
        self.setWindowTitle("Редактирование пользователя" if user_data else "Новый пользователь")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))
        self.login_edit = QLineEdit()
        layout.addWidget(self.login_edit)
        layout.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)
        if self.user_data:
            self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять")

        layout.addWidget(QLabel("Роль:"))
        self.role_combo = QComboBox()
        roles = self.controller.get_roles()
        for r in roles:
            self.role_combo.addItem(r.name, r.id)
        layout.addWidget(self.role_combo)

        layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Активен", "Заблокирован"])
        layout.addWidget(self.status_combo)

        if self.user_data:
            self.login_edit.setText(self.user_data.login)
            self.role_combo.setCurrentIndex(self.role_combo.findData(self.user_data.role_id))
            self.status_combo.setCurrentIndex(0 if self.user_data.status == UserStatus.ACTIVE else 1)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("✓ Сохранить")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 8px;")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("✗ Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save(self):
        login = self.login_edit.text().strip()
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
        password = self.password_edit.text()
        if not self.user_data and not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return
        role_id = self.role_combo.currentData()
        status = UserStatus.ACTIVE if self.status_combo.currentIndex() == 0 else UserStatus.BLOCKED
        try:
            if self.user_data:
                self.controller.update_user(self.user_data.id, login, role_id, status,
                                            password if password else None)
            else:
                self.controller.add_user(login, password, role_id, status)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class CategoriesTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Название", "Тип", "Родитель"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.itemDoubleClicked.connect(self.edit_category)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📁 Иерархия категорий:"))
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def load_data(self):
        self.tree.clear()
        roots = self.controller.get_categories_tree()
        self.add_tree_items(self.tree, roots)

    def add_tree_items(self, parent, categories):
        for cat in categories:
            item = QTreeWidgetItem(parent)
            item.setText(0, cat.name)
            item.setText(1, "Доход" if cat.type == CategoryType.INCOME else "Расход")
            item.setText(2, "—" if cat.parent_id is None else "")
            item.setData(0, Qt.ItemDataRole.UserRole, cat.id)
            if cat.children:
                self.add_tree_items(item, cat.children)

    def edit_category(self, item):
        cat_id = item.data(0, Qt.ItemDataRole.UserRole)
        cat = self.controller.repo.get_category_by_id(cat_id)
        if cat:
            form = CategoryForm(self.controller, cat_data=cat)
            if form.exec():
                self.load_data()

class CounterpartiesTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Название", "Тип", "Контакты", "Адрес", "Реквизиты", "Комментарий"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemDoubleClicked.connect(self.edit_counterparty)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("👥 Контрагенты:"))
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        data = self.controller.get_counterparties()
        self.table.setRowCount(len(data))
        for i, cp in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(cp.name))
            self.table.setItem(i, 1, QTableWidgetItem(cp.type))
            self.table.setItem(i, 2, QTableWidgetItem(cp.contact_info))
            self.table.setItem(i, 3, QTableWidgetItem(cp.address))
            self.table.setItem(i, 4, QTableWidgetItem(cp.requisites))
            self.table.setItem(i, 5, QTableWidgetItem(cp.comment))

    def edit_counterparty(self):
        row = self.table.currentRow()
        if row < 0: return
        cp_id = self.controller.get_counterparties()[row].id
        cp = self.controller.repo.get_counterparty_by_id(cp_id)
        form = CounterpartyForm(self.controller, cp)
        if form.exec():
            self.load_data()

class UsersTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Логин", "Роль", "Статус", "ID"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemDoubleClicked.connect(self.edit_user)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔐 Пользователи:"))
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        users = self.controller.get_users()
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(u.login))
            self.table.setItem(i, 1, QTableWidgetItem(u.role_name))
            self.table.setItem(i, 2, QTableWidgetItem("Активен" if u.status == UserStatus.ACTIVE else "Заблокирован"))
            self.table.setItem(i, 3, QTableWidgetItem(str(u.id)))

    def edit_user(self):
        row = self.table.currentRow()
        if row < 0: return
        uid = int(self.table.item(row, 3).text())
        user = self.controller.repo.get_user_by_id(uid)
        form = UserForm(self.controller, user)
        if form.exec():
            self.load_data()

class SettingsTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная"])
        layout.addWidget(QLabel("Тема:"))
        layout.addWidget(self.theme_combo)

        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["dd.MM.yyyy", "yyyy-MM-dd"])
        layout.addWidget(QLabel("Формат даты:"))
        layout.addWidget(self.date_format_combo)

        self.auto_refresh_check = QCheckBox("Автообновление данных")
        self.recurring_check = QCheckBox("Включить повторяющиеся операции")
        self.logging_check = QCheckBox("Логирование действий")
        layout.addWidget(self.auto_refresh_check)
        layout.addWidget(self.recurring_check)
        layout.addWidget(self.logging_check)

        save_btn = QPushButton("Сохранить настройки")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 8px;")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        s = self.controller.get_settings()
        self.theme_combo.setCurrentIndex(0 if s.theme == "light" else 1)
        self.date_format_combo.setCurrentText(s.date_format)
        self.auto_refresh_check.setChecked(s.auto_refresh)
        self.recurring_check.setChecked(s.recurring_enabled)
        self.logging_check.setChecked(s.logging_enabled)

    def save_settings(self):
        s = AppSettings(
            theme="light" if self.theme_combo.currentIndex() == 0 else "dark",
            date_format=self.date_format_combo.currentText(),
            auto_refresh=self.auto_refresh_check.isChecked(),
            recurring_enabled=self.recurring_check.isChecked(),
            logging_enabled=self.logging_check.isChecked()
        )
        self.controller.save_settings(s)
        QMessageBox.information(self, "Успех", "Настройки сохранены")