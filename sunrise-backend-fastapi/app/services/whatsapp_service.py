"""
WhatsApp Service - Twilio Integration for Fee Payment Notifications
Sends automated WhatsApp messages to parents/guardians upon successful fee payment
using approved Twilio WhatsApp templates.

Template 1: school_fee_receipt_v3 (Detailed Receipt - 13 variables)
Template SID: HXb36a35dd343b592599705bb677bb7870
Variables (13):
    {{1}} - School name
    {{2}} - Receipt No
    {{3}} - Payment Date
    {{4}} - Student Name
    {{5}} - Class
    {{6}} - Father's name
    {{7}} - Tuition Fee
    {{8}} - Transport Fee (or "-" if not applicable)
    {{9}} - Total Paid
    {{10}} - Payment Mode
    {{11}} - Fee Month
    {{12}} - Receipt URL (PDF link - displayed as text)
    {{13}} - Media URL (PDF attachment for download)

Template 2: school_fee_text_receipt_v6 (Simple Text Receipt - 2 variables)
Template SID: HX130ac4be5a9fca2e380fa87a3d19d37b
Content: "Dear {{1}}, We have received your fee payment of ₹{{2}} - Sunrise National Public School"
Variables (2):
    {{1}} - Student/Parent name
    {{2}} - Amount paid
"""

import logging
import json
import traceback
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings

logger = logging.getLogger("sunrise_app")

# Twilio WhatsApp Error Code Reference
TWILIO_ERROR_CODES = {
    21211: "Invalid 'To' Phone Number",
    21408: "Permission to send SMS not enabled",
    21610: "Message blocked (recipient unsubscribed)",
    21614: "Invalid 'To' phone number for WhatsApp",
    63001: "Channel not found for WhatsApp number",
    63003: "Channel could not authenticate the request",
    63007: "Twilio could not find a Channel with the specified From address - Number not WhatsApp enabled",
    63016: "Message failed to send - recipient not on WhatsApp or invalid number",
    63024: "WhatsApp: Invalid Content Type",
    63025: "WhatsApp: Number not registered on WhatsApp",
}


