# Module4Widget.py (исправленный модуль)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QLinearGradient, QBrush, QPalette, QColor
from references.AnimatedButton import AnimatedButton

# ВАЖНО: используем абсолютный импорт из папки references
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transactions.controller import ReferencesController
from transactions.models import CategoryType, AppSettings, UserStatus

class CategoriesView(QWidget):
    """Вкладка «Категории»"""

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller if controller else ReferencesController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Используем QTreeWidget для иерархического отображения
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Название", "Тип"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.tree)

        # Счётчик
        self.count_label = QLabel("Всего: 0 категорий")
        self.count_label.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(self.count_label)

        self.setLayout(layout)

    def load_data(self, search_text="", type_filter="Все"):
        self.tree.clear()

        # Проверка наличия метода
        if not hasattr(self.controller, 'get_categories_tree'):
            self.count_label.setText("Ошибка: контроллер не поддерживает категории")
            return

        roots = self.controller.get_categories_tree()

        # Фильтрация
        def filter_cat(cat):
            match_name = search_text.lower() in cat.name.lower() if search_text else True
            match_type = True
            if type_filter == "Доход":
                match_type = cat.type == CategoryType.INCOME
            elif type_filter == "Расход":
                match_type = cat.type == CategoryType.EXPENSE
            return match_name and match_type

        def build_filtered_tree(cats):
            result = []
            for cat in cats:
                if filter_cat(cat):
                    new_cat = cat
                    new_cat.children = build_filtered_tree(cat.children)
                    result.append(new_cat)
                else:
                    # Проверяем детей, даже если родитель не подходит
                    children_filtered = build_filtered_tree(cat.children)
                    if children_filtered:
                        result.extend(children_filtered)
            return result

        filtered_roots = build_filtered_tree(roots)
        self._add_tree_items(self.tree, filtered_roots)

        # Подсчёт всех категорий
        def count_cats(cats):
            total = len(cats)
            for cat in cats:
                total += count_cats(cat.children)
            return total

        total = count_cats(filtered_roots)
        self.count_label.setText(f"Всего: {total} категорий")

    def _add_tree_items(self, parent, categories):
        for cat in categories:
            item = QTreeWidgetItem(parent)
            item.setText(0, cat.name)
            type_text = "Доход" if cat.type == CategoryType.INCOME else "Расход"
            item.setText(1, type_text)
            # Цветовая маркировка
            if cat.type == CategoryType.INCOME:
                item.setForeground(1, QColor("#27ae60"))
            else:
                item.setForeground(1, QColor("#e74c3c"))
            item.setData(0, Qt.ItemDataRole.UserRole, cat.id)
            if cat.children:
                self._add_tree_items(item, cat.children)

    def get_selected_id(self):
        item = self.tree.currentItem()
        if item:
            return item.data(0, Qt.ItemDataRole.UserRole)
        return None


