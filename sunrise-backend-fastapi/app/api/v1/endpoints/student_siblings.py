from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.student import Student
from app.models.metadata import Class
from app.crud.crud_student_sibling import student_sibling_crud
from app.crud import student_crud
from app.schemas.student_sibling import (
    StudentSiblingWithDetails,
    SiblingDetectionResult,
    SiblingWaiverInfo,
    BulkSiblingLinkRequest,
    SiblingRecalculationResult,
    DetectedSibling,
    SiblingStudentInfo
)
from app.schemas.user import UserTypeEnum

router = APIRouter()


@router.get("/{student_id}/siblings", response_model=List[StudentSiblingWithDetails])
async def get_student_siblings(
    student_id: int,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all siblings for a student with full details
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get sibling relationships
    siblings = await student_sibling_crud.get_siblings_for_student(
        db, student_id=student_id, include_inactive=include_inactive
    )
    
    # Build response with sibling details
    result = []
    for sibling_rel in siblings:
        # Get sibling student details
        sibling_student = await student_crud.get_with_metadata(db, id=sibling_rel.sibling_student_id)
        if sibling_student:
            sibling_info = SiblingStudentInfo(
                id=sibling_student.id,
                admission_number=sibling_student.admission_number,
                first_name=sibling_student.first_name,
                last_name=sibling_student.last_name,
                full_name=f"{sibling_student.first_name} {sibling_student.last_name}",
                class_name=sibling_student.class_ref.description if sibling_student.class_ref else "",
                class_id=sibling_student.class_id,
                section=sibling_student.section,
                date_of_birth=str(sibling_student.date_of_birth) if sibling_student.date_of_birth else None,
                is_active=sibling_student.is_active
            )

            # Get the sibling's birth order from the reverse relationship
            # sibling_rel.birth_order is the CURRENT student's birth order
            # We need to find the sibling's birth order from their own relationship record
            sibling_birth_order_rel = await student_sibling_crud.get_siblings_for_student(
                db, student_id=sibling_rel.sibling_student_id, include_inactive=False
            )
            # Find the relationship where sibling points back to current student
            sibling_birth_order = sibling_rel.birth_order  # Default to current if not found
            sibling_waiver_percentage = sibling_rel.fee_waiver_percentage
            for reverse_rel in sibling_birth_order_rel:
                if reverse_rel.sibling_student_id == student_id:
                    sibling_birth_order = reverse_rel.birth_order
                    sibling_waiver_percentage = reverse_rel.fee_waiver_percentage
                    break

            # Calculate birth order description for the sibling
            if sibling_birth_order == 1:
                sibling_birth_order_desc = "Eldest"
            elif sibling_birth_order == 2:
                sibling_birth_order_desc = "2nd"
            elif sibling_birth_order == 3:
                sibling_birth_order_desc = "3rd"
            else:
                sibling_birth_order_desc = f"{sibling_birth_order}th"

            # Calculate waiver description for the sibling
            if sibling_waiver_percentage == 0:
                sibling_waiver_desc = "No waiver"
            else:
                sibling_waiver_desc = f"{sibling_waiver_percentage}% fee waiver"

            result.append(StudentSiblingWithDetails(
                id=sibling_rel.id,
                student_id=sibling_rel.student_id,
                sibling_student_id=sibling_rel.sibling_student_id,
                relationship_type=sibling_rel.relationship_type,
                is_auto_detected=sibling_rel.is_auto_detected,
                birth_order=sibling_birth_order,  # Use sibling's birth order
                fee_waiver_percentage=sibling_waiver_percentage,  # Use sibling's waiver
                is_active=sibling_rel.is_active,
                created_at=sibling_rel.created_at,
                updated_at=sibling_rel.updated_at,
                sibling_info=sibling_info,
                waiver_description=sibling_waiver_desc,  # Use sibling's waiver description
                birth_order_description=sibling_birth_order_desc  # Use sibling's birth order description
            ))

    return result


@router.get("/{student_id}/siblings/waiver-info", response_model=SiblingWaiverInfo)
async def get_sibling_waiver_info(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive sibling waiver information for a student
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get waiver info
    waiver_info = await student_sibling_crud.get_sibling_waiver_info(db, student_id=student_id)
    
    # Get sibling details
    siblings_with_details = await get_student_siblings(student_id, False, db, current_user)
    
    return SiblingWaiverInfo(
        has_siblings=waiver_info["has_siblings"],
        total_siblings_count=waiver_info["total_siblings_count"],
        birth_order=waiver_info["birth_order"],
        birth_order_description=waiver_info["birth_order_description"],
        fee_waiver_percentage=waiver_info["fee_waiver_percentage"],
        waiver_reason=waiver_info["waiver_reason"],
        siblings=siblings_with_details
    )


@router.post("/{student_id}/siblings/detect", response_model=SiblingDetectionResult)
async def detect_siblings(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually trigger sibling detection for a student
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Detect siblings
    detected = await student_sibling_crud.detect_siblings_by_father_and_phone(
        db,
        father_name=student.father_name,
        father_phone=student.father_phone,
        exclude_student_id=student_id
    )
    
    # Build detected siblings list
    detected_siblings_list = []
    for sibling in detected:
        sibling_with_class = await student_crud.get_with_metadata(db, id=sibling.id)
        detected_siblings_list.append(DetectedSibling(
            student_id=sibling.id,
            admission_number=sibling.admission_number,
            first_name=sibling.first_name,
            last_name=sibling.last_name,
            full_name=f"{sibling.first_name} {sibling.last_name}",
            class_name=sibling_with_class.class_ref.description if sibling_with_class and sibling_with_class.class_ref else "",
            section=sibling.section,
            date_of_birth=str(sibling.date_of_birth) if sibling.date_of_birth else None,
            matching_criteria="Same father name and phone"
        ))

    # Calculate what the waiver would be if linked
    total_siblings = len(detected) + 1  # +1 for current student

    # Determine birth order for current student
    all_students = detected + [student]
    all_students.sort(key=lambda s: s.date_of_birth)
    current_birth_order = next((i + 1 for i, s in enumerate(all_students) if s.id == student_id), 1)

    # Calculate waiver
    waiver_percentage, waiver_reason = await student_sibling_crud.calculate_sibling_waiver(
        db, total_siblings, current_birth_order
    )

    return SiblingDetectionResult(
        detected_siblings=detected_siblings_list,
        total_siblings_count=total_siblings,
        current_student_birth_order=current_birth_order,
        calculated_waiver_percentage=waiver_percentage,
        waiver_reason=waiver_reason
    )


@router.post("/{student_id}/siblings/link/{sibling_id}", response_model=Dict[str, Any])
async def link_sibling(
    student_id: int,
    sibling_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually link two students as siblings
    """
    try:
        sibling_rel = await student_sibling_crud.link_siblings(
            db,
            student_id=student_id,
            sibling_student_id=sibling_id,
            relationship_type="SIBLING",
            is_auto_detected=False
        )

        return {
            "message": "Siblings linked successfully",
            "sibling_relationship_id": sibling_rel.id,
            "birth_order": sibling_rel.birth_order,
            "fee_waiver_percentage": float(sibling_rel.fee_waiver_percentage)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link siblings: {str(e)}"
        )


@router.post("/{student_id}/siblings/link-multiple", response_model=Dict[str, Any])
async def link_multiple_siblings(
    student_id: int,
    request: BulkSiblingLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Link multiple siblings at once
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    try:
        # Create relationships with all siblings
        created_count = 0
        for sibling_id in request.sibling_student_ids:
            try:
                await student_sibling_crud.link_siblings(
                    db,
                    student_id=student_id,
                    sibling_student_id=sibling_id,
                    relationship_type=request.relationship_type,
                    is_auto_detected=False
                )
                created_count += 1
            except ValueError:
                # Skip if already linked
                continue

        # Get updated waiver info
        waiver_info = await student_sibling_crud.get_sibling_waiver_info(db, student_id=student_id)

        return {
            "message": f"Successfully linked {created_count} siblings",
            "total_siblings_count": waiver_info["total_siblings_count"],
            "birth_order": waiver_info["birth_order"],
            "fee_waiver_percentage": float(waiver_info["fee_waiver_percentage"]),
            "waiver_reason": waiver_info["waiver_reason"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link siblings: {str(e)}"
        )


@router.delete("/{student_id}/siblings/{sibling_id}", response_model=Dict[str, str])
async def unlink_sibling(
    student_id: int,
    sibling_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove sibling relationship between two students
    """
    try:
        success = await student_sibling_crud.unlink_siblings(
            db,
            student_id=student_id,
            sibling_student_id=sibling_id
        )

        if success:
            return {"message": "Sibling relationship removed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sibling relationship not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlink siblings: {str(e)}"
        )


@router.put("/{student_id}/siblings/recalculate-waiver", response_model=SiblingRecalculationResult)
async def recalculate_sibling_waiver(
    student_id: int,
    update_fee_records: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Recalculate fee waiver for a student and their siblings.

    Parameters:
    - student_id: The student ID to recalculate waivers for
    - update_fee_records: If True, also updates existing fee records and monthly tracking records
    """
    from app.models.fee import FeeRecord, MonthlyFeeTracking
    from sqlalchemy import select, update
    from decimal import Decimal

    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get current waiver info
    old_waiver_info = await student_sibling_crud.get_sibling_waiver_info(db, student_id=student_id)
    old_waiver = old_waiver_info["fee_waiver_percentage"]
    old_birth_order = old_waiver_info["birth_order"]

    # Get all family members
    family_ids = await student_sibling_crud.get_all_family_members(db, student_id)

    # Recalculate waivers in student_siblings table
    await student_sibling_crud._recalculate_family_waivers(db, family_ids)
    await db.commit()

    # Get new waiver info
    new_waiver_info = await student_sibling_crud.get_sibling_waiver_info(db, student_id=student_id)
    new_waiver = new_waiver_info["fee_waiver_percentage"]
    new_birth_order = new_waiver_info["birth_order"]

    # Update existing fee records and monthly tracking if requested
    if update_fee_records and new_waiver != old_waiver:
        # Get all fee records for this student that have monthly tracking enabled
        fee_records_result = await db.execute(
            select(FeeRecord).where(
                FeeRecord.student_id == student_id,
                FeeRecord.is_monthly_tracked == True,
                FeeRecord.is_active == True
            )
        )
        fee_records = fee_records_result.scalars().all()

        for fee_record in fee_records:
            # Calculate new amounts based on new waiver percentage
            if fee_record.original_total_amount:
                # Already has waiver, use original amount
                original_total = fee_record.original_total_amount
            else:
                # No previous waiver, current total is the original
                original_total = fee_record.total_amount

            # Calculate new waived amount
            if new_waiver > 0:
                new_total_amount = original_total * (Decimal("100") - new_waiver) / Decimal("100")
                new_monthly_amount = new_total_amount / Decimal("12")
            else:
                new_total_amount = original_total
                new_monthly_amount = original_total / Decimal("12")

            # Update fee record
            fee_record.has_sibling_waiver = (new_waiver > 0)
            fee_record.sibling_waiver_percentage = new_waiver
            fee_record.original_total_amount = original_total if new_waiver > 0 else None
            old_total = fee_record.total_amount
            fee_record.total_amount = new_total_amount
            # Adjust balance amount proportionally
            if old_total > 0:
                balance_ratio = fee_record.balance_amount / old_total
                fee_record.balance_amount = new_total_amount * balance_ratio
            else:
                fee_record.balance_amount = new_total_amount - fee_record.paid_amount

            db.add(fee_record)

            # Update monthly tracking records for this fee record
            monthly_records_result = await db.execute(
                select(MonthlyFeeTracking).where(
                    MonthlyFeeTracking.fee_record_id == fee_record.id,
                    MonthlyFeeTracking.payment_status_id == 1  # Only update unpaid records
                )
            )
            monthly_records = monthly_records_result.scalars().all()

            # Get waiver reason
            waiver_reason = None
            if new_waiver > 0:
                total_siblings = new_waiver_info["total_siblings_count"]
                result = await db.execute(
                    text("SELECT get_waiver_reason_text(:total, :order, :percentage)"),
                    {
                        "total": total_siblings,
                        "order": new_birth_order,
                        "percentage": float(new_waiver)
                    }
                )
                waiver_reason = result.scalar()

            for monthly_record in monthly_records:
                # Calculate original monthly amount if not set
                if not monthly_record.original_monthly_amount:
                    monthly_record.original_monthly_amount = monthly_record.monthly_amount if old_waiver == 0 else None

                # Update monthly amount with new waiver
                if new_waiver > 0:
                    if monthly_record.original_monthly_amount:
                        original_monthly = monthly_record.original_monthly_amount
                    else:
                        original_monthly = original_total / Decimal("12")

                    monthly_record.original_monthly_amount = original_monthly
                    monthly_record.monthly_amount = original_monthly * (Decimal("100") - new_waiver) / Decimal("100")
                else:
                    monthly_record.monthly_amount = original_total / Decimal("12")
                    monthly_record.original_monthly_amount = None

                monthly_record.fee_waiver_percentage = new_waiver
                monthly_record.waiver_reason = waiver_reason
                db.add(monthly_record)

        await db.commit()

    return SiblingRecalculationResult(
        student_id=student_id,
        previous_waiver_percentage=old_waiver,
        new_waiver_percentage=new_waiver,
        previous_birth_order=old_birth_order,
        new_birth_order=new_birth_order,
        total_siblings_count=new_waiver_info["total_siblings_count"],
        message=f"Waiver recalculated: {old_waiver}% -> {new_waiver}%. Fee records {'updated' if update_fee_records else 'not updated'}."
    )

