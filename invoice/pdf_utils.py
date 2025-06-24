from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from datetime import datetime
import pytz

class NumberedCanvas:
    def __init__(self, canvas, doc):
        self.canvas = canvas
        self.doc = doc
        
    def draw_page_decorations(self):
        canvas = self.canvas
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#1a365d"))
        canvas.setLineWidth(1)
        canvas.line(40, letter[1] - 50, letter[0] - 40, letter[1] - 50)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - 40, 30, f"Page {page_num}")
        canvas.setLineWidth(0.5)
        canvas.line(40, 50, letter[0] - 40, 50)
        canvas.restoreState()

def add_page_number(canvas, doc):
    page_decorations = NumberedCanvas(canvas, doc)
    page_decorations.draw_page_decorations()

def generate_invoice_pdf(invoice, response, is_download=True):
    client = invoice.client
    payments = invoice.payments.all()
    filename = f"Legal_Invoice_{invoice.invoice_number}.pdf"
    disposition = f'attachment; filename="{filename}"' if is_download else f'inline; filename="{filename}"'
    response['Content-Disposition'] = disposition
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=70,
        bottomMargin=70,
        title=f"Legal Invoice {invoice.invoice_number} - {client.name}"
    )
    styles = getSampleStyleSheet()
    firm_title_style = ParagraphStyle(
        name="FirmTitle",
        fontSize=24,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.HexColor("#1a365d"),
        leading=28
    )
    firm_subtitle_style = ParagraphStyle(
        name="FirmSubtitle",
        fontSize=11,
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#4a5568"),
        leading=14
    )
    invoice_title_style = ParagraphStyle(
        name="InvoiceTitle",
        fontSize=20,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=25,
        textColor=colors.HexColor("#2d3748"),
        leading=24,
        borderWidth=1,
        borderColor=colors.HexColor("#e2e8f0"),
        borderPadding=10,
        backColor=colors.HexColor("#f7fafc")
    )
    section_header_style = ParagraphStyle(
        name="SectionHeader",
        fontSize=14,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
        spaceAfter=12,
        spaceBefore=15,
        textColor=colors.HexColor("#1a365d"),
        leading=16,
        borderWidth=0,
        borderColor=colors.HexColor("#1a365d"),
        leftIndent=0,
        bulletIndent=0
    )
    field_label_style = ParagraphStyle(
        name="FieldLabel",
        fontSize=10,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
        textColor=colors.HexColor("#2d3748"),
        leading=14,
        spaceAfter=2
    )
    field_value_style = ParagraphStyle(
        name="FieldValue",
        fontSize=10,
        fontName="Helvetica",
        alignment=TA_LEFT,
        textColor=colors.HexColor("#4a5568"),
        leading=14,
        spaceAfter=8
    )
    table_header_style = ParagraphStyle(
        name="TableHeader",
        fontSize=10,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#ffffff"),
        leading=12
    )
    table_content_style = ParagraphStyle(
        name="TableContent",
        fontSize=9,
        fontName="Helvetica",
        alignment=TA_LEFT,
        textColor=colors.HexColor("#2d3748"),
        leading=11
    )
    amount_style = ParagraphStyle(
        name="Amount",
        fontSize=10,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#1a365d"),
        leading=12
    )
    total_amount_style = ParagraphStyle(
        name="TotalAmount",
        fontSize=14,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#c53030"),
        leading=16
    )
    story = []
    story.append(Paragraph("ADVOCATE & LEGAL SERVICES", firm_title_style))
    story.append(Paragraph(
        "Professional Legal Consultation • Court Representation • Legal Documentation",
        firm_subtitle_style
    ))
    story.append(Spacer(1, 10))
    header_line_table = Table(
        [[""]],
        colWidths=[7.5*inch],
        style=[
            ('LINEABOVE', (0,0), (-1,-1), 2, colors.HexColor("#1a365d")),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0"))
        ]
    )
    story.append(header_line_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("LEGAL SERVICES INVOICE", invoice_title_style))
    story.append(Paragraph("CLIENT INFORMATION", section_header_style))
    
    def safe_value(value):
        return str(value) if value else "Not Specified"

    client_info_data = [
        [
            Paragraph("Client Name:", field_label_style),
            Paragraph(safe_value(client.name), field_value_style)
        ],
        [
            Paragraph("Email Address:", field_label_style),
            Paragraph(safe_value(client.email), field_value_style)
        ],
        [
            Paragraph("Contact Number:", field_label_style),
            Paragraph(safe_value(client.contact_number), field_value_style)
        ],
        [
            Paragraph("Address:", field_label_style),
            Paragraph(safe_value(client.address), field_value_style)
        ]
    ]
    invoice_info_data = [
        [
            Paragraph("Invoice Number:", field_label_style),
            Paragraph(safe_value(invoice.invoice_number), field_value_style)
        ],
        [
            Paragraph("Due Date:", field_label_style),
            Paragraph(safe_value(invoice.due_date), field_value_style)
        ],
        [
            Paragraph("Reference Number:", field_label_style),
            Paragraph(safe_value(invoice.reference_no), field_value_style)
        ]
    ]
    client_table = Table(
        client_info_data,
        colWidths=[1.2*inch, 2.3*inch],
        style=[
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f7fafc")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]
    )
    invoice_table = Table(
        invoice_info_data,
        colWidths=[1.2*inch, 2.3*inch],
        style=[
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f7fafc")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]
    )
    main_info_table = Table(
        [[client_table, invoice_table]],
        colWidths=[3.5*inch, 3.5*inch],
        style=[
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]
    )
    story.append(main_info_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("FINANCIAL SUMMARY", section_header_style))
    financial_data = [
        [
            Paragraph("Total Amount:", field_label_style),
            Paragraph(f"₹ {invoice.amount:,.2f}", amount_style)
        ],
        [
            Paragraph("Amount Paid:", field_label_style),
            Paragraph(f"₹ {invoice.get_paid_amount():,.2f}", amount_style)
        ],
        [
            Paragraph("Outstanding Balance:", field_label_style),
            Paragraph(f"₹ {invoice.get_pending_amount():,.2f}", total_amount_style)
        ]
    ]
    financial_table = Table(
        financial_data,
        colWidths=[3*inch, 2*inch],
        style=[
            ('BACKGROUND', (0,0), (-1,1), colors.HexColor("#edf2f7")),
            ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#fed7d7")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]
    )
    story.append(financial_table)
    story.append(Spacer(1, 25))
    if invoice.additional_details:
        story.append(Paragraph("CASE NOTES & ADDITIONAL DETAILS", section_header_style))
        additional_details_style = ParagraphStyle(
            name="AdditionalDetails",
            fontSize=10,
            fontName="Helvetica",
            alignment=TA_LEFT,
            textColor=colors.HexColor("#4a5568"),
            leading=14,
            displayName="Additional Details",
            spaceBefore=6,
            spaceAfter=20,
            leftIndent=0,
            rightIndent=0,
            borderPadding=12,
            borderWidth=0.5,
            borderColor=colors.HexColor("#e2e8f0"),
            backColor=colors.HexColor("#f7fafc"),
        )
        story.append(Paragraph(invoice.additional_details.replace("\n", "<br/>"), additional_details_style))
        story.append(Spacer(1, 14))
        story.append(Spacer(1, 14))
    if payments:
        story.append(Paragraph("PAYMENT HISTORY", section_header_style))
        story.append(Spacer(1, 10))
        payment_headers = [
            Paragraph("Amount", table_header_style),
            Paragraph("Date", table_header_style),
            Paragraph("Method", table_header_style),
            Paragraph("Reference", table_header_style),
            Paragraph("Remarks", table_header_style),
            Paragraph("Processed By", table_header_style)
        ]
        payment_data = [payment_headers]
        for payment in payments:
            payment_data.append([
                Paragraph(f"₹ {payment.amount:,.2f}", table_content_style),
                Paragraph(safe_value(payment.payment_date), table_content_style),
                Paragraph(safe_value(payment.get_payment_mode_display()), table_content_style),
                Paragraph(safe_value(payment.reference_no), table_content_style),
                Paragraph(safe_value(payment.remarks)[:30] + "..." if len(str(payment.remarks)) > 30 else safe_value(payment.remarks), table_content_style),
                Paragraph(safe_value(payment.created_by.username if payment.created_by else "System"), table_content_style)
            ])
        payment_table = Table(
            payment_data,
            colWidths=[0.8*inch, 0.9*inch, 0.8*inch, 1*inch, 1.5*inch, 1*inch],
            style=[
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a365d")),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8f9fa")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8f9fa")])
            ]
        )
        story.append(payment_table)
        story.append(Spacer(1, 20))
    story.append(Spacer(1, 30))
    sri_lanka_tz = pytz.timezone("Asia/Colombo")
    current_time = datetime.now(sri_lanka_tz).strftime("%B %d, %Y at %I:%M %p")
    footer_style = ParagraphStyle(
        name="Footer",
        fontSize=8,
        fontName="Helvetica",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#718096"),
        leading=10,
        spaceAfter=5
    )
    disclaimer_style = ParagraphStyle(
        name="Disclaimer",
        fontSize=7,
        fontName="Helvetica",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#a0aec0"),
        leading=9
    )
    story.append(Paragraph(f"Generated on {current_time} (Indian Time)", footer_style))
    story.append(Paragraph("This is a computer-generated invoice from our legal practice management system.", disclaimer_style))
    story.append(Paragraph("For any queries, please contact our office during business hours.", disclaimer_style))
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return response