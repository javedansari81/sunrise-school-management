"""
Transport Receipt PDF Generation Service
Generates professional transport payment receipts with month-wise breakdown
"""

import io
import os
import calendar
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class TransportReceiptGenerator:
    """Service for generating PDF receipts for transport payments"""

    # School Information
    SCHOOL_NAME = "SUNRISE NATIONAL PUBLIC SCHOOL"
    SCHOOL_ADDRESS = "Sena road, Farsauliyana, Rath, Hamirpur, UP - 210431"
    SCHOOL_EMAIL = "sunrise.nps008@gmail.com"
    SCHOOL_WEBSITE = "sunrisenps.com"

    # Logo path (relative to this file)
    LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'school_logo.jpeg')

    def __init__(self):
        """Initialize the transport receipt generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the receipt"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='SchoolTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='SchoolSubtitle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            spaceAfter=3,
            alignment=TA_CENTER
        ))

        # Receipt title
        self.styles.add(ParagraphStyle(
            name='ReceiptTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#d32f2f'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        ))

    def generate_receipt(
        self,
        payment_data: Dict[str, Any],
        student_data: Dict[str, Any],
        transport_data: Dict[str, Any],
        month_breakdown: List[Dict[str, Any]]
    ) -> io.BytesIO:
        """
        Generate a PDF receipt for a transport payment

        Args:
            payment_data: Payment information (id, amount, payment_method, payment_date, transaction_id, receipt_number)
            student_data: Student information (name, admission_number, class, roll_number, father_name)
            transport_data: Transport information (transport_type, distance, monthly_fee, total_paid, balance)
            month_breakdown: List of months covered with payment details

        Returns:
            BytesIO buffer containing the PDF
        """
        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Container for the 'Flowable' objects
        elements = []

        # Add school header
        elements.extend(self._create_header())

        # Add receipt title and metadata
        elements.extend(self._create_receipt_metadata(payment_data))

        # Add student details
        elements.extend(self._create_student_details(student_data))

        # Add transport details
        elements.extend(self._create_transport_details(transport_data))

        # Add payment details
        elements.extend(self._create_payment_details(payment_data))

        # Add month-wise breakdown table
        elements.extend(self._create_month_breakdown_table(month_breakdown))

        # Add transport summary
        elements.extend(self._create_transport_summary(transport_data))

        # Add footer
        elements.extend(self._create_footer())

        # Build the PDF
        doc.build(elements)

        # Reset buffer position to the beginning
        buffer.seek(0)
        return buffer

    def _create_header(self) -> List:
        """Create school header section with logo"""
        elements = []

        # Try to load the school logo
        logo_element = None
        if os.path.exists(self.LOGO_PATH):
            try:
                logo_element = Image(self.LOGO_PATH, width=1.2*inch, height=1.2*inch)
            except Exception:
                logo_element = None

        # Fallback to text placeholder if logo not found
        if logo_element is None:
            logo_element = Paragraph(
                "<b>LOGO</b>",
                ParagraphStyle(
                    'LogoPlaceholder',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#999999')
                )
            )

        # School information
        school_info = Paragraph(
            f"<b><font size=18 color='#1976d2'>{self.SCHOOL_NAME}</font></b><br/>"
            f"<font size=9 color='#555555'>{self.SCHOOL_ADDRESS}</font><br/>"
            f"<font size=9 color='#666666'>Email: {self.SCHOOL_EMAIL} | "
            f"Website: {self.SCHOOL_WEBSITE}</font>",
            ParagraphStyle(
                'SchoolInfo',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                leading=14
            )
        )

        # Create header table (logo + school info)
        header_table = Table(
            [[logo_element, school_info]],
            colWidths=[1.4*inch, 5.6*inch]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))
        elements.append(header_table)

        elements.append(Spacer(1, 0.1*inch))

        # Horizontal line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1976d2')),
        ]))
        elements.append(line_table)

        return elements

    def _create_receipt_metadata(self, payment_data: Dict[str, Any]) -> List:
        """Create receipt title and metadata section"""
        elements = []

        elements.append(Spacer(1, 0.2*inch))

        # Receipt title
        receipt_title = Paragraph("TRANSPORT FEE PAYMENT RECEIPT", self.styles['ReceiptTitle'])
        elements.append(receipt_title)

        # Receipt number and date in a table
        receipt_number = payment_data.get('receipt_number', f"TRANSPORT-{payment_data['id']:06d}")
        payment_date = payment_data.get('payment_date')
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
        date_str = payment_date.strftime('%d-%b-%Y') if payment_date else 'N/A'

        metadata_data = [
            ['Receipt No:', receipt_number, 'Date:', date_str]
        ]

        metadata_table = Table(metadata_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#555555')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(metadata_table)

        return elements

    def _create_student_details(self, student_data: Dict[str, Any]) -> List:
        """Create student details section"""
        elements = []

        elements.append(Spacer(1, 0.1*inch))

        # Section header
        section_header = Paragraph("Student Details", self.styles['SectionHeader'])
        elements.append(section_header)

        # Student details table
        student_name = student_data.get('name', 'N/A')
        admission_number = student_data.get('admission_number', 'N/A')
        class_name = student_data.get('class_name', 'N/A')
        roll_number = student_data.get('roll_number', 'N/A')
        father_name = student_data.get('father_name', 'N/A')

        student_details_data = [
            ['Student Name:', student_name, 'Admission No:', admission_number],
            ['Class:', class_name, 'Roll No:', roll_number],
            ['Father\'s Name:', father_name, '', '']
        ]

        student_table = Table(student_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        student_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(student_table)

        return elements

    def _create_transport_details(self, transport_data: Dict[str, Any]) -> List:
        """Create transport details section"""
        elements = []

        elements.append(Spacer(1, 0.1*inch))

        # Section header
        section_header = Paragraph("Transport Details", self.styles['SectionHeader'])
        elements.append(section_header)

        # Transport details table
        transport_type = transport_data.get('transport_type', 'N/A')
        distance = transport_data.get('distance', 'N/A')
        monthly_fee = transport_data.get('monthly_fee', 0)

        transport_details_data = [
            ['Transport Type:', transport_type, 'Distance:', f"{distance} KM"],
            ['Monthly Fee:', f"₹ {monthly_fee:,.2f}", '', '']
        ]

        transport_table = Table(transport_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        transport_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(transport_table)

        return elements

    def _create_payment_details(self, payment_data: Dict[str, Any]) -> List:
        """Create payment details section"""
        elements = []

        elements.append(Spacer(1, 0.1*inch))

        # Section header
        section_header = Paragraph("Payment Details", self.styles['SectionHeader'])
        elements.append(section_header)

        # Payment details table
        amount = payment_data.get('amount', 0)
        payment_method = payment_data.get('payment_method', 'Cash')
        transaction_id = payment_data.get('transaction_id', 'N/A')

        payment_details_data = [
            ['Amount Paid:', f"₹ {amount:,.2f}", 'Payment Method:', payment_method],
            ['Transaction ID:', transaction_id, '', '']
        ]

        payment_table = Table(payment_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(payment_table)

        return elements

    def _create_month_breakdown_table(self, month_breakdown: List[Dict[str, Any]]) -> List:
        """Create month-wise breakdown table"""
        elements = []

        if not month_breakdown:
            return elements

        elements.append(Spacer(1, 0.15*inch))

        # Section header
        section_header = Paragraph("Month-wise Payment Breakdown", self.styles['SectionHeader'])
        elements.append(section_header)

        # Table header
        table_data = [['Month', 'Academic Year', 'Amount Paid']]

        # Add month rows
        for month_data in month_breakdown:
            month_name = month_data.get('month_name', 'N/A')
            academic_year = month_data.get('academic_year', 'N/A')
            amount = month_data.get('allocated_amount', 0)

            table_data.append([
                month_name,
                str(academic_year),
                f"₹ {amount:,.2f}"
            ])

        # Create table
        breakdown_table = Table(table_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        breakdown_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        elements.append(breakdown_table)

        return elements

    def _create_transport_summary(self, transport_data: Dict[str, Any]) -> List:
        """Create transport fee summary section"""
        elements = []

        elements.append(Spacer(1, 0.15*inch))

        # Section header
        section_header = Paragraph("Transport Fee Summary", self.styles['SectionHeader'])
        elements.append(section_header)

        # Summary data
        total_paid = transport_data.get('total_paid', 0)
        balance = transport_data.get('balance', 0)

        summary_data = [
            ['Total Paid:', f"₹ {total_paid:,.2f}"],
            ['Balance Remaining:', f"₹ {balance:,.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[4.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cccccc')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1976d2')),
        ]))
        elements.append(summary_table)

        return elements

    def _create_footer(self) -> List:
        """Create footer section"""
        elements = []

        elements.append(Spacer(1, 0.3*inch))

        # Thank you message
        thank_you = Paragraph(
            "Thank you for your payment!",
            self.styles['Footer']
        )
        elements.append(thank_you)

        elements.append(Spacer(1, 0.1*inch))

        # Note
        note = Paragraph(
            "This is a computer-generated receipt and does not require a signature.",
            self.styles['Footer']
        )
        elements.append(note)

        return elements

