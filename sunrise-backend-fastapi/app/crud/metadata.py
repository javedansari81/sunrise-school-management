"""
CRUD operations for metadata tables
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, text
from sqlalchemy.future import select

from app.models.metadata import (
    UserType, SessionYear, Gender, Class, PaymentType, PaymentStatus, PaymentMethod,
    LeaveType, LeaveStatus, ExpenseCategory, ExpenseStatus, EmploymentStatus, Qualification,
    Department, Position, ReversalReason
)
from app.models.transport import TransportType
from app.models.gallery import GalleryCategory
from app.models.attendance import AttendanceStatus, AttendancePeriod
# Note: Schema imports removed to avoid circular dependencies
# Schemas will be imported in endpoints as needed


class MetadataCRUD:
    """Generic CRUD operations for metadata tables"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def get_all(self, db: Session, active_only: bool = True) -> List[Any]:
        """Get all records from metadata table"""
        query = db.query(self.model_class)
        if active_only:
            query = query.filter(self.model_class.is_active == True)
        return query.order_by(self.model_class.id).all()

    async def get_all_async(self, db: AsyncSession, active_only: bool = True) -> List[Any]:
        """Get all records from metadata table (async version)"""
        query = select(self.model_class)
        if active_only:
            query = query.filter(self.model_class.is_active == True)
        query = query.order_by(self.model_class.id)
        result = await db.execute(query)
        return result.scalars().all()
    
    def get_by_id(self, db: Session, id: int) -> Optional[Any]:
        """Get record by ID"""
        return db.query(self.model_class).filter(self.model_class.id == id).first()

    async def get_by_id_async(self, db: AsyncSession, id: int) -> Optional[Any]:
        """Get record by ID (async version)"""
        query = select(self.model_class).filter(self.model_class.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    def get_by_name(self, db: Session, name: str) -> Optional[Any]:
        """Get record by name"""
        return db.query(self.model_class).filter(self.model_class.name == name).first()

    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[Any]:
        """Get record by name (async version)"""
        query = select(self.model_class).filter(self.model_class.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> Any:
        """Create new record"""
        db_obj = self.model_class(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: Any, obj_in: Dict[str, Any]) -> Any:
        """Update existing record"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Soft delete record (set is_active = False)"""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db_obj.is_active = False
            db.commit()
            return True
        return False


# Create CRUD instances for each metadata table
user_type_crud = MetadataCRUD(UserType)
session_year_crud = MetadataCRUD(SessionYear)
gender_crud = MetadataCRUD(Gender)
class_crud = MetadataCRUD(Class)
payment_type_crud = MetadataCRUD(PaymentType)
payment_status_crud = MetadataCRUD(PaymentStatus)
payment_method_crud = MetadataCRUD(PaymentMethod)
leave_type_crud = MetadataCRUD(LeaveType)
leave_status_crud = MetadataCRUD(LeaveStatus)
expense_category_crud = MetadataCRUD(ExpenseCategory)
expense_status_crud = MetadataCRUD(ExpenseStatus)
employment_status_crud = MetadataCRUD(EmploymentStatus)
qualification_crud = MetadataCRUD(Qualification)
department_crud = MetadataCRUD(Department)
position_crud = MetadataCRUD(Position)
transport_type_crud = MetadataCRUD(TransportType)
gallery_category_crud = MetadataCRUD(GalleryCategory)
reversal_reason_crud = MetadataCRUD(ReversalReason)
attendance_status_crud = MetadataCRUD(AttendanceStatus)
attendance_period_crud = MetadataCRUD(AttendancePeriod)


def get_all_metadata(db: Session) -> Dict[str, List[Any]]:
    """Get all metadata for configuration endpoint (sync version)"""
    return {
        "user_types": user_type_crud.get_all(db),
        "session_years": session_year_crud.get_all(db),
        "genders": gender_crud.get_all(db),
        "classes": class_crud.get_all(db),
        "payment_types": payment_type_crud.get_all(db),
        "payment_statuses": payment_status_crud.get_all(db),
        "payment_methods": payment_method_crud.get_all(db),
        "leave_types": leave_type_crud.get_all(db),
        "leave_statuses": leave_status_crud.get_all(db),
        "expense_categories": expense_category_crud.get_all(db),
        "expense_statuses": expense_status_crud.get_all(db),
        "employment_statuses": employment_status_crud.get_all(db),
        "qualifications": qualification_crud.get_all(db),
        "departments": department_crud.get_all(db),
        "positions": position_crud.get_all(db),
        "gallery_categories": gallery_category_crud.get_all(db)
    }


async def get_all_metadata_async(db: AsyncSession) -> Dict[str, List[Any]]:
    """Get all metadata for configuration endpoint (async version) - OPTIMIZED"""
    import time
    start_time = time.time()

    # Single optimized query to fetch all metadata tables at once
    query = text("""
        SELECT 'user_types' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM user_types WHERE is_active = true

        UNION ALL

        SELECT 'session_years' as table_name, id, name, description,
               NULL::INTEGER as sort_order, start_date, end_date, is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM session_years WHERE is_active = true

        UNION ALL

        SELECT 'genders' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM genders WHERE is_active = true

        UNION ALL

        SELECT 'classes' as table_name, id, name, description,
               sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM classes WHERE is_active = true

        UNION ALL

        SELECT 'payment_types' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM payment_types WHERE is_active = true

        UNION ALL

        SELECT 'payment_statuses' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM payment_statuses WHERE is_active = true

        UNION ALL

        SELECT 'payment_methods' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               requires_reference, is_active, created_at, updated_at
        FROM payment_methods WHERE is_active = true

        UNION ALL

        SELECT 'leave_types' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               max_days_per_year, requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM leave_types WHERE is_active = true

        UNION ALL

        SELECT 'leave_statuses' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, color_code, is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM leave_statuses WHERE is_active = true

        UNION ALL

        SELECT 'expense_categories' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, budget_limit,
               requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM expense_categories WHERE is_active = true

        UNION ALL

        SELECT 'expense_statuses' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, color_code, is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM expense_statuses WHERE is_active = true

        UNION ALL

        SELECT 'employment_statuses' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM employment_statuses WHERE is_active = true

        UNION ALL

        SELECT 'qualifications' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM qualifications WHERE is_active = true

        UNION ALL

        SELECT 'departments' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM departments WHERE is_active = true

        UNION ALL

        SELECT 'positions' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM positions WHERE is_active = true

        UNION ALL

        SELECT 'transport_types' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, base_monthly_fee as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, capacity as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM transport_types WHERE is_active = true

        UNION ALL

        SELECT 'gallery_categories' as table_name, id, name, description,
               display_order as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, icon as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM gallery_categories WHERE is_active = true

        UNION ALL

        SELECT 'inventory_item_types' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, category as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM inventory_item_types WHERE is_active = true

        UNION ALL

        SELECT 'inventory_size_types' as table_name, id, name, description,
               sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM inventory_size_types WHERE is_active = true

        UNION ALL

        SELECT 'reversal_reasons' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM reversal_reasons WHERE is_active = true

        UNION ALL

        SELECT 'attendance_statuses' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM attendance_statuses WHERE is_active = true

        UNION ALL

        SELECT 'attendance_periods' as table_name, id, name, description,
               NULL::INTEGER as sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
               NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, NULL::DECIMAL as budget_limit,
               NULL::BOOLEAN as requires_approval, NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
               NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
        FROM attendance_periods WHERE is_active = true

        ORDER BY table_name, id
    """)

    query_start = time.time()
    result = await db.execute(query)
    rows = result.fetchall()
    query_time_ms = (time.time() - query_start) * 1000

    # Group results by table name
    metadata = {
        "user_types": [],
        "session_years": [],
        "genders": [],
        "classes": [],
        "payment_types": [],
        "payment_statuses": [],
        "payment_methods": [],
        "leave_types": [],
        "leave_statuses": [],
        "expense_categories": [],
        "expense_statuses": [],
        "employment_statuses": [],
        "qualifications": [],
        "departments": [],
        "positions": [],
        "transport_types": [],
        "gallery_categories": [],
        "inventory_item_types": [],
        "inventory_size_types": [],
        "reversal_reasons": [],
        "attendance_statuses": [],
        "attendance_periods": []
    }

    # Process results efficiently
    for row in rows:
        table_name = row.table_name

        # Create object based on table type
        if table_name == 'user_types':
            obj = type('UserType', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'session_years':
            obj = type('SessionYear', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'start_date': row.start_date, 'end_date': row.end_date,
                'is_current': row.is_current, 'is_active': row.is_active
            })()
        elif table_name == 'genders':
            obj = type('Gender', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'classes':
            obj = type('Class', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'sort_order': row.sort_order,
                'is_active': row.is_active
            })()
        elif table_name == 'payment_types':
            obj = type('PaymentType', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'payment_statuses':
            obj = type('PaymentStatus', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'color_code': row.color_code, 'is_final': row.is_final,
                'is_active': row.is_active
            })()
        elif table_name == 'payment_methods':
            obj = type('PaymentMethod', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'requires_reference': row.requires_reference, 'is_active': row.is_active
            })()
        elif table_name == 'leave_types':
            obj = type('LeaveType', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'max_days_per_year': row.max_days_per_year,
                'requires_medical_certificate': row.requires_medical_certificate,
                'is_active': row.is_active
            })()
        elif table_name == 'leave_statuses':
            obj = type('LeaveStatus', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'color_code': row.color_code, 'is_final': row.is_final,
                'is_active': row.is_active
            })()
        elif table_name == 'expense_categories':
            obj = type('ExpenseCategory', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'budget_limit': row.budget_limit, 'requires_approval': row.requires_approval,
                'is_active': row.is_active
            })()
        elif table_name == 'expense_statuses':
            obj = type('ExpenseStatus', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'color_code': row.color_code, 'is_final': row.is_final,
                'is_active': row.is_active
            })()
        elif table_name == 'employment_statuses':
            obj = type('EmploymentStatus', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'qualifications':
            obj = type('Qualification', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'level_order': row.level_order, 'is_active': row.is_active
            })()
        elif table_name == 'departments':
            obj = type('Department', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'positions':
            obj = type('Position', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'transport_types':
            obj = type('TransportType', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'base_monthly_fee': row.budget_limit, 'capacity': row.level_order,
                'is_active': row.is_active
            })()
        elif table_name == 'gallery_categories':
            obj = type('GalleryCategory', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'icon': row.color_code, 'display_order': row.sort_order,
                'is_active': row.is_active
            })()
        elif table_name == 'inventory_item_types':
            obj = type('InventoryItemType', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'category': row.color_code, 'is_active': row.is_active
            })()
        elif table_name == 'inventory_size_types':
            obj = type('InventorySizeType', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'sort_order': row.sort_order, 'is_active': row.is_active
            })()
        elif table_name == 'reversal_reasons':
            obj = type('ReversalReason', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        elif table_name == 'attendance_statuses':
            obj = type('AttendanceStatus', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'color_code': row.color_code, 'is_active': row.is_active
            })()
        elif table_name == 'attendance_periods':
            obj = type('AttendancePeriod', (), {
                'id': row.id, 'name': row.name, 'description': row.description,
                'is_active': row.is_active
            })()
        else:
            continue

        metadata[table_name].append(obj)

    end_time = time.time()

    return metadata


