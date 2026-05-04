from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QDateEdit, QListWidget, QFrame,
    QGraphicsDropShadowEffect, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import QDate, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette
from references.form import TransactionForm
from datetime import datetime
from references.Module1Widget import Module1Widget
from transactions.Module4Widget import Module4Widget
from budget.Module2Widget import Module2Widget
from analytics.Module3Widget import Module3Widget
from references.AnimatedButton import AnimatedButton
from transactions.controller import ReferencesController

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