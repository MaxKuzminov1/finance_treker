from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QDateEdit, QListWidget, QFrame,
    QGraphicsDropShadowEffect, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import QDate, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette
from form import TransactionForm
from datetime import datetime


class AnimatedButton(QPushButton):
    """Анимированная кнопка с эффектом наведения"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.original_geometry = None

    def enterEvent(self, event):
        self.original_geometry = self.geometry()
        self.animation.stop()
        self.animation.setDuration(200)
        self.animation.setStartValue(self.original_geometry)
        self.animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self.animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setDuration(200)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.original_geometry)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        super().leaveEvent(event)

class Module2Widget(QWidget):
    """Модуль 2. Управление бюджетом"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)

        title = QLabel("📊 Модуль 2. Управление бюджетом")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel("Планирование бюджета и контроль расходов")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(subtitle)

        info_label = QLabel("🚧 В разработке\n\nФункционал управления бюджетом будет добавлен в следующих версиях")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 16px; 
            color: #95a5a6; 
            background-color: #f8f9fc; 
            border: 2px dashed #bdc3c7; 
            border-radius: 15px; 
            padding: 50px;
        """)
        layout.addWidget(info_label)
        layout.addStretch()

        self.setLayout(layout)


class Module3Widget(QWidget):
    """Модуль 3. Аналитика и отчётность"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)

        title = QLabel("📈 Модуль 3. Аналитика и отчётность")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel("Анализ доходов и расходов, отчёты и графики")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(subtitle)

        info_label = QLabel("🚧 В разработке\n\nФункционал аналитики и отчётности будет добавлен в следующих версиях")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 16px; 
            color: #95a5a6; 
            background-color: #f8f9fc; 
            border: 2px dashed #bdc3c7; 
            border-radius: 15px; 
            padding: 50px;
        """)
        layout.addWidget(info_label)
        layout.addStretch()

        self.setLayout(layout)


class Module4Widget(QWidget):
    """Модуль 4. Справочники"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)

        title = QLabel("📚 Модуль 4. Справочники")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel("Управление справочной информацией")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(subtitle)

        info_label = QLabel("🚧 В разработке\n\nФункционал справочников будет добавлен в следующих версиях")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 16px; 
            color: #95a5a6; 
            background-color: #f8f9fc; 
            border: 2px dashed #bdc3c7; 
            border-radius: 15px; 
            padding: 50px;
        """)
        layout.addWidget(info_label)
        layout.addStretch()

        self.setLayout(layout)


class Module1Widget(QWidget):
    """Модуль 1. Учёт операций"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(25)

        # HEADER
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

        title = QLabel("Модуль 1. Учёт операций")
        title.setObjectName("title")

        subtitle = QLabel("Ввод и управление доходами и расходами | Полный контроль ваших финансов")
        subtitle.setObjectName("subtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header.setLayout(header_layout)

        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(15)
        header_shadow.setColor(QColor(0, 0, 0, 30))
        header_shadow.setOffset(0, 4)
        header.setGraphicsEffect(header_shadow)

        layout.addWidget(header)

        # КАРТОЧКА ФИЛЬТРОВ
        filter_card = QFrame()
        filter_card.setObjectName("filter_card")

        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(15)
        card_shadow.setColor(QColor(0, 0, 0, 20))
        card_shadow.setOffset(0, 2)
        filter_card.setGraphicsEffect(card_shadow)

        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(20)
        filter_layout.setContentsMargins(25, 20, 25, 20)

        # Поиск
        search_label = QLabel("🔍 Поиск операций (по комментарию)")
        search_label.setObjectName("search_label")
        filter_layout.addWidget(search_label)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Введите текст для поиска в комментарии...")
        self.search.setObjectName("search_input")
        filter_layout.addWidget(self.search)

        # Период и категория
        filters_grid = QHBoxLayout()
        filters_grid.setSpacing(20)

        # Период
        period_widget = QFrame()
        period_widget.setObjectName("period_widget")
        period_layout = QHBoxLayout()
        period_layout.setSpacing(10)

        period_label = QLabel("📅 Период:")
        period_label.setObjectName("filter_label")

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setObjectName("date_edit")

        date_sep = QLabel("→")
        date_sep.setObjectName("date_sep")

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setObjectName("date_edit")

        period_layout.addWidget(period_label)
        period_layout.addWidget(self.date_from)
        period_layout.addWidget(date_sep)
        period_layout.addWidget(self.date_to)
        period_widget.setLayout(period_layout)

        # Тип операции
        type_widget = QFrame()
        type_widget.setObjectName("category_widget")
        type_layout = QHBoxLayout()
        type_layout.setSpacing(10)

        type_label = QLabel("🏷️ Тип:")
        type_label.setObjectName("filter_label")

        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "💰 Доход", "💸 Расход"])
        self.type_filter.setObjectName("category_combo")

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_filter)
        type_widget.setLayout(type_layout)

        # Фильтр по категориям
        category_widget = QFrame()
        category_widget.setObjectName("category_widget")
        category_layout = QHBoxLayout()
        category_layout.setSpacing(10)

        category_label = QLabel("📁 Категория:")
        category_label.setObjectName("filter_label")

        self.category_filter = QComboBox()
        self.category_filter.addItems(["Все категории"])
        self.category_filter.setObjectName("category_combo")

        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_filter)
        category_widget.setLayout(category_layout)

        filters_grid.addWidget(period_widget)
        filters_grid.addWidget(type_widget)
        filters_grid.addWidget(category_widget)
        filters_grid.addStretch()

        filter_layout.addLayout(filters_grid)

        # Кнопки действий
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        self.add_btn = AnimatedButton("➕ Добавить операцию")
        self.edit_btn = AnimatedButton("✏️ Редактировать")
        self.delete_btn = AnimatedButton("🗑 Удалить")
        self.reset_btn = AnimatedButton("🔄 Сброс")
        export_btn = AnimatedButton("📤 Экспорт")
        import_btn = AnimatedButton("📥 Импорт")

        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.reset_btn, export_btn, import_btn]:
            btn.setObjectName("action_btn")

        self.add_btn.setProperty("class", "primary")
        self.edit_btn.setProperty("class", "warning")
        self.delete_btn.setProperty("class", "danger")
        export_btn.setProperty("class", "success")
        import_btn.setProperty("class", "warning")
        self.reset_btn.setProperty("class", "secondary")

        buttons_row.addWidget(self.add_btn)
        buttons_row.addWidget(self.edit_btn)
        buttons_row.addWidget(self.delete_btn)
        buttons_row.addStretch()
        buttons_row.addWidget(self.reset_btn)
        buttons_row.addWidget(export_btn)
        buttons_row.addWidget(import_btn)

        filter_layout.addLayout(buttons_row)
        filter_card.setLayout(filter_layout)
        layout.addWidget(filter_card)

        # ТАБЛИЦА
        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_card.setGraphicsEffect(card_shadow)

        table_layout = QVBoxLayout()
        table_layout.setSpacing(15)
        table_layout.setContentsMargins(25, 20, 25, 20)

        table_header_widget = QFrame()
        table_header_layout = QHBoxLayout()
        table_header_layout.setContentsMargins(0, 0, 0, 0)

        table_title = QLabel("📋 Журнал операций")
        table_title.setObjectName("table_title")

        self.records_count = QLabel("Записей: 0")
        self.records_count.setObjectName("records_count_badge")

        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()
        table_header_layout.addWidget(self.records_count)
        table_header_widget.setLayout(table_header_layout)

        table_layout.addWidget(table_header_widget)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "📅 Дата", "📊 Тип", "💰 Сумма",
            "📁 Категории", "💬 Комментарий", "💳 Оплачено", "📊 Остаток", "📌 Статус"
        ])
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setObjectName("data_table")
        self.table.setSortingEnabled(True)

        table_layout.addWidget(self.table)
        table_card.setLayout(table_layout)
        layout.addWidget(table_card)

        self.setLayout(layout)

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

    def load_categories_for_filter(self):
        """Загрузка категорий для фильтра"""
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
        from PyQt6.QtWidgets import QFileDialog
        import pandas as pd

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Экспорт данных",
                "",
                "Excel (*.xlsx);;CSV (*.csv)"
            )

            if not file_path:
                return

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

            QMessageBox.information(
                self,
                "Экспорт завершён",
                f"✅ Данные успешно сохранены:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def refresh(self):
        data = self.controller.get_all()

        search_text = self.search.text().lower().strip()
        t_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()

        type_map = {
            "Все": None,
            "💰 Доход": "income",
            "💸 Расход": "expense"
        }

        db_filter = type_map.get(t_filter)

        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        filtered = []

        for t in data:
            # SEARCH
            comment = str(t.get("comment", "")).lower()
            if search_text and search_text not in comment:
                continue

            # TYPE
            if db_filter and t.get("type") != db_filter:
                continue

            # CATEGORY
            cats = t.get("categories", [])
            cat_names = []
            if isinstance(cats, list):
                for c in cats:
                    if isinstance(c, dict):
                        cat_names.append(str(c.get("name", "")))
                    else:
                        cat_names.append(str(c))
            elif isinstance(cats, str):
                cat_names = [cats]

            if category_filter != "Все категории":
                if category_filter not in cat_names:
                    continue

            # DATE
            raw_date = t.get("date")
            try:
                if isinstance(raw_date, datetime):
                    trans_date = raw_date.date()
                elif isinstance(raw_date, str):
                    from datetime import date
                    trans_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
                else:
                    continue
            except:
                continue

            if trans_date < date_from or trans_date > date_to:
                continue

            filtered.append(t)

        self.table.setRowCount(len(filtered))

        type_colors = {
            "income": QColor("#27ae60"),
            "expense": QColor("#e74c3c")
        }

        type_icons = {
            "income": "💰",
            "expense": "💸"
        }

        for i, t in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(str(t.get("id", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(t.get("date", ""))))

            t_type = t.get("type", "")
            type_item = QTableWidgetItem(f"{type_icons.get(t_type, '')} {'Доход' if t_type == 'income' else 'Расход'}")
            type_item.setForeground(type_colors.get(t_type, QColor("#333")))
            self.table.setItem(i, 2, type_item)

            amount = t.get("total_amount", 0)
            amount_item = QTableWidgetItem(f"{amount:,.2f} ₽")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 3, amount_item)

            # категории
            cats = t.get("categories", [])
            if isinstance(cats, list):
                names = [str(c.get("name", "")) for c in cats if isinstance(c, dict)]
            elif isinstance(cats, str):
                names = [cats]
            else:
                names = []
            self.table.setItem(i, 4, QTableWidgetItem(", ".join(names)))

            self.table.setItem(i, 5, QTableWidgetItem(str(t.get("comment", ""))))

            paid_item = QTableWidgetItem(f"{t.get('paid', 0):,.2f} ₽")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 6, paid_item)

            remaining_item = QTableWidgetItem(f"{t.get('remaining', 0):,.2f} ₽")
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 7, remaining_item)

            status_item = QTableWidgetItem(str(t.get("status", "")))
            if t.get("status") == "Оплачена":
                status_item.setForeground(QColor("#27ae60"))
            elif t.get("status") == "Частично":
                status_item.setForeground(QColor("#f39c12"))
            else:
                status_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(i, 8, status_item)

        self.records_count.setText(f"📊 Найдено записей: {len(filtered)}")
        self.table.resizeColumnsToContents()

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
        if row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите операцию для редактирования")
            return

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
        if row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите операцию для удаления")
            return

        tid = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы действительно хотите удалить операцию #{tid}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete(tid)
            self.load_categories_for_filter()
            self.refresh()
            QMessageBox.information(self, "Успех", "Операция успешно удалена!")

    def import_data(self):
        from PyQt6.QtWidgets import QFileDialog
        import pandas as pd
        from datetime import datetime

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

                    date = datetime.now().strftime("%Y-%m-%d")
                    if col_date and not pd.isna(row[col_date]):
                        try:
                            date = pd.to_datetime(row[col_date]).strftime("%Y-%m-%d")
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
                        "date": date,
                        "type": ttype,
                        "total_amount": amount,
                        "comment": comment,
                        "categories": [{"name": category, "amount": amount}],
                        "payments": [{"date": date, "amount": amount}]
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