class WhatsAppService:
    """
    Service class for sending WhatsApp notifications via Twilio

    Features:
    - Send fee payment confirmation messages
    - Send test messages for connectivity verification
    - Format phone numbers for WhatsApp
    - Handle Twilio API errors gracefully with detailed logging
    - Track message delivery status
    """

    def __init__(self):
        """Initialize Twilio client with credentials from settings"""
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
        self.template_sid = settings.TWILIO_WHATSAPP_TEMPLATE_SID
        self.client = None
        self._initialized = False

        # School name constant for template
        self.school_name = "Sunrise National Public School"

        # Log configuration (mask sensitive data)
        logger.info("WhatsApp Service Configuration:")
        logger.info(f"  Account SID: {self.account_sid[:10]}...{self.account_sid[-4:] if len(self.account_sid) > 14 else '***'}")
        logger.info(f"  Auth Token: {'*' * 20}")
        logger.info(f"  From Number: {self.from_number}")
        logger.info(f"  Template SID: {self.template_sid if self.template_sid else 'NOT CONFIGURED'}")

        # Initialize client if credentials are available
        if self.account_sid and self.auth_token and self.from_number:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self._initialized = True
                if self.template_sid:
                    logger.info("✅ WhatsApp Service initialized with template support")
                else:
                    logger.warning("⚠️ WhatsApp Service initialized but no template SID configured")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twilio client: {e}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                self._initialized = False
        else:
            missing = []
            if not self.account_sid:
                missing.append("TWILIO_ACCOUNT_SID")
            if not self.auth_token:
                missing.append("TWILIO_AUTH_TOKEN")
            if not self.from_number:
                missing.append("TWILIO_WHATSAPP_NUMBER")
            logger.warning(f"⚠️ WhatsApp Service not initialized - missing: {', '.join(missing)}")
    
    def is_available(self) -> bool:
        """Check if WhatsApp service is properly configured and available"""
        return self._initialized and self.client is not None
    
    def format_phone_number(self, phone: str) -> Optional[str]:
        """
        Format phone number for WhatsApp (E.164 format)
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Formatted phone number with whatsapp: prefix or None if invalid
        """
        if not phone:
            return None
        
        # Remove spaces, dashes, and other special characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Handle Indian phone numbers
        if len(cleaned) == 10:
            # Add India country code
            cleaned = '91' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('0'):
            # Remove leading 0 and add country code
            cleaned = '91' + cleaned[1:]
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            # Already has country code
            pass
        elif len(cleaned) == 13 and cleaned.startswith('091'):
            # Remove leading 0 from country code
            cleaned = cleaned[1:]
        else:
            # For international numbers or already formatted
            if not cleaned.startswith('+'):
                cleaned = '+' + cleaned
            else:
                cleaned = cleaned
        
        # Ensure it starts with + for E.164
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        return f"whatsapp:{cleaned}"
    
    def _get_month_name(self, month_num: int) -> str:
        """Convert month number to name"""
        months = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        return months.get(month_num, str(month_num))
    
    def generate_payment_message(
        self,
        student_name: str,
        receipt_number: str,
        receipt_date: str,
        class_name: str,
        father_name: str,
        tuition_fee: float,
        transport_fee: Optional[float],
        total_amount: float,
        payment_method: str,
        months_covered: str
    ) -> str:
        """
        Generate a plain text WhatsApp message for fee receipt.

        DEPRECATED: This method is kept for test messages and fallback purposes.
        Production notifications should use the approved Twilio template via
        send_fee_payment_notification() which uses content_sid and content_variables.

        Args:
            student_name: Full name of the student
            receipt_number: Receipt number (e.g., FEE-000048)
            receipt_date: Date of receipt (e.g., 10 Jan 2026)
            class_name: Student's class (e.g., 2, 5, 10)
            father_name: Father's name
            tuition_fee: Tuition fee amount
            transport_fee: Transport fee amount (None if not applicable)
            total_amount: Total paid amount
            payment_method: Method used for payment
            months_covered: Months covered by the payment

        Returns:
            Formatted WhatsApp message string
        """
        # Format transport fee display
        transport_fee_display = f"₹{transport_fee:,.0f}" if transport_fee else "—"

        # Build the plain text message (for sandbox/testing only)
        message_lines = [
            "🏫 Sunrise National Public School",
            "",
            "🧾 FEE RECEIPT",
            f"Receipt No: {receipt_number}",
            f"Payment Date: {receipt_date}",
            "",
            "👧 Student Details",
            f"Name: {student_name}",
            f"Class: {class_name}",
            f"Father: {father_name}",
            "",
            "💰 Fee Details",
            f"Tuition Fee     : ₹{tuition_fee:,.0f}",
            f"Transport Fee   : {transport_fee_display}",
            "———————————————",
            f"✅ Total Paid   : ₹{total_amount:,.0f}",
            "",
            f"💳 Payment Mode: {payment_method}",
            f"📆 Fee Month(s): {months_covered}",
            "",
            "———————————————",
            "This is a system-generated receipt.",
            "Thank you for your payment."
        ]

        return "\n".join(message_lines)

    def _log_twilio_error(self, e: TwilioRestException, context: str) -> Dict[str, Any]:
        """
        Log detailed Twilio error information

        Args:
            e: TwilioRestException instance
            context: Context string (e.g., "payment 47" or "test message")

        Returns:
            Dict with error details
        """
        error_explanation = TWILIO_ERROR_CODES.get(e.code, "Unknown error code")

        logger.error("=" * 60)
        logger.error(f"❌ TWILIO WHATSAPP ERROR - {context}")
        logger.error("=" * 60)
        logger.error(f"   Error Code: {e.code}")
        logger.error(f"   Error Message: {e.msg}")
        logger.error(f"   Error Explanation: {error_explanation}")
        logger.error(f"   HTTP Status: {e.status}")
        logger.error(f"   URI: {e.uri}")

        # Log additional details if available
        if hasattr(e, 'details') and e.details:
            logger.error(f"   Details: {e.details}")

        # Specific guidance based on error code
        if e.code == 63007:
            logger.error("   🔧 FIX: Your WhatsApp number is not registered with Twilio.")
            logger.error("      Go to Twilio Console → Messaging → Senders → WhatsApp senders")
            logger.error("      and add your number, OR use sandbox number +14155238886")
        elif e.code == 63016 or e.code == 63025:
            logger.error("   🔧 FIX: The recipient number is not registered on WhatsApp.")
        elif e.code == 21614:
            logger.error("   🔧 FIX: Invalid phone number format for WhatsApp.")

        logger.error("=" * 60)

        return {
            "code": e.code,
            "message": e.msg,
            "explanation": error_explanation,
            "http_status": e.status,
            "uri": e.uri
        }

    async def send_test_message(
        self,
        phone_number: str,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a simple test message to verify WhatsApp connectivity

        Args:
            phone_number: Recipient's phone number
            custom_message: Optional custom message (default: "MJ Testing twilio whatsapp service")

        Returns:
            Dict with success status, message_sid, and any errors
        """
        test_message = custom_message or "🧪 MJ Testing twilio whatsapp service\n\nThis is a test message from Sunrise School Management System.\n\nTimestamp: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "success": False,
            "message_sid": None,
            "status": "NOT_SENT",
            "error": None,
            "error_details": None,
            "phone_number": phone_number,
            "from_number": self.from_number,
            "message_preview": test_message[:100] + "..." if len(test_message) > 100 else test_message
        }

        logger.info("=" * 60)
        logger.info("🧪 WHATSAPP TEST MESSAGE")
        logger.info("=" * 60)
        logger.info(f"   Service Available: {self.is_available()}")
        logger.info(f"   From Number: {self.from_number}")
        logger.info(f"   To Number (raw): {phone_number}")

        # Check if service is available
        if not self.is_available():
            result["error"] = "WhatsApp service not configured"
            result["status"] = "SERVICE_UNAVAILABLE"
            logger.error("   ❌ Service not available - check Twilio credentials")
            return result

        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        if not formatted_phone:
            result["error"] = f"Invalid phone number: {phone_number}"
            result["status"] = "INVALID_PHONE"
            logger.error(f"   ❌ Invalid phone number format: {phone_number}")
            return result

        result["formatted_phone"] = formatted_phone
        from_whatsapp = f"whatsapp:{self.from_number}"

        logger.info(f"   To Number (formatted): {formatted_phone}")
        logger.info(f"   From WhatsApp: {from_whatsapp}")
        logger.info(f"   Message Length: {len(test_message)} chars")
        logger.info("-" * 60)

        try:
            logger.info("   📤 Sending message via Twilio...")

            message = self.client.messages.create(
                body=test_message,
                from_=from_whatsapp,
                to=formatted_phone
            )

            result["success"] = True
            result["message_sid"] = message.sid
            result["status"] = "SENT"

            logger.info("   ✅ MESSAGE SENT SUCCESSFULLY!")
            logger.info(f"   Message SID: {message.sid}")
            logger.info(f"   Status: {message.status}")
            logger.info("=" * 60)

        except TwilioRestException as e:
            error_details = self._log_twilio_error(e, "test message")
            result["error"] = f"Twilio error ({e.code}): {e.msg}"
            result["error_details"] = error_details
            result["status"] = "TWILIO_ERROR"

        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            result["status"] = "ERROR"
            logger.error("=" * 60)
            logger.error(f"❌ UNEXPECTED ERROR sending test message")
            logger.error(f"   Error Type: {type(e).__name__}")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            logger.error("=" * 60)

        return result

    async def send_fee_payment_notification(
        self,
        phone_number: str,
        student_name: str,
        receipt_number: str,
        receipt_date: str,
        class_name: str,
        father_name: str,
        tuition_fee: float,
        transport_fee: Optional[float],
        total_amount: float,
        payment_method: str,
        months_covered: str,
        payment_id: Optional[int] = None,
        receipt_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp notification for fee receipt using approved Twilio template.

        Uses template: school_fee_receipt_v3 (SID: HXb36a35dd343b592599705bb677bb7870)

        Template Variables (13):
            {{1}} - School name (Sunrise National Public School)
            {{2}} - Receipt No (e.g., FEE-000052)
            {{3}} - Payment Date (e.g., 10 Jan 2026)
            {{4}} - Student Name
            {{5}} - Class
            {{6}} - Father's name
            {{7}} - Tuition Fee
            {{8}} - Transport Fee (or "-" if not applicable)
            {{9}} - Total Paid
            {{10}} - Payment Mode
            {{11}} - Fee Month
            {{12}} - Receipt URL (PDF link - displayed as text)
            {{13}} - Media URL (PDF attachment for download)

        Args:
            phone_number: Recipient's phone number
            student_name: Student's full name
            receipt_number: Receipt number (e.g., FEE-000048)
            receipt_date: Date of receipt
            class_name: Student's class (e.g., 2, 5, 10)
            father_name: Father's name
            tuition_fee: Tuition fee amount
            transport_fee: Transport fee amount (None if not applicable)
            total_amount: Total paid amount
            payment_method: Payment method used
            months_covered: Months covered by payment
            payment_id: Payment record ID for logging
            receipt_url: Cloudinary URL for the PDF receipt

        Returns:
            Dict with success status, message_sid, and any errors
        """
        result = {
            "success": False,
            "message_sid": None,
            "status": "NOT_SENT",
            "error": None,
            "error_details": None,
            "phone_number": phone_number
        }

        logger.info("-" * 40)
        logger.info(f"📱 WhatsApp Template Notification - Payment #{payment_id}")
        logger.info(f"   To: {phone_number}")
        logger.info(f"   Student: {student_name}")
        logger.info(f"   Total Amount: ₹{total_amount}")
        logger.info(f"   Receipt URL: {receipt_url if receipt_url else 'Not available'}")
        logger.info(f"   Template SID: {self.template_sid}")

        # Check if service is available
        if not self.is_available():
            result["error"] = "WhatsApp service not configured"
            result["status"] = "SERVICE_UNAVAILABLE"
            logger.warning("   ⚠️ WhatsApp service unavailable")
            return result

        # Check if template SID is configured
        if not self.template_sid:
            result["error"] = "WhatsApp template SID not configured"
            result["status"] = "TEMPLATE_NOT_CONFIGURED"
            logger.warning("   ⚠️ Template SID not configured - set TWILIO_WHATSAPP_TEMPLATE_SID")
            return result

        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        if not formatted_phone:
            result["error"] = f"Invalid phone number: {phone_number}"
            result["status"] = "INVALID_PHONE"
            logger.warning(f"   ⚠️ Invalid phone number: {phone_number}")
            return result

        from_whatsapp = f"whatsapp:{self.from_number}"

        # Format transport fee display (use "-" if not applicable)
        transport_fee_display = f"{int(transport_fee)}" if transport_fee else "-"

        # Format tuition fee without decimal if whole number
        tuition_fee_display = f"{int(tuition_fee)}" if tuition_fee == int(tuition_fee) else f"{tuition_fee:.2f}"

        # Format total amount without decimal if whole number
        total_amount_display = f"{int(total_amount)}" if total_amount == int(total_amount) else f"{total_amount:.2f}"

        # Prepare template variables as JSON string
        # Template: school_fee_receipt_v3 has 13 variables
        content_variables = json.dumps({
            "1": self.school_name,           # {{1}} - School name
            "2": receipt_number,              # {{2}} - Receipt No
            "3": receipt_date,                # {{3}} - Payment Date
            "4": student_name,                # {{4}} - Student Name
            "5": str(class_name),             # {{5}} - Class
            "6": father_name,                 # {{6}} - Father's name
            "7": tuition_fee_display,         # {{7}} - Tuition Fee
            "8": transport_fee_display,       # {{8}} - Transport Fee
            "9": total_amount_display,        # {{9}} - Total Paid
            "10": payment_method,             # {{10}} - Payment Mode
            "11": months_covered,             # {{11}} - Fee Month
            "12": receipt_url or "",          # {{12}} - Receipt URL (text link)
            "13": receipt_url or ""           # {{13}} - Media URL (PDF attachment)
        })

        logger.info(f"   From: {from_whatsapp}")
        logger.info(f"   To (formatted): {formatted_phone}")
        logger.info(f"   Content Variables: {content_variables}")

        try:
            # Send WhatsApp message using approved template
            message = self.client.messages.create(
                from_=from_whatsapp,
                to=formatted_phone,
                content_sid=self.template_sid,
                content_variables=content_variables
            )

            result["success"] = True
            result["message_sid"] = message.sid
            result["status"] = "SENT"

            logger.info(f"   ✅ Template message sent! SID: {message.sid}")

        except TwilioRestException as e:
            error_details = self._log_twilio_error(e, f"payment {payment_id}")
            result["error"] = f"Twilio error ({e.code}): {e.msg}"
            result["error_details"] = error_details
            result["status"] = "TWILIO_ERROR"

        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            result["status"] = "ERROR"
            logger.error(f"   ❌ Unexpected error: {str(e)}")
            logger.error(f"   Traceback: {traceback.format_exc()}")

        logger.info("-" * 40)
        return result

    async def send_fee_text_receipt(
        self,
        phone_number: str,
        student_name: str,
        amount: float,
        payment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send simple WhatsApp text receipt notification using approved template.

        Uses template: school_fee_text_receipt_v6
        Template SID: HX130ac4be5a9fca2e380fa87a3d19d37b
        Content: "Dear {{1}}, We have received your fee payment of ₹{{2}}
                  - Sunrise National Public School"

        Variables (2):
            {{1}} - Student name
            {{2}} - Amount paid

        Args:
            phone_number: Recipient's phone number (student/parent)
            student_name: Student's name
            amount: Payment amount
            payment_id: Payment record ID for logging

        Returns:
            Dict with success status, message_sid, and any errors
        """
        # Get template SID from config (school_fee_text_receipt_v6)
        text_receipt_template_sid = settings.TWILIO_WHATSAPP_TEXT_RECEIPT_SID

        result = {
            "success": False,
            "message_sid": None,
            "status": "NOT_SENT",
            "error": None,
            "error_details": None,
            "phone_number": phone_number
        }

        logger.info("-" * 40)
        logger.info(f"📱 WhatsApp Text Receipt - Payment #{payment_id}")
        logger.info(f"   To: {phone_number}")
        logger.info(f"   Student: {student_name}")
        logger.info(f"   Amount: ₹{amount}")
        logger.info(f"   Template SID: {text_receipt_template_sid}")

        # Check if service is available
        if not self.is_available():
            result["error"] = "WhatsApp service not configured"
            result["status"] = "SERVICE_UNAVAILABLE"
            logger.warning("   ⚠️ WhatsApp service unavailable")
            return result

        # Check if template SID is configured
        if not text_receipt_template_sid:
            result["error"] = "Text receipt template SID not configured"
            result["status"] = "TEMPLATE_NOT_CONFIGURED"
            logger.warning("   ⚠️ TWILIO_WHATSAPP_TEXT_RECEIPT_SID not set in environment")
            return result

        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        if not formatted_phone:
            result["error"] = f"Invalid phone number: {phone_number}"
            result["status"] = "INVALID_PHONE"
            logger.warning(f"   ⚠️ Invalid phone number: {phone_number}")
            return result

        from_whatsapp = f"whatsapp:{self.from_number}"

        # Format amount (remove decimals if whole number)
        amount_display = f"{int(amount)}" if amount == int(amount) else f"{amount:.2f}"

        # Prepare template variables as JSON string
        content_variables = json.dumps({
            "1": student_name,      # {{1}} - Student name
            "2": amount_display     # {{2}} - Amount paid
        })

        logger.info(f"   From: {from_whatsapp}")
        logger.info(f"   To (formatted): {formatted_phone}")
        logger.info(f"   Content Variables: {content_variables}")

        try:
            # Send WhatsApp message using approved template
            message = self.client.messages.create(
                from_=from_whatsapp,
                to=formatted_phone,
                content_sid=text_receipt_template_sid,
                content_variables=content_variables
            )

            result["success"] = True
            result["message_sid"] = message.sid
            result["status"] = "SENT"

            logger.info(f"   ✅ Text receipt sent! SID: {message.sid}")

        except TwilioRestException as e:
            error_details = self._log_twilio_error(e, f"payment {payment_id}")
            result["error"] = f"Twilio error ({e.code}): {e.msg}"
            result["error_details"] = error_details
            result["status"] = "TWILIO_ERROR"

        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            result["status"] = "ERROR"
            logger.error(f"   ❌ Unexpected error: {str(e)}")
            logger.error(f"   Traceback: {traceback.format_exc()}")

        logger.info("-" * 40)
        return result

    def validate_phone_number(self, phone: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate if a phone number is valid for WhatsApp messaging

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, cleaned_phone_number)
        """
        if not phone:
            return False, None

        cleaned = phone.strip()
        if len(cleaned) >= 10:
            return True, cleaned

        return False, None


# Create singleton instance
whatsapp_service = WhatsAppService()

