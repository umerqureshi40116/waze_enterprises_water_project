"""
Professional PDF Report Generator
Generates reports in the format similar to Care Packages invoice
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfgen import canvas
from datetime import datetime
from decimal import Decimal
import io
import os

try:
    from num2words import num2words
except ImportError:
    num2words = None


class InvoiceReportGenerator:
    """Generate professional invoice PDFs matching the Care Packages format"""
    
    def __init__(self, filename="invoice.pdf"):
        self.filename = filename
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#333333'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
    
    def format_currency(self, amount):
        """Format amount as currency (PKR)"""
        if isinstance(amount, (int, float)):
            return f"Rs {amount:,.2f}"
        return f"Rs {float(amount):,.2f}"
    
    def format_amount_words(self, amount):
        """Convert amount to words in Urdu/English"""
        amount_int = int(float(amount))
        
        # Try using num2words if available
        if num2words:
            try:
                words = num2words(amount_int, lang='en')
                return f"Rs {words.title()}"
            except:
                pass
        
        # Fallback: simple conversion
        return f"Rs {amount_int} (Rupees only)"
    
    def generate_invoice_pdf(self, 
                           company_name="Waze Enterprises",
                           company_address="",
                           company_phone="",
                           company_email="",
                           invoice_no="",
                           invoice_date="",
                           bill_to_name="",
                           bill_to_address="",
                           bill_to_contact="",
                           items=None,
                           terms="",
                           signature_line="Authorized Signatory",
                           received_amount=0,
                           payment_status="pending"):
        """
        Generate a professional invoice PDF
        
        items: List of dicts with keys: item_name, quantity, unit_price, amount
        Example item: {
            'item_name': 'Deosal Water 500ml',
            'quantity': 45.3,
            'unit_price': 1350.00,
            'amount': 61155.00
        }
        received_amount: Amount already paid
        payment_status: 'pending', 'partial', or 'paid'
        """
        
        if items is None:
            items = []
        
        # Create document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
        )
        
        story = []
        
        # ===== HEADER =====
        # Try to load logo
        logo_element = None
        try:
            # Look for Water_Logo.jpg in the project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            logo_path = os.path.join(project_root, 'Water_Logo.jpg')
            if os.path.exists(logo_path):
                logo_element = Image(logo_path, width=2.4*inch, height=1.2*inch)
        except Exception as e:
            pass
        
        # Company name and details on left, logo on far right
        if logo_element:
            header_left = [
                [Paragraph(f"<b>{company_name}</b>", ParagraphStyle('CompanyName', parent=self.styles['Normal'], fontSize=12))],
                [Paragraph(company_address, self.styles['Normal'])],
            ]
            if company_phone:
                header_left.append([Paragraph(f"Phone: {company_phone}", self.styles['Normal'])])
            if company_email:
                header_left.append([Paragraph(f"Email: {company_email}", self.styles['Normal'])])
            
            left_table = Table(header_left, colWidths=[2.5*inch])
            left_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ]))
            
            # Spacer column to push logo to the right
            header_data = [
                [left_table, '', logo_element]
            ]
            header_table = Table(header_data, colWidths=[2.5*inch, 2*inch, 1.3*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (2, 0), (2, 0), 0),
                ('LEFTPADDING', (2, 0), (2, 0), 20),
            ]))
        else:
            header_data = [
                [Paragraph(f"<b>{company_name}</b>", ParagraphStyle('CompanyName', parent=self.styles['Normal'], fontSize=12)), ""],
                [Paragraph(company_address, self.styles['Normal']), ""],
            ]
            if company_phone:
                header_data.append([Paragraph(f"Phone: {company_phone}", self.styles['Normal']), ""])
            if company_email:
                header_data.append([Paragraph(f"Email: {company_email}", self.styles['Normal']), ""])
            
            header_table = Table(header_data, colWidths=[4*inch, 1.5*inch])
            header_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
        
        story.append(header_table)
        story.append(Spacer(1, 6))
        
        # Invoice title
        title = Paragraph("Invoice", self.title_style)
        story.append(title)
        story.append(Spacer(1, 15))
        
        # ===== INVOICE DETAILS (Left and Right) =====
        # Left side: Bill To | Right side: Invoice Details
        left_col = [
            Paragraph("<b>Bill To</b>", self.heading_style),
            Paragraph(bill_to_name, self.styles['Normal']),
            Paragraph(bill_to_address, self.styles['Normal']),
            Spacer(1, 5),
            Paragraph(f"<b>Contact No.:</b> {bill_to_contact}", self.styles['Normal']),
        ]
        
        right_col = [
            Paragraph("<b>Invoice Details</b>", self.heading_style),
            Table([
                [Paragraph("<b>Invoice No.:</b>", self.styles['Normal']), Paragraph(str(invoice_no), self.styles['Normal'])],
                [Paragraph("<b>Date:</b>", self.styles['Normal']), Paragraph(str(invoice_date), self.styles['Normal'])],
            ], colWidths=[2*inch, 2*inch]),
        ]
        
        details_table = Table([
            [left_col, right_col]
        ], colWidths=[3.5*inch, 3.5*inch])
        details_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 12))
        
        # ===== ITEMS TABLE =====
        table_data = [
            ['#', 'Item name', 'Quantity', 'Price/Unit', 'Amount']
        ]
        
        # Add items
        for idx, item in enumerate(items, 1):
            table_data.append([
                str(idx),
                item.get('item_name', ''),
                f"{item.get('quantity', 0):.2f}",
                self.format_currency(item.get('unit_price', 0)),
                self.format_currency(item.get('amount', 0)),
            ])
        
        # Calculate totals
        total_quantity = sum(float(item.get('quantity', 0)) for item in items)
        total_amount = sum(float(item.get('amount', 0)) for item in items)
        
        # Add totals row (use Paragraph for proper formatting)
        table_data.append([
            '',
            Paragraph('<b>Total</b>', self.styles['Normal']),
            Paragraph(f'<b>{total_quantity:.2f}</b>', self.styles['Normal']),
            '',
            Paragraph(f'<b>{self.format_currency(total_amount)}</b>', self.styles['Normal']),
        ])
        
        # Create table
        items_table = Table(
            table_data,
            colWidths=[0.4*inch, 2.2*inch, 1.1*inch, 1.2*inch, 1.3*inch]
        )
        
        # Style the table
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b69ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')]),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9f3ff')),
            ('ALIGN', (1, -1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0b69ff')),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 15))
        
        # ===== AMOUNT IN WORDS AND TOTALS SUMMARY =====
        summary_data = [
            [
                Paragraph(f"<b>Invoice Amount In Words</b><br/>{self.format_amount_words(total_amount)}", self.styles['Normal']),
                Table([
                    ['Sub Total', self.format_currency(total_amount)],
                ], colWidths=[1.5*inch, 1.2*inch]),
            ]
        ]
        
        summary_table = Table(summary_data, colWidths=[3.5*inch, 2.7*inch])
        summary_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))
        
        # ===== TOTAL AMOUNT BOX =====
        total_box_data = [
            ['Total', self.format_currency(total_amount)]
        ]
        total_box = Table(total_box_data, colWidths=[1.5*inch, 1.5*inch])
        total_box.setStyle(TableStyle([
            # Red background for both cells
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c1201e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(total_box)
        story.append(Spacer(1, 15))
        
        # ===== ADDITIONAL INFO =====
        received = float(received_amount) if received_amount else 0
        balance = total_amount - received
        
        info_data = [
            [Paragraph("<b>Received</b>", self.styles['Normal']), Paragraph(self.format_currency(received), self.styles['Normal'])],
            [Paragraph("<b>Balance</b>", self.styles['Normal']), Paragraph(self.format_currency(max(0, balance)), self.styles['Normal'])],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # ===== TERMS AND CONDITIONS =====
        if terms:
            story.append(Paragraph("<b>Terms and Conditions</b>", self.heading_style))
            story.append(Paragraph(terms, self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # ===== SIGNATURE =====
        story.append(Spacer(1, 30))
        story.append(Paragraph(signature_line, self.styles['Normal']))
        story.append(Spacer(1, 5))
        story.append(Paragraph("_" * 40, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        self.buffer.seek(0)
        return self.buffer


def generate_sales_invoice_pdf(sale_bill, customer, line_items, items_db):
    """
    Helper function to generate invoice PDF from database objects
    """
    generator = InvoiceReportGenerator()
    
    # Prepare items for PDF
    pdf_items = []
    total_amount = 0
    
    for line_item in line_items:
        item = next((i for i in items_db if i.id == line_item.item_id), None)
        item_name = item.name if item else line_item.item_id
        amount = float(line_item.quantity) * float(line_item.unit_price)
        
        pdf_items.append({
            'item_name': item_name,
            'quantity': float(line_item.quantity),
            'unit_price': float(line_item.unit_price),
            'amount': amount,
        })
        total_amount += amount
    
    # Get received amount and payment status from sale
    received_amount = float(sale_bill.paid_amount) if sale_bill.paid_amount else 0
    payment_status = sale_bill.payment_status if hasattr(sale_bill, 'payment_status') else 'pending'
    
    # Generate PDF
    pdf_buffer = generator.generate_invoice_pdf(
        company_name="Waze Enterprises - Water Bottle Division",
        company_address="Your Company Address",
        company_phone="+92 XXX XXXXXXX",
        company_email="info@waze-enterprises.com",
        invoice_no=sale_bill.bill_number,
        invoice_date=sale_bill.date.strftime('%d-%m-%Y') if hasattr(sale_bill.date, 'strftime') else str(sale_bill.date),
        bill_to_name=customer.name if customer else "Unknown Customer",
        bill_to_address=customer.address if customer and hasattr(customer, 'address') else "",
        bill_to_contact=customer.phone if customer and hasattr(customer, 'phone') else "",
        items=pdf_items,
        terms="Thank you for doing business with us!",
        signature_line="Authorized Signatory",
        received_amount=received_amount,
        payment_status=payment_status
    )
    
    return pdf_buffer


def generate_purchase_invoice_pdf(purchase_bill, supplier, line_items, items_db):
    """
    Helper function to generate purchase invoice PDF from database objects
    """
    generator = InvoiceReportGenerator()
    
    # Prepare items for PDF
    pdf_items = []
    total_amount = 0
    
    for line_item in line_items:
        item = next((i for i in items_db if i.id == line_item.item_id), None)
        item_name = item.name if item else line_item.item_id
        amount = float(line_item.quantity) * float(line_item.unit_price)
        
        pdf_items.append({
            'item_name': item_name,
            'quantity': float(line_item.quantity),
            'unit_price': float(line_item.unit_price),
            'amount': amount,
        })
        total_amount += amount
    
    # Get received amount and payment status from purchase
    received_amount = float(purchase_bill.paid_amount) if purchase_bill.paid_amount else 0
    payment_status = purchase_bill.payment_status if hasattr(purchase_bill, 'payment_status') else 'pending'
    
    # Generate PDF
    pdf_buffer = generator.generate_invoice_pdf(
        company_name="Waze Enterprises - Water Bottle Division",
        company_address="Your Company Address",
        company_phone="+92 XXX XXXXXXX",
        company_email="info@waze-enterprises.com",
        invoice_no=purchase_bill.bill_number,
        invoice_date=purchase_bill.date.strftime('%d-%m-%Y') if hasattr(purchase_bill.date, 'strftime') else str(purchase_bill.date),
        bill_to_name=supplier.name if supplier else "Unknown Supplier",
        bill_to_address=supplier.address if supplier and hasattr(supplier, 'address') else "",
        bill_to_contact=supplier.phone if supplier and hasattr(supplier, 'phone') else "",
        items=pdf_items,
        terms="Thank you for doing business with us!",
        signature_line="Authorized Signatory",
        received_amount=received_amount,
        payment_status=payment_status
    )
    
    return pdf_buffer
