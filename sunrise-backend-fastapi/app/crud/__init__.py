# CRUD module
from .crud_user import user_crud
from .crud_student import student_crud
from .crud_teacher import teacher_crud
from .crud_fee import fee_structure_crud, fee_record_crud, fee_payment_crud
from .crud_leave import leave_request_crud
from .crud_expense import expense_crud

__all__ = [
    "user_crud",
    "student_crud",
    "teacher_crud",
    "fee_structure_crud",
    "fee_record_crud",
    "fee_payment_crud",
    "leave_request_crud",
    "expense_crud"
]
