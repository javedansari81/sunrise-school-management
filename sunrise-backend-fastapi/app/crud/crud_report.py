from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, case, desc, text
from decimal import Decimal
from datetime import datetime, date

from app.models.student import Student
from app.models.metadata import Gender, Class, SessionYear, PaymentMethod
from app.models.user import User
from app.modules.fees.constants import DueStatus, FeeHeadCategory, OPEN_DUE_STATUSES, PaymentKind
from app.modules.fees.models import FeeHead, Payment, PaymentAllocation, StudentDue
from app.modules.transport.models import TransportAssignment, TransportType

ZERO = Decimal("0.00")


def _status(paid: Decimal, total: Decimal) -> str:
    if total > 0 and paid >= total:
        return "Paid"
    if paid > 0:
        return "Partial"
    return "Pending"


class CRUDReport:
    """CRUD operations for reports"""

    async def get_udise_report_data(
        self,
        db: AsyncSession,
        *,
        session_year_id: Optional[int] = None,
        class_id: Optional[int] = None,
        section: Optional[str] = None,
        gender_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get UDISE report data with comprehensive student information
        Returns: (list of student data, total count)
        """
        # Build base query
        query = select(Student).options(
            joinedload(Student.gender),
            joinedload(Student.class_ref),
            joinedload(Student.session_year)
        )

        # Apply filters
        filters = []
        
        # Exclude soft deleted
        filters.append(
            or_(Student.is_deleted == False, Student.is_deleted.is_(None))
        )

        if session_year_id is not None:
            filters.append(Student.session_year_id == session_year_id)

        if class_id is not None:
            filters.append(Student.class_id == class_id)

        if section is not None and section.strip():
            filters.append(Student.section == section.strip())

        if gender_id is not None:
            filters.append(Student.gender_id == gender_id)

        if is_active is not None:
            filters.append(Student.is_active == is_active)

        if search:
            search_filter = or_(
                Student.first_name.ilike(f"%{search}%"),
                Student.last_name.ilike(f"%{search}%"),
                Student.admission_number.ilike(f"%{search}%"),
                Student.father_name.ilike(f"%{search}%"),
                Student.mother_name.ilike(f"%{search}%")
            )
            filters.append(search_filter)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Student)
        if filters:
            count_query = count_query.where(and_(*filters))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Student.admission_number)
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Execute query
        result = await db.execute(query)
        students = result.scalars().all()

        # Transform to dict format
        student_data = []
        for student in students:
            # Calculate age
            age = None
            if student.date_of_birth:
                today = date.today()
                age = today.year - student.date_of_birth.year - (
                    (today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day)
                )

            data = {
                "id": student.id,
                "admission_number": student.admission_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "full_name": f"{student.first_name} {student.last_name}",
                "date_of_birth": student.date_of_birth,
                "age": age,
                "class_id": student.class_id,
                "class_name": student.class_ref.description if student.class_ref else "",
                "section": student.section,
                "roll_number": student.roll_number,
                "session_year_id": student.session_year_id,
                "session_year_name": student.session_year.description if student.session_year else "",
                "admission_date": student.admission_date,
                "gender_id": student.gender_id,
                "gender_name": student.gender.description if student.gender else "",
                "blood_group": student.blood_group,
                "aadhar_no": student.aadhar_no,
                "phone": student.phone,
                "email": student.email,
                "address": student.address,
                "city": student.city,
                "state": student.state,
                "postal_code": student.postal_code,
                "country": student.country,
                "father_name": student.father_name,
                "father_phone": student.father_phone,
                "father_email": student.father_email,
                "father_occupation": student.father_occupation,
                "mother_name": student.mother_name,
                "mother_phone": student.mother_phone,
                "mother_email": student.mother_email,
                "mother_occupation": student.mother_occupation,
                "guardian_name": student.guardian_name,
                "guardian_phone": student.guardian_phone,
                "guardian_email": student.guardian_email,
                "guardian_relation": student.guardian_relation,
                "is_active": student.is_active,
            }
            student_data.append(data)

        return student_data, total

    async def get_fee_tracking_report_data(
        self,
        db: AsyncSession,
        *,
        session_year_id: int,
        class_id: Optional[int] = None,
        section: Optional[str] = None,
        payment_status: Optional[str] = None,
        transport_opted: Optional[bool] = None,
        pending_only: bool = False,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """
        Fee tracking per student of a session, from the unified fee ledger.
        Returns: (page of rows, total count, summary statistics)

        "Fee" amounts are every due that is not a transport due; "transport" amounts
        are the dues of transport fee heads. Cancelled dues are left out. A student
        has opted for transport when they have an assignment (not cancelled) in the
        session; type and monthly fee come from the latest one.
        """
        student_query = (
            select(Student)
            .options(joinedload(Student.class_ref), joinedload(Student.session_year))
            .where(
                Student.session_year_id == session_year_id,
                or_(Student.is_deleted == False, Student.is_deleted.is_(None)),  # noqa: E712
            )
        )
        if class_id is not None:
            student_query = student_query.where(Student.class_id == class_id)
        if section is not None and section.strip():
            student_query = student_query.where(Student.section == section.strip())
        if search:
            pattern = f"%{search}%"
            student_query = student_query.where(or_(
                Student.first_name.ilike(pattern), Student.last_name.ilike(pattern),
                Student.admission_number.ilike(pattern),
            ))
        students = (await db.execute(student_query)).unique().scalars().all()
        student_ids = [st.id for st in students]

        # Dues per student, split into transport and the rest
        is_transport = FeeHead.category == FeeHeadCategory.TRANSPORT.value
        open_amount = case(
            (StudentDue.status.in_(OPEN_DUE_STATUSES), StudentDue.net_amount - StudentDue.paid_amount), else_=0
        )
        due_rows = (await db.execute(
            select(StudentDue.student_id, is_transport, func.sum(StudentDue.net_amount),
                   func.sum(StudentDue.paid_amount), func.sum(open_amount))
            .join(FeeHead, FeeHead.id == StudentDue.fee_head_id)
            .where(
                StudentDue.session_year_id == session_year_id,
                StudentDue.status != DueStatus.CANCELLED.value,
                StudentDue.student_id.in_(student_ids),
            )
            .group_by(StudentDue.student_id, is_transport)
        )).all() if student_ids else []
        amounts: Dict[Tuple[int, bool], Tuple[Decimal, Decimal, Decimal]] = {
            (sid, bool(transport)): (Decimal(t or 0), Decimal(p or 0), Decimal(o or 0))
            for sid, transport, t, p, o in due_rows
        }

        # Latest transport assignment (not cancelled) per student in the session
        assignment_rows = (await db.execute(
            select(TransportAssignment, TransportType.name, TransportType.description)
            .join(TransportType, TransportType.id == TransportAssignment.transport_type_id)
            .where(
                TransportAssignment.session_year_id == session_year_id,
                TransportAssignment.is_active == True,  # noqa: E712
                TransportAssignment.student_id.in_(student_ids),
            )
            .order_by(TransportAssignment.start_date, TransportAssignment.id)
        )).all() if student_ids else []
        latest_assignment = {a.student_id: (a, type_desc or type_name) for a, type_name, type_desc in assignment_rows}

        filtered_records = []
        ordered = sorted(students, key=lambda st: (st.class_id or 0, st.section or "", st.first_name, st.last_name))
        for student in ordered:
            assignment = latest_assignment.get(student.id)
            opted = assignment is not None
            if transport_opted is not None and opted != transport_opted:
                continue

            total_fee, paid_fee, pending_fee = amounts.get((student.id, False), (ZERO, ZERO, ZERO))
            total_transport, paid_transport, pending_transport = amounts.get((student.id, True), (ZERO, ZERO, ZERO))

            total_amount = total_fee + total_transport
            total_paid = paid_fee + paid_transport
            total_pending = pending_fee + pending_transport

            fee_payment_status = _status(paid_fee, total_fee)
            transport_payment_status = _status(paid_transport, total_transport) if opted else None

            if payment_status and payment_status.lower() != fee_payment_status.lower():
                continue
            if pending_only and total_pending <= 0:
                continue

            filtered_records.append({
                "student_id": student.id,
                "admission_number": student.admission_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "full_name": f"{student.first_name} {student.last_name}",
                "class_id": student.class_id,
                "class_name": student.class_ref.description if student.class_ref else "",
                "section": student.section,
                "session_year_id": student.session_year_id,
                "session_year_name": student.session_year.description if student.session_year else "",
                "total_fee_amount": total_fee,
                "paid_fee_amount": paid_fee,
                "pending_fee_amount": pending_fee,
                "fee_collection_rate": float(paid_fee / total_fee * 100) if total_fee > 0 else 0.0,
                "fee_payment_status": fee_payment_status,
                "transport_opted": opted,
                "transport_type": assignment[1] if opted else None,
                "monthly_transport_fee": assignment[0].monthly_amount if opted else None,
                "total_transport_amount": total_transport if opted else None,
                "paid_transport_amount": paid_transport if opted else None,
                "pending_transport_amount": pending_transport if opted else None,
                "transport_collection_rate": (
                    float(paid_transport / total_transport * 100) if total_transport > 0 else 0.0
                ) if opted else None,
                "transport_payment_status": transport_payment_status,
                "total_amount": total_amount,
                "total_paid": total_paid,
                "total_pending": total_pending,
                "overall_collection_rate": float(total_paid / total_amount * 100) if total_amount > 0 else 0.0,
            })

        with_transport = [r for r in filtered_records if r["transport_opted"]]
        total_count = len(filtered_records)
        summary = {
            "total_students": total_count,
            "total_fee_amount": sum((r["total_fee_amount"] for r in filtered_records), ZERO),
            "total_paid_amount": sum((r["total_paid"] for r in filtered_records), ZERO),
            "total_pending_amount": sum((r["total_pending"] for r in filtered_records), ZERO),
            "overall_collection_rate": 0.0,
            "students_with_transport": len(with_transport),
            "transport_total_amount": sum((r["total_transport_amount"] for r in with_transport), ZERO),
            "transport_paid_amount": sum((r["paid_transport_amount"] for r in with_transport), ZERO),
            "transport_pending_amount": sum((r["pending_transport_amount"] for r in with_transport), ZERO),
        }
        grand_total = summary["total_fee_amount"] + summary["transport_total_amount"]
        if grand_total > 0:
            summary["overall_collection_rate"] = float(summary["total_paid_amount"] / grand_total * 100)

        start_idx = (page - 1) * per_page
        return filtered_records[start_idx:start_idx + per_page], total_count, summary

    async def get_daily_collection_report_data(
        self,
        db: AsyncSession,
        *,
        from_date: date,
        to_date: date,
        class_id: Optional[int] = None,
        section: Optional[str] = None,
        payment_method_id: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """
        Payments received between two dates, from the unified fee ledger.
        Returns: (page of rows, total count, summary statistics)

        Each payment is shown net of its reversals; a fully reversed payment is left
        out. The transport part is what the payment settled on transport dues; the
        fee part is the rest, including any advance held as credit.
        """
        query = (
            select(Payment, Student)
            .join(Student, Student.id == Payment.student_id)
            .options(joinedload(Student.class_ref))
            .where(
                Payment.kind == PaymentKind.PAYMENT.value,
                Payment.payment_date >= from_date,
                Payment.payment_date <= to_date,
            )
        )
        if class_id:
            query = query.where(Student.class_id == class_id)
        if section:
            query = query.where(Student.section == section)
        if payment_method_id:
            query = query.where(Payment.payment_method_id == payment_method_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(or_(
                Student.first_name.ilike(pattern), Student.last_name.ilike(pattern),
                Student.admission_number.ilike(pattern),
            ))
        rows = (await db.execute(query)).unique().all()
        payment_ids = [p.id for p, _ in rows]

        reversed_by: Dict[int, Decimal] = {}
        transport_by: Dict[int, Decimal] = {}
        if payment_ids:
            # Reversal rows carry negative amounts
            reversed_by = {pid: -Decimal(total) for pid, total in (await db.execute(
                select(Payment.reverses_payment_id, func.sum(Payment.amount))
                .where(Payment.kind == PaymentKind.REVERSAL.value, Payment.reverses_payment_id.in_(payment_ids))
                .group_by(Payment.reverses_payment_id)
            )).all()}
            # Allocations of each payment to transport dues, net of reversal allocations
            transport_by = {pid: Decimal(total) for pid, total in (await db.execute(
                select(PaymentAllocation.payment_id, func.sum(PaymentAllocation.amount))
                .join(StudentDue, StudentDue.id == PaymentAllocation.student_due_id)
                .join(FeeHead, FeeHead.id == StudentDue.fee_head_id)
                .where(PaymentAllocation.payment_id.in_(payment_ids),
                       FeeHead.category == FeeHeadCategory.TRANSPORT.value)
                .group_by(PaymentAllocation.payment_id)
            )).all()}

        methods = {m.id: m.name for m in (await db.execute(select(PaymentMethod))).scalars()}
        sessions = {s.id: s.name for s in (await db.execute(select(SessionYear))).scalars()}
        creator_ids = {p.created_by for p, _ in rows if p.created_by}
        creators = {}
        if creator_ids:
            creators = {u.id: u for u in (await db.execute(select(User).where(User.id.in_(creator_ids)))).scalars()}

        all_records = []
        for payment, student in rows:
            amount = payment.amount - reversed_by.get(payment.id, ZERO)
            if amount <= 0:
                continue
            transport_amount = max(transport_by.get(payment.id, ZERO), ZERO)
            fee_amount = amount - transport_amount
            if transport_amount > 0 and fee_amount > 0:
                payment_type = "Fee + Transport"
            elif transport_amount > 0:
                payment_type = "Transport"
            else:
                payment_type = "Fee"
            creator = creators.get(payment.created_by)
            all_records.append({
                "payment_id": payment.id,
                "receipt_number": payment.receipt_number,
                "payment_date": payment.payment_date,
                "amount": float(amount),
                "payment_method": methods.get(payment.payment_method_id) or "Cash",
                "payment_method_id": payment.payment_method_id,
                "transaction_id": payment.transaction_id,
                "student_id": student.id,
                "admission_number": student.admission_number,
                "student_name": f"{student.first_name} {student.last_name}",
                "class_name": student.class_ref.description if student.class_ref else "",
                "section": student.section,
                "fee_record_id": None,
                "session_year_name": sessions.get(payment.session_year_id, ""),
                "payment_type": payment_type,
                "fee_amount": fee_amount,
                "transport_amount": transport_amount,
                "remarks": payment.remarks,
                "created_by_name": f"{creator.first_name} {creator.last_name}" if creator else None,
                "created_at": payment.created_at,
            })

        all_records.sort(key=lambda x: (x["payment_date"], x["created_at"]), reverse=True)
        total_count = len(all_records)

        def by_method(name: str) -> float:
            return sum(r["amount"] for r in all_records if r["payment_method"].lower() == name)

        summary = {
            "total_collections": total_count,
            "total_amount": sum(r["amount"] for r in all_records),
            "cash_amount": by_method("cash"),
            "online_amount": by_method("online"),
            "upi_amount": by_method("upi"),
            "cheque_amount": by_method("cheque"),
            "card_amount": by_method("card"),
            "fee_collections": float(sum((r["fee_amount"] for r in all_records), ZERO)),
            "transport_collections": float(sum((r["transport_amount"] for r in all_records), ZERO)),
        }

        start_idx = (page - 1) * per_page
        return all_records[start_idx:start_idx + per_page], total_count, summary


# Create singleton instance
report_crud = CRUDReport()

