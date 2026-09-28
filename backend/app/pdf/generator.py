import io
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.config import settings

def get_clinic_header(styles) -> list:
    """Reusable clinic branding header."""
    header_elements = []
    
    clinic_title_style = ParagraphStyle(
        'ClinicTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0d9488'), # Primary medical teal
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    clinic_sub_style = ParagraphStyle(
        'ClinicSub',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#4b5563')
    )
    
    header_elements.append(Paragraph(settings.CLINIC_NAME, clinic_title_style))
    header_elements.append(Paragraph(f"{settings.CLINIC_ADDRESS} | Phone: {settings.CLINIC_PHONE}", clinic_sub_style))
    header_elements.append(Paragraph(f"Email: {settings.CLINIC_EMAIL} | Reg No: {settings.CLINIC_REG_NO}", clinic_sub_style))
    header_elements.append(Spacer(1, 8))
    header_elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d9488'), spaceBefore=2, spaceAfter=12))
    
    return header_elements


def generate_prescription_pdf(prescription, patient, dentist) -> bytes:
    """Generate a high-grade professional prescription PDF document."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldNormal', parent=normal_style, fontName='Helvetica-Bold')

    story = []
    story.extend(get_clinic_header(styles))

    # Doctor and Prescription Meta Info Box
    dentist_name = dentist.user.full_name if dentist and dentist.user else "Dr. In-Charge"
    dentist_spec = dentist.specialization if dentist else "Dental Surgeon"
    dentist_lic = dentist.license_number if dentist else "N/A"

    doc_meta_data = [
        [
            Paragraph(f"<b>Prescribing Doctor:</b><br/>{dentist_name}<br/><i>{dentist_spec}</i><br/>Reg/License: {dentist_lic}", normal_style),
            Paragraph(
                f"<b>Prescription #:</b> {prescription.prescription_number}<br/>"
                f"<b>Date:</b> {prescription.created_at.strftime('%d-%b-%Y')}<br/>"
                f"<b>Visit Date:</b> {prescription.created_at.strftime('%I:%M %p')}",
                normal_style
            )
        ]
    ]

    t_doc = Table(doc_meta_data, colWidths=[270, 270])
    t_doc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_doc)
    story.append(Spacer(1, 10))

    # Patient Information Box
    dob_str = patient.date_of_birth.strftime('%d-%b-%Y') if patient.date_of_birth else 'N/A'
    patient_data = [
        [
            Paragraph(f"<b>Patient:</b> {patient.full_name} ({patient.gender})", normal_style),
            Paragraph(f"<b>Code:</b> {patient.patient_code}", normal_style),
            Paragraph(f"<b>DOB:</b> {dob_str}", normal_style),
            Paragraph(f"<b>Phone:</b> {patient.phone}", normal_style)
        ]
    ]
    t_patient = Table(patient_data, colWidths=[170, 110, 130, 130])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdfa')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#99f6e4')),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 12))

    # Diagnosis if present
    if prescription.diagnosis_summary:
        story.append(Paragraph(f"<b>Diagnosis / Clinical Summary:</b> {prescription.diagnosis_summary}", normal_style))
        story.append(Spacer(1, 10))

    # Prescribed Medicines Header
    story.append(Paragraph("<b>℞ MEDICATION & DOSAGE SCHEDULE</b>", ParagraphStyle('RxHeader', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0f766e'))))
    story.append(Spacer(1, 6))

    # Table of Medicines
    med_table_data = [
        [
            Paragraph("<b>#</b>", bold_style),
            Paragraph("<b>Medicine Name</b>", bold_style),
            Paragraph("<b>Dosage</b>", bold_style),
            Paragraph("<b>Frequency</b>", bold_style),
            Paragraph("<b>Duration</b>", bold_style),
            Paragraph("<b>Timing & Instructions</b>", bold_style)
        ]
    ]

    for idx, item in enumerate(prescription.items, start=1):
        med_table_data.append([
            Paragraph(str(idx), normal_style),
            Paragraph(f"<b>{item.medicine_name}</b>", normal_style),
            Paragraph(item.dosage, normal_style),
            Paragraph(item.frequency, normal_style),
            Paragraph(item.duration, normal_style),
            Paragraph(f"{item.timing} {(' - ' + item.instructions) if item.instructions else ''}", normal_style)
        ])

    t_meds = Table(med_table_data, colWidths=[25, 140, 75, 80, 70, 150])
    t_meds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d9488')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_meds)
    story.append(Spacer(1, 12))

    # General Instructions
    if prescription.general_instructions:
        story.append(Paragraph("<b>General Advice & Instructions:</b>", bold_style))
        story.append(Paragraph(prescription.general_instructions, normal_style))
        story.append(Spacer(1, 15))

    # Footer and Signature block
    story.append(Spacer(1, 30))
    sig_data = [
        [
            Paragraph("<i>* Valid for 30 days from date of issue.<br/>* Keep medications out of reach of children.</i>", ParagraphStyle('Foot', parent=normal_style, fontSize=8, textColor=colors.gray)),
            Paragraph(f"____________________________________<br/><b>{dentist_name}</b><br/>Authorized Doctor Signature", ParagraphStyle('Sig', parent=normal_style, alignment=2))
        ]
    ]
    t_sig = Table(sig_data, colWidths=[300, 240])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_sig)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_invoice_pdf(invoice, patient) -> bytes:
    """Generate a clean, professional dental treatment invoice PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldNormal', parent=normal_style, fontName='Helvetica-Bold')

    story = []
    story.extend(get_clinic_header(styles))

    # Invoice Header Title & Meta
    status_color = colors.HexColor('#10b981') if invoice.status == 'paid' else (colors.HexColor('#f59e0b') if invoice.status == 'partially_paid' else colors.HexColor('#ef4444'))
    
    meta_table_data = [
        [
            Paragraph(
                f"<b>Billed To:</b><br/>"
                f"<b>{patient.full_name}</b><br/>"
                f"Patient ID: {patient.patient_code}<br/>"
                f"Phone: {patient.phone}<br/>"
                f"Address: {patient.address or 'N/A'}",
                normal_style
            ),
            Paragraph(
                f"<b>INVOICE:</b> {invoice.invoice_number}<br/>"
                f"<b>Issue Date:</b> {invoice.issue_date.strftime('%d-%b-%Y')}<br/>"
                f"<b>Due Date:</b> {invoice.due_date.strftime('%d-%b-%Y')}<br/>"
                f"<b>Status:</b> <font color='{status_color.hexval()}'><b>{invoice.status.upper().replace('_', ' ')}</b></font>",
                normal_style
            )
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # Items Table
    item_rows = [
        [
            Paragraph("<b>#</b>", bold_style),
            Paragraph("<b>Item / Procedure Description</b>", bold_style),
            Paragraph("<b>Qty</b>", bold_style),
            Paragraph("<b>Unit Price (₹)</b>", bold_style),
            Paragraph("<b>Total (₹)</b>", bold_style)
        ]
    ]

    for idx, item in enumerate(invoice.items, start=1):
        item_rows.append([
            Paragraph(str(idx), normal_style),
            Paragraph(item.description, normal_style),
            Paragraph(str(item.quantity), normal_style),
            Paragraph(f"{item.unit_price:.2f}", normal_style),
            Paragraph(f"{item.total:.2f}", normal_style)
        ])

    t_items = Table(item_rows, colWidths=[30, 270, 50, 95, 95])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d9488')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_items)
    story.append(Spacer(1, 12))

    # Totals breakdown
    totals_data = [
        [Paragraph("<b>Subtotal:</b>", normal_style), Paragraph(f"₹{invoice.subtotal:.2f}", bold_style)],
        [Paragraph("<b>Discount:</b>", normal_style), Paragraph(f"-₹{invoice.discount:.2f}", normal_style)],
        [Paragraph("<b>GST (Tax):</b>", normal_style), Paragraph(f"₹{invoice.tax:.2f}", normal_style)],
        [Paragraph("<b>Grand Total:</b>", bold_style), Paragraph(f"<b>₹{invoice.total:.2f}</b>", bold_style)],
        [Paragraph("<b>Amount Paid:</b>", normal_style), Paragraph(f"₹{invoice.paid_amount:.2f}", normal_style)],
        [Paragraph("<b>Balance Due:</b>", bold_style), Paragraph(f"<font color='#dc2626'><b>₹{invoice.balance:.2f}</b></font>", bold_style)]
    ]
    t_totals = Table(totals_data, colWidths=[120, 100])
    t_totals.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,3), (-1,3), 1, colors.HexColor('#0d9488')),
    ]))
    
    # Wrap totals in outer alignment container
    outer_table = Table([[Paragraph("", normal_style), t_totals]], colWidths=[320, 220])
    outer_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(outer_table)
    story.append(Spacer(1, 20))

    # Payment History if present
    if invoice.payments:
        story.append(Paragraph("<b>Recorded Payments:</b>", bold_style))
        pay_rows = [
            [Paragraph("<b>Date</b>", bold_style), Paragraph("<b>Method</b>", bold_style), Paragraph("<b>Reference</b>", bold_style), Paragraph("<b>Amount (₹)</b>", bold_style)]
        ]
        for p in invoice.payments:
            pay_rows.append([
                Paragraph(p.payment_date.strftime('%d-%b-%Y %H:%M'), normal_style),
                Paragraph(p.payment_method.upper(), normal_style),
                Paragraph(p.transaction_reference or '-', normal_style),
                Paragraph(f"₹{p.amount:.2f}", normal_style)
            ])
        t_pay = Table(pay_rows, colWidths=[140, 100, 180, 120])
        t_pay.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
        ]))
        story.append(t_pay)
        story.append(Spacer(1, 15))

    # Footer notice
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Thank you for trusting Apex Dental Care with your oral health. Please retain this invoice for your medical insurance and personal records.</i>", ParagraphStyle('Foot', parent=normal_style, fontSize=8, textColor=colors.gray, alignment=1)))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
