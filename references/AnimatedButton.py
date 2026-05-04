from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QDateEdit, QListWidget, QFrame,
    QGraphicsDropShadowEffect, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import QDate, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette
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
