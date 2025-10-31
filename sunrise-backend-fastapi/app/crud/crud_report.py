from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, case, desc, text
from decimal import Decimal
from datetime import datetime, date

from app.models.student import Student
from app.models.metadata import Gender, Class, SessionYear
from app.models.fee import FeeRecord, MonthlyFeeTracking
from app.models.transport import StudentTransportEnrollment, TransportMonthlyTracking, TransportType


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
        Get fee tracking report data with fee and transport information
        Returns: (list of fee tracking data, total count, summary statistics)
        """
        # Build complex query with JOINs and aggregations
        # Using raw SQL for better performance with complex aggregations
        
        base_query = """
        SELECT 
            s.id as student_id,
            s.admission_number,
            s.first_name,
            s.last_name,
            s.class_id,
            c.description as class_name,
            s.section,
            s.session_year_id,
            sy.description as session_year_name,
            
            -- Fee aggregations
            COALESCE(SUM(mft.monthly_amount), 0) as total_fee_amount,
            COALESCE(SUM(mft.paid_amount), 0) as paid_fee_amount,
            COALESCE(SUM(mft.balance_amount), 0) as pending_fee_amount,

            -- Transport information
            CASE WHEN ste.id IS NOT NULL THEN TRUE ELSE FALSE END as transport_opted,
            tt.description as transport_type,
            ste.monthly_fee as monthly_transport_fee,
            COALESCE(SUM(tmt.monthly_amount), 0) as total_transport_amount,
            COALESCE(SUM(tmt.paid_amount), 0) as paid_transport_amount,
            COALESCE(SUM(tmt.balance_amount), 0) as pending_transport_amount

        FROM students s
        LEFT JOIN classes c ON s.class_id = c.id
        LEFT JOIN session_years sy ON s.session_year_id = sy.id
        LEFT JOIN monthly_fee_tracking mft ON s.id = mft.student_id AND mft.session_year_id = :session_year_id
        LEFT JOIN student_transport_enrollment ste ON s.id = ste.student_id
            AND ste.session_year_id = :session_year_id
            AND ste.is_active = TRUE
        LEFT JOIN transport_types tt ON ste.transport_type_id = tt.id
        LEFT JOIN transport_monthly_tracking tmt ON ste.id = tmt.enrollment_id
        
        WHERE (s.is_deleted = FALSE OR s.is_deleted IS NULL)
            AND s.session_year_id = :session_year_id
        """

        # Build dynamic filters
        params = {"session_year_id": session_year_id}
        additional_filters = []

        if class_id is not None:
            additional_filters.append("AND s.class_id = :class_id")
            params["class_id"] = class_id

        if section is not None and section.strip():
            additional_filters.append("AND s.section = :section")
            params["section"] = section.strip()

        if search:
            additional_filters.append(
                "AND (s.first_name ILIKE :search OR s.last_name ILIKE :search OR s.admission_number ILIKE :search)"
            )
            params["search"] = f"%{search}%"

        if transport_opted is not None:
            if transport_opted:
                additional_filters.append("AND ste.id IS NOT NULL")
            else:
                additional_filters.append("AND ste.id IS NULL")

        # Add additional filters to query
        if additional_filters:
            base_query += " " + " ".join(additional_filters)

        # Add GROUP BY
        base_query += """
        GROUP BY s.id, s.admission_number, s.first_name, s.last_name, s.class_id,
                 c.description, s.section, s.session_year_id, sy.description,
                 ste.id, tt.description, ste.monthly_fee
        """

        # Execute query to get all matching records (for filtering and summary)
        result = await db.execute(text(base_query), params)
        all_records = result.fetchall()

        # Apply post-query filters (payment_status, pending_only)
        filtered_records = []
        for record in all_records:
            # Calculate derived fields
            total_fee = Decimal(str(record.total_fee_amount))
            paid_fee = Decimal(str(record.paid_fee_amount))
            pending_fee = Decimal(str(record.pending_fee_amount))

            total_transport = Decimal(str(record.total_transport_amount)) if record.transport_opted else Decimal("0")
            paid_transport = Decimal(str(record.paid_transport_amount)) if record.transport_opted else Decimal("0")
            pending_transport = Decimal(str(record.pending_transport_amount)) if record.transport_opted else Decimal("0")

            total_amount = total_fee + total_transport
            total_paid = paid_fee + paid_transport
            total_pending = pending_fee + pending_transport

            # Calculate collection rates
            fee_collection_rate = float((paid_fee / total_fee * 100) if total_fee > 0 else 0)
            transport_collection_rate = float((paid_transport / total_transport * 100) if total_transport > 0 else 0) if record.transport_opted else None
            overall_collection_rate = float((total_paid / total_amount * 100) if total_amount > 0 else 0)

            # Determine payment status
            if paid_fee >= total_fee and total_fee > 0:
                fee_payment_status = "Paid"
            elif paid_fee > 0:
                fee_payment_status = "Partial"
            else:
                fee_payment_status = "Pending"

            if record.transport_opted:
                if paid_transport >= total_transport and total_transport > 0:
                    transport_payment_status = "Paid"
                elif paid_transport > 0:
                    transport_payment_status = "Partial"
                else:
                    transport_payment_status = "Pending"
            else:
                transport_payment_status = None

            # Apply payment_status filter
            if payment_status:
                if payment_status.lower() == "paid" and fee_payment_status != "Paid":
                    continue
                elif payment_status.lower() == "partial" and fee_payment_status != "Partial":
                    continue
                elif payment_status.lower() == "pending" and fee_payment_status != "Pending":
                    continue

            # Apply pending_only filter
            if pending_only and total_pending <= 0:
                continue

            # Build record dict
            record_dict = {
                "student_id": record.student_id,
                "admission_number": record.admission_number,
                "first_name": record.first_name,
                "last_name": record.last_name,
                "full_name": f"{record.first_name} {record.last_name}",
                "class_id": record.class_id,
                "class_name": record.class_name or "",
                "section": record.section,
                "session_year_id": record.session_year_id,
                "session_year_name": record.session_year_name or "",
                "total_fee_amount": total_fee,
                "paid_fee_amount": paid_fee,
                "pending_fee_amount": pending_fee,
                "fee_collection_rate": fee_collection_rate,
                "fee_payment_status": fee_payment_status,
                "transport_opted": record.transport_opted,
                "transport_type": record.transport_type,
                "monthly_transport_fee": Decimal(str(record.monthly_transport_fee)) if record.monthly_transport_fee else None,
                "total_transport_amount": total_transport if record.transport_opted else None,
                "paid_transport_amount": paid_transport if record.transport_opted else None,
                "pending_transport_amount": pending_transport if record.transport_opted else None,
                "transport_collection_rate": transport_collection_rate,
                "transport_payment_status": transport_payment_status,
                "total_amount": total_amount,
                "total_paid": total_paid,
                "total_pending": total_pending,
                "overall_collection_rate": overall_collection_rate,
            }

            filtered_records.append(record_dict)

        # Calculate summary statistics
        total_count = len(filtered_records)
        summary = {
            "total_students": total_count,
            "total_fee_amount": sum(r["total_fee_amount"] for r in filtered_records),
            "total_paid_amount": sum(r["total_paid"] for r in filtered_records),
            "total_pending_amount": sum(r["total_pending"] for r in filtered_records),
            "overall_collection_rate": 0.0,
            "students_with_transport": sum(1 for r in filtered_records if r["transport_opted"]),
            "transport_total_amount": sum(r["total_transport_amount"] for r in filtered_records if r["transport_opted"]),
            "transport_paid_amount": sum(r["paid_transport_amount"] for r in filtered_records if r["transport_opted"]),
            "transport_pending_amount": sum(r["pending_transport_amount"] for r in filtered_records if r["transport_opted"]),
        }

        if summary["total_fee_amount"] > 0:
            summary["overall_collection_rate"] = float(
                summary["total_paid_amount"] / (summary["total_fee_amount"] + summary["transport_total_amount"]) * 100
            )

        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = filtered_records[start_idx:end_idx]

        return paginated_records, total_count, summary


# Create singleton instance
report_crud = CRUDReport()

