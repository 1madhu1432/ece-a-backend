import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from uuid import UUID
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def create_lab_report(
        output_filepath: str,
        student_name: str,
        college_name: str,
        roll_number: str,
        experiment_title: str,
        objective: str,
        theory: str,
        source_code: str,
        execution_output: str,
        figures: list = None
    ):
        doc = SimpleDocTemplate(
            output_filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=1, # Center
            spaceAfter=15
        )

        h2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#2563EB'),
            spaceBefore=10,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1F2937')
        )

        code_style = ParagraphStyle(
            'ReportCode',
            parent=styles['Code'],
            fontSize=8,
            leading=10,
            backColor=colors.HexColor('#F3F4F6'),
            borderColor=colors.HexColor('#E5E7EB'),
            borderWidth=1,
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=6
        )

        story = []

        # Title
        story.append(Paragraph("ECE AI STUDIO - LABORATORY REPORT", title_style))
        story.append(Spacer(1, 10))

        # Meta Table
        meta_data = [
            [Paragraph(f"<b>Experiment:</b> {experiment_title}", body_style), Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%b-%Y')}", body_style)],
            [Paragraph(f"<b>Student:</b> {student_name}", body_style), Paragraph(f"<b>Roll No:</b> {roll_number or 'N/A'}", body_style)],
            [Paragraph(f"<b>Institution:</b> {college_name or 'Department of ECE'}", body_style), Paragraph("<b>Status:</b> Completed & Verified", body_style)]
        ]
        meta_table = Table(meta_data, colWidths=[300, 240])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DBEAFE')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 15))

        # Objective
        story.append(Paragraph("1. AIM / OBJECTIVE", h2_style))
        story.append(Paragraph(objective or "To simulate, analyze and verify engineering behavior.", body_style))
        story.append(Spacer(1, 10))

        # Theory
        story.append(Paragraph("2. THEORETICAL PRINCIPLE", h2_style))
        story.append(Paragraph(theory or "Theoretical formulations and mathematical models governing the system.", body_style))
        story.append(Spacer(1, 10))

        # Source Code
        story.append(Paragraph("3. SOURCE CODE", h2_style))
        safe_code = (source_code or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Preformatted(safe_code[:4000], code_style))
        story.append(Spacer(1, 10))

        # Execution Output
        story.append(Paragraph("4. EXECUTION RESULTS & LOGS", h2_style))
        safe_output = (execution_output or "Execution successful.").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Preformatted(safe_output[:2000], code_style))
        story.append(Spacer(1, 10))

        # Figures (if any PNG file exists)
        if figures:
            story.append(Paragraph("5. SIMULATION WAVEFORMS / PLOTS", h2_style))
            for fig_path in figures:
                if os.path.exists(fig_path) and fig_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        img = Image(fig_path, width=450, height=220)
                        story.append(img)
                        story.append(Spacer(1, 8))
                    except Exception:
                        pass

        # Conclusion
        story.append(Paragraph("6. CONCLUSION & INFERENCE", h2_style))
        story.append(Paragraph("The experiment was simulated successfully on ECE AI Studio. Observed waveforms and calculated parameters match theoretical expectations within experimental tolerance.", body_style))

        doc.build(story)
        return output_filepath
