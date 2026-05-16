# main_view.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor, QFont
from references.Module1Widget import Module1Widget
from transactions.Module4Widget import Module4Widget
from budget.Module2Widget import Module2Widget
from analytics.Module3Widget import Module3Widget


class ModuleButton(QPushButton):
    """Карточка модуля с кастомным Layout для заголовка, подзаголовка и анимацией тени."""

    def __init__(self, icon: str, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(72)

        # Внутренний Layout кнопки
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Иконка
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 18))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Контейнер для текстов
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        text_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setFont(QFont("Segoe UI", 10))
        text_layout.addWidget(self.subtitle_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Эффект тени
        self._shadow_radius = 8
        self._shadow_effect = QGraphicsDropShadowEffect()
        self._shadow_effect.setBlurRadius(self._shadow_radius)
        self._shadow_effect.setColor(QColor(0, 0, 0, 15))
        self._shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow_effect)

        # Привязка переключения состояния к обновлению стилей
        self.toggled.connect(self.update_style)
        self.update_style(False)

    def update_style(self, checked=None):
        """Обновление цветов элементов внутри Layout при выделении."""
        if checked is None:
            checked = self.isChecked()

        if checked:
            self.setStyleSheet("""
                ModuleButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6C5CE7, stop:1 #4F46E5);
                    border-radius: 14px;
                    border: none;
                }
            """)
            self.title_label.setStyleSheet("color: #FFFFFF;")
            self.subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.75);")
        else:
            self.setStyleSheet("""
                ModuleButton {
                    background: #FFFFFF;
                    border-radius: 14px;
                    border: 1px solid #E2E8F0;
                }
                ModuleButton:hover {
                    background: #F8FAFC;
                    border: 1px solid #CBD5E1;
                }
            """)
            self.title_label.setStyleSheet("color: #1E293B;")
            self.subtitle_label.setStyleSheet("color: #64748B;")

    def enterEvent(self, event):
        if not self.isChecked():
            self.animate_shadow(16)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_shadow(8)
        super().leaveEvent(event)

    def animate_shadow(self, target_radius: int):
        """Плавная анимация размытия тени."""
        self.anim = QPropertyAnimation(self._shadow_effect, b"blurRadius")
        self.anim.setDuration(250)
        self.anim.setStartValue(self._shadow_effect.blurRadius())
        self.anim.setEndValue(target_radius)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()


