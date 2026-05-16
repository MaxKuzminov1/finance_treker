from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QComboBox, QFrame, QTabWidget, QHeaderView,
    QDateEdit, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor

import calendar
from .dialogs import BudgetAddDialog, BudgetEditDialog
from .plan_fact import PlanFactTab


class TemplateSaveDialog(QDialog):
    """Кастомный диалог для сохранения шаблона с красивым UI"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_name = ""

        self.setWindowTitle("⭐ Сохранение шаблона")
        self.setFixedSize(400, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #F8FAFC; color: #1E293B;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Название нового шаблона")
        title.setStyleSheet("font-weight: 800; font-size: 16px; color: #1E293B;")
        layout.addWidget(title)

        desc = QLabel("Введите понятное имя, чтобы легко найти его позже.")
        desc.setStyleSheet("color: #64748B; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Базовый на месяц...")
        self.name_input.setStyleSheet("""
            QLineEdit { padding: 12px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; font-size: 14px; color: #1E293B; }
            QLineEdit:focus { border-color: #4F46E5; }
        """)
        layout.addWidget(self.name_input)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton { background: white; color: #475569; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 16px; font-weight: bold; }
            QPushButton:hover { background: #F1F5F9; }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("""
            QPushButton { background: #4F46E5; color: white; border: none; border-radius: 8px; padding: 10px 24px; font-weight: bold; }
            QPushButton:hover { background: #4338CA; }
        """)
        save_btn.clicked.connect(self.save)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название шаблона!")
            return
        self.template_name = name
        self.accept()


class TemplateManagerDialog(QDialog):
    """Диалог управления (загрузка/удаление) именованными шаблонами"""

    def __init__(self, templates, parent=None):
        super().__init__(parent)
        self.templates = templates
        self.selected_template_id = None
        self.selected_template_name = None
        self.action = None

        self.setWindowTitle("📥 Менеджер шаблонов")
        self.setFixedSize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #F8FAFC; color: #1E293B;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Выберите сохраненный шаблон:")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E293B;")
        layout.addWidget(title)

        self.combo = QComboBox()
        for tid, tname in self.templates:
            self.combo.addItem(f"📁 {tname}", tid)
        self.combo.setStyleSheet("""
            QComboBox { padding: 10px 12px; border: 1px solid #CBD5E1; border-radius: 8px; background: white; font-size: 14px; color: #1E293B; }
        """)
        layout.addWidget(self.combo)

        layout.addStretch()

        btn_layout = QHBoxLayout()

        del_btn = QPushButton("🗑 Удалить")
        del_btn.setStyleSheet("""
            QPushButton { background: #FEE2E2; color: #DC2626; border-radius: 8px; padding: 10px 16px; font-weight: bold; } 
            QPushButton:hover { background: #FECACA; }
        """)
        del_btn.clicked.connect(self.on_delete)

        load_btn = QPushButton("📥 Загрузить")
        load_btn.setStyleSheet("""
            QPushButton { background: #4F46E5; color: white; border-radius: 8px; padding: 10px 24px; font-weight: bold; } 
            QPushButton:hover { background: #4338CA; }
        """)
        load_btn.clicked.connect(self.on_load)

        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(load_btn)

        layout.addLayout(btn_layout)

    def on_load(self):
        self.selected_template_id = self.combo.currentData()
        self.selected_template_name = self.combo.currentText().replace("📁 ", "")
        self.action = 'load'
        self.accept()

    def on_delete(self):
        self.selected_template_id = self.combo.currentData()
        self.selected_template_name = self.combo.currentText().replace("📁 ", "")
        self.action = 'delete'
        self.accept()


class Module2Widget(QWidget):
    """Модуль 2. Управление бюджетом"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.budget_ids = []
        self.budget_counts = []
        self.budget_cat_ids = []
        self.categories = []
        self.current_theme = "light"
        self.block_refresh = False

        self.setStyleSheet("background-color: #F3F4F6;")

        # Автоматическое создание таблиц для именных шаблонов (выполнится один раз)
        self._init_template_tables()

        self.init_ui()
        self.load_categories()
        self.load_budgets()

        # 🔄 УМНЫЙ ТАЙМЕР АВТООБНОВЛЕНИЯ
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.setInterval(2000)
        self.auto_refresh_timer.timeout.connect(self.auto_refresh_data)
        self.auto_refresh_timer.start()

    def _init_template_tables(self):
        """Создает таблицы для хранения шаблонов, если их еще нет в базе"""
        try:
            self.controller.execute("""
                CREATE TABLE IF NOT EXISTS budget_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE
                )
            """)
            self.controller.execute("""
                CREATE TABLE IF NOT EXISTS budget_template_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    template_id INT NOT NULL,
                    category_id INT NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    FOREIGN KEY (template_id) REFERENCES budget_templates(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)
        except Exception as e:
            print(f"Ошибка при инициализации таблиц шаблонов: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_all()

    def auto_refresh_data(self):
        if self.isVisible() and not self.block_refresh:
            self.refresh_all()

    def apply_theme(self, theme: str):
        self.current_theme = theme
        self.refresh_all()

    def sync_matplotlib_theme(self):
        try:
            import matplotlib
            if self.current_theme == "dark":
                matplotlib.rcParams.update({
                    'figure.facecolor': '#111827',
                    'axes.facecolor': '#111827',
                    'text.color': '#E5E7EB',
                    'axes.labelcolor': '#E5E7EB',
                    'xtick.color': '#94A3B8',
                    'ytick.color': '#94A3B8',
                    'grid.color': '#334155',
                    'legend.facecolor': '#182235',
                    'legend.edgecolor': '#334155',
                })
            else:
                matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        except ImportError:
            pass

    def patch_all_charts(self):
        for widget in self.plan_fact_tab.findChildren(QWidget):
            if hasattr(widget, 'figure'):
                self._patch_chart_widget(widget)

    def _patch_chart_widget(self, widget):
        if not widget or not hasattr(widget, 'figure'):
            return
        try:
            fig = widget.figure
            is_dark = self.current_theme == "dark"
            bg_color = '#111827' if is_dark else '#FFFFFF'
            text_color = '#E5E7EB' if is_dark else '#1E293B'
            grid_color = '#334155' if is_dark else '#E2E8F0'
            tick_color = '#94A3B8' if is_dark else '#475569'

            fig.patch.set_facecolor(bg_color)
            for ax in fig.axes:
                ax.set_facecolor(bg_color)
                ax.title.set_color(text_color)
                ax.xaxis.label.set_color(text_color)
                ax.yaxis.label.set_color(text_color)
                for spine in ax.spines.values():
                    spine.set_color(grid_color)
                ax.tick_params(colors=tick_color)
                for text in ax.texts:
                    text.set_color(text_color)
                legend = ax.get_legend()
                if legend:
                    legend.get_frame().set_facecolor('#182235' if is_dark else '#FFFFFF')
                    legend.get_frame().set_edgecolor(grid_color)
                    for text in legend.get_texts():
                        text.set_color(text_color)
            widget.draw()
        except Exception as e:
            print(f"Ошибка кастомизации графика: {e}")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ЗАГОЛОВОК
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        title = QLabel("Управление бюджетом")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px;")
        subtitle = QLabel("Планирование лимитов и анализ исполнения")
        subtitle.setStyleSheet("color: #64748B; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # КАРТОЧКА ФИЛЬТРОВ
        filter_card = QFrame()
        filter_card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(16)

        filter_layout.addWidget(QLabel("🗓️ Период:", styleSheet="font-weight: bold; color: #475569;"))

        combo_style = "QComboBox { padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px; background: #F8FAFC; }"
        self.period_type_combo = QComboBox()
        self.period_type_combo.addItems(["Месяц", "Квартал", "Год", "Произвольный"])
        self.period_type_combo.setStyleSheet(combo_style)
        self.period_type_combo.currentTextChanged.connect(self.on_period_type_changed)
        filter_layout.addWidget(self.period_type_combo)

        self.dynamic_filters = QWidget()
        self.dynamic_layout = QHBoxLayout(self.dynamic_filters)
        self.dynamic_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_layout.setSpacing(8)

        self.month_combo = QComboBox()
        self.month_combo.addItems(
            ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
             "Декабрь"])
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.month_combo.setStyleSheet(combo_style)

        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(y) for y in range(current_year - 3, current_year + 4)])
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.setStyleSheet(combo_style)

        self.dynamic_layout.addWidget(self.month_combo)
        self.dynamic_layout.addWidget(self.year_combo)

        filter_layout.addWidget(self.dynamic_filters)

        self.period_hint_lbl = QLabel("")
        self.period_hint_lbl.setStyleSheet("color: #D97706; font-size: 12px; font-weight: bold;")
        filter_layout.addWidget(self.period_hint_lbl)

        filter_layout.addStretch()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton { background: #4F46E5; color: white; border-radius: 6px; padding: 8px 20px; font-weight: bold; }
            QPushButton:hover { background: #4338CA; }
        """)
        refresh_btn.clicked.connect(self.refresh_all)
        filter_layout.addWidget(refresh_btn)

        main_layout.addWidget(filter_card)

        # TAB WIDGET
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { background: transparent; border: none; }
            QTabBar::tab { background: #F1F5F9; color: #64748B; padding: 10px 24px; margin-right: 4px; border-radius: 8px 8px 0 0; font-weight: bold; }
            QTabBar::tab:selected { background: white; color: #4F46E5; border-bottom: 3px solid #4F46E5; }
        """)

        self.budget_tab = QWidget()
        self.setup_budget_tab()
        self.tab_widget.addTab(self.budget_tab, "📋 Планирование")

        self.plan_fact_tab = PlanFactTab(self.controller, self)
        self.tab_widget.addTab(self.plan_fact_tab, "📊 Исполнение (План/Факт)")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tab_widget)

    def setup_budget_tab(self):
        layout = QVBoxLayout(self.budget_tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        add_btn = QPushButton("➕ Добавить лимит")
        add_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; } QPushButton:hover { background: #059669; }")
        add_btn.clicked.connect(self.show_add_dialog)

        sec_btn_style = """
            QPushButton { background: white; color: #475569; border: 1px solid #CBD5E1; padding: 10px 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #F8FAFC; border-color: #94A3B8; }
        """

        copy_prev_btn = QPushButton("🔄 Из прошлого месяца")
        copy_prev_btn.setStyleSheet(sec_btn_style)
        copy_prev_btn.clicked.connect(self.copy_from_previous)
        copy_prev_btn.setToolTip("Работает только если выбран период 'Месяц'")

        save_tpl_btn = QPushButton("⭐ Сохранить как шаблон")
        save_tpl_btn.setStyleSheet(sec_btn_style)
        save_tpl_btn.clicked.connect(self.save_as_template)

        load_tpl_btn = QPushButton("📥 Шаблоны")
        load_tpl_btn.setStyleSheet(sec_btn_style)
        load_tpl_btn.clicked.connect(self.manage_templates)

        toolbar.addWidget(add_btn)
        toolbar.addWidget(copy_prev_btn)
        toolbar.addWidget(save_tpl_btn)
        toolbar.addWidget(load_tpl_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels(["Категория", "Тип", "Плановая сумма (₽)", "Действия"])
        self.budget_table.setStyleSheet("""
            QTableWidget { 
                background: white; 
                alternate-background-color: #F8FAFC;
                border: 1px solid #E2E8F0; 
                border-radius: 12px; 
                gridline-color: #F1F5F9; 
            }
            QTableWidget::item:selected {
                background-color: #EEF2FF;
                color: #4F46E5;
            }
            QHeaderView::section { 
                background: #F8FAFC; 
                padding: 12px; 
                border: none; 
                border-bottom: 2px solid #E2E8F0; 
                font-weight: bold; 
                color: #475569; 
            }
            QTableWidget::item { padding: 8px; }
        """)
        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.verticalHeader().setVisible(False)
        self.budget_table.verticalHeader().setDefaultSectionSize(55)
        self.budget_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.budget_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.budget_table.setColumnWidth(3, 100)

        layout.addWidget(self.budget_table)

    def _transfer_budgets(self, source_start, source_end, target_start, target_end):
        try:
            source_budgets = self.controller.execute("""
                SELECT category_id, SUM(planned_amount) 
                FROM budgets 
                WHERE period_start >= %s AND period_end <= %s
                GROUP BY category_id
            """, (source_start, source_end), fetch=True)

            if not source_budgets:
                QMessageBox.information(self, "Инфо", "Нет данных для переноса.")
                return

            target_existing = self.controller.execute("""
                SELECT category_id FROM budgets 
                WHERE period_start >= %s AND period_end <= %s
            """, (target_start, target_end), fetch=True)
            existing_ids = {row[0] for row in target_existing}

            added_count = 0
            for cat_id, amount in source_budgets:
                if cat_id not in existing_ids:
                    self.controller.execute(
                        "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                        (cat_id, target_start, target_end, amount)
                    )
                    added_count += 1

            if added_count > 0:
                self.refresh_all()
                QMessageBox.information(self, "Успех", f"Успешно перенесено лимитов: {added_count}.")
            else:
                QMessageBox.information(self, "Инфо", "В текущем периоде уже установлены лимиты (дубликаты пропущены).")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при переносе: {e}")

    def copy_from_previous(self):
        if self.period_type_combo.currentText() != "Месяц":
            QMessageBox.warning(self, "Внимание", "Авто-перенос работает только когда в фильтре выбран 'Месяц'.")
            return
        dates = self.get_period_dates()
        current_start = QDate.fromString(dates['start'], "yyyy-MM-dd")
        prev_start_date = current_start.addMonths(-1)
        prev_year = prev_start_date.year()
        prev_month = prev_start_date.month()
        last_day = calendar.monthrange(prev_year, prev_month)[1]

        self._transfer_budgets(f"{prev_year}-{prev_month:02d}-01", f"{prev_year}-{prev_month:02d}-{last_day}",
                               dates['start'], dates['end'])

    def save_as_template(self):
        if self.budget_table.rowCount() == 0:
            QMessageBox.warning(self, "Внимание", "Добавьте лимиты в таблицу, чтобы сохранить их как шаблон.")
            return

        dialog = TemplateSaveDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name = dialog.template_name
        self.block_refresh = True
        try:
            dates = self.get_period_dates()
            current = self.controller.execute("""
                SELECT category_id, SUM(planned_amount) 
                FROM budgets 
                WHERE period_start >= %s AND period_end <= %s
                GROUP BY category_id
            """, (dates['start'], dates['end']), fetch=True)

            existing = self.controller.execute("SELECT id FROM budget_templates WHERE name = %s", (name,), fetch=True)

            if existing:
                reply = QMessageBox.question(self, "Замена", f"Шаблон '{name}' уже существует.\nПерезаписать его?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return
                tid = existing[0][0]
                self.controller.execute("DELETE FROM budget_template_items WHERE template_id = %s", (tid,))
            else:
                self.controller.execute("INSERT INTO budget_templates (name) VALUES (%s)", (name,))
                res = self.controller.execute("SELECT id FROM budget_templates WHERE name = %s", (name,), fetch=True)
                tid = res[0][0]

            for cat_id, amount in current:
                self.controller.execute(
                    "INSERT INTO budget_template_items (template_id, category_id, amount) VALUES (%s, %s, %s)",
                    (tid, cat_id, amount)
                )
            QMessageBox.information(self, "Успех", f"Шаблон '{name}' успешно сохранен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")
        finally:
            self.block_refresh = False

    def manage_templates(self):
        self.block_refresh = True
        try:
            templates = self.controller.execute("SELECT id, name FROM budget_templates ORDER BY name", fetch=True)
            if not templates:
                QMessageBox.information(self, "Инфо",
                                        "У вас пока нет сохраненных шаблонов.\n\nНастройте лимиты и нажмите 'Сохранить как шаблон'.")
                return

            dialog = TemplateManagerDialog(templates, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                tid = dialog.selected_template_id
                tname = dialog.selected_template_name

                if dialog.action == 'delete':
                    confirm = QMessageBox.question(self, "Подтверждение", f"Точно удалить шаблон '{tname}'?",
                                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if confirm == QMessageBox.StandardButton.Yes:
                        self.controller.execute("DELETE FROM budget_templates WHERE id = %s", (tid,))
                        QMessageBox.information(self, "Успех", "Шаблон успешно удален.")

                elif dialog.action == 'load':
                    items = self.controller.execute(
                        "SELECT category_id, amount FROM budget_template_items WHERE template_id = %s", (tid,),
                        fetch=True)
                    if not items:
                        QMessageBox.warning(self, "Пусто", "Этот шаблон пуст.")
                        return

                    dates = self.get_period_dates()
                    target_start = dates['start']
                    target_end = dates['end']

                    target_existing = self.controller.execute("""
                        SELECT category_id FROM budgets 
                        WHERE period_start >= %s AND period_end <= %s
                    """, (target_start, target_end), fetch=True)
                    existing_ids = {row[0] for row in target_existing}

                    added_count = 0
                    for cat_id, amount in items:
                        if cat_id not in existing_ids:
                            self.controller.execute(
                                "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                                (cat_id, target_start, target_end, amount)
                            )
                            added_count += 1

                    if added_count > 0:
                        QMessageBox.information(self, "Успех",
                                                f"Из шаблона '{tname}' успешно загружено лимитов: {added_count}.")
                    else:
                        QMessageBox.information(self, "Инфо",
                                                "Все категории из этого шаблона уже существуют в текущем периоде (дубликаты пропущены).")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            self.block_refresh = False
            self.refresh_all()

    def on_period_type_changed(self):
        for i in reversed(range(self.dynamic_layout.count())):
            self.dynamic_layout.itemAt(i).widget().setParent(None)

        period_type = self.period_type_combo.currentText()
        combo_style = "QComboBox { padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px; background: #F8FAFC; }"

        if period_type == "Месяц":
            self.month_combo = QComboBox()
            self.month_combo.addItems(
                ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
                 "Ноябрь", "Декабрь"])
            self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
            self.month_combo.setStyleSheet(combo_style)
            self.dynamic_layout.addWidget(self.month_combo)
            self.dynamic_layout.addWidget(self.year_combo)
            self.period_hint_lbl.setText("")

        elif period_type == "Квартал":
            self.quarter_combo = QComboBox()
            self.quarter_combo.addItems(["1-й квартал", "2-й квартал", "3-й квартал", "4-й квартал"])
            self.quarter_combo.setStyleSheet(combo_style)
            self.dynamic_layout.addWidget(self.quarter_combo)
            self.dynamic_layout.addWidget(self.year_combo)
            self.period_hint_lbl.setText("💡 Показана сумма всех лимитов внутри квартала")

        elif period_type == "Год":
            self.dynamic_layout.addWidget(self.year_combo)
            self.period_hint_lbl.setText("💡 Показана сумма всех лимитов внутри года")

        else:
            self.start_date = QDateEdit()
            self.end_date = QDateEdit()
            for de in [self.start_date, self.end_date]:
                de.setCalendarPopup(True)
                de.setDate(QDate.currentDate())
                de.setStyleSheet(combo_style.replace("QComboBox", "QDateEdit"))
            self.dynamic_layout.addWidget(QLabel("С:"))
            self.dynamic_layout.addWidget(self.start_date)
            self.dynamic_layout.addWidget(QLabel("По:"))
            self.dynamic_layout.addWidget(self.end_date)
            self.period_hint_lbl.setText("")

    def get_period_dates(self):
        period_type = self.period_type_combo.currentText()
        if period_type == "Месяц":
            year = int(self.year_combo.currentText())
            month = self.month_combo.currentIndex() + 1
            last_day = calendar.monthrange(year, month)[1]
            return {'start': f"{year}-{month:02d}-01", 'end': f"{year}-{month:02d}-{last_day}",
                    'display': f"{self.month_combo.currentText()} {year}"}
        elif period_type == "Квартал":
            year = int(self.year_combo.currentText())
            q = self.quarter_combo.currentIndex() + 1
            starts = [f"{year}-01-01", f"{year}-04-01", f"{year}-07-01", f"{year}-10-01"]
            ends = [f"{year}-03-31", f"{year}-06-30", f"{year}-09-30", f"{year}-12-31"]
            return {'start': starts[q - 1], 'end': ends[q - 1], 'display': f"{q}-й квартал {year}"}
        elif period_type == "Год":
            year = int(self.year_combo.currentText())
            return {'start': f"{year}-01-01", 'end': f"{year}-12-31", 'display': f"{year} год"}
        else:
            s, e = self.start_date.date(), self.end_date.date()
            return {'start': s.toString("yyyy-MM-dd"), 'end': e.toString("yyyy-MM-dd"),
                    'display': f"{s.toString('dd.MM.yyyy')} - {e.toString('dd.MM.yyyy')}"}

    def load_categories(self):
        try:
            rows = self.controller.execute("SELECT id, name, type FROM categories", fetch=True)
            self.categories = [
                {'id': r[0], 'name': r[1], 'type': 'Доход' if r[2] == 'income' else 'Расход', 'type_en': r[2]} for r in
                rows]
        except Exception as e:
            print(f"Ошибка загрузки категорий: {e}")

    def load_budgets(self):
        try:
            dates = self.get_period_dates()
            rows = self.controller.execute("""
                SELECT 
                    MIN(b.id), c.id, c.name, c.type, SUM(b.planned_amount), COUNT(b.id)
                FROM budgets b JOIN categories c ON c.id = b.category_id
                WHERE b.period_start >= %s AND b.period_end <= %s 
                GROUP BY c.id, c.name, c.type
                ORDER BY c.type DESC, c.name
            """, (dates['start'], dates['end']), fetch=True)

            self.budget_table.setRowCount(len(rows))
            self.budget_ids = []
            self.budget_counts = []
            self.budget_cat_ids = []

            is_dark = self.current_theme == "dark"

            edit_bg = "#334155" if is_dark else "#F1F5F9"
            edit_hover = "#475569" if is_dark else "#E2E8F0"

            del_bg = "#7F1D1D" if is_dark else "#FEE2E2"
            del_color = "#FCA5A5" if is_dark else "#EF4444"
            del_hover = "#991B1B" if is_dark else "#FECACA"

            for i, (bid, cat_id, cat_name, cat_type, plan, count) in enumerate(rows):
                self.budget_ids.append(bid)
                self.budget_counts.append(count)
                self.budget_cat_ids.append(cat_id)

                plan_val = float(plan) if plan else 0

                self.budget_table.setItem(i, 0, QTableWidgetItem(f"{'💰' if cat_type == 'income' else '💸'} {cat_name}"))
                type_item = QTableWidgetItem("Доход" if cat_type == 'income' else "Расход")
                type_item.setForeground(QColor("#10B981" if cat_type == 'income' else "#EF4444"))
                self.budget_table.setItem(i, 1, type_item)

                plan_item = QTableWidgetItem(f"{plan_val:,.2f} ₽")
                font = plan_item.font()
                font.setBold(True)
                plan_item.setFont(font)
                self.budget_table.setItem(i, 2, plan_item)

                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(8)
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)

                if count > 1:
                    edit_btn.setDisabled(True)
                    edit_btn.setToolTip("Составной бюджет. Для редактирования переключитесь на период 'Месяц'.")
                    edit_btn.setStyleSheet(
                        f"QPushButton {{ background: {edit_bg}; border-radius: 6px; color: transparent; }}")
                else:
                    edit_btn.setStyleSheet(
                        f"QPushButton {{ background: {edit_bg}; border-radius: 6px; }} QPushButton:hover {{ background: {edit_hover}; }}")
                    edit_btn.clicked.connect(lambda checked, r=i: self.edit_budget(r))

                delete_btn = QPushButton("🗑")
                delete_btn.setFixedSize(30, 30)
                delete_btn.setStyleSheet(
                    f"QPushButton {{ background: {del_bg}; color: {del_color}; border-radius: 6px; }} QPushButton:hover {{ background: {del_hover}; }}")
                delete_btn.clicked.connect(lambda checked, r=i: self.delete_budget(r))

                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                self.budget_table.setCellWidget(i, 3, btn_widget)

        except Exception as e:
            print(f"Ошибка загрузки бюджетов: {e}")

    def show_add_dialog(self):
        self.block_refresh = True
        try:
            period_type = self.period_type_combo.currentText()
            dialog = BudgetAddDialog(self.categories, self.get_period_dates(), period_type, self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                dates = self.get_period_dates()

                if dialog.allocation_method == 'divide':
                    year = int(self.year_combo.currentText())
                    if period_type == "Год":
                        months = list(range(1, 13))
                    elif period_type == "Квартал":
                        q = self.quarter_combo.currentIndex() + 1
                        start_m = (q - 1) * 3 + 1
                        months = [start_m, start_m + 1, start_m + 2]

                    div_amount = dialog.amount / len(months)
                    added = 0
                    for m in months:
                        last_day = calendar.monthrange(year, m)[1]
                        m_start = f"{year}-{m:02d}-01"
                        m_end = f"{year}-{m:02d}-{last_day}"

                        existing = self.controller.execute(
                            "SELECT id FROM budgets WHERE category_id = %s AND period_start = %s AND period_end = %s",
                            (dialog.category_id, m_start, m_end), fetch=True)
                        if not existing:
                            self.controller.execute(
                                "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                                (dialog.category_id, m_start, m_end, div_amount))
                            added += 1

                    QMessageBox.information(self, "Успех", f"Сумма разбита на {added} мес. (по {div_amount:,.2f} ₽)")
                else:
                    existing = self.controller.execute(
                        "SELECT id FROM budgets WHERE category_id = %s AND period_start = %s AND period_end = %s",
                        (dialog.category_id, dates['start'], dates['end']), fetch=True)
                    if existing:
                        QMessageBox.warning(self, "Ошибка",
                                            "Бюджет для этой категории на выбранный период уже существует")
                        return
                    self.controller.execute(
                        "INSERT INTO budgets (category_id, period_start, period_end, planned_amount) VALUES (%s, %s, %s, %s)",
                        (dialog.category_id, dates['start'], dates['end'], dialog.amount))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            self.block_refresh = False
            self.refresh_all()

    def edit_budget(self, row):
        self.block_refresh = True
        try:
            bid = self.budget_ids[row]
            category_name = self.budget_table.item(row, 0).text()

            amount_str = self.budget_table.item(row, 2).text()
            clean_amount = amount_str.replace(" ₽", "").replace(" ", "").replace("\xa0", "").replace(",", "")
            current_amount = float(clean_amount)

            dialog = BudgetEditDialog(category_name, current_amount, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.controller.execute("UPDATE budgets SET planned_amount=%s WHERE id=%s", (dialog.amount, bid))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Сбой при редактировании: {e}")
        finally:
            self.block_refresh = False
            self.refresh_all()

    def delete_budget(self, row):
        self.block_refresh = True
        try:
            category = self.budget_table.item(row, 0).text()
            count = self.budget_counts[row]
            cat_id = self.budget_cat_ids[row]

            msg = f"Удалить лимит '{category}'?"
            if count > 1:
                msg = f"Внимание! Внутри этого периода есть {count} отдельных записей для '{category}'.\nУдалить их все?"

            if QMessageBox.question(self, "Удаление", msg) == QMessageBox.StandardButton.Yes:
                dates = self.get_period_dates()
                self.controller.execute("""
                    DELETE FROM budgets 
                    WHERE category_id = %s AND period_start >= %s AND period_end <= %s
                """, (cat_id, dates['start'], dates['end']))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
        finally:
            self.block_refresh = False
            self.refresh_all()

    def refresh_all(self):
        if self.block_refresh:
            return

        selected_rows = [item.row() for item in self.budget_table.selectedItems()]
        v_scroll = self.budget_table.verticalScrollBar().value()
        h_scroll = self.budget_table.horizontalScrollBar().value()

        pf_table = self.plan_fact_tab.plan_fact_table
        pf_selected_rows = [item.row() for item in pf_table.selectedItems()]
        pf_v_scroll = pf_table.verticalScrollBar().value()
        pf_h_scroll = pf_table.horizontalScrollBar().value()

        self.sync_matplotlib_theme()
        self.load_categories()
        self.load_budgets()
        self.plan_fact_tab.load_data(self.get_period_dates())

        self.budget_table.clearSelection()
        for row in selected_rows:
            if row < self.budget_table.rowCount():
                self.budget_table.selectRow(row)
        self.budget_table.verticalScrollBar().setValue(v_scroll)
        self.budget_table.horizontalScrollBar().setValue(h_scroll)

        pf_table.clearSelection()
        for row in pf_selected_rows:
            if row < pf_table.rowCount():
                pf_table.selectRow(row)
        pf_table.verticalScrollBar().setValue(pf_v_scroll)
        pf_table.horizontalScrollBar().setValue(pf_h_scroll)

        QTimer.singleShot(100, self.patch_all_charts)

    def on_tab_changed(self, index):
        if index == 1:
            self.plan_fact_tab.load_data(self.get_period_dates())
            self.sync_matplotlib_theme()