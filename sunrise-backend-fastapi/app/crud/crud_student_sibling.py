from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, text
from decimal import Decimal
from datetime import date

from app.crud.base import CRUDBase
from app.models.student_sibling import StudentSibling
from app.models.student import Student
from app.schemas.student_sibling import StudentSiblingCreate, StudentSiblingUpdate


class CRUDStudentSibling(CRUDBase[StudentSibling, StudentSiblingCreate, StudentSiblingUpdate]):
    def __init__(self):
        super().__init__(StudentSibling)

    async def detect_siblings_by_father_and_phone(
        self,
        db: AsyncSession,
        father_name: str,
        father_phone: Optional[str],
        exclude_student_id: Optional[int] = None
    ) -> List[Student]:
        """
        Detect potential siblings based on matching father_name and father_phone.
        Returns list of students ordered by date_of_birth (eldest first).
        """
        if not father_name or not father_phone:
            return []
        
        # Build query to find students with matching father details
        query = select(Student).where(
            and_(
                func.lower(Student.father_name) == func.lower(father_name.strip()),
                Student.father_phone == father_phone.strip(),
                Student.is_active == True,
                or_(Student.is_deleted == False, Student.is_deleted.is_(None))
            )
        )
        
        # Exclude the current student if provided
        if exclude_student_id:
            query = query.where(Student.id != exclude_student_id)
        
        # Order by date of birth (eldest first)
        query = query.order_by(Student.date_of_birth.asc())
        
        result = await db.execute(query)
        return result.scalars().all()

    async def calculate_sibling_waiver(
        self,
        db: AsyncSession,
        total_siblings: int,
        birth_order: int
    ) -> Tuple[Decimal, Optional[str]]:
        """
        Calculate fee waiver percentage based on total siblings and birth order.
        Uses the database function for calculation.
        Returns: (waiver_percentage, waiver_reason)
        """
        # Call database function to calculate waiver
        result = await db.execute(
            text("SELECT calculate_sibling_fee_waiver(:total, :order)"),
            {"total": total_siblings, "order": birth_order}
        )
        waiver_percentage = result.scalar() or Decimal("0.00")
        
        # Get waiver reason text
        if waiver_percentage > 0:
            reason_result = await db.execute(
                text("SELECT get_waiver_reason_text(:total, :order, :waiver)"),
                {"total": total_siblings, "order": birth_order, "waiver": float(waiver_percentage)}
            )
            waiver_reason = reason_result.scalar()
        else:
            waiver_reason = None
        
        return Decimal(str(waiver_percentage)), waiver_reason

    async def get_siblings_for_student(
        self,
        db: AsyncSession,
        student_id: int,
        include_inactive: bool = False
    ) -> List[StudentSibling]:
        """Get all sibling relationships for a student"""
        query = select(StudentSibling).where(
            StudentSibling.student_id == student_id
        )
        
        if not include_inactive:
            query = query.where(StudentSibling.is_active == True)
        
        query = query.order_by(StudentSibling.birth_order)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all_family_members(
        self,
        db: AsyncSession,
        student_id: int
    ) -> List[int]:
        """
        Get all student IDs in the same family (including the given student).
        This includes bidirectional sibling relationships.
        """
        # Get siblings where student is the primary
        query1 = select(StudentSibling.sibling_student_id).where(
            and_(
                StudentSibling.student_id == student_id,
                StudentSibling.is_active == True
            )
        )
        
        # Get siblings where student is the sibling
        query2 = select(StudentSibling.student_id).where(
            and_(
                StudentSibling.sibling_student_id == student_id,
                StudentSibling.is_active == True
            )
        )
        
        result1 = await db.execute(query1)
        result2 = await db.execute(query2)
        
        sibling_ids = set(result1.scalars().all())
        sibling_ids.update(result2.scalars().all())
        sibling_ids.add(student_id)
        
        return list(sibling_ids)

    async def link_siblings(
        self,
        db: AsyncSession,
        student_id: int,
        sibling_student_id: int,
        relationship_type: str = "SIBLING",
        is_auto_detected: bool = False
    ) -> StudentSibling:
        """
        Create a sibling relationship between two students.
        This creates a bidirectional relationship.
        """
        # Validate students exist
        student = await db.get(Student, student_id)
        sibling = await db.get(Student, sibling_student_id)
        
        if not student or not sibling:
            raise ValueError("One or both students not found")
        
        if student_id == sibling_student_id:
            raise ValueError("Cannot link student to themselves")
        
        # Check if relationship already exists
        existing = await db.execute(
            select(StudentSibling).where(
                or_(
                    and_(
                        StudentSibling.student_id == student_id,
                        StudentSibling.sibling_student_id == sibling_student_id
                    ),
                    and_(
                        StudentSibling.student_id == sibling_student_id,
                        StudentSibling.sibling_student_id == student_id
                    )
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Sibling relationship already exists")
        
        # Get all family members to recalculate birth orders
        family_ids = await self.get_all_family_members(db, student_id)
        family_ids.append(sibling_student_id)
        family_ids = list(set(family_ids))
        
        # Recalculate birth orders and waivers for entire family
        await self._recalculate_family_waivers(db, family_ids)
        
        await db.commit()
        
        # Return the created relationship
        result = await db.execute(
            select(StudentSibling).where(
                StudentSibling.student_id == student_id,
                StudentSibling.sibling_student_id == sibling_student_id
            )
        )
        return result.scalar_one()

    async def unlink_siblings(
        self,
        db: AsyncSession,
        student_id: int,
        sibling_student_id: int
    ) -> bool:
        """
        Remove sibling relationship between two students.
        This removes the bidirectional relationship.
        """
        # Delete both directions of the relationship
        await db.execute(
            text("""
                DELETE FROM student_siblings
                WHERE (student_id = :sid1 AND sibling_student_id = :sid2)
                   OR (student_id = :sid2 AND sibling_student_id = :sid1)
            """),
            {"sid1": student_id, "sid2": sibling_student_id}
        )

        # Recalculate waivers for both families
        family1_ids = await self.get_all_family_members(db, student_id)
        family2_ids = await self.get_all_family_members(db, sibling_student_id)

        if family1_ids:
            await self._recalculate_family_waivers(db, family1_ids)
        if family2_ids and family2_ids != family1_ids:
            await self._recalculate_family_waivers(db, family2_ids)

        await db.commit()
        return True

    async def _recalculate_family_waivers(
        self,
        db: AsyncSession,
        family_student_ids: List[int]
    ) -> None:
        """
        Recalculate birth orders and fee waivers for all students in a family.
        This creates/updates bidirectional sibling relationships.
        """
        if len(family_student_ids) < 2:
            # No siblings, remove any existing relationships
            if len(family_student_ids) == 1:
                await db.execute(
                    text("DELETE FROM student_siblings WHERE student_id = :sid OR sibling_student_id = :sid"),
                    {"sid": family_student_ids[0]}
                )
            return

        # Get all students with their DOB
        result = await db.execute(
            select(Student.id, Student.date_of_birth).where(
                Student.id.in_(family_student_ids)
            ).order_by(Student.date_of_birth.asc())
        )
        students_by_dob = result.all()

        total_siblings = len(students_by_dob)

        # Delete existing relationships for this family
        await db.execute(
            text("DELETE FROM student_siblings WHERE student_id = ANY(:ids) OR sibling_student_id = ANY(:ids)"),
            {"ids": family_student_ids}
        )

        # Create bidirectional relationships for each pair
        for i, (student_id, _) in enumerate(students_by_dob):
            birth_order = i + 1
            waiver_percentage, waiver_reason = await self.calculate_sibling_waiver(
                db, total_siblings, birth_order
            )

            # Create relationships with all other siblings
            for j, (other_student_id, _) in enumerate(students_by_dob):
                if i != j:
                    sibling_relationship = StudentSibling(
                        student_id=student_id,
                        sibling_student_id=other_student_id,
                        relationship_type="SIBLING",
                        is_auto_detected=True,
                        birth_order=birth_order,
                        fee_waiver_percentage=waiver_percentage,
                        is_active=True
                    )
                    db.add(sibling_relationship)

        await db.flush()

    async def create_sibling_relationships_for_student(
        self,
        db: AsyncSession,
        student_id: int,
        detected_sibling_ids: List[int]
    ) -> List[StudentSibling]:
        """
        Create sibling relationships for a newly created student with detected siblings.
        """
        if not detected_sibling_ids:
            return []

        # Add the current student to the family
        all_family_ids = detected_sibling_ids + [student_id]

        # Recalculate waivers for the entire family
        await self._recalculate_family_waivers(db, all_family_ids)
        await db.commit()

        # Return the created relationships for this student
        result = await db.execute(
            select(StudentSibling).where(
                StudentSibling.student_id == student_id
            ).order_by(StudentSibling.birth_order)
        )
        return result.scalars().all()

    async def get_sibling_waiver_info(
        self,
        db: AsyncSession,
        student_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive sibling waiver information for a student.
        """
        siblings = await self.get_siblings_for_student(db, student_id)

        if not siblings:
            return {
                "has_siblings": False,
                "total_siblings_count": 1,
                "birth_order": 1,
                "birth_order_description": "Only child",
                "fee_waiver_percentage": Decimal("0.00"),
                "waiver_reason": None,
                "siblings": []
            }

        # Get the first sibling record to extract student's info
        first_sibling = siblings[0]

        return {
            "has_siblings": True,
            "total_siblings_count": len(siblings) + 1,  # +1 for the student themselves
            "birth_order": first_sibling.birth_order,
            "birth_order_description": self._get_birth_order_description(first_sibling.birth_order),
            "fee_waiver_percentage": first_sibling.fee_waiver_percentage,
            "waiver_reason": await self._get_waiver_reason(
                db, len(siblings) + 1, first_sibling.birth_order, first_sibling.fee_waiver_percentage
            ),
            "siblings": siblings
        }

    def _get_birth_order_description(self, birth_order: int) -> str:
        """Get human-readable birth order description"""
        if birth_order == 1:
            return "Eldest"
        elif birth_order == 2:
            return "2nd"
        elif birth_order == 3:
            return "3rd"
        else:
            return f"{birth_order}th"

    async def _get_waiver_reason(
        self,
        db: AsyncSession,
        total_siblings: int,
        birth_order: int,
        waiver_percentage: Decimal
    ) -> Optional[str]:
        """Get waiver reason text"""
        if waiver_percentage == 0:
            return None

        result = await db.execute(
            text("SELECT get_waiver_reason_text(:total, :order, :waiver)"),
            {"total": total_siblings, "order": birth_order, "waiver": float(waiver_percentage)}
        )
        return result.scalar()


# Create instance
student_sibling_crud = CRUDStudentSibling()

