"""
Report Generator Service
Genera reportes PDF con métricas de analytics
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from io import BytesIO
import os

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ReportGeneratorService:
    """
    Servicio para generar reportes PDF de analytics
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6
        ))

    def generate_monthly_summary_pdf(
        self,
        report_data: Dict[str, Any],
        file_path: str
    ) -> str:
        """
        Genera un PDF de resumen mensual

        Args:
            report_data: Datos del reporte (period, totals, trends, topProblems)
            file_path: Ruta donde guardar el PDF

        Returns:
            str: Ruta del archivo generado
        """
        # Crear documento
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Contenedor de elementos
        elements = []

        # Título
        title = Paragraph(
            "AutoDiag - Reporte Mensual de Diagnósticos",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        # Período
        period = report_data.get('period', {})
        period_text = f"Período: {period.get('fromDate', 'N/A')} a {period.get('toDate', 'N/A')}"
        elements.append(Paragraph(period_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))

        # Sección de totales
        elements.append(Paragraph("📊 Métricas Generales", self.styles['CustomHeading']))

        totals = report_data.get('totals', {})
        totals_data = [
            ['Métrica', 'Valor'],
            ['Total de Diagnósticos', f"{totals.get('totalDiagnoses', 0):,}"],
            ['Usuarios Únicos', f"{totals.get('totalUsers', 0):,}"],
            ['Talleres Registrados', f"{totals.get('totalWorkshops', 0):,}"],
            ['Citas Totales', f"{totals.get('totalAppointments', 0):,}"],
        ]

        totals_table = Table(totals_data, colWidths=[3 * inch, 2 * inch])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Sección de tendencias
        elements.append(Paragraph("📈 Tendencias", self.styles['CustomHeading']))

        trends = report_data.get('trends', {})
        trends_data = [
            ['Métrica', 'Valor'],
            ['Crecimiento de Diagnósticos', f"{trends.get('diagnosesGrowth', 0):.1f}%"],
            ['Tiempo Promedio de Respuesta', f"{trends.get('avgResponseTime', 0):.1f} min"],
        ]

        trends_table = Table(trends_data, colWidths=[3 * inch, 2 * inch])
        trends_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(trends_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Sección de top problemas
        top_problems = report_data.get('topProblems', [])
        if top_problems:
            elements.append(Paragraph("🔧 Top 5 Problemas Más Frecuentes", self.styles['CustomHeading']))

            problems_data = [['Categoría', 'Cantidad', 'Porcentaje']]
            for problem in top_problems[:5]:
                problems_data.append([
                    problem.get('category', 'N/A'),
                    str(problem.get('count', 0)),
                    f"{problem.get('percentage', 0):.1f}%"
                ])

            problems_table = Table(problems_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
            problems_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(problems_table)

        elements.append(Spacer(1, 0.5 * inch))

        # Footer
        footer_text = f"Generado el {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        elements.append(Paragraph(footer_text, self.styles['CustomBody']))

        # Construir PDF
        doc.build(elements)

        return file_path

    def generate_quarterly_summary_pdf(
        self,
        report_data: Dict[str, Any],
        file_path: str
    ) -> str:
        """
        Genera un PDF de resumen trimestral
        Similar a monthly pero con más detalle
        """
        # Por ahora, usar el mismo template que monthly
        return self.generate_monthly_summary_pdf(report_data, file_path)

    def generate_custom_report_pdf(
        self,
        report_data: Dict[str, Any],
        metrics: List[str],
        file_path: str
    ) -> str:
        """
        Genera un PDF personalizado según métricas seleccionadas
        """
        # Por ahora, usar el mismo template que monthly
        # En el futuro, filtrar según las métricas solicitadas
        return self.generate_monthly_summary_pdf(report_data, file_path)

    def generate_problems_analysis_pdf(
        self,
        report_data: Dict[str, Any],
        file_path: str
    ) -> str:
        """
        Genera un PDF enfocado en análisis de problemas
        """
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        elements = []

        # Título
        title = Paragraph(
            "AutoDiag - Análisis de Problemas Automotrices",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        # Período
        period = report_data.get('period', 'N/A')
        period_text = f"Período analizado: {period}"
        elements.append(Paragraph(period_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))

        # Total de problemas
        total_problems = report_data.get('totalProblems', 0)
        elements.append(Paragraph(
            f"Total de problemas diagnosticados: {total_problems:,}",
            self.styles['CustomHeading']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Distribución por categoría
        category_distribution = report_data.get('categoryDistribution', [])
        if category_distribution:
            elements.append(Paragraph("📊 Distribución por Categoría", self.styles['CustomHeading']))

            cat_data = [['Categoría', 'Cantidad', 'Porcentaje']]
            for cat in category_distribution:
                cat_data.append([
                    cat.get('category', 'N/A'),
                    str(cat.get('count', 0)),
                    f"{cat.get('percentage', 0):.1f}%"
                ])

            cat_table = Table(cat_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(cat_table)

        elements.append(Spacer(1, 0.3 * inch))

        # Distribución por urgencia
        urgency_distribution = report_data.get('urgencyDistribution', {})
        if urgency_distribution:
            elements.append(Paragraph("⚠️ Distribución por Nivel de Urgencia", self.styles['CustomHeading']))

            urgency_data = [
                ['Nivel', 'Cantidad'],
                ['🔴 CRITICAL', str(urgency_distribution.get('critical', 0))],
                ['🟠 HIGH', str(urgency_distribution.get('high', 0))],
                ['🟡 MEDIUM', str(urgency_distribution.get('medium', 0))],
                ['🟢 LOW', str(urgency_distribution.get('low', 0))],
            ]

            urgency_table = Table(urgency_data, colWidths=[3 * inch, 2 * inch])
            urgency_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(urgency_table)

        elements.append(Spacer(1, 0.5 * inch))

        # Footer
        footer_text = f"Generado el {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        elements.append(Paragraph(footer_text, self.styles['CustomBody']))

        doc.build(elements)

        return file_path
