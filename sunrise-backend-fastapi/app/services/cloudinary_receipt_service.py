"""
Cloudinary Receipt Upload Service
Handles uploading receipt PDFs to Cloudinary
"""

import io
import logging
from typing import Tuple, Dict, Any, Optional
from datetime import datetime

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status

from app.core.cloudinary_config import configure_cloudinary


logger = logging.getLogger(__name__)


class CloudinaryReceiptService:
    """Service for uploading receipt PDFs to Cloudinary"""

    RECEIPT_FOLDER = "receipts/fees"
    MAX_FILE_SIZE_MB = 10  # 10MB max for PDFs

    def __init__(self):
        """Initialize the Cloudinary receipt service"""
        # Ensure Cloudinary is configured
        configure_cloudinary()

    def upload_receipt(
        self,
        pdf_buffer: io.BytesIO,
        payment_id: int,
        receipt_number: str
    ) -> Tuple[str, str]:
        """
        Upload receipt PDF to Cloudinary

        Args:
            pdf_buffer: BytesIO buffer containing the PDF
            payment_id: Payment ID for unique identification
            receipt_number: Receipt number (e.g., FEE-000123)

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

            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"receipt_{payment_id}_{timestamp}"

            logger.info(f"Uploading receipt PDF to Cloudinary: {filename}")

            # Upload to Cloudinary
            # Note: flags="attachment:false" allows browser to display PDF inline instead of forcing download
            cloudinary_response = cloudinary.uploader.upload(
                pdf_buffer,
                folder=self.RECEIPT_FOLDER,
                public_id=filename,
                resource_type="raw",  # Use 'raw' for PDFs
                overwrite=False,  # Don't overwrite existing files
                tags=[f"payment_{payment_id}", receipt_number, "fee_receipt"],
                flags="attachment:false"  # Allow inline display in browser
            )

            cloudinary_url = cloudinary_response.get('secure_url')
            cloudinary_public_id = cloudinary_response.get('public_id')

            logger.info(f"Receipt uploaded successfully: {cloudinary_url}")

            return cloudinary_url, cloudinary_public_id

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to upload receipt to Cloudinary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload receipt to Cloudinary: {str(e)}"
            )

    def delete_receipt(self, cloudinary_public_id: str) -> bool:
        """
        Delete receipt PDF from Cloudinary

        Args:
            cloudinary_public_id: Cloudinary public ID of the receipt

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if not cloudinary_public_id:
                logger.warning("No cloudinary_public_id provided for deletion")
                return False

            logger.info(f"Deleting receipt from Cloudinary: {cloudinary_public_id}")

            # Delete from Cloudinary
            result = cloudinary.uploader.destroy(
                cloudinary_public_id,
                resource_type="raw"
            )

            if result.get('result') == 'ok':
                logger.info(f"Receipt deleted successfully: {cloudinary_public_id}")
                return True
            else:
                logger.warning(f"Failed to delete receipt: {result}")
                return False

        except Exception as e:
            logger.error(f"Error deleting receipt from Cloudinary: {str(e)}")
            return False

    def get_receipt_url(self, cloudinary_public_id: str) -> Optional[str]:
        """
        Get the secure URL for a receipt from Cloudinary

        Args:
            cloudinary_public_id: Cloudinary public ID of the receipt

        Returns:
            Secure URL of the receipt, or None if not found
        """
        try:
            if not cloudinary_public_id:
                return None

            # Generate secure URL
            url = cloudinary.CloudinaryImage(cloudinary_public_id).build_url(
                resource_type="raw",
                secure=True
            )

            return url

        except Exception as e:
            logger.error(f"Error generating receipt URL: {str(e)}")
            return None

