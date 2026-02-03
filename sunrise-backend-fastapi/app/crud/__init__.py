# CRUD module
from .crud_user import user_crud
from .crud_student import student_crud
from .crud_teacher import teacher_crud
from .crud_fee import fee_structure_crud, fee_record_crud, fee_payment_crud
from .crud_leave import leave_request_crud
from .crud_expense import expense_crud
from .crud_report import report_crud
from .crud_alert import alert_crud
from .metadata import (
    user_type_crud, session_year_crud, gender_crud, class_crud,
    payment_type_crud, payment_status_crud, payment_method_crud,
    leave_type_crud, leave_status_crud, expense_category_crud,
    expense_status_crud, employment_status_crud, qualification_crud,
    department_crud, position_crud,
    get_all_metadata, get_all_metadata_async, get_current_session_year, get_dropdown_options,
    validate_metadata_ids, get_metadata_name_by_id
)
from .crud_session_progression import (
    get_progression_actions, get_progression_action_by_id,
    get_eligible_students_for_progression, get_next_class_id, get_previous_class_id,
    create_session_history_record, progress_student, bulk_progress_students,
    get_student_progression_history, rollback_progression_batch,
    get_progression_statistics, ProgressionActionIds, HIGHEST_CLASS_ID
)

__all__ = [
    "user_crud",
    "student_crud",
    "teacher_crud",
    "fee_structure_crud",
    "fee_record_crud",
    "fee_payment_crud",
    "leave_request_crud",
    "expense_crud",
    "alert_crud",
    # Metadata CRUD
    "user_type_crud", "session_year_crud", "gender_crud", "class_crud",
    "payment_type_crud", "payment_status_crud", "payment_method_crud",
    "leave_type_crud", "leave_status_crud", "expense_category_crud",
    "expense_status_crud", "employment_status_crud", "qualification_crud",
    "department_crud", "position_crud",
    # Metadata helpers
    "get_all_metadata", "get_all_metadata_async", "get_current_session_year", "get_dropdown_options",
    "validate_metadata_ids", "get_metadata_name_by_id",
    # Session Progression
    "get_progression_actions", "get_progression_action_by_id",
    "get_eligible_students_for_progression", "get_next_class_id", "get_previous_class_id",
    "create_session_history_record", "progress_student", "bulk_progress_students",
    "get_student_progression_history", "rollback_progression_batch",
    "get_progression_statistics", "ProgressionActionIds", "HIGHEST_CLASS_ID"
]
