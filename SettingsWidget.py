# SettingsWidget.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QMessageBox, QScrollArea, QApplication, QGridLayout
)
from PyQt6.QtCore import Qt


class SettingsWidget(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background-color: #F8FAFC;")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        self.scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.scroll)

        # 1. ЗАГОЛОВОК
        header = QVBoxLayout()
        header.addWidget(
            QLabel("⚙️ Глобальные Настройки", styleSheet="font-size: 24px; font-weight: bold; color: #1E293B;"))
        header.addWidget(
            QLabel("Управление конфигурацией всего приложения", styleSheet="color: #64748B; font-size: 13px;"))
        main_layout.addLayout(header)

        # ГРИД ДЛЯ КАРТОЧЕК
        grid = QGridLayout()
        grid.setSpacing(20)

        # --- КАРТОЧКА: ВНЕШНИЙ ВИД ---
        ui_card = self._create_card("Внешний вид и локализация")
        ui_layout = QVBoxLayout(ui_card)

        ui_layout.addWidget(QLabel("Цветовая тема:", styleSheet="font-weight: bold; color: #334155;"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая (По умолчанию)", "Темная (Ночной режим)"])
        self.theme_combo.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")
        ui_layout.addWidget(self.theme_combo)

        ui_layout.addWidget(
            QLabel("Основная валюта:", styleSheet="font-weight: bold; color: #334155; margin-top: 10px;"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["₽ Российский рубль", "$ Доллар США", "€ Евро"])
        self.currency_combo.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")
        ui_layout.addWidget(self.currency_combo)
        ui_layout.addStretch()

        btn_save_ui = QPushButton("💾 Применить настройки")
        btn_save_ui.setStyleSheet(
            "background: #4F46E5; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        btn_save_ui.clicked.connect(self.apply_ui_settings)
        ui_layout.addWidget(btn_save_ui)
        grid.addWidget(ui_card, 0, 0)

        # --- КАРТОЧКА: УПРАВЛЕНИЕ ДАННЫМИ ---
        db_card = self._create_card("Резервное копирование БД")
        db_layout = QVBoxLayout(db_card)
        db_layout.addWidget(QLabel("Создавайте резервные копии, чтобы избежать потери финансовых записей.",
                                   styleSheet="color: #64748B; margin-bottom: 15px;", wordWrap=True))

        btn_backup = QPushButton("📥 Экспорт базы данных (.sql)")
        btn_backup.setStyleSheet(
            "background: #10B981; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        btn_backup.clicked.connect(
            lambda: QMessageBox.information(self, "Экспорт", "Функция сохранения БД успешно запущена."))

        btn_restore = QPushButton("📤 Импорт базы данных")
        btn_restore.setStyleSheet(
            "background: #F59E0B; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")

        db_layout.addWidget(btn_backup)
        db_layout.addWidget(btn_restore)
        db_layout.addStretch()
        grid.addWidget(db_card, 0, 1)

        # --- КАРТОЧКА: ОПАСНАЯ ЗОНА ---
        danger_card = self._create_card("Опасная зона", border_color="#EF4444")
        danger_layout = QVBoxLayout(danger_card)
        danger_layout.addWidget(
            QLabel("Эти действия необратимы. Будьте осторожны.", styleSheet="color: #EF4444; margin-bottom: 10px;",
                   wordWrap=True))

        btn_clear = QPushButton("🚨 Удалить все транзакции")
        btn_clear.setStyleSheet(
            "background: white; color: #EF4444; border: 2px solid #EF4444; padding: 10px; border-radius: 6px; font-weight: bold;")
        btn_clear.clicked.connect(self.clear_data_warning)

        danger_layout.addWidget(btn_clear)
        danger_layout.addStretch()
        grid.addWidget(danger_card, 1, 0, 1, 2)

        main_layout.addLayout(grid)
        main_layout.addStretch()

    def _create_card(self, title, border_color="#E2E8F0"):
        card = QFrame()
        card.setStyleSheet(f"background: white; border-radius: 12px; border: 1px solid {border_color};")
        layout = QVBoxLayout(card)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #1E293B; border: none; margin-bottom: 10px;")
        layout.addWidget(title_lbl)
        return card

    def apply_ui_settings(self):
        theme = self.theme_combo.currentIndex()
        app = QApplication.instance()
        if theme == 1:  # Темная тема
            app.setStyleSheet("""
                QWidget { background-color: #121212; color: #E0E0E0; }
                QFrame { background-color: #1E1E1E; border: 1px solid #333333; }
                QLabel { color: #E0E0E0; border: none; }
                QPushButton { background: #333333; color: white; border: 1px solid #555555; }
                QLineEdit, QComboBox, QTreeWidget, QTableWidget { background: #2A2A2A; color: white; border: 1px solid #444444; }
                QHeaderView::section { background-color: #1E1E1E; color: white; }
            """)
        else:  # Светлая тема (сброс к дефолту окна)
            app.setStyleSheet("")
            # Либо вызов вашей функции apply_styles() из View

        QMessageBox.information(self, "Успех",
                                f"Настройки применены.\n\nТема: {self.theme_combo.currentText()}\nВалюта: {self.currency_combo.currentText()}")

    def clear_data_warning(self):
        reply = QMessageBox.critical(self, "Критическое предупреждение",
                                     "Вы уверены, что хотите безвозвратно удалить ВСЕ транзакции?\nЭто действие нельзя отменить!",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Очистка", "Данные успешно очищены (имитация).")