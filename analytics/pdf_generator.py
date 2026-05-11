import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


class PDFReportGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        # Регистрируем шрифт с поддержкой кириллицы (убедитесь, что путь к .ttf верный)
        # Для Windows обычно: "C:/Windows/Fonts/arial.ttf"
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
            self.font_name = 'Arial'
        except:
            self.font_name = 'Helvetica'

    def generate(self, kpi, report_rows, period_str: str):
        doc = SimpleDocTemplate(self.output_path, pagesize=A4)
        styles = getSampleStyleSheet()

        # Кастомный стиль для заголовка
        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'], fontName=self.font_name,
            fontSize=18, alignment=1, spaceAfter=20
        )

        elements = [
            Paragraph(f"Финансовый отчёт: {period_str}", title_style),
            Paragraph(f"Сформирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']),
            Spacer(1, 20)
        ]

        # Таблица KPI
        kpi_data = [
            ["Показатель", "Значение"],
            ["Общий доход", f"{kpi.total_income:,.2f} руб."],
            ["Общий расход", f"{kpi.total_expense:,.2f} руб."],
            ["Чистая прибыль", f"{kpi.profit:,.2f} руб."],
            ["Рентабельность", f"{kpi.profitability:.1f}%"],
            ["Средний чек", f"{kpi.avg_check:,.2f} руб."]
        ]

        t_kpi = Table(kpi_data, colWidths=[200, 150])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT')
        ]))
        elements.append(Paragraph("Ключевые показатели", styles['Heading2']))
        elements.append(t_kpi)
        elements.append(Spacer(1, 25))

        # Основная таблица операций
        header = ["Период", "Доход", "Расход", "Прибыль", "Изм. %"]
        table_data = [header]
        for row in report_rows:
            table_data.append([
                row.period_label,
                f"{row.income:,.0f}",
                f"{row.expense:,.0f}",
                f"{row.profit:,.0f}",
                f"{row.change_pct:+.1f}%" if row.change_pct else "-"
            ])

        t_main = Table(table_data, colWidths=[100, 100, 100, 100, 80])
        t_main.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        elements.append(Paragraph("Динамика по периодам", styles['Heading2']))
        elements.append(t_main)

        doc.build(elements)