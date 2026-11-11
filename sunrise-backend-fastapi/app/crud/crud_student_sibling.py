from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, delete, or_, func, text
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

        Handles multi-word names with varying whitespace patterns by:
        - Normalizing multiple spaces to single space
        - Case-insensitive comparison
        - Trimming leading/trailing whitespace
        """
        if not father_name or not father_phone:
            return []

        # Normalize the input father name: trim and collapse multiple spaces to single space
        import re
        normalized_father_name = re.sub(r'\s+', ' ', father_name.strip()).lower()
        normalized_phone = father_phone.strip()

        # Build query to find students with matching father details
        # Use REGEXP_REPLACE in PostgreSQL to normalize whitespace in database values
        query = select(Student).where(
            and_(
                func.lower(
                    func.regexp_replace(Student.father_name, r'\s+', ' ', 'g')
                ) == normalized_father_name,
                Student.father_phone == normalized_phone,
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

    async def suggest_siblings(self, db: AsyncSession, *, student: Student) -> List[Student]:
        """
        Possible siblings of a student: same father name and phone, not yet in the
        student's family. Only a suggestion; nothing is linked (decision 13).
        """
        candidates = await self.detect_siblings_by_father_and_phone(
            db, father_name=student.father_name, father_phone=student.father_phone,
            exclude_student_id=student.id,
        )
        family = set(await self.get_all_family_members(db, student.id))
        return [c for c in candidates if c.id not in family]

    async def get_all_family_members(
        self,
        db: AsyncSession,
        student_id: int
    ) -> List[int]:
        """
        All student IDs in the same family, including the given student. Follows
        links in both directions and across siblings, so a family is complete
        even if a pair link is missing.
        """
        family = {student_id}
        frontier = {student_id}
        while frontier:
            rows = await db.execute(
                select(StudentSibling.student_id, StudentSibling.sibling_student_id).where(
                    StudentSibling.is_active == True,  # noqa: E712
                    or_(StudentSibling.student_id.in_(frontier), StudentSibling.sibling_student_id.in_(frontier)),
                )
            )
            found = {i for pair in rows.all() for i in pair}
            frontier = found - family
            family |= found
        return list(family)

    async def _pair_types(self, db: AsyncSession, family_ids: List[int]) -> Dict[Tuple[int, int], str]:
        """Relationship type of each linked pair in a family, keyed by (smaller id, larger id)."""
        rows = await db.execute(
            select(StudentSibling.student_id, StudentSibling.sibling_student_id, StudentSibling.relationship_type)
            .where(StudentSibling.student_id.in_(family_ids))
        )
        return {(min(a, b), max(a, b)): t for a, b, t in rows.all()}

    async def link_siblings(
        self,
        db: AsyncSession,
        student_id: int,
        sibling_student_id: int,
        relationship_type: str = "SIBLING",
        is_auto_detected: bool = False
    ) -> StudentSibling:
        """
        Link two students as siblings. Their two families become one: every member
        is linked to every other member. Existing pair types are kept.
        """
        student = await db.get(Student, student_id)
        sibling = await db.get(Student, sibling_student_id)
        if not student or not sibling:
            raise ValueError("One or both students not found")
        if student_id == sibling_student_id:
            raise ValueError("Cannot link student to themselves")

        family_a = await self.get_all_family_members(db, student_id)
        if sibling_student_id in family_a:
            raise ValueError("Sibling relationship already exists")
        family_b = await self.get_all_family_members(db, sibling_student_id)
        family_ids = list(set(family_a) | set(family_b))

        pair_types = await self._pair_types(db, family_ids)
        pair_types[(min(student_id, sibling_student_id), max(student_id, sibling_student_id))] = relationship_type
        await self._recalculate_family_waivers(db, family_ids, pair_types)
        await db.commit()

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
        Remove `sibling_student_id` from `student_id`'s family. The removed student
        loses every sibling link; the rest of the family stays linked. Returns False
        when the two are not in the same family.
        """
        family_ids = await self.get_all_family_members(db, student_id)
        if sibling_student_id not in family_ids or sibling_student_id == student_id:
            return False

        pair_types = await self._pair_types(db, family_ids)
        remaining = [i for i in family_ids if i != sibling_student_id]
        await db.execute(
            delete(StudentSibling).where(
                or_(StudentSibling.student_id == sibling_student_id,
                    StudentSibling.sibling_student_id == sibling_student_id)
            )
        )
        await self._recalculate_family_waivers(db, remaining, pair_types)
        await db.commit()
        return True

    async def set_relationship_type(
        self,
        db: AsyncSession,
        student_id: int,
        sibling_student_id: int,
        relationship_type: str
    ) -> bool:
        """Change the relationship type of one linked pair (both directions). False if not linked."""
        rows = (await db.execute(
            select(StudentSibling).where(
                or_(
                    and_(StudentSibling.student_id == student_id,
                         StudentSibling.sibling_student_id == sibling_student_id),
                    and_(StudentSibling.student_id == sibling_student_id,
                         StudentSibling.sibling_student_id == student_id),
                )
            )
        )).scalars().all()
        if not rows:
            return False
        for row in rows:
            row.relationship_type = relationship_type
        await db.commit()
        return True

    async def _recalculate_family_waivers(
        self,
        db: AsyncSession,
        family_student_ids: List[int],
        pair_types: Optional[Dict[Tuple[int, int], str]] = None
    ) -> None:
        """
        Rebuild the links of a family: every member linked to every other member,
        with birth order (eldest first by date of birth, then admission number)
        and the old fee module's waiver. Kept for the old fee screens until Phase 4;
        the unified fee module works out birth order and concession itself.
        """
        if pair_types is None:
            pair_types = await self._pair_types(db, family_student_ids)

        await db.execute(
            delete(StudentSibling).where(
                or_(StudentSibling.student_id.in_(family_student_ids),
                    StudentSibling.sibling_student_id.in_(family_student_ids))
            )
        )
        if len(family_student_ids) < 2:
            await db.flush()
            return

        result = await db.execute(
            select(Student.id).where(Student.id.in_(family_student_ids))
            .order_by(Student.date_of_birth.asc(), Student.admission_number.asc())
        )
        ordered_ids = list(result.scalars().all())
        total_siblings = len(ordered_ids)

        for i, student_id in enumerate(ordered_ids):
            birth_order = i + 1
            waiver_percentage, _ = await self.calculate_sibling_waiver(db, total_siblings, birth_order)
            for other_student_id in ordered_ids:
                if other_student_id == student_id:
                    continue
                db.add(StudentSibling(
                    student_id=student_id,
                    sibling_student_id=other_student_id,
                    relationship_type=pair_types.get(
                        (min(student_id, other_student_id), max(student_id, other_student_id)), "SIBLING"
                    ),
                    is_auto_detected=False,
                    birth_order=birth_order,
                    fee_waiver_percentage=waiver_percentage,
                    is_active=True
                ))

        await db.flush()

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

