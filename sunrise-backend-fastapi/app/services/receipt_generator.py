"""
Receipt PDF Generation Service
Generates professional fee payment receipts with month-wise breakdown
"""

import io
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


class ReceiptGenerator:
    """Service for generating PDF receipts for fee payments"""

    # School Information
    SCHOOL_NAME = "Sunrise National Public School"
    SCHOOL_ADDRESS = "Sena road, Farsauliyana, Rath, Hamirpur, UP - 210431"
    SCHOOL_PHONE = "6392171614, 9198627786"
    SCHOOL_EMAIL = "sunrise.nps008@gmail.com"
    SCHOOL_HOURS = "Mon-Sat 8:00 AM - 2:30 PM"

    def __init__(self):
        """Initialize the receipt generator"""
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
        month_breakdown: List[Dict[str, Any]],
        fee_summary: Dict[str, Any]
    ) -> io.BytesIO:
        """
        Generate a PDF receipt for a fee payment

        Args:
            payment_data: Payment information (id, amount, payment_method, payment_date, transaction_id, receipt_number)
            student_data: Student information (name, admission_number, class, roll_number, father_name)
            month_breakdown: List of months covered with payment details
            fee_summary: Summary of total fees (total_annual_fee, total_paid, balance_remaining)

        Returns:
            BytesIO object containing the PDF
        """
        # Create a BytesIO buffer
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

        # Add payment details
        elements.extend(self._create_payment_details(payment_data))

        # Add month-wise breakdown table
        elements.extend(self._create_month_breakdown_table(month_breakdown))

        # Add fee summary
        elements.extend(self._create_fee_summary(fee_summary))

        # Add footer
        elements.extend(self._create_footer())

        # Build the PDF
        doc.build(elements)

        # Reset buffer position to the beginning
        buffer.seek(0)
        return buffer

    def _create_header(self) -> List:
        """Create school header section"""
        elements = []

        # School name
        school_name = Paragraph(self.SCHOOL_NAME, self.styles['SchoolTitle'])
        elements.append(school_name)

        # School address
        school_address = Paragraph(self.SCHOOL_ADDRESS, self.styles['SchoolSubtitle'])
        elements.append(school_address)

        # Contact information
        contact_info = Paragraph(
            f"Phone: {self.SCHOOL_PHONE} | Email: {self.SCHOOL_EMAIL}",
            self.styles['SchoolSubtitle']
        )
        elements.append(contact_info)

        # Hours
        hours = Paragraph(f"Hours: {self.SCHOOL_HOURS}", self.styles['SchoolSubtitle'])
        elements.append(hours)

        elements.append(Spacer(1, 0.3*inch))

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
        receipt_title = Paragraph("FEE PAYMENT RECEIPT", self.styles['ReceiptTitle'])
        elements.append(receipt_title)

        # Receipt number and date in a table
        receipt_number = payment_data.get('receipt_number', f"FEE-{payment_data['id']:06d}")
        payment_date = payment_data.get('payment_date')
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
        date_str = payment_date.strftime('%d-%b-%Y') if payment_date else 'N/A'

        metadata_data = [
            ['Receipt No:', receipt_number, 'Date:', date_str]
        ]
        metadata_table = Table(metadata_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2.5*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ]))
        elements.append(metadata_table)

        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_student_details(self, student_data: Dict[str, Any]) -> List:
        """Create student details section"""
        elements = []

        # Section header
        section_header = Paragraph("Student Details", self.styles['SectionHeader'])
        elements.append(section_header)

        # Student details table
        student_details_data = [
            ['Student Name:', student_data.get('name', 'N/A'), 'Admission No:', student_data.get('admission_number', 'N/A')],
            ['Class:', student_data.get('class_name', 'N/A'), 'Roll No:', student_data.get('roll_number', 'N/A')],
            ['Father\'s Name:', student_data.get('father_name', 'N/A'), '', '']
        ]

        student_table = Table(student_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        student_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(student_table)

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

        payment_table = Table(payment_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#2e7d32')),  # Green for amount
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(payment_table)

        return elements

    def _create_month_breakdown_table(self, month_breakdown: List[Dict[str, Any]]) -> List:
        """Create month-wise breakdown table"""
        elements = []

        elements.append(Spacer(1, 0.1*inch))

        # Section header
        section_header = Paragraph("Month-wise Payment Breakdown", self.styles['SectionHeader'])
        elements.append(section_header)

        # Table header
        table_data = [
            ['Month', 'Monthly Fee', 'Previous Paid', 'Amount Paid', 'New Balance', 'Status']
        ]

        # Add month data
        for month_data in month_breakdown:
            month_name = month_data.get('month_name', 'N/A')
            monthly_fee = month_data.get('monthly_fee', 0)
            previous_paid = month_data.get('previous_paid', 0)
            allocated_amount = month_data.get('allocated_amount', 0)
            new_balance = month_data.get('remaining_balance', 0)
            status = month_data.get('status', 'Pending')

            table_data.append([
                month_name,
                f"₹ {monthly_fee:,.2f}",
                f"₹ {previous_paid:,.2f}",
                f"₹ {allocated_amount:,.2f}",
                f"₹ {new_balance:,.2f}",
                status
            ])

        # Create table
        breakdown_table = Table(table_data, colWidths=[1.2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch, 0.9*inch])

        # Style the table
        table_style = [
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-2, -1), 'RIGHT'),  # Right align amounts
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Left align month names
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'), # Center align status
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]

        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5')))

        # Highlight "Paid" status in green
        for i, row in enumerate(table_data[1:], start=1):
            if row[-1] == 'Paid':
                table_style.append(('TEXTCOLOR', (-1, i), (-1, i), colors.HexColor('#2e7d32')))
                table_style.append(('FONTNAME', (-1, i), (-1, i), 'Helvetica-Bold'))

        breakdown_table.setStyle(TableStyle(table_style))
        elements.append(breakdown_table)

        return elements

    def _create_fee_summary(self, fee_summary: Dict[str, Any]) -> List:
        """Create fee summary section"""
        elements = []

        elements.append(Spacer(1, 0.2*inch))

        # Section header
        section_header = Paragraph("Fee Summary", self.styles['SectionHeader'])
        elements.append(section_header)

        # Summary data
        total_annual_fee = fee_summary.get('total_annual_fee', 0)
        total_paid = fee_summary.get('total_paid', 0)
        balance_remaining = fee_summary.get('balance_remaining', 0)

        summary_data = [
            ['Total Annual Fee:', f"₹ {total_annual_fee:,.2f}"],
            ['Total Paid (Till Date):', f"₹ {total_paid:,.2f}"],
            ['Balance Remaining:', f"₹ {balance_remaining:,.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),  # Bold for balance
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#d32f2f')),  # Red for balance
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#cccccc')),
        ]))
        elements.append(summary_table)

        return elements

    def _create_footer(self) -> List:
        """Create receipt footer"""
        elements = []

        elements.append(Spacer(1, 0.4*inch))

        # Terms and conditions
        terms = Paragraph(
            "<b>Terms & Conditions:</b> This is a computer-generated receipt. "
            "Please keep this receipt for your records. "
            "Fees once paid are non-refundable. "
            "For any queries, please contact the school office.",
            self.styles['Footer']
        )
        elements.append(terms)

        elements.append(Spacer(1, 0.2*inch))

        # Thank you message
        thank_you = Paragraph(
            "Thank you for your payment!",
            self.styles['Footer']
        )
        elements.append(thank_you)

        # Generated timestamp
        generated_at = datetime.now().strftime('%d-%b-%Y %I:%M %p')
        timestamp = Paragraph(
            f"Generated on: {generated_at}",
            self.styles['Footer']
        )
        elements.append(timestamp)

        return elements

