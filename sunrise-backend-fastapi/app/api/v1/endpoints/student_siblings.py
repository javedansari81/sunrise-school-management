from typing import List, Dict, Any

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
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
from app.models.student_sibling import RelationshipTypeEnum

router = APIRouter()

# Sibling links change fees (sibling concession), so only admins change them.
# They are always set by hand; /siblings/suggestions only proposes candidates.


class SiblingRelationshipUpdate(BaseModel):
    relationship_type: RelationshipTypeEnum


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


@router.get("/{student_id}/siblings/suggestions", response_model=SiblingDetectionResult)
@router.post("/{student_id}/siblings/detect", response_model=SiblingDetectionResult)
async def detect_siblings(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Suggest possible siblings: students with the same father name and phone who
    are not yet in this student's family. Nothing is linked; the admin confirms
    each one with POST /{student_id}/siblings/link/{sibling_id}.
    (POST /detect is the old name of this route, kept for the current screens.)
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    detected = await student_sibling_crud.suggest_siblings(db, student=student)
    family_ids = await student_sibling_crud.get_all_family_members(db, student_id)
    
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

    # What the family would look like if every suggestion were linked
    family = [await db.get(Student, i) for i in family_ids]
    all_students = [s for s in family if s is not None] + list(detected)
    total_siblings = len(all_students)
    all_students.sort(key=lambda s: (s.date_of_birth, s.admission_number))
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
    relationship_type: RelationshipTypeEnum = RelationshipTypeEnum.SIBLING,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Link two students as siblings. Their families are merged: the new sibling is
    linked to every sibling the student already has, and the other way round.
    """
    try:
        sibling_rel = await student_sibling_crud.link_siblings(
            db,
            student_id=student_id,
            sibling_student_id=sibling_id,
            relationship_type=relationship_type.value,
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


@router.post("/{student_id}/siblings/link-multiple", response_model=Dict[str, Any])
async def link_multiple_siblings(
    student_id: int,
    request: BulkSiblingLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
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
    current_user: User = Depends(get_current_admin_user)
):
    """
    Remove a sibling from the student's family. The removed student loses all
    sibling links; the rest of the family stays linked.
    """
    success = await student_sibling_crud.unlink_siblings(
        db,
        student_id=student_id,
        sibling_student_id=sibling_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sibling relationship not found"
        )
    return {"message": "Sibling removed from the family"}


@router.patch("/{student_id}/siblings/{sibling_id}", response_model=Dict[str, str])
async def update_sibling_relationship(
    student_id: int,
    sibling_id: int,
    body: SiblingRelationshipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Change the relationship type (SIBLING, TWIN, HALF_SIBLING) of two linked siblings."""
    updated = await student_sibling_crud.set_relationship_type(
        db, student_id=student_id, sibling_student_id=sibling_id, relationship_type=body.relationship_type.value
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sibling relationship not found")
    return {"message": "Sibling relationship updated"}


@router.put("/{student_id}/siblings/recalculate-waiver", response_model=SiblingRecalculationResult)
async def recalculate_sibling_waiver(
    student_id: int,
    update_fee_records: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Recalculate the sibling waiver of a student and their family.

    Parameters:
    - student_id: The student ID to recalculate waivers for
    - update_fee_records: If True, also re-prices the unpaid dues of every family
      member in their current session. The fee module works the sibling
      concession out on each dues generation; paid dues never change.
    """
    from app.modules.fees import repository as fee_repo
    from app.modules.fees.schemas import DuesGenerateRequest
    from app.modules.fees.service.dues import generate_dues

    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    old_waiver_info = await student_sibling_crud.get_sibling_waiver_info(db, student_id=student_id)
    old_waiver = old_waiver_info["fee_waiver_percentage"]
    old_birth_order = old_waiver_info["birth_order"]

    family_ids = await student_sibling_crud.get_all_family_members(db, student_id)
    await student_sibling_crud._recalculate_family_waivers(db, family_ids)
    await db.commit()

    new_waiver_info = await student_sibling_crud.get_sibling_waiver_info(db, student_id=student_id)
    new_waiver = new_waiver_info["fee_waiver_percentage"]
    new_birth_order = new_waiver_info["birth_order"]

    repriced = 0
    if update_fee_records:
        for member_id in sorted(set(family_ids) | {student_id}):
            member = await db.get(Student, member_id)
            if member is None or member.session_year_id is None:
                continue
            if not await fee_repo.enrolled_students(db, member.session_year_id, student_ids=[member_id]):
                continue
            result = await generate_dues(
                db, DuesGenerateRequest(session_year_id=member.session_year_id, student_id=member_id),
                user_id=current_user.id,
            )
            repriced += result["repriced"]
        await db.commit()

    return SiblingRecalculationResult(
        student_id=student_id,
        previous_waiver_percentage=old_waiver,
        new_waiver_percentage=new_waiver,
        previous_birth_order=old_birth_order,
        new_birth_order=new_birth_order,
        total_siblings_count=new_waiver_info["total_siblings_count"],
        message=(
            f"Waiver recalculated: {old_waiver}% -> {new_waiver}%. "
            + (f"{repriced} unpaid dues re-priced." if update_fee_records else "Dues not updated.")
        )
    )
