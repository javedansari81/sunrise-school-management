"""
Alert Service - Business logic for creating alerts
Provides helper methods for different alert types with pre-built messages
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.crud.crud_alert import alert_crud
from app.models.alert import Alert


class AlertService:
    """
    Service class for alert generation with pre-defined alert types
    
    Alert Type IDs (matching database values in D800_alert_types.sql):
    - Leave Management: 1-9
    - Fee Management: 10-19
    - Transport: 20-29
    - Student: 30-39
    - Attendance: 40-49
    - Inventory: 50-59
    - System: 100+
    """

    # Alert Type ID constants
    class AlertTypes:
        # Leave Management
        LEAVE_REQUEST_CREATED = 1
        LEAVE_REQUEST_APPROVED = 2
        LEAVE_REQUEST_REJECTED = 3

        # Fee Management
        FEE_PAYMENT_RECEIVED = 10
        FEE_PAYMENT_REVERSED = 11
        FEE_OVERDUE = 12

        # Transport Fee Management
        TRANSPORT_PAYMENT_RECEIVED = 20
        TRANSPORT_PAYMENT_REVERSED = 21

        # Student Management
        STUDENT_ENROLLED = 30
        STUDENT_PROMOTED = 31

        # Attendance
        ATTENDANCE_MARKED = 40
        ATTENDANCE_LOW = 41

        # Inventory
        INVENTORY_LOW_STOCK = 50
        INVENTORY_PURCHASE_CREATED = 51
        INVENTORY_STOCK_PROCURED = 52

        # Expense Management
        EXPENSE_CREATED = 60
        EXPENSE_APPROVED = 61
        EXPENSE_REJECTED = 62
        EXPENSE_PAID = 63
        EXPENSE_UPDATED = 64

        # System
        SYSTEM_ANNOUNCEMENT = 100

    @staticmethod
    async def create_leave_request_alert(
        db: AsyncSession,
        *,
        leave_request_id: int,
        applicant_name: str,
        applicant_type: str,  # 'student' or 'teacher'
        leave_type: str,
        start_date: str,
        end_date: str,
        total_days: int,
        actor_user_id: int,
        class_info: Optional[str] = None
    ) -> Alert:
        """Create alert when a leave request is submitted"""
        title = f"New Leave Request: {applicant_name}"
        
        if applicant_type.lower() == 'student':
            class_text = f" ({class_info})" if class_info else ""
            message = f"{applicant_name}{class_text} has submitted a {leave_type} leave request for {total_days} day(s) from {start_date} to {end_date}."
        else:
            message = f"Teacher {applicant_name} has submitted a {leave_type} leave request for {total_days} day(s) from {start_date} to {end_date}."

        return await alert_crud.create_alert(
            db,
            alert_type_id=AlertService.AlertTypes.LEAVE_REQUEST_CREATED,
            title=title,
            message=message,
            entity_type="LEAVE_REQUEST",
            entity_id=leave_request_id,
            entity_display_name=applicant_name,
            actor_user_id=actor_user_id,
            actor_type=applicant_type.upper(),
            actor_name=applicant_name,
            target_role="ADMIN",  # Admin sees leave requests
            alert_metadata={
                "leave_type": leave_type,
                "start_date": start_date,
                "end_date": end_date,
                "total_days": total_days,
                "applicant_type": applicant_type,
                "class_info": class_info
            },
            priority_level=2,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )

    @staticmethod
    async def create_fee_payment_alert(
        db: AsyncSession,
        *,
        payment_id: int,
        student_id: int,
        student_name: str,
        class_name: str,
        amount: float,
        payment_method: str,
        fee_type: str,  # 'TUITION' or 'TRANSPORT'
        months_paid: Optional[str] = None,
        actor_user_id: int,
        actor_name: str
    ) -> Alert:
        """Create alert when a fee payment is processed"""
        alert_type_id = (
            AlertService.AlertTypes.FEE_PAYMENT_RECEIVED 
            if fee_type == 'TUITION' 
            else AlertService.AlertTypes.TRANSPORT_PAYMENT_RECEIVED
        )
        
        fee_label = "Tuition Fee" if fee_type == 'TUITION' else "Transport Fee"
        title = f"{fee_label} Payment: ₹{amount:,.2f}"
        
        month_info = f" for {months_paid}" if months_paid else ""
        message = f"{actor_name} processed {fee_label} payment of ₹{amount:,.2f} for {student_name} ({class_name}){month_info} via {payment_method}."

        return await alert_crud.create_alert(
            db,
            alert_type_id=alert_type_id,
            title=title,
            message=message,
            entity_type="FEE_PAYMENT" if fee_type == 'TUITION' else "TRANSPORT_PAYMENT",
            entity_id=payment_id,
            entity_display_name=student_name,
            actor_user_id=actor_user_id,
            actor_type="ADMIN",
            actor_name=actor_name,
            target_role="ADMIN",  # Visible to all admins
            alert_metadata={
                "student_id": student_id,
                "student_name": student_name,
                "class_name": class_name,
                "amount": amount,
                "payment_method": payment_method,
                "fee_type": fee_type,
                "months_paid": months_paid
            },
            priority_level=2,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

    @staticmethod
    async def create_payment_reversal_alert(
        db: AsyncSession,
        *,
        reversal_payment_id: int,
        original_payment_id: int,
        student_name: str,
        class_name: str,
        amount: float,
        reversal_reason: str,
        fee_type: str,  # 'TUITION' or 'TRANSPORT'
        actor_user_id: int,
        actor_name: str
    ) -> Alert:
        """Create alert when a payment is reversed"""
        alert_type_id = (
            AlertService.AlertTypes.FEE_PAYMENT_REVERSED
            if fee_type == 'TUITION'
            else AlertService.AlertTypes.TRANSPORT_PAYMENT_REVERSED
        )

        fee_label = "Tuition Fee" if fee_type == 'TUITION' else "Transport Fee"
        title = f"{fee_label} Reversed: ₹{amount:,.2f}"
        message = f"{actor_name} reversed {fee_label} payment of ₹{amount:,.2f} for {student_name} ({class_name}). Reason: {reversal_reason}"

        return await alert_crud.create_alert(
            db,
            alert_type_id=alert_type_id,
            title=title,
            message=message,
            entity_type="FEE_PAYMENT" if fee_type == 'TUITION' else "TRANSPORT_PAYMENT",
            entity_id=reversal_payment_id,
            entity_display_name=student_name,
            actor_user_id=actor_user_id,
            actor_type="ADMIN",
            actor_name=actor_name,
            target_role="ADMIN",
            alert_metadata={
                "original_payment_id": original_payment_id,
                "student_name": student_name,
                "class_name": class_name,
                "amount": amount,
                "reversal_reason": reversal_reason,
                "fee_type": fee_type
            },
            priority_level=3,  # Higher priority for reversals
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

    @staticmethod
    async def create_leave_status_alert(
        db: AsyncSession,
        *,
        leave_request_id: int,
        applicant_name: str,
        applicant_type: str,
        applicant_user_id: Optional[int] = None,  # User ID of the applicant to receive the alert
        leave_type: str,
        status: str,  # 'APPROVED' or 'REJECTED'
        start_date: str,
        end_date: str,
        reviewer_name: str,
        reviewer_user_id: int,
        comments: Optional[str] = None
    ) -> Alert:
        """Create alert when a leave request is approved or rejected"""
        alert_type_id = (
            AlertService.AlertTypes.LEAVE_REQUEST_APPROVED
            if status == 'APPROVED'
            else AlertService.AlertTypes.LEAVE_REQUEST_REJECTED
        )

        status_text = "approved" if status == 'APPROVED' else "rejected"
        title = f"Leave Request {status_text.title()}"
        message = f"Your {leave_type} leave request ({start_date} to {end_date}) has been {status_text} by {reviewer_name}."

        if comments:
            message += f" Comments: {comments}"

        return await alert_crud.create_alert(
            db,
            alert_type_id=alert_type_id,
            title=title,
            message=message,
            entity_type="LEAVE_REQUEST",
            entity_id=leave_request_id,
            entity_display_name=applicant_name,
            actor_user_id=reviewer_user_id,
            actor_type="ADMIN",
            actor_name=reviewer_name,
            target_role=applicant_type.upper(),  # Notify the applicant's role
            target_user_id=applicant_user_id,  # Specific user to receive the alert
            alert_metadata={
                "leave_type": leave_type,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "reviewer_name": reviewer_name,
                "comments": comments
            },
            priority_level=2 if status == 'APPROVED' else 3,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )

    @staticmethod
    async def create_inventory_purchase_alert(
        db: AsyncSession,
        *,
        purchase_id: int,
        student_id: int,
        student_name: str,
        class_name: str,
        total_amount: float,
        payment_method: str,
        items_summary: str,  # e.g., "2x Shirt (Size 32), 1x Trouser (Size 34)"
        actor_user_id: int,
        actor_name: str
    ) -> Alert:
        """Create alert when an inventory purchase is made"""
        title = f"Inventory Purchase: ₹{total_amount:,.2f}"
        message = f"{actor_name} processed inventory purchase of ₹{total_amount:,.2f} for {student_name} ({class_name}). Items: {items_summary}. Payment via {payment_method}."

        return await alert_crud.create_alert(
            db,
            alert_type_id=AlertService.AlertTypes.INVENTORY_PURCHASE_CREATED,
            title=title,
            message=message,
            entity_type="INVENTORY_PURCHASE",
            entity_id=purchase_id,
            entity_display_name=student_name,
            actor_user_id=actor_user_id,
            actor_type="ADMIN",
            actor_name=actor_name,
            target_role="ADMIN",  # Visible to all admins
            alert_metadata={
                "student_id": student_id,
                "student_name": student_name,
                "class_name": class_name,
                "total_amount": total_amount,
                "payment_method": payment_method,
                "items_summary": items_summary
            },
            priority_level=2,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

    @staticmethod
    async def create_inventory_stock_procurement_alert(
        db: AsyncSession,
        *,
        procurement_id: int,
        total_amount: float,
        vendor_name: Optional[str],
        items_summary: str,  # e.g., "50x Shirt (Size 32), 30x Trouser (Size 34)"
        actor_user_id: int,
        actor_name: str
    ) -> Alert:
        """Create alert when inventory stock is procured"""
        vendor_info = f" from {vendor_name}" if vendor_name else ""
        title = f"Stock Procured: ₹{total_amount:,.2f}"
        message = f"{actor_name} procured inventory stock worth ₹{total_amount:,.2f}{vendor_info}. Items: {items_summary}."

        return await alert_crud.create_alert(
            db,
            alert_type_id=AlertService.AlertTypes.INVENTORY_STOCK_PROCURED,
            title=title,
            message=message,
            entity_type="INVENTORY_PROCUREMENT",
            entity_id=procurement_id,
            entity_display_name=f"Procurement #{procurement_id}",
            actor_user_id=actor_user_id,
            actor_type="ADMIN",
            actor_name=actor_name,
            target_role="ADMIN",  # Visible to all admins
            alert_metadata={
                "total_amount": total_amount,
                "vendor_name": vendor_name,
                "items_summary": items_summary
            },
            priority_level=2,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

    @staticmethod
    async def create_expense_alert(
        db: AsyncSession,
        *,
        expense_id: int,
        expense_category: str,
        description: str,
        amount: float,
        vendor_name: Optional[str],
        requester_name: str,
        requester_user_id: int,
        priority: str = "Medium"
    ) -> Alert:
        """
        Create alert when a new expense is created.
        Notification is sent to SUPER_ADMIN users only since they are the ones
        who can approve/reject expenses. ADMIN users create expenses but cannot approve them.
        """
        vendor_info = f" to {vendor_name}" if vendor_name else ""
        title = f"Expense Pending Approval: ₹{amount:,.2f}"
        message = f"{requester_name} created a {priority.lower()} priority expense of ₹{amount:,.2f} for {expense_category}{vendor_info}. This expense requires SUPER_ADMIN approval. Description: {description}"

        return await alert_crud.create_alert(
            db,
            alert_type_id=AlertService.AlertTypes.EXPENSE_CREATED,
            title=title,
            message=message,
            entity_type="EXPENSE",
            entity_id=expense_id,
            entity_display_name=description[:50],  # Truncate long descriptions
            actor_user_id=requester_user_id,
            actor_type="ADMIN",
            actor_name=requester_name,
            target_role="SUPER_ADMIN",  # Only SUPER_ADMIN can approve expenses
            alert_metadata={
                "expense_category": expense_category,
                "description": description,
                "amount": amount,
                "vendor_name": vendor_name,
                "priority": priority,
                "requires_approval": True
            },
            priority_level=3 if priority in ['High', 'Urgent'] else 2,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

    @staticmethod
    async def create_expense_update_alert(
        db: AsyncSession,
        *,
        expense_id: int,
        expense_category: str,
        description: str,
        amount: float,
        vendor_name: Optional[str],
        updater_name: str,
        updater_user_id: int,
        priority: str = "Medium"
    ) -> Alert:
        """
        Create alert when an expense is updated.
        Notification is sent to SUPER_ADMIN users only since they are the ones
        who can approve/reject expenses. This keeps them informed of changes to pending expenses.
        """
        vendor_info = f" to {vendor_name}" if vendor_name else ""
        title = f"Expense Updated: ₹{amount:,.2f}"
        message = f"{updater_name} updated a {priority.lower()} priority expense of ₹{amount:,.2f} for {expense_category}{vendor_info}. This expense is pending SUPER_ADMIN approval. Description: {description}"

        return await alert_crud.create_alert(
            db,
            alert_type_id=AlertService.AlertTypes.EXPENSE_UPDATED,
            title=title,
            message=message,
            entity_type="EXPENSE",
            entity_id=expense_id,
            entity_display_name=description[:50],  # Truncate long descriptions
            actor_user_id=updater_user_id,
            actor_type="ADMIN",
            actor_name=updater_name,
            target_role="SUPER_ADMIN",  # Only SUPER_ADMIN can approve expenses
            alert_metadata={
                "expense_category": expense_category,
                "description": description,
                "amount": amount,
                "vendor_name": vendor_name,
                "priority": priority,
                "requires_approval": True
            },
            priority_level=3 if priority in ['High', 'Urgent'] else 2,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

    @staticmethod
    async def create_expense_status_change_alert(
        db: AsyncSession,
        *,
        expense_id: int,
        description: str,
        amount: float,
        old_status: str,
        new_status: str,  # 'APPROVED', 'REJECTED', or 'PAID'
        reviewer_name: str,
        reviewer_user_id: int,
        requester_user_id: Optional[int] = None,
        comments: Optional[str] = None
    ) -> Alert:
        """Create alert when expense status changes (approved/rejected/paid)"""
        # Determine alert type based on new status
        if new_status == 'APPROVED':
            alert_type_id = AlertService.AlertTypes.EXPENSE_APPROVED
            status_text = "approved"
        elif new_status == 'REJECTED':
            alert_type_id = AlertService.AlertTypes.EXPENSE_REJECTED
            status_text = "rejected"
        elif new_status == 'PAID':
            alert_type_id = AlertService.AlertTypes.EXPENSE_PAID
            status_text = "marked as paid"
        else:
            alert_type_id = AlertService.AlertTypes.EXPENSE_APPROVED
            status_text = f"updated to {new_status}"

        title = f"Expense {status_text.title()}: ₹{amount:,.2f}"
        message = f"{reviewer_name} {status_text} expense of ₹{amount:,.2f} ({description})."

        if comments:
            message += f" Comments: {comments}"

        return await alert_crud.create_alert(
            db,
            alert_type_id=alert_type_id,
            title=title,
            message=message,
            entity_type="EXPENSE",
            entity_id=expense_id,
            entity_display_name=description[:50],
            actor_user_id=reviewer_user_id,
            actor_type="ADMIN",
            actor_name=reviewer_name,
            target_role="ADMIN",  # Visible to all admins
            target_user_id=requester_user_id,  # Notify the requester specifically
            alert_metadata={
                "description": description,
                "amount": amount,
                "old_status": old_status,
                "new_status": new_status,
                "reviewer_name": reviewer_name,
                "comments": comments
            },
            priority_level=3 if new_status == 'REJECTED' else 2,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )


# Create singleton instance
alert_service = AlertService()

