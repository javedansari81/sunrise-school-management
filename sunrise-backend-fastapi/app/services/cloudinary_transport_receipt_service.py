"""
Cloudinary Transport Receipt Upload Service
Handles uploading transport receipt PDFs to Cloudinary
"""

import io
import logging
from typing import Tuple
from datetime import datetime

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status

from app.core.cloudinary_config import configure_cloudinary


logger = logging.getLogger(__name__)


class CloudinaryTransportReceiptService:
    """Service for uploading transport receipt PDFs to Cloudinary"""

    RECEIPT_FOLDER = "receipts/transport"
    MAX_FILE_SIZE_MB = 10  # 10MB max for PDFs

    def __init__(self):
        """Initialize the Cloudinary transport receipt service"""
        # Ensure Cloudinary is configured
        configure_cloudinary()

    def upload_receipt(
        self,
        pdf_buffer: io.BytesIO,
        payment_id: int,
        receipt_number: str
    ) -> Tuple[str, str]:
        """
        Upload transport receipt PDF to Cloudinary

        Args:
            pdf_buffer: BytesIO buffer containing the PDF
            payment_id: Payment ID for unique identification
            receipt_number: Receipt number (e.g., TRANSPORT-000123)

        Returns:
            Tuple of (cloudinary_url, cloudinary_public_id)

        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate file size
            pdf_buffer.seek(0, 2)  # Seek to end
            file_size_mb = pdf_buffer.tell() / (1024 * 1024)
            pdf_buffer.seek(0)  # Reset to beginning

            if file_size_mb > self.MAX_FILE_SIZE_MB:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Receipt PDF size ({file_size_mb:.2f}MB) exceeds maximum allowed size of {self.MAX_FILE_SIZE_MB}MB"
                )

            # Generate unique filename (without .pdf extension as format parameter handles it)
            # IMPORTANT: The format="pdf" parameter ensures:
            # 1. Cloudinary serves proper Content-Type: application/pdf header
            # 2. WhatsApp/Twilio can validate and download the file correctly
            # 3. The URL ends with .pdf extension automatically
            # 4. The URL is publicly accessible with proper MIME type
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"receipt_{payment_id}_{timestamp}"

            logger.info(f"Uploading transport receipt PDF to Cloudinary: {filename}")

            # Upload to Cloudinary
            # Note: flags="attachment:false" allows browser to display PDF inline
            # format="pdf" explicitly tells Cloudinary this is a PDF file and adds .pdf extension
            cloudinary_response = cloudinary.uploader.upload(
                pdf_buffer,
                folder=self.RECEIPT_FOLDER,
                public_id=filename,
                resource_type="raw",  # Use 'raw' for PDFs and documents
                format="pdf",  # Adds .pdf extension and sets proper Content-Type header
                overwrite=False,  # Don't overwrite existing files
                tags=[f"transport_payment_{payment_id}", receipt_number, "transport_receipt"],
                flags="attachment:false"  # Allow inline display in browser
                # Note: access_mode defaults to "public", no need to specify
            )

            cloudinary_url = cloudinary_response.get('secure_url')
            cloudinary_public_id = cloudinary_response.get('public_id')

            logger.info(f"Transport receipt uploaded successfully: {cloudinary_url}")

            return cloudinary_url, cloudinary_public_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload transport receipt to Cloudinary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload transport receipt: {str(e)}"
            )

    def delete_receipt(self, cloudinary_public_id: str) -> bool:
        """
        Delete transport receipt PDF from Cloudinary

        Args:
            cloudinary_public_id: Cloudinary public ID of the receipt

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if not cloudinary_public_id:
                logger.warning("No cloudinary_public_id provided for deletion")
                return False

            logger.info(f"Deleting transport receipt from Cloudinary: {cloudinary_public_id}")

            # Delete from Cloudinary
            result = cloudinary.uploader.destroy(
                cloudinary_public_id,
                resource_type="raw"
            )

            if result.get('result') == 'ok':
                logger.info(f"Transport receipt deleted successfully: {cloudinary_public_id}")
                return True
            else:
                logger.warning(f"Failed to delete transport receipt: {result}")
                return False

        except Exception as e:
            logger.error(f"Error deleting transport receipt from Cloudinary: {str(e)}")
            return False