class View(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Программа комплексного учёта доходов и расходов малого бизнеса")
        self.resize(1400, 850)
        self.setMinimumSize(1200, 700)
        self.setObjectName("main_window")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ========================= SIDEBAR =========================
        sidebar = QFrame()
        sidebar.setFixedWidth(280)  # Слегка расширил для комфортного размещения подзаголовков
        sidebar.setObjectName("sidebar")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(2, 0)
        sidebar.setGraphicsEffect(shadow)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)

        # Логотип
        logo = QLabel("💰 FINANCE PRO")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #F1F5F9; max-height: 1px;")
        sidebar_layout.addWidget(line)

        # Модули
        modules_scroll = QScrollArea()
        modules_scroll.setWidgetResizable(True)
        modules_scroll.setFrameShape(QFrame.Shape.NoFrame)
        modules_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #F8FAFC;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        modules_widget = QWidget()
        modules_widget.setObjectName("modules_container")
        modules_layout = QVBoxLayout()
        modules_layout.setSpacing(12)
        modules_layout.setContentsMargins(0, 0, 4, 0)  # Небольшой отступ справа для скролла

        self.module_buttons = []
        self.btn_group = QButtonGroup()
        self.btn_group.setExclusive(True)

        modules_data = [
            ("📊", "Учёт операций", "Доходы / расходы"),
            ("💰", "Управление бюджетом", "Планирование"),
            ("📈", "Аналитика", "KPI и графики"),
            ("📚", "Справочники", "Категории, контрагенты"),
        ]

        for icon, title, subtitle in modules_data:
            btn = ModuleButton(icon, title, subtitle)
            modules_layout.addWidget(btn)
            self.module_buttons.append(btn)
            self.btn_group.addButton(btn)

        modules_layout.addStretch()  # Прижимаем кнопки кверху
        modules_widget.setLayout(modules_layout)
        modules_scroll.setWidget(modules_widget)
        sidebar_layout.addWidget(modules_scroll)

        # Блок "О программе"
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        info_title = QLabel("ℹ️ О программе")
        info_title.setStyleSheet("color: #4F46E5; font-weight: 700; font-size: 13px;")
        info_layout.addWidget(info_title)

        for text in ["• Локальная база данных", "• Работа без интернета", "• Автосохранение"]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #64748B; font-size: 12px;")
            info_layout.addWidget(lbl)

        info_frame.setLayout(info_layout)
        info_frame.setStyleSheet("""
            #info_frame {
                background-color: #F8FAFC;
                border-radius: 14px;
                padding: 16px;
                border: 1px solid #E2E8F0;
            }
        """)
        sidebar_layout.addWidget(info_frame)
        sidebar.setLayout(sidebar_layout)

        # ========================= STACKED WIDGET =========================
        self.stacked_widget = QStackedWidget()

        self.module1 = Module1Widget(controller)  # Учет операций (индекс 0)
        self.module2 = Module2Widget(controller)  # Управление бюджетом (индекс 1)
        self.module3 = Module3Widget(controller)  # Аналитика (индекс 2)
        self.module4 = Module4Widget(controller)  # Справочники (индекс 3)

        self.stacked_widget.addWidget(self.module1)
        self.stacked_widget.addWidget(self.module2)
        self.stacked_widget.addWidget(self.module3)
        self.stacked_widget.addWidget(self.module4)

        # Синхронизация выбора модуля с кнопками
        self.btn_group.buttonClicked.connect(self.on_module_selected)

        # Подключаем Drill-down сигнал из Модуля 3
        self.module3.drill_down_requested.connect(self.navigate_to_operations_and_filter)

        # Инициализация первого модуля
        self.module_buttons[0].setChecked(True)
        self.module_buttons[0].update_style(True)
        self.stacked_widget.setCurrentIndex(0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget, 1)
        self.setLayout(main_layout)
        self.apply_styles()

    def on_module_selected(self, btn):
        idx = self.module_buttons.index(btn)
        self.stacked_widget.setCurrentIndex(idx)

    def navigate_to_operations_and_filter(self, category_name: str):
        """
        Метод ловит сигнал из аналитики, откладывает переключение вкладки на 50 мс
        (чтобы Matplotlib успел завершить клик без падения), и переключает окно.
        """
        # 1. Визуально выделяем кнопку "Учёт операций" в боковом меню
        self.module_buttons[0].setChecked(True)

        # 2. Оборачиваем логику в функцию, чтобы вызвать ее с задержкой
        def switch_and_filter():
            try:
                # Физически переключаем экраны на Модуль 1
                self.stacked_widget.setCurrentIndex(0)

                # Вызываем метод фильтрации внутри Module1Widget
                if hasattr(self.module1, 'filter_by_category'):
                    self.module1.filter_by_category(category_name)
                else:
                    print(f"[DRILL-DOWN] Внимание: В классе Module1Widget не найден метод filter_by_category.")
            except Exception as e:
                print(f"Ошибка при переключении Drill-down: {e}")

        # 3. Делаем отложенный вызов через 50 миллисекунд (магия против крашей)
        QTimer.singleShot(50, switch_and_filter)

    def apply_styles(self):
        self.setStyleSheet("""
            #main_window {
                background-color: #F3F4F6;
            }
            QWidget {
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 14px;
                color: #1E293B;
            }
            #sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E2E8F0;
            }
            #logo {
                font-size: 20px;
                font-weight: 800;
                color: #4F46E5;
                padding: 10px;
                letter-spacing: 1px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                gridline-color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                padding: 12px;
                font-weight: 700;
                color: #475569;
            }
        """)