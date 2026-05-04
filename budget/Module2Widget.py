from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QDateEdit, QListWidget, QFrame,
    QGraphicsDropShadowEffect, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import QDate, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette
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