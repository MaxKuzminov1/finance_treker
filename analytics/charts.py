# charts.py
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Optional
import matplotlib.ticker as ticker


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)


def create_line_chart(title: str, labels: List[str],
                      income_values: List[float], expense_values: List[float],
                      profit_values: List[float] = None) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout()
    canvas = MplCanvas(widget, width=8, height=5, dpi=100)
    ax = canvas.fig.add_subplot(111)

    x = range(len(labels))
    ax.plot(x, income_values, marker='o', color='#10B981', linewidth=2.5,
            markersize=6, label='Доход')
    ax.fill_between(x, income_values, alpha=0.08, color='#10B981')

    ax.plot(x, expense_values, marker='s', color='#EF4444', linewidth=2.5,
            markersize=6, label='Расход')
    ax.fill_between(x, expense_values, alpha=0.08, color='#EF4444')

    if profit_values:
        ax.plot(x, profit_values, marker='^', color='#4F46E5', linewidth=2.5,
                markersize=6, label='Прибыль')
        ax.fill_between(x, profit_values, alpha=0.08, color='#4F46E5')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=12)
    ax.legend(loc='upper left', frameon=True, fancybox=True, framealpha=0.8,
              fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.4, color='#64748B')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#475569')
    canvas.fig.tight_layout()

    layout.addWidget(canvas)
    widget.setLayout(layout)
    return widget


def create_pie_chart(title: str, labels: List[str], values: List[float],
                     colors: Optional[List[str]] = None) -> QWidget:
    """Donut chart с возможностью задать собственную палитру."""
    widget = QWidget()
    layout = QVBoxLayout()
    canvas = MplCanvas(widget, width=6, height=5, dpi=100)
    ax = canvas.fig.add_subplot(111)

    # Если палитра не передана, используем современный набор по умолчанию
    if colors is None:
        colors = ['#6C5CE7', '#00B894', '#E17055', '#FDCB6E', '#0984E3',
                  '#E84393', '#636E72', '#2D3436', '#FF7675', '#74B9FF']

    used_colors = colors[:len(values)]

    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='%1.1f%%',
        startangle=140, pctdistance=0.78,
        colors=used_colors,
        wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 1.5},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )
    # Стиль процентов
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')

    # Центральная подпись (общая сумма)
    total = sum(values)
    ax.text(0, 0, f'{total:,.0f} ₽', ha='center', va='center',
            fontsize=16, fontweight='bold', color='#1E293B')

    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=12)
    canvas.fig.tight_layout()

    layout.addWidget(canvas)
    widget.setLayout(layout)
    return widget


def create_bar_chart(title: str, categories: List[str],
                     planned: List[float], actual: List[float]) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout()
    canvas = MplCanvas(widget, width=8, height=5, dpi=100)
    ax = canvas.fig.add_subplot(111)

    x = range(len(categories))
    width = 0.35
    ax.bar([i - width/2 for i in x], planned, width, label='План',
           color='#F59E0B', edgecolor='white', linewidth=0.8)
    ax.bar([i + width/2 for i in x], actual, width, label='Факт',
           color='#4F46E5', edgecolor='white', linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=12)
    ax.legend(frameon=True, fancybox=True, framealpha=0.8, fontsize=10)
    ax.grid(True, axis='y', linestyle=':', alpha=0.4, color='#64748B')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#475569')
    canvas.fig.tight_layout()

    layout.addWidget(canvas)
    widget.setLayout(layout)
    return widget