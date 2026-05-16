# main_view.py
import re

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor, QFont
from references.Module1Widget import Module1Widget
from transactions.Module4Widget import Module4Widget
from budget.Module2Widget import Module2Widget
from analytics.Module3Widget import Module3Widget


class ThemeHelper:
    """Централизованная палитра и мягкая перекраска уже существующих inline-style."""

    LIGHT = {
        "window": "#F3F4F6",
        "surface": "#FFFFFF",
        "surface_2": "#F8FAFC",
        "surface_3": "#F1F5F9",
        "border": "#E2E8F0",
        "border_strong": "#CBD5E1",
        "text": "#1E293B",
        "text_strong": "#0F172A",
        "muted": "#64748B",
        "muted_2": "#475569",
        "muted_3": "#94A3B8",
        "accent": "#4F46E5",
        "accent_hover": "#6366F1",
        "accent_dark": "#4338CA",
        "selection": "#EEF2FF",
    }

    DARK = {
        "window": "#0B1120",
        "surface": "#111827",
        "surface_2": "#182235",
        "surface_3": "#1E293B",
        "border": "#334155",
        "border_strong": "#475569",
        "text": "#E5E7EB",
        "text_strong": "#F8FAFC",
        "muted": "#94A3B8",
        "muted_2": "#CBD5E1",
        "muted_3": "#64748B",
        "accent": "#818CF8",
        "accent_hover": "#A5B4FC",
        "accent_dark": "#6366F1",
        "selection": "#312E81",
    }

    COLOR_KEYS = [
        "#F3F4F6", "#FFFFFF", "#ffffff", "#fff", "#F8FAFC", "#F1F5F9", "#EEF2FF",
        "#E2E8F0", "#CBD5E1", "#94A3B8", "#64748B", "#475569",
        "#334155", "#1E293B", "#0F172A", "#4F46E5", "#6366F1", "#4338CA",
    ]

    DARK_REPLACE = {
        "#F3F4F6": DARK["window"],
        "#FFFFFF": DARK["surface"],
        "#ffffff": DARK["surface"],
        "#fff": DARK["surface"],
        "#F8FAFC": DARK["surface_2"],
        "#F1F5F9": DARK["surface_3"],
        "#EEF2FF": DARK["selection"],
        "#E2E8F0": DARK["border"],
        "#CBD5E1": DARK["border_strong"],
        "#94A3B8": DARK["muted_3"],
        "#64748B": DARK["muted"],
        "#475569": DARK["muted_2"],
        "#334155": DARK["muted_2"],
        "#1E293B": DARK["text"],
        "#0F172A": DARK["text_strong"],
        "#4F46E5": DARK["accent"],
        "#6366F1": DARK["accent_hover"],
        "#4338CA": DARK["accent_dark"],
    }

    @classmethod
    def palette(cls, theme: str) -> dict:
        return cls.DARK if theme == "dark" else cls.LIGHT

    @classmethod
    def restyle_inline(cls, style: str, theme: str) -> str:
        if not style or theme == "light":
            return style

        themed = style
        themed = re.sub(
            r"(background(?:-color)?\s*:\s*)(?:white|#(?:[fF]{3}){1,2})\b",
            rf"\g<1>{cls.DARK['surface']}",
            themed,
            flags=re.IGNORECASE,
        )

        for old in cls.COLOR_KEYS:
            new = cls.DARK_REPLACE.get(old, old)
            themed = themed.replace(old, new).replace(old.lower(), new)
        return themed


class ModuleButton(QPushButton):
    def __init__(self, icon: str, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(72)
        self.theme = "light"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 18))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

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

        self._shadow_radius = 8
        self._shadow_effect = QGraphicsDropShadowEffect()
        self._shadow_effect.setBlurRadius(self._shadow_radius)
        self._shadow_effect.setColor(QColor(0, 0, 0, 15))
        self._shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow_effect)

        self.toggled.connect(self.update_style)
        self.update_style(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update_style(self.isChecked())

    def update_style(self, checked=None):
        if checked is None:
            checked = self.isChecked()

        p = ThemeHelper.palette(self.theme)

        if checked:
            self.setStyleSheet(f"""
                ModuleButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6C5CE7, stop:1 {p['accent']});
                    border-radius: 14px;
                    border: none;
                }}
            """)
            self.title_label.setStyleSheet("color: #FFFFFF;")
            self.subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.78);")
        else:
            self.setStyleSheet(f"""
                ModuleButton {{
                    background: {p['surface']};
                    border-radius: 14px;
                    border: 1px solid {p['border']};
                }}
                ModuleButton:hover {{
                    background: {p['surface_2']};
                    border: 1px solid {p['border_strong']};
                }}
            """)
            self.title_label.setStyleSheet(f"color: {p['text']};")
            self.subtitle_label.setStyleSheet(f"color: {p['muted']};")

    def enterEvent(self, event):
        if not self.isChecked():
            self.animate_shadow(16)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_shadow(8)
        super().leaveEvent(event)

    def animate_shadow(self, target_radius: int):
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
        self.current_theme = "light"
        self.setWindowTitle("Программа комплексного учёта доходов и расходов малого бизнеса")
        self.resize(1400, 850)
        self.setMinimumSize(1200, 700)
        self.setObjectName("main_window")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ========================= SIDEBAR =========================
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setObjectName("sidebar")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(2, 0)
        sidebar.setGraphicsEffect(shadow)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)

        logo = QLabel("💰 FINANCE PRO")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #F1F5F9; max-height: 1px;")
        sidebar_layout.addWidget(line)

        self.modules_scroll = QScrollArea()
        self.modules_scroll.setWidgetResizable(True)
        self.modules_scroll.setFrameShape(QFrame.Shape.NoFrame)
        # Убираем внутреннее автозаполнение холста скролл-бара, убирая белый фон
        self.modules_scroll.viewport().setAutoFillBackground(False)

        modules_widget = QWidget()
        modules_widget.setObjectName("modules_container")
        modules_layout = QVBoxLayout()
        modules_layout.setSpacing(12)
        modules_layout.setContentsMargins(0, 0, 4, 0)

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

        modules_layout.addStretch()
        modules_widget.setLayout(modules_layout)
        self.modules_scroll.setWidget(modules_widget)
        sidebar_layout.addWidget(self.modules_scroll)

        self.theme_btn = QPushButton("🌙 Тёмная тема")
        self.theme_btn.setCheckable(True)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_btn)

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

        self.module1 = Module1Widget(controller)
        self.module2 = Module2Widget(controller)
        self.module3 = Module3Widget(controller)
        self.module4 = Module4Widget(controller)

        self.stacked_widget.addWidget(self.module1)
        self.stacked_widget.addWidget(self.module2)
        self.stacked_widget.addWidget(self.module3)
        self.stacked_widget.addWidget(self.module4)

        self.btn_group.buttonClicked.connect(self.on_module_selected)
        self.module3.drill_down_requested.connect(self.navigate_to_operations_and_filter)

        self.module_buttons[0].setChecked(True)
        self.module_buttons[0].update_style(True)
        self.stacked_widget.setCurrentIndex(0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget, 1)
        self.setLayout(main_layout)
        self.apply_theme("light")

    def on_module_selected(self, btn):
        idx = self.module_buttons.index(btn)
        self.stacked_widget.setCurrentIndex(idx)
        self._apply_inline_theme(self.stacked_widget.currentWidget(), self.current_theme)

    def navigate_to_operations_and_filter(self, category_name: str):
        self.module_buttons[0].setChecked(True)

        def switch_and_filter():
            try:
                self.stacked_widget.setCurrentIndex(0)
                if hasattr(self.module1, 'filter_by_category'):
                    self.module1.filter_by_category(category_name)
            except Exception as e:
                print(f"Ошибка при переключении Drill-down: {e}")

        QTimer.singleShot(50, switch_and_filter)

    def toggle_theme(self):
        next_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(next_theme)

    def apply_theme(self, theme: str):
        """Единая точка применения темы ко всему окну."""
        self.current_theme = theme
        self.apply_styles()

        for btn in self.module_buttons:
            btn.set_theme(theme)
        self._update_theme_button_style()

        for module in [self.module1, self.module2, self.module3, self.module4]:
            if hasattr(module, 'apply_theme'):
                module.apply_theme(theme)

        self._apply_inline_theme(self, theme)
        self._install_theme_event_filter()

    def _update_theme_button_style(self):
        p = ThemeHelper.palette(self.current_theme)
        if self.current_theme == "dark":
            self.theme_btn.setText("☀️ Светлая тема")
        else:
            self.theme_btn.setText("🌙 Тёмная тема")

        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background: {p['surface_2']};
                color: {p['text']};
                border: 1px solid {p['border']};
                border-radius: 12px;
                padding: 10px 14px;
                font-weight: 700;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {p['surface_3']};
                border-color: {p['accent']};
            }}
        """)

    def _apply_inline_theme(self, root: QWidget, theme: str):
        skip_widgets = set(self.module_buttons + [self.theme_btn, self])
        widgets_to_process = [root] + root.findChildren(QWidget)

        for widget in widgets_to_process:
            if widget in skip_widgets:
                continue

            base_style = widget.property("_base_stylesheet")
            if base_style is None:
                base_style = widget.styleSheet()
                widget.setProperty("_base_stylesheet", base_style)

            if base_style:
                widget.setStyleSheet(ThemeHelper.restyle_inline(base_style, theme))

    def _install_theme_event_filter(self):
        app = QApplication.instance()
        if app and not app.property("_theme_filter_installed"):
            app.installEventFilter(self)
            app.setProperty("_theme_filter_installed", True)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Show and isinstance(watched, QDialog):
            if getattr(self, "current_theme", "light") == "dark":
                self._apply_inline_theme(watched, "dark")
        return super().eventFilter(watched, event)

    def apply_styles(self):
        p = ThemeHelper.palette(self.current_theme)
        stylesheet = f"""
            #main_window {{
                background-color: {p['window']};
            }}
            QWidget {{
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 14px;
                color: {p['text']};
            }}
            #sidebar {{
                background-color: {p['surface']};
                border-right: 1px solid {p['border']};
            }}
            #logo {{
                font-size: 20px;
                font-weight: 800;
                color: {p['accent']};
                padding: 10px;
                letter-spacing: 1px;
            }}
            QFrame {{ color: {p['text']}; }}
            QLabel {{ color: {p['text']}; }}
            QLineEdit, QComboBox, QDateEdit, QSpinBox {{
                background-color: {p['surface']};
                color: {p['text']};
                border: 1px solid {p['border_strong']};
                border-radius: 8px;
                selection-background-color: {p['accent']};
                selection-color: #FFFFFF;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
                border-color: {p['accent']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {p['surface']};
                color: {p['text']};
                border: 1px solid {p['border']};
                selection-background-color: {p['selection']};
            }}
            QTableWidget, QTreeWidget {{
                background-color: {p['surface']};
                alternate-background-color: {p['surface_2']};
                color: {p['text']};
                border: 1px solid {p['border']};
                border-radius: 12px;
                gridline-color: {p['border']};
            }}
            QTableWidget::item, QTreeWidget::item {{
                color: {p['text']};
                border-bottom: 1px solid {p['border']};
            }}
            QTableWidget::item:selected, QTreeWidget::item:selected {{
                background-color: {p['selection']};
                color: {p['text_strong']};
            }}
            QHeaderView::section {{
                background-color: {p['surface_2']};
                border: none;
                border-bottom: 2px solid {p['border']};
                padding: 12px;
                font-weight: 700;
                color: {p['muted_2']};
            }}
            QTabWidget::pane {{
                background: transparent;
                border: none;
            }}
            QTabBar::tab {{
                background: {p['surface_3']};
                color: {p['muted']};
                padding: 10px 24px;
                margin-right: 4px;
                border-radius: 8px 8px 0 0;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {p['surface']};
                color: {p['accent']};
                border-bottom: 3px solid {p['accent']};
            }}

            /* Исправление скролл-панели модулей */
            QScrollArea, #modules_container {{
                border: none;
                background: transparent;
                background-color: transparent;
            }}

            /* Динамический скроллбар */
            QScrollBar:vertical {{
                background: {p['surface_2']};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {p['border_strong']};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {p['muted']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        self.setStyleSheet(stylesheet)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)