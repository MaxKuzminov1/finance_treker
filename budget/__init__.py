from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QDateEdit, QMessageBox,
    QFrame
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor

def init_ui(self):
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(25, 25, 25, 25)
    main_layout.setSpacing(15)

    # =========================
    # 🟢 HEADER CARD
    # =========================
    header = QFrame()
    header.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2ecc71, stop:1 #27ae60);
            border-radius: 15px;
            padding: 15px;
        }
    """)

    header_layout = QVBoxLayout()

    title = QLabel("📊 Модуль 2. Управление бюджетом")
    title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")

    subtitle = QLabel("Планирование бюджета и контроль отклонений")
    subtitle.setStyleSheet("color: #ecf0f1; font-size: 13px;")

    header_layout.addWidget(title)
    header_layout.addWidget(subtitle)
    header.setLayout(header_layout)

    main_layout.addWidget(header)

    # =========================
    # 🔵 TOP PANEL
    # =========================
    top_panel = QFrame()
    top_panel.setStyleSheet("""
        QFrame {
            background: white;
            border-radius: 12px;
            padding: 10px;
        }
    """)

    top_layout = QHBoxLayout()

    self.period_edit = QDateEdit()
    self.period_edit.setDate(QDate.currentDate())
    self.period_edit.setDisplayFormat("MMMM yyyy")
    self.period_edit.setCalendarPopup(True)
    self.period_edit.setStyleSheet("padding: 6px;")

    refresh_btn = QPushButton("🔄 Обновить")
    refresh_btn.setStyleSheet("""
        QPushButton {
            background-color: #27ae60;
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #2ecc71;
        }
    """)
    refresh_btn.clicked.connect(self.load_data)

    top_layout.addWidget(QLabel("Период:"))
    top_layout.addWidget(self.period_edit)
    top_layout.addWidget(refresh_btn)
    top_layout.addStretch()

    top_panel.setLayout(top_layout)
    main_layout.addWidget(top_panel)

    # =========================
    # 🟡 MAIN CONTENT
    # =========================
    content_layout = QHBoxLayout()

    # =========================
    # 📋 TABLE CARD
    # =========================
    table_card = QFrame()
    table_card.setStyleSheet("""
        QFrame {
            background: white;
            border-radius: 12px;
            padding: 10px;
        }
    """)

    table_layout = QVBoxLayout()

    table_title = QLabel("Таблица бюджетов")
    table_title.setStyleSheet("font-weight: bold; font-size: 14px;")
    table_layout.addWidget(table_title)

    self.table = QTableWidget()
    self.table.setColumnCount(5)
    self.table.setHorizontalHeaderLabels([
        "Категория", "План", "Факт", "Отклонение", "Статус"
    ])

    self.table.setStyleSheet("""
        QTableWidget {
            background: #fdfdfd;
            border: none;
        }
        QHeaderView::section {
            background: #ecf0f1;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
    """)

    self.table.horizontalHeader().setStretchLastSection(True)

    table_layout.addWidget(self.table)
    table_card.setLayout(table_layout)

    content_layout.addWidget(table_card, 3)

    # =========================
    # 🔷 RIGHT PANEL
    # =========================
    right_panel = QVBoxLayout()

    # 📊 Chart card
    chart_card = QFrame()
    chart_card.setStyleSheet("""
        QFrame {
            background: white;
            border-radius: 12px;
            padding: 10px;
        }
    """)

    chart_layout = QVBoxLayout()

    chart_title = QLabel("План vs Факт")
    chart_title.setStyleSheet("font-weight: bold;")
    chart_layout.addWidget(chart_title)
    self.figure = Figure(figsize=(4, 3))
    self.canvas = FigureCanvas(self.figure)
    chart_layout.addWidget(self.canvas)
    self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.chart_label.setStyleSheet("color:#7f8c8d; padding:20px;")

    chart_layout.addWidget(self.chart_label)
    chart_card.setLayout(chart_layout)

    right_panel.addWidget(chart_card)

    # ➕ Add budget card
    form_card = QFrame()
    form_card.setStyleSheet("""
        QFrame {
            background: white;
            border-radius: 12px;
            padding: 10px;
        }
    """)

    form_layout = QVBoxLayout()

    form_title = QLabel("Быстрое добавление")
    form_title.setStyleSheet("font-weight: bold;")
    form_layout.addWidget(form_title)

    self.category_box = QComboBox()
    self.category_box.setStyleSheet("padding:5px;")
    form_layout.addWidget(self.category_box)

    self.amount_input = QLineEdit()
    self.amount_input.setPlaceholderText("Сумма")
    self.amount_input.setStyleSheet("padding:5px;")
    form_layout.addWidget(self.amount_input)

    add_btn = QPushButton("➕ Сохранить")
    add_btn.setStyleSheet("""
        QPushButton {
            background-color: #27ae60;
            color: white;
            padding: 8px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #2ecc71;
        }
    """)
    add_btn.clicked.connect(self.add_budget)

    form_layout.addWidget(add_btn)

    form_card.setLayout(form_layout)
    right_panel.addWidget(form_card)

    right_panel.addStretch()

    content_layout.addLayout(right_panel, 1)

    main_layout.addLayout(content_layout)

    self.setLayout(main_layout)
    self.setStyleSheet("""
    QWidget {
        background-color: #f4f6f9;
        font-family: Arial;
    }

    QTableWidget {
        background: white;
        border-radius: 10px;
        gridline-color: #ecf0f1;
    }

    QHeaderView::section {
        background-color: #2ecc71;
        color: white;
        padding: 5px;
        border: none;
    }

    QPushButton {
        background-color: #2ecc71;
        color: white;
        border-radius: 6px;
        padding: 5px;
    }

    QPushButton:hover {
        background-color: #27ae60;
    }

    QLineEdit, QComboBox, QDateEdit {
        padding: 5px;
        border: 1px solid #dcdde1;
        border-radius: 6px;
        background: white;
    }
    """)