class View(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Программа комплексного учёта доходов и расходов малого бизнеса")
        self.resize(1400, 850)
        self.setMinimumSize(1200, 700)

        # Главный layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =========================
        # SIDEBAR
        # =========================
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setObjectName("sidebar")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(4, 0)
        sidebar.setGraphicsEffect(shadow)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(25)
        sidebar_layout.setContentsMargins(20, 35, 20, 35)

        # Логотип
        logo_container = QLabel()
        logo_container.setText("💰 FINANCE PRO")
        logo_container.setObjectName("logo")
        sidebar_layout.addWidget(logo_container)

        # Декоративная линия
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("sidebar_line")
        sidebar_layout.addWidget(line)

        # Модули
        modules_label = QLabel("МОДУЛИ")
        modules_label.setObjectName("modules_label")
        sidebar_layout.addWidget(modules_label)

        self.menu = QListWidget()
        self.menu.addItems([
            "📊 Учёт операций",
            "💰 Управление бюджетом",
            "📈 Аналитика и отчётность",
            "📚 Справочники"
        ])
        self.menu.setObjectName("menu_list")
        self.menu.setCurrentRow(0)
        sidebar_layout.addWidget(self.menu)

        sidebar_layout.addStretch()

        # Информация о программе
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_layout = QVBoxLayout()

        prog_label = QLabel("ℹ️ О программе")
        prog_label.setObjectName("info_title")
        info_layout.addWidget(prog_label)

        info1 = QLabel("• Локальная база данных")
        info2 = QLabel("• Работа без интернета")
        info3 = QLabel("• Автосохранение")
        info1.setObjectName("info_text")
        info2.setObjectName("info_text")
        info3.setObjectName("info_text")

        info_layout.addWidget(info1)
        info_layout.addWidget(info2)
        info_layout.addWidget(info3)
        info_frame.setLayout(info_layout)
        sidebar_layout.addWidget(info_frame)

        sidebar.setLayout(sidebar_layout)

        # =========================
        # STACKED WIDGET (для переключения модулей)
        # =========================
        self.stacked_widget = QStackedWidget()

        # Создаём виджеты для каждого модуля
        self.module1 = Module1Widget(controller)
        self.module2 = Module2Widget(controller)
        self.module3 = Module3Widget(controller)
        self.module4 = Module4Widget(controller)

        # Добавляем в стек
        self.stacked_widget.addWidget(self.module1)  # индекс 0
        self.stacked_widget.addWidget(self.module2)  # индекс 1
        self.stacked_widget.addWidget(self.module3)  # индекс 2
        self.stacked_widget.addWidget(self.module4)  # индекс 3

        # Подключаем сигнал переключения меню
        self.menu.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget, 1)

        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #f8f9fc;
            font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        #sidebar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
            border-right: none;
        }

        #logo {
            font-size: 26px;
            font-weight: bold;
            color: #00d2ff;
            padding: 10px 0px;
            letter-spacing: 1px;
        }

        #sidebar_line {
            background-color: rgba(255, 255, 255, 0.1);
            max-height: 1px;
        }

        #modules_label {
            font-size: 11px;
            letter-spacing: 2px;
            color: #a8b2c9;
            margin-top: 10px;
            margin-bottom: 5px;
        }

        #menu_list {
            background-color: transparent;
            border: none;
            color: #c4c4e6;
            font-size: 14px;
            outline: none;
        }

        #menu_list::item {
            padding: 12px 15px;
            border-radius: 12px;
            margin: 4px 0px;
            background-color: transparent;
            color: #c4c4e6;
        }

        #menu_list::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d2ff, stop:1 #3a7bd5);
            color: white;
        }

        #menu_list::item:hover {
            background-color: rgba(0, 210, 255, 0.2);
            color: white;
        }

        #info_frame {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 15px;
            margin-top: 10px;
        }

        #info_title {
            color: #00d2ff;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        #info_text {
            color: #a8b2c9;
            font-size: 11px;
            margin: 4px 0px;
        }

        #header {
            border-radius: 20px;
            padding: 25px 30px;
        }

        #title {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            letter-spacing: -0.5px;
        }

        #subtitle {
            font-size: 13px;
            color: #7f8c8d;
            margin-top: 5px;
        }

        #filter_card, #table_card {
            background-color: white;
            border-radius: 20px;
            border: none;
        }

        #search_label {
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }

        #search_input {
            background-color: #f8f9fc;
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            padding: 12px 15px;
            font-size: 13px;
            color: #2c3e50;
        }

        #search_input:focus {
            border-color: #3498db;
            background-color: white;
        }

        #period_widget, #category_widget {
            background-color: #f8f9fc;
            border-radius: 12px;
            padding: 8px 15px;
        }

        .filter_label, #filter_label {
            font-size: 13px;
            font-weight: 500;
            color: #7f8c8d;
        }

        #date_edit, #category_combo {
            background-color: white;
            border: 1px solid #dcdde1;
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 120px;
            font-size: 12px;
            color: #2c3e50;
        }

        #date_edit:focus, #category_combo:focus {
            border-color: #3498db;
        }

        #date_sep {
            font-weight: bold;
            color: #3498db;
            margin: 0px 5px;
        }

        #action_btn {
            border: none;
            border-radius: 10px;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 11px;
        }

        #action_btn[class="primary"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2980b9);
            color: white;
            padding: 8px 18px;
            font-size: 12px;
        }

        #action_btn[class="warning"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f39c12, stop:1 #e67e22);
            color: white;
        }

        #action_btn[class="danger"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e74c3c, stop:1 #c0392b);
            color: white;
        }

        #action_btn[class="success"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #27ae60, stop:1 #229954);
            color: white;
        }

        #action_btn[class="secondary"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #95a5a6, stop:1 #7f8c8d);
            color: white;
        }

        #table_title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }

        #records_count_badge {
            background-color: #ecf0f1;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 12px;
            color: #7f8c8d;
            font-weight: 500;
        }

        #data_table {
            background-color: white;
            border: none;
            alternate-background-color: #fafbfc;
            gridline-color: #e1e8ed;
            border-radius: 12px;
        }

        #data_table::item {
            padding: 12px;
            color: #2c3e50;
        }

        #data_table::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2980b9);
            color: white;
        }

        QHeaderView::section {
            background-color: #f1f2f6;
            padding: 15px;
            border: none;
            border-bottom: 2px solid #e1e8ed;
            font-weight: bold;
            font-size: 12px;
            color: #2c3e50;
        }

        QTableCornerButton::section {
            background-color: #f1f2f6;
            border: none;
        }

        QScrollBar:vertical {
            background: #f0f2f5;
            width: 10px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2980b9);
            border-radius: 5px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2980b9, stop:1 #2471a3);
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """)