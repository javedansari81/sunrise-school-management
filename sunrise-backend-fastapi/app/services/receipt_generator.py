"""
Receipt PDF Generation Service
Generates professional fee payment receipts with month-wise breakdown
Enhanced with comprehensive student information, transport details, and amount in words
Compact v2 layout with logo support
"""

import io
import os
import calendar
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter  # Letter size (8.5x11 inches)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class ReceiptGenerator:
    """Service for generating PDF receipts for fee payments (WhatsApp version)"""

    # School Information
    SCHOOL_NAME = "SUNRISE NATIONAL PUBLIC SCHOOL"
    SCHOOL_ADDRESS = "Sena road, Farsauliyana, Rath, Hamirpur, UP - 210431"
    SCHOOL_EMAIL = "sunrise.nps008@gmail.com"
    SCHOOL_WEBSITE = "sunrisenps.com"

    # Logo path (relative to this file)
    LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'school_logo.jpeg')

    def __init__(self):
        """Initialize the receipt generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _number_to_words(self, amount: float) -> str:
        """
        Convert amount to words (Indian numbering system)
        Example: 3200.50 -> "Three Thousand Two Hundred Rupees and Fifty Paise Only"
        """
        # Handle zero
        if amount == 0:
            return "Zero Rupees Only"

        # Split into rupees and paise
        rupees = int(amount)
        paise = int(round((amount - rupees) * 100))

        # Number to words mapping
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
                 "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        def convert_below_thousand(n):
            if n == 0:
                return ""
            elif n < 10:
                return ones[n]
            elif n < 20:
                return teens[n - 10]
            elif n < 100:
                return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
            else:
                return ones[n // 100] + " Hundred" + (" " + convert_below_thousand(n % 100) if n % 100 != 0 else "")

        def convert_to_words(n):
            if n == 0:
                return ""

            # Indian numbering system: crore, lakh, thousand, hundred
            crore = n // 10000000
            n %= 10000000
            lakh = n // 100000
            n %= 100000
            thousand = n // 1000
            n %= 1000
            hundred = n

            result = []
            if crore > 0:
                result.append(convert_below_thousand(crore) + " Crore")
            if lakh > 0:
                result.append(convert_below_thousand(lakh) + " Lakh")
            if thousand > 0:
                result.append(convert_below_thousand(thousand) + " Thousand")
            if hundred > 0:
                result.append(convert_below_thousand(hundred))

            return " ".join(result)

        # Convert rupees
        rupees_words = convert_to_words(rupees)
        result = f"{rupees_words} Rupees"

        # Add paise if present
        if paise > 0:
            paise_words = convert_below_thousand(paise)
            result += f" and {paise_words} Paise"

        result += " Only"
        return result

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
        fee_summary: Dict[str, Any],
        transport_data: Optional[Dict[str, Any]] = None,
        created_by_name: Optional[str] = None
    ) -> io.BytesIO:
        """
        Generate a PDF receipt for a fee payment (Compact v2 layout)

        Args:
            payment_data: Payment information (id, amount, payment_method, payment_date)
            student_data: Student information (name, admission_number, class, roll_number, father_name, address, mobile)
            month_breakdown: List of months covered with payment details
            fee_summary: Summary of total fees (total_annual_fee, total_paid, balance_remaining)
            transport_data: Optional transport fee details (monthly_fee, total_paid, balance, months_covered)
            created_by_name: Name of admin user who processed the payment (not used in compact v2)

        Returns:
            BytesIO object containing the PDF
        """
        # Create a BytesIO buffer
        buffer = io.BytesIO()

        # Create the PDF document (letter size = 8.5x11 inches)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        # Container for the 'Flowable' objects
        elements = []

        # Add school header with logo
        elements.extend(self._create_header(payment_data))

        # Add receipt title
        elements.extend(self._create_receipt_metadata(payment_data))

        # Add compact student info + payment details (side by side)
        elements.extend(self._create_student_and_payment_details(student_data, payment_data))

        # Add month-wise breakdown table
        elements.extend(self._create_month_breakdown_table(month_breakdown))

        # Add fee summary and transport (side by side if transport exists)
        elements.extend(self._create_summary_section(fee_summary, transport_data))

        # Add footer with signature area
        elements.extend(self._create_footer())

        # Build the PDF
        doc.build(elements)

        # Reset buffer position to the beginning
        buffer.seek(0)
        return buffer

    def _create_header(self, payment_data: Dict[str, Any]) -> List:
        """Create school header section with logo and school info (WhatsApp version - no phone)"""
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

        # School information - bigger name, no phone, clean layout
        school_info = Paragraph(
            f"<b><font size=18 color='#1976d2'>{self.SCHOOL_NAME}</font></b><br/>"
            f"<font size=9 color='#555555'>{self.SCHOOL_ADDRESS}</font><br/>"
            f"<font size=9 color='#666666'>Email: {self.SCHOOL_EMAIL} | Website: {self.SCHOOL_WEBSITE}</font>",
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
        """Create receipt title section (removed Receipt No and Date - using Payment Date instead)"""
        elements = []

        elements.append(Spacer(1, 0.15*inch))

        # Receipt title with decorative borders
        receipt_title = Paragraph("FEE PAYMENT RECEIPT", self.styles['ReceiptTitle'])
        elements.append(receipt_title)

        elements.append(Spacer(1, 0.1*inch))

        return elements

    def _create_student_and_payment_details(self, student_data: Dict[str, Any], payment_data: Dict[str, Any]) -> List:
        """Create compact side-by-side student info and payment details section"""
        elements = []

        # Get payment details
        amount = float(payment_data.get('amount', 0))
        payment_method = payment_data.get('payment_method', 'Cash')
        payment_date_str = payment_data.get('payment_date_str', 'N/A')
        amount_in_words = self._number_to_words(amount)

        # Get student details
        student_name = student_data.get('name', 'N/A')
        father_name = student_data.get('father_name', 'N/A')
        class_name = student_data.get('class_name', 'N/A')
        roll_number = student_data.get('roll_number', 'N/A')
        admission_number = student_data.get('admission_number', 'N/A')
        mobile = student_data.get('mobile', student_data.get('father_phone', 'N/A'))
        address = student_data.get('address', '')

        # Create left column (Student Info)
        student_info_style = ParagraphStyle(
            'StudentInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=14
        )

        student_lines = [
            f"<b>Student:</b> {student_name}",
            f"<b>Father:</b> {father_name}",
            f"<b>Class:</b> {class_name} | <b>Roll:</b> {roll_number}",
            f"<b>Adm No:</b> {admission_number} | <b>Mobile:</b> {mobile}",
        ]

        # Add address if available
        if address and address.strip():
            student_lines.append(f"<b>Address:</b> {address}")

        student_info = Paragraph("<br/>".join(student_lines), student_info_style)

        # Create right column (Payment Details)
        payment_info_style = ParagraphStyle(
            'PaymentInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=14,
            alignment=TA_RIGHT
        )

        payment_lines = [
            f"<b>Amount:</b> <font color='#2e7d32' size=11><b>₹ {amount:,.2f}</b></font>",
            f"<b>Date:</b> {payment_date_str}",
            f"<b>Method:</b> {payment_method}",
            f"<font size=8><i>({amount_in_words})</i></font>",
        ]

        payment_info = Paragraph("<br/>".join(payment_lines), payment_info_style)

        # Create side-by-side table
        info_table = Table(
            [[student_info, payment_info]],
            colWidths=[4*inch, 3*inch]
        )
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
        ]))
        elements.append(info_table)

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

    def _create_summary_section(self, fee_summary: Dict[str, Any], transport_data: Optional[Dict[str, Any]] = None) -> List:
        """Create Template C style summary section with proper table and header"""
        elements = []

        elements.append(Spacer(1, 0.15*inch))

        # Get fee summary data
        total_annual_fee = fee_summary.get('total_annual_fee', 0)
        total_paid = fee_summary.get('total_paid', 0)
        balance_remaining = fee_summary.get('balance_remaining', 0)

        if transport_data:
            # With transport - two column table
            monthly_fee = transport_data.get('monthly_fee', 0)
            transport_paid = transport_data.get('total_paid', 0)
            transport_balance = transport_data.get('balance', 0)
            months_covered = transport_data.get('months_covered', [])
            months_str = ', '.join(months_covered) if months_covered else 'N/A'

            # Create table data with header
            summary_data = [
                ['PAYMENT SUMMARY', ''],  # Header row (will be merged)
                ['Annual Fee', f'₹ {total_annual_fee:,.2f}', 'Transport Monthly', f'₹ {monthly_fee:,.2f}'],
                ['Total Paid', f'₹ {total_paid:,.2f}', 'Transport Paid', f'₹ {transport_paid:,.2f}'],
                ['', '', 'Transport Balance', f'₹ {transport_balance:,.2f}'],
                ['BALANCE DUE', f'₹ {balance_remaining:,.2f}', 'Months', months_str],
            ]

            summary_table = Table(summary_data, colWidths=[1.6*inch, 1.9*inch, 1.6*inch, 1.9*inch])
            summary_table.setStyle(TableStyle([
                # Header row styling
                ('SPAN', (0, 0), (3, 0)),  # Merge header across all columns
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#1976d2')),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (3, 0), 11),
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                ('TOPPADDING', (0, 0), (3, 0), 8),
                ('BOTTOMPADDING', (0, 0), (3, 0), 8),

                # Data rows styling
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),

                # Balance row highlighting
                ('FONTNAME', (0, 4), (1, 4), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1, 4), (1, 4), colors.HexColor('#d32f2f')),
                ('FONTSIZE', (0, 4), (1, 4), 10),
                ('LINEABOVE', (0, 4), (1, 4), 1, colors.HexColor('#cccccc')),

                # Transport column background
                ('BACKGROUND', (2, 1), (3, -1), colors.HexColor('#f0f8ff')),

                # Grid and box
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1976d2')),
                ('LINEAFTER', (1, 1), (1, -1), 0.5, colors.HexColor('#cccccc')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        else:
            # Without transport - single column table
            summary_data = [
                ['PAYMENT SUMMARY', ''],  # Header row
                ['Annual Fee', f'₹ {total_annual_fee:,.2f}'],
                ['Total Paid', f'₹ {total_paid:,.2f}'],
                ['BALANCE DUE', f'₹ {balance_remaining:,.2f}'],
            ]

            summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
            summary_table.setStyle(TableStyle([
                # Header row styling
                ('SPAN', (0, 0), (1, 0)),
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1976d2')),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 11),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('TOPPADDING', (0, 0), (1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (1, 0), 8),

                # Data rows styling
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),

                # Balance row highlighting
                ('FONTNAME', (0, 3), (1, 3), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1, 3), (1, 3), colors.HexColor('#d32f2f')),
                ('FONTSIZE', (0, 3), (1, 3), 10),
                ('LINEABOVE', (0, 3), (1, 3), 1, colors.HexColor('#cccccc')),

                # Grid and box
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1976d2')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

        elements.append(summary_table)

        return elements

    def _create_footer(self) -> List:
        """Create simple footer for WhatsApp receipt (no signatures)"""
        elements = []

        elements.append(Spacer(1, 0.2*inch))

        # Horizontal line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cccccc')),
        ]))
        elements.append(line_table)

        elements.append(Spacer(1, 0.1*inch))

        # Simple footer message
        footer_msg = Paragraph(
            "This is a computer-generated receipt. Thank you!",
            ParagraphStyle(
                'FooterMsg',
                parent=self.styles['Footer'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER
            )
        )
        elements.append(footer_msg)

        return elements