def get_current_session_year(db: Session) -> Optional[SessionYear]:
    """Get the current active session year"""
    return db.query(SessionYear).filter(
        and_(SessionYear.is_current == True, SessionYear.is_active == True)
    ).first()


def get_dropdown_options(db: Session, table_name: str) -> List[Dict[str, Any]]:
    """Get dropdown options for a specific metadata table"""
    crud_mapping = {
        "user_types": user_type_crud,
        "session_years": session_year_crud,
        "genders": gender_crud,
        "classes": class_crud,
        "payment_types": payment_type_crud,
        "payment_statuses": payment_status_crud,
        "payment_methods": payment_method_crud,
        "leave_types": leave_type_crud,
        "leave_statuses": leave_status_crud,
        "expense_categories": expense_category_crud,
        "expense_statuses": expense_status_crud,
        "employment_statuses": employment_status_crud,
        "qualifications": qualification_crud
    }
    
    crud_instance = crud_mapping.get(table_name)
    if not crud_instance:
        return []
    
    records = crud_instance.get_all(db)
    return [
        {
            "id": record.id,
            "name": record.name,
            "is_active": record.is_active
        }
        for record in records
    ]


def validate_metadata_ids(db: Session, **kwargs) -> Dict[str, bool]:
    """Validate that metadata IDs exist and are active"""
    results = {}
    
    if 'user_type_id' in kwargs and kwargs['user_type_id']:
        results['user_type_id'] = bool(user_type_crud.get_by_id(db, kwargs['user_type_id']))
    
    if 'gender_id' in kwargs and kwargs['gender_id']:
        results['gender_id'] = bool(gender_crud.get_by_id(db, kwargs['gender_id']))
    
    if 'class_id' in kwargs and kwargs['class_id']:
        results['class_id'] = bool(class_crud.get_by_id(db, kwargs['class_id']))
    
    if 'session_year_id' in kwargs and kwargs['session_year_id']:
        results['session_year_id'] = bool(session_year_crud.get_by_id(db, kwargs['session_year_id']))
    
    if 'payment_type_id' in kwargs and kwargs['payment_type_id']:
        results['payment_type_id'] = bool(payment_type_crud.get_by_id(db, kwargs['payment_type_id']))
    
    if 'payment_status_id' in kwargs and kwargs['payment_status_id']:
        results['payment_status_id'] = bool(payment_status_crud.get_by_id(db, kwargs['payment_status_id']))
    
    if 'payment_method_id' in kwargs and kwargs['payment_method_id']:
        results['payment_method_id'] = bool(payment_method_crud.get_by_id(db, kwargs['payment_method_id']))
    
    if 'qualification_id' in kwargs and kwargs['qualification_id']:
        results['qualification_id'] = bool(qualification_crud.get_by_id(db, kwargs['qualification_id']))
    
    if 'employment_status_id' in kwargs and kwargs['employment_status_id']:
        results['employment_status_id'] = bool(employment_status_crud.get_by_id(db, kwargs['employment_status_id']))
    
    return results


def get_metadata_name_by_id(db: Session, table_name: str, id: int) -> Optional[str]:
    """Get metadata name by table name and ID"""
    crud_mapping = {
        "user_types": user_type_crud,
        "session_years": session_year_crud,
        "genders": gender_crud,
        "classes": class_crud,
        "payment_types": payment_type_crud,
        "payment_statuses": payment_status_crud,
        "payment_methods": payment_method_crud,
        "leave_types": leave_type_crud,
        "leave_statuses": leave_status_crud,
        "expense_categories": expense_category_crud,
        "expense_statuses": expense_status_crud,
        "employment_statuses": employment_status_crud,
        "qualifications": qualification_crud
    }
    
    crud_instance = crud_mapping.get(table_name)
    if not crud_instance:
        return None
    
    record = crud_instance.get_by_id(db, id)
    return record.name if record else None
