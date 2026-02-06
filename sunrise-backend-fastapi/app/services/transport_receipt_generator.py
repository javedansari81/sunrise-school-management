"""
Transport Receipt PDF Generation Service
Generates professional transport payment receipts with month-wise breakdown
Matches the combined tuition+transport receipt format from ReceiptGenerator
Black & white design for WhatsApp UTILITY template compliance
"""

import io
import os
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class TransportReceiptGenerator:
    """Service for generating PDF receipts for transport payments (matches ReceiptGenerator format)"""

    # School Information
    SCHOOL_NAME = "SUNRISE NATIONAL PUBLIC SCHOOL"
    SCHOOL_ADDRESS = "Sena road, Farsauliyana, Rath, Hamirpur, UP - 210431"
    SCHOOL_EMAIL = "sunrise.nps008@gmail.com"
    SCHOOL_WEBSITE = "https://sunrisenps.com"

    # Logo path (B&W version - same as ReceiptGenerator)
    LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'school_logo_bw.jpeg')

    def __init__(self):
        """Initialize the transport receipt generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup paragraph styles for professional B&W receipt (matches ReceiptGenerator)"""
        # School name style
        self.styles.add(ParagraphStyle(
            name='SchoolName',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))

        # School address style
        self.styles.add(ParagraphStyle(
            name='SchoolAddress',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=2
        ))

        # Receipt title style
        self.styles.add(ParagraphStyle(
            name='ReceiptTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceBefore=8,
            spaceAfter=8
        ))

        # Section header style - CENTER ALIGNED
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceBefore=6,
            spaceAfter=4
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceBefore=12
        ))

    def generate_receipt(
        self,
        payment_data: Dict[str, Any],
        student_data: Dict[str, Any],
        transport_data: Dict[str, Any],
        month_breakdown: List[Dict[str, Any]]
    ) -> io.BytesIO:
        """
        Generate a PDF receipt for a transport payment (matches ReceiptGenerator format)

        Args:
            payment_data: Payment information (id, amount, payment_method, payment_date, transaction_id, receipt_number)
            student_data: Student information (name, admission_number, class_name, roll_number, father_name, mobile)
            transport_data: Transport information (transport_type, distance, monthly_fee, total_paid, balance)
            month_breakdown: List of months covered with payment details

        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        elements = []

        # === HEADER WITH LOGO ===
        elements.extend(self._create_header())

        # === RECEIPT TITLE ===
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("FEE PAYMENT RECEIPT", self.styles['ReceiptTitle']))
        elements.append(Spacer(1, 0.1*inch))

        # === EXTRACT DATA ===
        amount = float(payment_data.get('amount', 0))
        payment_method = payment_data.get('payment_method', 'Cash')
        payment_date = payment_data.get('payment_date')
        if isinstance(payment_date, str):
            payment_date_str = payment_date
        elif payment_date:
            payment_date_str = payment_date.strftime('%d-%b-%Y')
        else:
            payment_date_str = 'N/A'
        receipt_number = payment_data.get('receipt_number', f"TRANSPORT-{payment_data.get('id', 0):06d}")

        student_name = student_data.get('name', 'N/A')
        father_name = student_data.get('father_name', 'N/A')
        class_name = student_data.get('class_name', 'N/A')
        admission_number = student_data.get('admission_number', 'N/A')
        roll_number = student_data.get('roll_number', 'N/A')
        mobile = student_data.get('mobile', student_data.get('father_phone', 'N/A'))

        # === RECEIPT INFO TABLE ===
        elements.extend(self._create_receipt_info_table(receipt_number, payment_date_str, amount))

        # === STUDENT DETAILS TABLE ===
        elements.extend(self._create_student_table(
            student_name, father_name, class_name, roll_number, admission_number, mobile
        ))

        # === TUITION FEE MONTH-WISE TABLE (show "-" for transport-only payment) ===
        elements.extend(self._create_tuition_month_table())

        # === TRANSPORT FEE MONTH-WISE BREAKDOWN TABLE ===
        elements.extend(self._create_transport_month_breakdown_table(month_breakdown, transport_data))

        # === SUMMARY TABLE ===
        elements.extend(self._create_summary_table(transport_data))

        # === FOOTER ===
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph(
            "System generated receipt. Contact school office for queries.",
            self.styles['Footer']
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _create_header(self) -> List:
        """Create header with B&W logo and school info (matches ReceiptGenerator)"""
        elements = []

        # Try to load the B&W logo
        logo_element = None
        if os.path.exists(self.LOGO_PATH):
            try:
                logo_element = Image(self.LOGO_PATH, width=0.9*inch, height=0.9*inch)
            except Exception:
                logo_element = None

        # School info paragraph - BIGGER school name (18pt)
        school_info = Paragraph(
            f"<b><font size=18>{self.SCHOOL_NAME}</font></b><br/>"
            f"<font size=9>{self.SCHOOL_ADDRESS}</font><br/>"
            f"<font size=9>Email: {self.SCHOOL_EMAIL} | Web: {self.SCHOOL_WEBSITE}</font>",
            ParagraphStyle(
                'HeaderInfo',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                leading=16
            )
        )

        if logo_element:
            # Create header table with logo - full width
            header_data = [[logo_element, school_info]]
            header_table = Table(header_data, colWidths=[1.1*inch, 5.9*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            elements.append(header_table)
        else:
            # No logo - just school info
            elements.append(Paragraph(self.SCHOOL_NAME, self.styles['SchoolName']))
            elements.append(Paragraph(self.SCHOOL_ADDRESS, self.styles['SchoolAddress']))
            elements.append(Paragraph(
                f"Email: {self.SCHOOL_EMAIL} | Web: {self.SCHOOL_WEBSITE}",
                self.styles['SchoolAddress']
            ))

        # Horizontal line - full width
        elements.append(Spacer(1, 0.08*inch))
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ]))
        elements.append(line_table)

        return elements

    def _create_receipt_info_table(
        self, receipt_number: str, payment_date: str, paid_amount: float
    ) -> List:
        """Create receipt number, date and paid amount table - full width"""
        elements = []
        elements.append(Spacer(1, 0.1*inch))

        data = [
            ['Receipt No:', receipt_number, 'Date:', payment_date],
            ['Paid Amount:', f'Rs. {paid_amount:,.0f}', '', '']
        ]

        # Full width table (7 inches)
        table = Table(data, colWidths=[1.2*inch, 2.3*inch, 1*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # Merge cells for Paid Amount row
            ('SPAN', (1, 1), (3, 1)),
        ]))
        elements.append(table)

        return elements

    def _create_student_table(
        self, name: str, guardian: str, class_name: str,
        roll_number: str, admission_number: str, mobile: str
    ) -> List:
        """Create student details table - full width"""
        elements = []
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("STUDENT DETAILS", self.styles['SectionHeader']))

        data = [
            ['Name:', name, 'Guardian:', guardian],
            ['Class:', class_name, 'Roll No:', roll_number],
            ['Adm. No:', admission_number, 'Mobile:', mobile],
        ]

        # Full width table (7 inches)
        table = Table(data, colWidths=[1.1*inch, 2.4*inch, 1.1*inch, 2.4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        return elements

    def _create_tuition_month_table(self) -> List:
        """Create tuition fee table with "-" for transport-only payments"""
        elements = []
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("TUITION FEE - MONTH WISE", self.styles['SectionHeader']))

        # Show "-" for all columns since this is transport-only payment
        data = [
            ['Month', 'Monthly Fee', 'Pre-Paid', 'Paid Now', 'Balance', 'Status'],
            ['-', '-', '-', '-', '-', '-']
        ]

        # Full width table (7 inches) - 6 columns
        col_widths = [1.2*inch, 1.15*inch, 1.15*inch, 1.15*inch, 1.15*inch, 1.2*inch]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header row styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        return elements

    def _create_transport_month_breakdown_table(
        self, month_breakdown: List[Dict[str, Any]], transport_data: Dict[str, Any]
    ) -> List:
        """Create transport fee month-wise breakdown table - full width"""
        elements = []
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("TRANSPORT FEE - MONTH WISE", self.styles['SectionHeader']))

        # Header row with Pre-Paid and Paid Now columns
        data = [['Month', 'Monthly Fee', 'Pre-Paid', 'Paid Now', 'Balance', 'Status']]

        monthly_fee = transport_data.get('monthly_fee', 0)

        if month_breakdown:
            for month in month_breakdown:
                month_name = month.get('month_name', '-')
                # Use transport monthly fee
                fee = monthly_fee
                # Previous paid amount before this transaction
                pre_paid = month.get('previous_paid', 0)
                # Amount being paid in this transaction
                paid_now = month.get('allocated_amount', 0)
                # Calculate balance
                balance = fee - pre_paid - paid_now

                # Determine status
                if balance <= 0.01:
                    status = 'Paid'
                elif (pre_paid + paid_now) > 0:
                    status = 'Partial'
                else:
                    status = 'Unpaid'

                data.append([
                    month_name,
                    f'Rs. {fee:,.0f}',
                    f'Rs. {pre_paid:,.0f}',
                    f'Rs. {paid_now:,.0f}',
                    f'Rs. {max(0, balance):,.0f}',
                    status
                ])
        else:
            # No month breakdown, show summary row
            data.append(['-', '-', '-', '-', '-', '-'])

        # Full width table (7 inches) - 6 columns
        col_widths = [1.2*inch, 1.15*inch, 1.15*inch, 1.15*inch, 1.15*inch, 1.2*inch]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header row styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Month name left
            ('ALIGN', (1, 1), (4, -1), 'RIGHT'),  # Amounts right
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Status center
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        return elements

    def _create_summary_table(self, transport_data: Dict[str, Any]) -> List:
        """Create fee summary table - full width, matching ReceiptGenerator format"""
        elements = []
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("ANNUAL FEE SUMMARY", self.styles['SectionHeader']))

        # Transport data
        total_transport_fee = transport_data.get('total_fee', 0)
        # If total_fee not provided, calculate from monthly_fee * 12
        if total_transport_fee == 0:
            monthly_fee = transport_data.get('monthly_fee', 0)
            total_transport_fee = monthly_fee * 12
        total_transport_paid = transport_data.get('total_paid', 0)
        total_transport_due = transport_data.get('balance', 0)

        # Build summary data - show "-" for tuition since this is transport-only
        data = [
            ['Description', 'Tuition Fee', 'Transport Fee'],
            ['Total Fee', '-', f'Rs. {total_transport_fee:,.0f}'],
            ['Total Paid', '-', f'Rs. {total_transport_paid:,.0f}'],
            ['Balance Due', '-', f'Rs. {total_transport_due:,.0f}'],
        ]

        # Full width table (7 inches)
        table = Table(data, colWidths=[2.4*inch, 2.3*inch, 2.3*inch])
        table.setStyle(TableStyle([
            # Header row styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # Bold and highlight the balance row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ]))
        elements.append(table)

        return elements