class CounterpartiesView(QWidget):
    """Вкладка «Контрагенты»"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Название", "Тип", "Контакты", "Адрес", "Реквизиты", "Комментарий"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.count_label = QLabel("Всего: 0 контрагентов")
        self.count_label.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(self.count_label)

        self.setLayout(layout)

    def load_data(self, search_text="", type_filter="Все"):
        data = self.controller.get_counterparties()
        filtered = []
        for cp in data:
            match_name = search_text.lower() in cp.name.lower() if search_text else True
            match_type = True
            if type_filter != "Все":
                match_type = cp.type == type_filter
            if match_name and match_type:
                filtered.append(cp)

        self.table.setRowCount(len(filtered))
        for i, cp in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(cp.name))
            self.table.setItem(i, 1, QTableWidgetItem(cp.type))
            self.table.setItem(i, 2, QTableWidgetItem(cp.contact_info))
            self.table.setItem(i, 3, QTableWidgetItem(cp.address or ""))
            self.table.setItem(i, 4, QTableWidgetItem(cp.requisites or ""))
            self.table.setItem(i, 5, QTableWidgetItem(cp.comment or ""))
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, cp.id)

        self.count_label.setText(f"Всего: {len(filtered)} контрагентов")

    def get_selected_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return None


class CategoryForm(QDialog):
    def __init__(self, controller, cat_data=None):
        super().__init__()
        self.controller = controller
        self.cat_data = cat_data
        self.setWindowTitle("Редактирование категории" if cat_data else "Новая категория")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Доход", "Расход"])
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Родительская категория:"))
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("Нет (корневая категория)", None)

        # Заполним категории, исключая текущую
        all_cats = self.controller.get_all_categories()
        for cat in all_cats:
            if not self.cat_data or cat.id != self.cat_data.id:
                indent = "  " if cat.parent_id else ""
                self.parent_combo.addItem(f"{indent}{cat.name}", cat.id)
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
        self.setMinimumWidth(400)

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
    def __init__(self, controller, cp_data=None):
        super().__init__()
        self.controller = controller
        self.cp_data = cp_data
        self.setWindowTitle("Редактирование контрагента" if cp_data else "Новый контрагент")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        fields = [
            ("name", "Название", QLineEdit),
            ("type", "Тип", QComboBox),
            ("contact_info", "Контакты", QLineEdit),
            ("address", "Адрес", QLineEdit),
            ("requisites", "Реквизиты", QLineEdit),
            ("comment", "Комментарий", QLineEdit),
        ]

        self.inputs = {}
        for field, label, widget_cls in fields:
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
            self.inputs["address"].setText(self.cp_data.address or "")
            self.inputs["requisites"].setText(self.cp_data.requisites or "")
            self.inputs["comment"].setText(self.cp_data.comment or "")

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
        self.setMinimumWidth(400)

    def save(self):
        data = {}
        for field in ["name", "type", "contact_info", "address", "requisites", "comment"]:
            widget = self.inputs[field]
            if isinstance(widget, QComboBox):
                data[field] = widget.currentText()
            else:
                data[field] = widget.text()

        if not data["name"].strip():
            QMessageBox.warning(self, "Ошибка", "Введите название")
            return

        try:
            if self.cp_data:
                self.controller.update_counterparty(self.cp_data.id, data)
            else:
                self.controller.add_counterparty(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class SettingsView(QWidget):
    """Вкладка «Настройки»"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Тема
        layout.addWidget(QLabel("Тема оформления:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная"])
        layout.addWidget(self.theme_combo)

        # Формат даты
        layout.addWidget(QLabel("Формат даты:"))
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["dd.MM.yyyy", "yyyy-MM-dd", "MM/dd/yyyy"])
        layout.addWidget(self.date_format_combo)

        # Чекбоксы
        self.auto_refresh_check = QCheckBox("Автообновление данных")
        self.recurring_check = QCheckBox("Включить повторяющиеся операции")
        self.logging_check = QCheckBox("Логирование действий")
        layout.addWidget(self.auto_refresh_check)
        layout.addWidget(self.recurring_check)
        layout.addWidget(self.logging_check)

        layout.addSpacing(20)

        # Кнопка сохранения
        save_btn = AnimatedButton("💾 Сохранить настройки")
        save_btn.setObjectName("save_settings_btn")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        try:
            s = self.controller.get_settings()
            self.theme_combo.setCurrentIndex(0 if s.theme == "light" else 1)
            self.date_format_combo.setCurrentText(s.date_format)
            self.auto_refresh_check.setChecked(s.auto_refresh)
            self.recurring_check.setChecked(s.recurring_enabled)
            self.logging_check.setChecked(s.logging_enabled)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        try:
            s = AppSettings(
                theme="light" if self.theme_combo.currentIndex() == 0 else "dark",
                date_format=self.date_format_combo.currentText(),
                auto_refresh=self.auto_refresh_check.isChecked(),
                recurring_enabled=self.recurring_check.isChecked(),
                logging_enabled=self.logging_check.isChecked()
            )
            self.controller.save_settings(s)
            QMessageBox.information(self, "Успех", "Настройки сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")


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
        layout.setSpacing(10)

        layout.addWidget(QLabel("Логин:"))
        self.login_edit = QLineEdit()
        layout.addWidget(self.login_edit)

        layout.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)
        if self.user_data:
            self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять пароль")

        layout.addWidget(QLabel("Роль:"))
        self.role_combo = QComboBox()
        roles = self.controller.get_roles()
        for role in roles:
            self.role_combo.addItem(role.name, role.id)
        layout.addWidget(self.role_combo)

        layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Активен", "Заблокирован"])
        layout.addWidget(self.status_combo)

        if self.user_data:
            self.login_edit.setText(self.user_data.login)
            idx = self.role_combo.findData(self.user_data.role_id)
            if idx >= 0:
                self.role_combo.setCurrentIndex(idx)
            self.status_combo.setCurrentIndex(0 if self.user_data.status == UserStatus.ACTIVE else 1)

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
        self.setMinimumWidth(400)

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
                self.controller.update_user(
                    self.user_data.id, login, role_id, status,
                    password if password else None
                )
            else:
                self.controller.add_user(login, password, role_id, status)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class Module4Widget(QWidget):
    """Модуль 4. Справочники"""

    def __init__(self, controller=None):
        super().__init__()
        # ВАЖНО: создаем свой контроллер, а не используем переданный
        # Это позволяет избежать конфликта имен с transactions/controller.py
        self.controller = ReferencesController()

        self.init_ui()
        self.connect_signals()
        self.load_current_view()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 35, 35, 35)
        main_layout.setSpacing(25)

        # --------------- HEADER ---------------
        header = QFrame()
        header.setObjectName("header")
        gradient = QLinearGradient(0, 0, 1000, 0)
        gradient.setColorAt(0, QColor(52, 152, 219))
        gradient.setColorAt(1, QColor(155, 89, 182))
        palette = header.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        header.setPalette(palette)
        header.setAutoFillBackground(True)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        title = QLabel("📚 Модуль 4. Справочники")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        subtitle = QLabel("Управление категориями, контрагентами и настройками системы")
        subtitle.setObjectName("subtitle")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header.setLayout(header_layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        header.setGraphicsEffect(shadow)
        main_layout.addWidget(header)

        # --------------- ВКЛАДКИ (КНОПКИ) ---------------
        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(10)

        self.categories_tab_btn = AnimatedButton("📁 Категории")
        self.contractors_tab_btn = AnimatedButton("👥 Контрагенты")
        self.settings_tab_btn = AnimatedButton("⚙️ Настройки")

        tab_btn_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #555;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover:!checked {
                background-color: #e0e0e0;
            }
        """

        for btn in [self.categories_tab_btn, self.contractors_tab_btn, self.settings_tab_btn]:
            btn.setCheckable(True)
            btn.setStyleSheet(tab_btn_style)
            tabs_row.addWidget(btn)

        tabs_row.addStretch()
        main_layout.addLayout(tabs_row)

        # --------------- STACKED WIDGET ---------------
        self.stacked = QStackedWidget()
        self.categories_view = CategoriesView(self.controller)
        self.contractors_view = CounterpartiesView(self.controller)
        self.settings_view = SettingsView(self.controller)
        self.stacked.addWidget(self.categories_view)  # 0
        self.stacked.addWidget(self.contractors_view)  # 1
        self.stacked.addWidget(self.settings_view)  # 2
        main_layout.addWidget(self.stacked)

        # --------------- ФИЛЬТРЫ И ДЕЙСТВИЯ ---------------
        filter_card = QFrame()
        filter_card.setObjectName("filter_card")
        filter_card.setStyleSheet("""
            QFrame#filter_card {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(10)

        # Поиск
        search_row = QHBoxLayout()
        search_label = QLabel("🔍 Поиск:")
        search_label.setStyleSheet("font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input)

        # Фильтр типа
        type_row = QHBoxLayout()
        type_label = QLabel("🏷 Тип:")
        type_label.setStyleSheet("font-weight: bold;")
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "Доход", "Расход"])
        self.type_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 8px;
                min-width: 150px;
            }
        """)
        type_row.addWidget(type_label)
        type_row.addWidget(self.type_filter)

        # Кнопки действий
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        self.add_btn = AnimatedButton("➕ Добавить")
        self.edit_btn = AnimatedButton("✏️ Редактировать")
        self.delete_btn = AnimatedButton("🗑 Удалить")
        self.reset_btn = AnimatedButton("🔄 Сброс")
        self.export_btn = AnimatedButton("📤 Экспорт")
        self.import_btn = AnimatedButton("📥 Импорт")

        action_btn_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e8f4fd;
                border-color: #3498db;
            }
        """

        for btn in [self.add_btn, self.edit_btn, self.delete_btn,
                    self.reset_btn, self.export_btn, self.import_btn]:
            btn.setStyleSheet(action_btn_style)

        actions_row.addWidget(self.add_btn)
        actions_row.addWidget(self.edit_btn)
        actions_row.addWidget(self.delete_btn)
        actions_row.addWidget(self.reset_btn)
        actions_row.addStretch()
        actions_row.addWidget(self.export_btn)
        actions_row.addWidget(self.import_btn)

        filter_layout.addLayout(search_row)
        filter_layout.addLayout(type_row)
        filter_layout.addLayout(actions_row)
        filter_card.setLayout(filter_layout)
        main_layout.addWidget(filter_card)

        self.setLayout(main_layout)
        self.categories_tab_btn.setChecked(True)

    def connect_signals(self):
        # Переключение вкладок
        self.categories_tab_btn.clicked.connect(lambda: self.switch_tab(0))
        self.contractors_tab_btn.clicked.connect(lambda: self.switch_tab(1))
        self.settings_tab_btn.clicked.connect(lambda: self.switch_tab(2))

        # Поиск и фильтр
        self.search_input.textChanged.connect(lambda: self.load_current_view())
        self.type_filter.currentTextChanged.connect(lambda: self.load_current_view())

        # Действия
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.reset_btn.clicked.connect(self.reset_filters)
        self.export_btn.clicked.connect(self.export_data)
        self.import_btn.clicked.connect(self.import_data)

    def switch_tab(self, index):
        self.stacked.setCurrentIndex(index)
        # Обновить состояние кнопок
        self.categories_tab_btn.setChecked(index == 0)
        self.contractors_tab_btn.setChecked(index == 1)
        self.settings_tab_btn.setChecked(index == 2)

        # Сбросить тип фильтра при переходе
        if index == 0:  # Категории
            self.type_filter.blockSignals(True)
            self.type_filter.clear()
            self.type_filter.addItems(["Все", "Доход", "Расход"])
            self.type_filter.blockSignals(False)
        elif index == 1:  # Контрагенты
            self.type_filter.blockSignals(True)
            self.type_filter.clear()
            self.type_filter.addItems(["Все", "Клиент", "Поставщик", "Прочие"])
            self.type_filter.blockSignals(False)
        else:  # Настройки
            self.type_filter.blockSignals(True)
            self.type_filter.clear()
            self.type_filter.blockSignals(False)

        # Обновить данные
        self.load_current_view()

    def current_view_info(self):
        """Возвращает активное представление и его тип"""
        if self.stacked.currentIndex() == 0:
            return self.categories_view, "categories"
        elif self.stacked.currentIndex() == 1:
            return self.contractors_view, "counterparties"
        else:
            return None, "settings"

    def load_current_view(self):
        view, vtype = self.current_view_info()
        if view is None or vtype == "settings":
            return
        search = self.search_input.text()
        type_filter = self.type_filter.currentText() if self.type_filter.count() > 0 else "Все"
        view.load_data(search, type_filter)

    def get_current_selected_id(self):
        view, vtype = self.current_view_info()
        if view is None:
            return None
        if hasattr(view, 'get_selected_id'):
            return view.get_selected_id()
        return None

    def add_item(self):
        vtype = self.current_view_info()[1]
        try:
            if vtype == "categories":
                form = CategoryForm(self.controller)
                if form.exec():
                    self.load_current_view()
            elif vtype == "counterparties":
                form = CounterpartyForm(self.controller)
                if form.exec():
                    self.load_current_view()
            else:
                QMessageBox.information(self, "Информация", "Добавление доступно только для категорий и контрагентов")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def edit_item(self):
        view, vtype = self.current_view_info()
        if vtype == "settings":
            QMessageBox.information(self, "Информация", "Редактирование настроек доступно на вкладке настроек")
            return

        selected_id = self.get_current_selected_id()
        if selected_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите элемент для редактирования")
            return

        try:
            if vtype == "categories":
                cat = self.controller.get_category_by_id(selected_id)
                if cat:
                    form = CategoryForm(self.controller, cat_data=cat)
                    if form.exec():
                        self.load_current_view()
            elif vtype == "counterparties":
                cp = self.controller.get_counterparty_by_id(selected_id)
                if cp:
                    form = CounterpartyForm(self.controller, cp_data=cp)
                    if form.exec():
                        self.load_current_view()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_item(self):
        view, vtype = self.current_view_info()
        if vtype == "settings":
            QMessageBox.information(self, "Информация", "Удаление недоступно на вкладке настроек")
            return

        selected_id = self.get_current_selected_id()
        if selected_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите элемент для удаления")
            return

        item_name = ""
        if vtype == "categories":
            cat = self.controller.get_category_by_id(selected_id)
            item_name = cat.name if cat else "категорию"
        else:
            cp = self.controller.get_counterparty_by_id(selected_id)
            item_name = cp.name if cp else "контрагента"

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы действительно хотите удалить {item_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if vtype == "categories":
                    self.controller.delete_category(selected_id)
                else:
                    self.controller.delete_counterparty(selected_id)
                self.load_current_view()
                QMessageBox.information(self, "Успех", "Элемент успешно удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def reset_filters(self):
        self.search_input.clear()
        if self.type_filter.count() > 0:
            self.type_filter.setCurrentIndex(0)
        self.load_current_view()

    def export_data(self):
        vtype = self.current_view_info()[1]
        if vtype == "settings":
            QMessageBox.information(self, "Информация", "Экспорт недоступен для настроек")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Экспорт CSV", "", "CSV файлы (*.csv)")
        if not path:
            return

        try:
            if vtype == "categories":
                self.controller.export_categories_to_csv(path)
            else:
                self.controller.export_counterparties_to_csv(path)
            QMessageBox.information(self, "Успех", f"Данные экспортированы в {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def import_data(self):
        vtype = self.current_view_info()[1]
        if vtype == "settings":
            QMessageBox.information(self, "Информация", "Импорт недоступен для настроек")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Импорт CSV", "", "CSV файлы (*.csv)")
        if not path:
            return

        reply = QMessageBox.question(
            self, "Подтверждение импорта",
            "Импорт добавит новые записи. Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if vtype == "categories":
                    self.controller.import_categories_from_csv(path)
                else:
                    self.controller.import_counterparties_from_csv(path)
                self.load_current_view()
                QMessageBox.information(self, "Успех", "Данные импортированы")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка импорта", str(e))