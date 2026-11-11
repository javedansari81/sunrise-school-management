"""
Queries shared by the fee services. Every query runs on a school-bound session,
so app.core.tenant adds the school filter; nothing here filters by school by hand.
"""
from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple, Type, TypeVar

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import Class, SessionYear
from app.models.school import School, SchoolSetting
from app.models.student import Student
from app.models.student_session_history import StudentSessionHistory
from app.modules.fees.errors import NotFound
from app.modules.fees.models import (
    FeeHead, FeeStructure, FeeStructureItem, StudentDue, StudentFeePlan,
)
from app.modules.fees.periods import month_start

T = TypeVar("T")


async def get_or_404(db: AsyncSession, model: Type[T], id_: int, what: str) -> T:
    obj = await db.get(model, id_)
    if obj is None:
        raise NotFound(f"{what} {id_} not found")
    return obj


async def head_by_code(db: AsyncSession, code: str) -> Optional[FeeHead]:
    return (await db.execute(select(FeeHead).where(FeeHead.code == code))).scalar_one_or_none()


async def heads_by_id(db: AsyncSession, ids) -> Dict[int, FeeHead]:
    ids = set(ids)
    if not ids:
        return {}
    rows = (await db.execute(select(FeeHead).where(FeeHead.id.in_(ids)))).scalars().all()
    return {h.id: h for h in rows}


async def existing_class_ids(db: AsyncSession, ids) -> set:
    ids = set(i for i in ids if i is not None)
    if not ids:
        return set()
    return set((await db.execute(select(Class.id).where(Class.id.in_(ids)))).scalars())


async def session_year_or_404(db: AsyncSession, session_year_id: int) -> SessionYear:
    return await get_or_404(db, SessionYear, session_year_id, "Session year")


async def session_start(db: AsyncSession, session_year: SessionYear) -> date:
    """First month of a session: its start date, else the school's academic year start month."""
    if session_year.start_date is not None:
        return month_start(session_year.start_date)
    school = await db.get(School, session_year.school_id)
    start_month = (school.academic_year_start_month if school else None) or 4
    first_year = int(session_year.name[:4])
    return date(first_year, start_month, 1)


async def published_structure(db: AsyncSession, session_year_id: int) -> Optional[FeeStructure]:
    return (await db.execute(
        select(FeeStructure).where(
            FeeStructure.session_year_id == session_year_id, FeeStructure.status == "PUBLISHED"
        )
    )).scalar_one_or_none()


async def head_in_use(db: AsyncSession, head_id: int) -> bool:
    for model in (FeeStructureItem, StudentFeePlan, StudentDue):
        if (await db.execute(select(exists().where(model.fee_head_id == head_id)))).scalar():
            return True
    return False


def _is_current(student_cls):
    return (student_cls.is_deleted == False) | (student_cls.is_deleted.is_(None))  # noqa: E712


async def enrolled_students(
    db: AsyncSession,
    session_year_id: int,
    *,
    class_id: Optional[int] = None,
    student_ids: Optional[Sequence[int]] = None,
) -> List[Tuple[Student, int]]:
    """
    Students enrolled in a session, with their class in that session: the current
    class when the session is the student's current one, else the class recorded
    in student_session_history. Active, not deleted students only.
    """
    current = select(Student, Student.class_id).where(
        Student.session_year_id == session_year_id, Student.is_active == True, _is_current(Student),  # noqa: E712
    )
    past = (
        select(Student, StudentSessionHistory.class_id)
        .join(StudentSessionHistory, StudentSessionHistory.student_id == Student.id)
        .where(
            StudentSessionHistory.session_year_id == session_year_id,
            Student.session_year_id != session_year_id,
            Student.is_active == True, _is_current(Student),  # noqa: E712
        )
    )
    if student_ids is not None:
        current = current.where(Student.id.in_(student_ids))
        past = past.where(Student.id.in_(student_ids))
    rows = list((await db.execute(current)).all()) + list((await db.execute(past)).all())
    if class_id is not None:
        rows = [r for r in rows if r[1] == class_id]
    return sorted(((s, c) for s, c in rows), key=lambda r: r[0].id)


async def student_or_404(db: AsyncSession, student_id: int) -> Student:
    return await get_or_404(db, Student, student_id, "Student")


async def setting(db: AsyncSession, key: str, default: Optional[str] = None) -> Optional[str]:
    value = (await db.execute(select(SchoolSetting.value).where(SchoolSetting.key == key))).scalar_one_or_none()
    return default if value is None else value


async def count(db: AsyncSession, stmt) -> int:
    return (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()

