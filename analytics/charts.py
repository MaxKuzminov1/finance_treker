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
                     colors: Optional[List[str]] = None,
                     on_click_callback=None) -> QWidget:
    """Donut chart с легендой снизу и поддержкой Drill-down кликов."""
    widget = QWidget()
    layout = QVBoxLayout()
    canvas = MplCanvas(widget, width=5, height=6, dpi=100)
    ax = canvas.fig.add_subplot(111)

    if colors is None:
        colors = ['#6C5CE7', '#00B894', '#E17055', '#FDCB6E', '#0984E3',
                  '#E84393', '#636E72', '#2D3436', '#FF7675', '#74B9FF']

    used_colors = colors[:len(values)]
    explode = [0.0] * len(values)
    if values:
        explode[values.index(max(values))] = 0.05

    # picker=True делает график интерактивным
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='%1.1f%%',
        startangle=140, pctdistance=0.82,
        colors=used_colors, explode=explode,
        wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 1.5, 'picker': True},
        textprops={'fontsize': 9, 'fontweight': 'bold'}
    )

    # Привязываем имя категории к каждому сектору
    for i, w in enumerate(wedges):
        w.set_gid(labels[i])

    for at in autotexts:
        at.set_color('white')

    total = sum(values)
    if total > 0:
        ax.text(0, 0, f'{total:,.0f} ₽', ha='center', va='center',
                fontsize=15, fontweight='bold', color='#1E293B')

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=12)

    if labels and values:
        legend_labels = [f"{label}  —  {val:,.0f} ₽" for label, val in zip(labels, values)]
        legend = ax.legend(
            wedges, legend_labels, title="Категории (Кликните для фильтра)", loc="upper center",
            bbox_to_anchor=(0.5, -0.05), ncol=1, frameon=True, fancybox=True, framealpha=0.9,
            edgecolor='#E2E8F0', fontsize=10
        )
        legend.get_title().set_fontweight('bold')
        legend.get_title().set_color('#64748B')

    # Обработчик клика
        # Обработчик клика
    def on_pick(event):
        try:
            if on_click_callback and hasattr(event.artist, 'get_gid'):
                cat_name = event.artist.get_gid()
                if cat_name:
                    on_click_callback(cat_name)
        except Exception as e:
            print(f"Ошибка при клике на график: {e}")

    canvas.mpl_connect('pick_event', on_pick)
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