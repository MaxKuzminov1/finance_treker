import os
import re
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
        # Регистрация шрифта для кириллицы
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
            self.font_name = 'Arial'
        except:
            self.font_name = 'Helvetica'  # Резервный вариант, если Arial не найден

    def generate(self, kpi, report_rows, period_str: str, shares: list = None, trend_text: str = ""):
        doc = SimpleDocTemplate(self.output_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40,
                                bottomMargin=40)
        styles = getSampleStyleSheet()

        # Кастомные стили
        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'], fontName=self.font_name,
            fontSize=18, alignment=1, spaceAfter=20, textColor=colors.HexColor('#1E293B')
        )
        h2_style = ParagraphStyle(
            'H2', parent=styles['Heading2'], fontName=self.font_name,
            fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#4F46E5')
        )
        normal_style = ParagraphStyle(
            'Normal_Ru', parent=styles['Normal'], fontName=self.font_name,
            fontSize=10, spaceAfter=10, leading=14
        )

        elements = [
            Paragraph(f"ФИНАНСОВЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ", title_style),
            Paragraph(f"Период анализа: {period_str}", normal_style),
            Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style),
            Spacer(1, 20)
        ]

        # 1. Таблица KPI
        elements.append(Paragraph("Ключевые финансовые показатели", h2_style))
        kpi_data = [
            ["Показатель", "Значение"],
            ["Общий доход", f"{kpi.total_income:,.2f} руб."],
            ["Общий расход", f"{kpi.total_expense:,.2f} руб."],
            ["Чистая прибыль", f"{kpi.profit:,.2f} руб."],
            ["Рентабельность", f"{kpi.profitability:.1f}%"],
            ["Средний чек", f"{kpi.avg_check:,.2f} руб."]
        ]

        t_kpi = Table(kpi_data, colWidths=[250, 150])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('FONTWEIGHT', (0, 0), (-1, 0), 'BOLD'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT')
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 15))

        # 2. Структура расходов
        if shares:
            elements.append(Paragraph("Структура расходов (Топ категорий)", h2_style))
            shares_data = [["Категория", "Сумма", "Доля %"]]
            for s in sorted(shares, key=lambda x: x.amount, reverse=True)[:10]:  # Топ-10 чтобы не перегружать PDF
                shares_data.append([s.category_name, f"{s.amount:,.2f} руб.", f"{s.percentage:.1f}%"])

            t_shares = Table(shares_data, colWidths=[200, 120, 80])
            t_shares.setStyle(t_kpi.getStyle())
            elements.append(t_shares)
            elements.append(Spacer(1, 15))

        # 3. Нейро-сводка (очищаем от UI HTML тегов)
        if trend_text:
            # Заменяем <br> на переносы строк, удаляем остальные теги
            clean_text = trend_text.replace('<br><br>', '\n\n').replace('<br>', '\n')
            clean_text = re.sub('<[^<]+?>', '', clean_text)

            elements.append(Paragraph("Интеллектуальный анализ и тренды", h2_style))
            for line in clean_text.split('\n'):
                if line.strip():
                    elements.append(Paragraph(line.strip(), normal_style))
            elements.append(Spacer(1, 15))

        # 4. Основная таблица (Cash Flow)
        if report_rows:
            elements.append(Paragraph("Динамика Cash Flow по периодам", h2_style))
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

            t_main = Table(table_data, colWidths=[100, 90, 90, 90, 70])
            t_main.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ]))
            elements.append(t_main)

        doc.build(elements)