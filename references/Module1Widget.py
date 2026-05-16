# Module1Widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QDateEdit, QFrame,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime, date
import pandas as pd

from .form import TransactionForm


class Module1Widget(QWidget):
    """Модуль 1. Учёт операций"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_theme = "light"
        # ИСПРАВЛЕНИЕ: Убрали жестко заданный белый фон, чтобы окно было прозрачным
        # и наследовало правильный тёмный или светлый фон от main_view.
        self.init_ui()

    def apply_theme(self, theme: str):
        """Перехват смены темы для динамического обновления цветов"""
        self.current_theme = theme
        self.refresh()

    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # ЗАГОЛОВОК
        header = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.addWidget(
            QLabel("Модуль 1. Учёт операций",
                   styleSheet="font-size: 24px; font-weight: bold; color: #1E293B;"))
        title_vbox.addWidget(QLabel("Ввод и управление доходами и расходами | Полный контроль ваших финансов",
                                    styleSheet="color: #64748B; font-size: 13px;"))

        header.addLayout(title_vbox)
        header.addStretch()
        main_layout.addLayout(header)

        # КАРТОЧКА ФИЛЬТРОВ
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)

        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(15)
        filter_layout.setContentsMargins(20, 20, 20, 20)

        # Поиск
        search_label = QLabel("🔍 Поиск операций")
        search_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")
        filter_layout.addWidget(search_label)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Введите текст для поиска в комментарии...")
        self.search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4F46E5;
            }
        """)
        filter_layout.addWidget(self.search)

        # Строка фильтров
        filters_row = QHBoxLayout()
        filters_row.setSpacing(15)

        # Период
        period_frame = QFrame()
        period_frame.setStyleSheet("""
            QFrame {
                background: #F8FAFC;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        period_layout = QHBoxLayout(period_frame)
        period_layout.setSpacing(8)
        period_layout.setContentsMargins(10, 5, 10, 5)

        period_label = QLabel("📅 Период:")
        period_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setStyleSheet("""
            QDateEdit {
                padding: 6px 10px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background: white;
                font-size: 12px;
            }
        """)

        date_sep = QLabel("→")
        date_sep.setStyleSheet("color: #94A3B8; font-weight: bold;")

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setStyleSheet("""
            QDateEdit {
                padding: 6px 10px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background: white;
                font-size: 12px;
            }
        """)

        period_layout.addWidget(period_label)
        period_layout.addWidget(self.date_from)
        period_layout.addWidget(date_sep)
        period_layout.addWidget(self.date_to)

        # Тип операции
        type_frame = QFrame()
        type_frame.setStyleSheet("""
            QFrame {
                background: #F8FAFC;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        type_layout = QHBoxLayout(type_frame)
        type_layout.setSpacing(8)
        type_layout.setContentsMargins(10, 5, 10, 5)

        type_label = QLabel("🏷️ Тип:")
        type_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")

        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "💰 Доход", "💸 Расход"])
        self.type_filter.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background: white;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #4F46E5;
            }
        """)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_filter)

        # Категория
        category_frame = QFrame()
        category_frame.setStyleSheet("""
            QFrame {
                background: #F8FAFC;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        category_layout = QHBoxLayout(category_frame)
        category_layout.setSpacing(8)
        category_layout.setContentsMargins(10, 5, 10, 5)

        category_label = QLabel("📁 Категория:")
        category_label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")

        self.category_filter = QComboBox()
        self.category_filter.addItems(["Все категории"])
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background: white;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #4F46E5;
            }
        """)

        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_filter)

        filters_row.addWidget(period_frame)
        filters_row.addWidget(type_frame)
        filters_row.addWidget(category_frame)
        filters_row.addStretch()

        filter_layout.addLayout(filters_row)

        # Кнопки действий
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        self.add_btn = QPushButton("➕ Добавить операцию")
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.delete_btn = QPushButton("🗑 Удалить")
        self.reset_btn = QPushButton("🔄 Сброс")
        export_btn = QPushButton("📤 Экспорт")
        import_btn = QPushButton("📥 Импорт")

        button_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
        """

        self.add_btn.setStyleSheet(button_style + """
            QPushButton { background-color: #4F46E5; color: white; border: none; }
            QPushButton:hover { background-color: #6366F1; }
        """)

        self.edit_btn.setStyleSheet(button_style + """
            QPushButton { background-color: #F59E0B; color: white; border: none; }
            QPushButton:hover { background-color: #D97706; }
        """)

        self.delete_btn.setStyleSheet(button_style + """
            QPushButton { background-color: #EF4444; color: white; border: none; }
            QPushButton:hover { background-color: #DC2626; }
        """)

        self.reset_btn.setStyleSheet(button_style + """
            QPushButton { background-color: #64748B; color: white; border: none; }
            QPushButton:hover { background-color: #475569; }
        """)

        export_btn.setStyleSheet(button_style + """
            QPushButton { background-color: #10B981; color: white; border: none; }
            QPushButton:hover { background-color: #059669; }
        """)

        import_btn.setStyleSheet(button_style + """
            QPushButton { background-color: #8B5CF6; color: white; border: none; }
            QPushButton:hover { background-color: #7C3AED; }
        """)

        buttons_row.addWidget(self.add_btn)
        buttons_row.addWidget(self.edit_btn)
        buttons_row.addWidget(self.delete_btn)
        buttons_row.addStretch()
        buttons_row.addWidget(self.reset_btn)
        buttons_row.addWidget(export_btn)
        buttons_row.addWidget(import_btn)

        filter_layout.addLayout(buttons_row)
        filter_card.setLayout(filter_layout)
        main_layout.addWidget(filter_card)

        # КАРТОЧКА ТАБЛИЦЫ
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)

        table_layout = QVBoxLayout()
        table_layout.setSpacing(15)
        table_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок таблицы
        table_header = QHBoxLayout()
        table_title = QLabel("📋 Журнал операций")
        table_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")

        self.records_count = QLabel("Записей: 0")
        self.records_count.setStyleSheet("""
            background-color: #F1F5F9;
            padding: 4px 12px;
            border-radius: 12px;
            color: #475569;
            font-size: 12px;
            font-weight: bold;
        """)

        table_header.addWidget(table_title)
        table_header.addStretch()
        table_header.addWidget(self.records_count)

        table_layout.addLayout(table_header)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "📅 Дата", "📊 Тип", "💰 Сумма",
            "📁 Категории", "💬 Комментарий", "💳 Оплачено", "📊 Остаток", "📌 Статус"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                alternate-background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected { background-color: #EEF2FF; color: #4F46E5; }
            QHeaderView::section {
                background: #F8FAFC;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: bold;
                color: #475569;
                font-size: 12px;
            }
        """)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)  # ID
        self.table.setColumnWidth(1, 150)  # Дата
        self.table.setColumnWidth(2, 100)  # Тип
        self.table.setColumnWidth(3, 150)  # Сумма
        self.table.setColumnWidth(4, 150)  # Категории
        self.table.setColumnWidth(5, 200)  # Комментарий
        self.table.setColumnWidth(6, 100)  # Оплачено
        self.table.setColumnWidth(7, 100)  # Остаток
        self.table.setColumnWidth(8, 100)  # Статус

        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.table)
        table_card.setLayout(table_layout)
        main_layout.addWidget(table_card)

        self.setLayout(main_layout)

        # Подключаем сигналы
        self.search.textChanged.connect(self.refresh)
        self.type_filter.currentTextChanged.connect(self.refresh)
        self.category_filter.currentTextChanged.connect(self.refresh)
        self.date_from.dateChanged.connect(self.refresh)
        self.date_to.dateChanged.connect(self.refresh)
        self.add_btn.clicked.connect(self.add)
        self.edit_btn.clicked.connect(self.edit)
        self.delete_btn.clicked.connect(self.delete)
        self.reset_btn.clicked.connect(self.reset_filters)
        export_btn.clicked.connect(self.export_data)
        import_btn.clicked.connect(self.import_data)

        self.load_categories_for_filter()
        self.refresh()

    def filter_by_category(self, category_name: str):
        """Метод для внешнего вызова (Drill-down из аналитики)"""
        index = self.category_filter.findText(category_name)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)

    def load_categories_for_filter(self):
        try:
            categories = self.controller.get_categories()
            current_text = self.category_filter.currentText()

            self.category_filter.blockSignals(True)
            self.category_filter.clear()
            self.category_filter.addItem("Все категории")
            for cat in categories:
                self.category_filter.addItem(cat["name"])

            index = self.category_filter.findText(current_text)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)
            self.category_filter.blockSignals(False)
        except Exception as e:
            print(f"Ошибка при загрузке категорий: {e}")

    def reset_filters(self):
        self.search.clear()
        self.type_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.refresh()

    def export_data(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Экспорт данных", "", "Excel (*.xlsx);;CSV (*.csv)")
            if not file_path: return

            data = self.controller.get_all()
            rows = []
            for t in data:
                cats = t.get("categories", [])
                if isinstance(cats, list):
                    category = ", ".join(str(c.get("name", "")) for c in cats if isinstance(c, dict))
                else:
                    category = str(cats)

                rows.append({
                    "date": t.get("date", ""),
                    "type": t.get("type", ""),
                    "amount": t.get("total_amount", 0),
                    "comment": t.get("comment", ""),
                    "category": category,
                    "payment_date": t.get("date", ""),
                    "payment_amount": t.get("paid", 0),
                })

            df = pd.DataFrame(rows)
            if file_path.endswith(".csv"):
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
            else:
                df.to_excel(file_path, index=False)

            QMessageBox.information(self, "Экспорт завершён", f"✅ Данные успешно сохранены:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def refresh(self):
        data = self.controller.get_all()

        search_text = self.search.text().lower().strip()
        t_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()

        type_map = {"Все": None, "💰 Доход": "income", "💸 Расход": "expense"}
        db_filter = type_map.get(t_filter)

        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        filtered = []

        for t in data:
            comment = str(t.get("comment", "")).lower()
            if search_text and search_text not in comment: continue
            if db_filter and t.get("type") != db_filter: continue

            cats = t.get("categories", [])
            cat_names = []
            if isinstance(cats, list):
                for c in cats:
                    if isinstance(c, dict):
                        cat_names.append(str(c.get("name", "")))
                    else:
                        cat_names.append(str(c))
            elif isinstance(cats, str):
                cat_names = [c.strip() for c in cats.split(',')]

            if category_filter != "Все категории" and category_filter not in cat_names:
                continue

            raw_date = t.get("date")
            try:
                if isinstance(raw_date, datetime):
                    trans_date = raw_date.date()
                elif isinstance(raw_date, date):
                    trans_date = raw_date
                elif isinstance(raw_date, str):
                    trans_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
                else:
                    continue
            except:
                continue

            if trans_date < date_from or trans_date > date_to: continue

            filtered.append(t)

        self.table.setRowCount(len(filtered))

        type_colors = {"income": QColor("#10B981"), "expense": QColor("#EF4444")}
        type_icons = {"income": "💰", "expense": "💸"}

        # Динамический цвет текста для записей таблицы
        base_text_color = QColor("#E5E7EB") if getattr(self, "current_theme", "light") == "dark" else QColor("#475569")

        for i, t in enumerate(filtered):
            # ID
            item_id = QTableWidgetItem(str(t.get("id", "")))
            item_id.setForeground(base_text_color)
            self.table.setItem(i, 0, item_id)

            # ДАТА
            date_value = t.get("date", "")
            if isinstance(date_value, (datetime, date)):
                date_str = date_value.strftime("%d.%m.%Y")
            elif isinstance(date_value, str):
                date_str = f"{date_value[8:10]}.{date_value[5:7]}.{date_value[0:4]}" if len(
                    date_value) >= 10 else date_value
            else:
                date_str = str(date_value)

            item_date = QTableWidgetItem(date_str)
            item_date.setForeground(base_text_color)
            self.table.setItem(i, 1, item_date)

            # Тип
            t_type = t.get("type", "")
            type_item = QTableWidgetItem(f"{type_icons.get(t_type, '')} {'Доход' if t_type == 'income' else 'Расход'}")
            type_item.setForeground(type_colors.get(t_type, base_text_color))
            self.table.setItem(i, 2, type_item)

            # Сумма
            amount = t.get("total_amount", 0)
            amount_item = QTableWidgetItem(f"{amount:,.2f} ₽")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            amount_item.setForeground(base_text_color)
            font = amount_item.font()
            font.setBold(True)
            amount_item.setFont(font)
            self.table.setItem(i, 3, amount_item)

            # Категории
            cats_display = t.get("categories", "")
            cats_str = ", ".join([str(c.get("name", "")) for c in cats_display if isinstance(c, dict)]) if isinstance(
                cats_display, list) else (str(cats_display) if cats_display else "Без категории")
            item_cat = QTableWidgetItem(cats_str)
            item_cat.setForeground(base_text_color)
            self.table.setItem(i, 4, item_cat)

            # Комментарий
            item_com = QTableWidgetItem(str(t.get("comment", "")))
            item_com.setForeground(base_text_color)
            self.table.setItem(i, 5, item_com)

            # Оплачено
            paid_item = QTableWidgetItem(f"{t.get('paid', 0):,.2f} ₽")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            paid_item.setForeground(base_text_color)
            self.table.setItem(i, 6, paid_item)

            # Остаток
            remaining_item = QTableWidgetItem(f"{t.get('remaining', 0):,.2f} ₽")
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            remaining_item.setForeground(base_text_color)
            self.table.setItem(i, 7, remaining_item)

            # Статус
            status = t.get("status", "")
            status_item = QTableWidgetItem(status)
            if status == "Оплачена":
                status_item.setForeground(QColor("#10B981"))
            elif status == "Частично":
                status_item.setForeground(QColor("#F59E0B"))
            else:
                status_item.setForeground(QColor("#EF4444"))
            self.table.setItem(i, 8, status_item)

        self.records_count.setText(f"📊 Записей: {len(filtered)}")

    def add(self):
        try:
            form = TransactionForm(self.controller)
            if form.exec():
                self.load_categories_for_filter()
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму: {e}")

    def edit(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Предупреждение",
                                               "Пожалуйста, выберите операцию для редактирования")

        try:
            tid = int(self.table.item(row, 0).text())
            form = TransactionForm(self.controller, tid)
            if form.exec():
                self.load_categories_for_filter()
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму редактирования: {e}")

    def delete(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите операцию для удаления")

        tid = int(self.table.item(row, 0).text())
        if QMessageBox.question(self, "Подтверждение", f"Удалить операцию #{tid}?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.controller.delete(tid)
            self.load_categories_for_filter()
            self.refresh()

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для импорта",
            "",
            "Excel (*.xlsx *.xls);;CSV (*.csv)"
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                try:
                    df = pd.read_csv(file_path, encoding="utf-8")
                except:
                    df = pd.read_csv(file_path, encoding="cp1251")
            else:
                df = pd.read_excel(file_path)

            if df.empty:
                QMessageBox.warning(self, "Ошибка", "Файл пуст")
                return

            df.columns = [str(c).strip().lower() for c in df.columns]

            def find(*keys):
                for k in keys:
                    for col in df.columns:
                        if k in col:
                            return col
                return None

            col_amount = find("amount", "сумма", "total", "sum")
            col_date = find("date", "дата")
            col_type = find("type", "тип")
            col_comment = find("comment", "коммент", "опис")
            col_category = find("category", "категор")

            if not col_amount:
                QMessageBox.critical(self, "Ошибка", "Не найдена колонка суммы")
                return

            transactions = []

            for i, row in df.iterrows():
                try:
                    raw_amount = row[col_amount]
                    if pd.isna(raw_amount):
                        continue

                    amount = float(str(raw_amount).replace(",", "."))
                    if amount == 0:
                        continue

                    date_str_val = datetime.now().strftime("%Y-%m-%d")
                    if col_date and not pd.isna(row[col_date]):
                        try:
                            date_str_val = pd.to_datetime(row[col_date]).strftime("%Y-%m-%d")
                        except:
                            pass

                    ttype = "expense"
                    if col_type and not pd.isna(row[col_type]):
                        if "доход" in str(row[col_type]).lower() or "income" in str(row[col_type]).lower():
                            ttype = "income"

                    comment = ""
                    if col_comment and not pd.isna(row[col_comment]):
                        comment = str(row[col_comment])

                    category = "Прочее"
                    if col_category and not pd.isna(row[col_category]):
                        category = str(row[col_category])

                    transactions.append({
                        "date": date_str_val,
                        "type": ttype,
                        "total_amount": amount,
                        "comment": comment,
                        "categories": [{"name": category, "amount": amount}],
                        "payments": [{"date": date_str_val, "amount": amount}]
                    })

                except Exception as e:
                    print(f"Ошибка строки {i + 1}: {e}")

            if not transactions:
                QMessageBox.warning(self, "Ошибка", "Нет валидных данных")
                return

            imported, errors = self.controller.import_transactions(transactions)

            self.load_categories_for_filter()
            self.refresh()

            QMessageBox.information(
                self,
                "Импорт завершён",
                f"✅ Успешно: {imported}\n❌ Ошибок: {len(errors) if errors else 0}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка импорта", str(e))