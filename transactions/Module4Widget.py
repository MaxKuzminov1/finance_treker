import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSplitter,
    QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QMessageBox, QDialog,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QAbstractItemView, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor, QFont, QDesktopServices

from transactions.controller import ReferencesController
from transactions.models import CategoryType
from transactions.views import CategoryForm, CounterpartyForm, MergeCategoryDialog


class CategoriesView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Название", "Тип", "Лимит в мес."])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet("""
            QTreeWidget { border: 1px solid #E2E8F0; border-radius: 8px; background-color: white; font-size: 14px; }
            QTreeWidget::item { padding: 6px; border-bottom: 1px solid #F1F5F9; }
            QTreeWidget::item:selected { background-color: #EEF2FF; color: #4F46E5; }
        """)
        layout.addWidget(self.tree)

    def load_data(self, search_text="", type_filter="Все"):
        self.tree.clear()
        roots = self.controller.get_categories_tree()

        def filter_cat(cat):
            match_name = search_text.lower() in cat.name.lower() if search_text else True
            match_type = True
            if type_filter == "Доход":
                match_type = cat.type == CategoryType.INCOME
            elif type_filter == "Расход":
                match_type = cat.type == CategoryType.EXPENSE
            return match_name and match_type

        def build_filtered(cats):
            res = []
            for c in cats:
                if filter_cat(c):
                    c.children = build_filtered(c.children)
                    res.append(c)
                else:
                    cf = build_filtered(c.children)
                    if cf:
                        c.children = cf
                        res.append(c)
            return res

        filtered_roots = build_filtered(roots)
        self._add_tree_items(self.tree, filtered_roots, is_root=True)
        self.tree.expandAll()

    def _add_tree_items(self, parent, categories, is_root=False):
        for cat in categories:
            item = QTreeWidgetItem(parent)
            icon = "📁 " if is_root and cat.children else "📄 "

            # Защита от пустых названий
            safe_name = cat.name if cat.name else "Без названия"
            item.setText(0, f"{icon}{safe_name}")

            type_text = "Доход" if cat.type == CategoryType.INCOME else "Расход"
            item.setText(1, "Смешанный" if is_root and cat.children and not cat.type else type_text)

            color = "#10B981" if cat.type == CategoryType.INCOME else "#EF4444"
            item.setForeground(1, QColor(color))

            limit_str = f"{cat.monthly_limit:,.2f} ₽" if cat.monthly_limit else "—"
            item.setText(2, limit_str)

            item.setData(0, Qt.ItemDataRole.UserRole, cat.id)
            if cat.children:
                self._add_tree_items(item, cat.children, is_root=False)

    def get_selected_id(self):
        item = self.tree.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None


class CounterpartiesView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Дерево контрагентов (Иерархия)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Название", "Тип", "Контакты"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet("""
            QTreeWidget { border: 1px solid #E2E8F0; border-radius: 8px; background-color: white; font-size: 14px; }
            QTreeWidget::item { padding: 6px; border-bottom: 1px solid #F1F5F9; }
            QTreeWidget::item:selected { background-color: #EEF2FF; color: #4F46E5; }
        """)
        self.tree.itemSelectionChanged.connect(self.update_360_card)
        splitter.addWidget(self.tree)

        # Карточка 360° (Правая панель)
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #E2E8F0;")
        card_layout = QVBoxLayout(self.card_frame)

        self.card_title = QLabel("Карточка 360°")
        self.card_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")
        card_layout.addWidget(self.card_title)

        self.lbl_paid = QLabel("Всего выплачено: —")
        self.lbl_debt = QLabel("Текущая задолженность: —")
        self.lbl_date = QLabel("Последняя операция: —")
        for lbl in [self.lbl_paid, self.lbl_debt, self.lbl_date]:
            lbl.setStyleSheet("font-size: 13px; color: #475569; padding: 4px 0;")
            card_layout.addWidget(lbl)

        self.btn_check_inn = QPushButton("🔍 Проверить ИНН (ЕГРЮЛ)")
        self.btn_check_inn.setStyleSheet("background: #F1F5F9; color: #475569; padding: 8px; border-radius: 6px;")
        self.btn_check_inn.clicked.connect(self.check_inn)
        self.btn_check_inn.setVisible(False)
        card_layout.addWidget(self.btn_check_inn)

        card_layout.addStretch()
        splitter.addWidget(self.card_frame)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

    def load_data(self, search_text="", type_filter="Все"):
        self.tree.clear()
        roots = self.controller.get_counterparties_tree()
        self._add_tree_items(self.tree, roots, search_text, type_filter)
        self.tree.expandAll()

    def _add_tree_items(self, parent, counterparties, search, type_f):
        for cp in counterparties:
            # СТРАХОВКА: Исключаем краш при поиске по None
            safe_name = cp.name if cp.name else "Без названия"
            safe_type = cp.type if cp.type else ""

            match_name = search.lower() in safe_name.lower() if search else True
            match_type = type_f == "Все" or safe_type == type_f

            item = QTreeWidgetItem(parent)
            icon = "🏢 " if cp.children else "👤 "
            item.setText(0, f"{icon}{safe_name}")
            item.setText(1, safe_type)
            item.setText(2, cp.contact_info or "")  # <-- or "" спасает от None
            item.setData(0, Qt.ItemDataRole.UserRole, cp.id)
            item.setData(1, Qt.ItemDataRole.UserRole, cp.requisites or "")

            if cp.children:
                self._add_tree_items(item, cp.children, search, type_f)
            elif not (match_name and match_type):
                item.setHidden(True)

    def update_360_card(self):
        item = self.tree.currentItem()
        if not item: return
        cp_id = item.data(0, Qt.ItemDataRole.UserRole)
        reqs = item.data(1, Qt.ItemDataRole.UserRole)

        name = item.text(0).replace("🏢 ", "").replace("👤 ", "")
        self.card_title.setText(f"Сводка: {name}")

        stats = self.controller.get_counterparty_summary(cp_id)
        self.lbl_paid.setText(f"Всего выплачено: {stats['total_paid']:,.2f} ₽")
        self.lbl_debt.setText(f"Текущая задолженность: {stats['current_debt']:,.2f} ₽")
        self.lbl_date.setText(f"Последняя операция: {stats['last_date'] or 'Нет данных'}")

        # Поиск ИНН (10 или 12 цифр) в реквизитах
        inn_match = re.search(r'\b\d{10,12}\b', reqs) if reqs else None
        if inn_match:
            self.btn_check_inn.setVisible(True)
            self.btn_check_inn.setProperty("inn", inn_match.group())
        else:
            self.btn_check_inn.setVisible(False)

    def check_inn(self):
        inn = self.btn_check_inn.property("inn")
        if inn:
            url = f"https://egrul.nalog.ru/index.html?query={inn}"
            QDesktopServices.openUrl(QUrl(url))

    def get_selected_id(self):
        item = self.tree.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None


class Module4Widget(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        # Сохраняем главный контроллер (на всякий случай, если он понадобится для других модулей)
        self.main_controller = controller

        # ИСПОЛЬЗУЕМ РОДНОЙ КОНТРОЛЛЕР СПРАВОЧНИКОВ:
        self.controller = ReferencesController()

        self.init_ui()
        self.load_current_view()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # 1. ЗАГОЛОВОК
        header = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.addWidget(QLabel("📚 Справочники", styleSheet="font-size: 24px; font-weight: bold; color: #1E293B;"))
        header.addLayout(title_vbox)
        header.addStretch()
        main_layout.addLayout(header)

        # 2. ПАНЕЛЬ ФИЛЬТРОВ И ВКЛАДОК
        controls_frame = QFrame(styleSheet="background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        controls_layout = QVBoxLayout(controls_frame)

        # Вкладки
        tabs_row = QHBoxLayout()
        self.btn_cats = QPushButton("📁 Категории")
        self.btn_cps = QPushButton("👥 Контрагенты")

        tab_style = """
            QPushButton { background: #F1F5F9; color: #475569; border-radius: 8px; padding: 8px 16px; border: none; font-weight: bold;}
            QPushButton:checked { background: #4F46E5; color: white; }
        """
        for btn in [self.btn_cats, self.btn_cps]:
            btn.setCheckable(True)
            btn.setStyleSheet(tab_style)
            tabs_row.addWidget(btn)

        self.btn_cats.setChecked(True)
        tabs_row.addStretch()
        controls_layout.addLayout(tabs_row)

        # Поиск и фильтры
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit(placeholderText="🔍 Поиск...")
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")

        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "Доход", "Расход"])
        self.type_filter.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")

        filter_row.addWidget(self.search_input)
        filter_row.addWidget(self.type_filter)
        filter_row.addStretch()

        # Кнопки действий
        btn_style = "padding: 8px 16px; border-radius: 6px; font-weight: bold; color: white; "

        self.merge_btn = QPushButton("🔗 Слияние")
        self.merge_btn.setStyleSheet(btn_style + "background: #8B5CF6;")

        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setStyleSheet(btn_style + "background: #10B981;")
        self.edit_btn = QPushButton("✏️ Изменить")
        self.edit_btn.setStyleSheet(btn_style + "background: #F59E0B;")
        self.delete_btn = QPushButton("🗑 Удалить")
        self.delete_btn.setStyleSheet(btn_style + "background: #EF4444;")

        filter_row.addWidget(self.merge_btn)
        filter_row.addWidget(self.add_btn)
        filter_row.addWidget(self.edit_btn)
        filter_row.addWidget(self.delete_btn)

        controls_layout.addLayout(filter_row)
        main_layout.addWidget(controls_frame)

        # 3. STACKED WIDGET
        self.stacked = QStackedWidget()
        self.categories_view = CategoriesView(self.controller)
        self.contractors_view = CounterpartiesView(self.controller)
        self.stacked.addWidget(self.categories_view)
        self.stacked.addWidget(self.contractors_view)
        main_layout.addWidget(self.stacked)

        # Сигналы
        self.btn_cats.clicked.connect(lambda: self.switch_tab(0))
        self.btn_cps.clicked.connect(lambda: self.switch_tab(1))
        self.search_input.textChanged.connect(self.load_current_view)
        self.type_filter.currentTextChanged.connect(self.load_current_view)

        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.merge_btn.clicked.connect(self.open_merge_dialog)

    def switch_tab(self, index):
        self.stacked.setCurrentIndex(index)
        self.btn_cats.setChecked(index == 0)
        self.btn_cps.setChecked(index == 1)
        self.merge_btn.setVisible(index == 0)  # Слияние только для категорий

        self.type_filter.blockSignals(True)
        self.type_filter.clear()
        if index == 0:
            self.type_filter.addItems(["Все", "Доход", "Расход"])
        else:
            self.type_filter.addItems(["Все", "Клиент", "Поставщик", "Сотрудник", "Прочие"])
        self.type_filter.blockSignals(False)
        self.load_current_view()

    def load_current_view(self):
        view = self.categories_view if self.stacked.currentIndex() == 0 else self.contractors_view
        view.load_data(self.search_input.text(), self.type_filter.currentText())

    def get_current_selected_id(self):
        view = self.categories_view if self.stacked.currentIndex() == 0 else self.contractors_view
        return view.get_selected_id()

    def open_merge_dialog(self):
        dlg = MergeCategoryDialog(self.controller)
        if dlg.exec():
            src, tgt = dlg.get_data()
            if src and tgt:
                try:
                    self.controller.merge_categories(src, tgt)
                    self.load_current_view()
                    QMessageBox.information(self, "Успех", "Категории успешно объединены!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", str(e))

    def add_item(self):
        is_cat = self.stacked.currentIndex() == 0
        sid = self.get_current_selected_id()

        if is_cat:
            form = CategoryForm(self.controller, initial_parent_id=sid)
        else:
            form = CounterpartyForm(self.controller, initial_parent_id=sid)

        if form.exec():
            self.load_current_view()

    def edit_item(self):
        sid = self.get_current_selected_id()
        if not sid: return QMessageBox.warning(self, "Внимание", "Выберите элемент")

        is_cat = self.stacked.currentIndex() == 0
        item = self.controller.get_category_by_id(sid) if is_cat else self.controller.get_counterparty_by_id(sid)
        form = CategoryForm(self.controller, cat_data=item) if is_cat else CounterpartyForm(self.controller,
                                                                                            cp_data=item)
        if form.exec(): self.load_current_view()

    def delete_item(self):
        sid = self.get_current_selected_id()
        if not sid: return QMessageBox.warning(self, "Внимание", "Выберите элемент")

        if QMessageBox.question(self, "Подтверждение", "Удалить элемент?") == QMessageBox.StandardButton.Yes:
            try:
                if self.stacked.currentIndex() == 0:
                    self.controller.delete_category(sid)
                else:
                    self.controller.delete_counterparty(sid)
                self.load_current_view()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))