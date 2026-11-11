"""
WhatsApp Service - Twilio integration for fee receipts.
Sends the receipt PDF to parents/guardians after a payment, using an approved
Twilio media template. The template SID is per school (school setting
whatsapp.media_receipt_template_sid, see app/modules/fees/receipts.py), with
TWILIO_WHATSAPP_MEDIA_RECEIPT_SID as the fallback.

Media template: school_fee_media_template_v4 (Media Receipt with PDF - 3 variables)
Template SID: HX15Ib79a0cfdd1dc1fd6G23ec5b50a71c
Content:
    Updated template with improved language formatting
    {{3}} - Media URL (PDF attachment)
Variables (3):
    {{1}} - Student/Parent name
    {{2}} - Amount paid
    {{3}} - Media URL (PDF attachment for download)
"""

import logging
import json
import traceback
from typing import Optional, Dict, Any, Tuple
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
        self.client = None
        self._initialized = False

        # Log configuration (mask sensitive data)
        logger.info("WhatsApp Service Configuration:")
        logger.info(f"  Account SID: {self.account_sid[:10]}...{self.account_sid[-4:] if len(self.account_sid) > 14 else '***'}")
        logger.info(f"  Auth Token: {'*' * 20}")
        logger.info(f"  From Number: {self.from_number}")

        # Initialize client if credentials are available
        if self.account_sid and self.auth_token and self.from_number:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self._initialized = True
                logger.info("✅ WhatsApp Service initialized")
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

    async def send_fee_media_receipt(
        self,
        phone_number: str,
        student_name: str,
        amount: float,
        receipt_url: Optional[str] = None,
        payment_id: Optional[int] = None,
        template_sid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp media receipt notification with PDF attachment.
        `template_sid` overrides TWILIO_WHATSAPP_MEDIA_RECEIPT_SID (per-school template).

        Uses template: school_fee_media_template_v4
        Template SID: HX15Ib79a0cfdd1dc1fd6G23ec5b50a71c
        Content:
            Updated template with improved language formatting
            {{3}} - Media URL (PDF attachment)

        Variables (3):
            {{1}} - Student/Parent name
            {{2}} - Amount paid
            {{3}} - Media URL (PDF attachment for download)

        Args:
            phone_number: Recipient's phone number (student/parent)
            student_name: Student's name
            amount: Payment amount
            receipt_url: Cloudinary URL for the PDF receipt
            payment_id: Payment record ID for logging

        Returns:
            Dict with success status, message_sid, and any errors
        """
        # Get template SID from config (school_fee_media_template_v4)
        media_receipt_template_sid = template_sid or settings.TWILIO_WHATSAPP_MEDIA_RECEIPT_SID

        result = {
            "success": False,
            "message_sid": None,
            "status": "NOT_SENT",
            "error": None,
            "error_details": None,
            "phone_number": phone_number
        }

        logger.info("-" * 40)
        logger.info(f"📱 WhatsApp Media Receipt - Payment #{payment_id}")
        logger.info(f"   To: {phone_number}")
        logger.info(f"   Student: {student_name}")
        logger.info(f"   Amount: ₹{amount}")
        logger.info(f"   Receipt URL: {receipt_url or 'Not provided'}")
        logger.info(f"   Template SID: {media_receipt_template_sid}")

        # Check if service is available
        if not self.is_available():
            result["error"] = "WhatsApp service not configured"
            result["status"] = "SERVICE_UNAVAILABLE"
            logger.warning("   ⚠️ WhatsApp service unavailable")
            return result

        # Check if template SID is configured
        if not media_receipt_template_sid:
            result["error"] = "Media receipt template SID not configured"
            result["status"] = "TEMPLATE_NOT_CONFIGURED"
            logger.warning("   ⚠️ TWILIO_WHATSAPP_MEDIA_RECEIPT_SID not set in environment")
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

        # Prepare template variables as JSON string (3 variables for media template v4)
        content_variables = json.dumps({
            "1": student_name,           # {{1}} - Student/Parent name
            "2": amount_display,         # {{2}} - Amount paid
            "3": receipt_url or ""       # {{3}} - Media URL (PDF attachment)
        })

        logger.info(f"   From: {from_whatsapp}")
        logger.info(f"   To (formatted): {formatted_phone}")
        logger.info(f"   Content Variables: {content_variables}")

        try:
            # Send WhatsApp message using approved media template
            message = self.client.messages.create(
                from_=from_whatsapp,
                to=formatted_phone,
                content_sid=media_receipt_template_sid,
                content_variables=content_variables
            )

            result["success"] = True
            result["message_sid"] = message.sid
            result["status"] = "SENT"

            logger.info(f"   ✅ Media receipt sent! SID: {message.sid}")

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

