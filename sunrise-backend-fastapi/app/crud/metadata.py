"""
CRUD operations for metadata tables
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from sqlalchemy.future import select

from app.models.metadata import (
    UserType, SessionYear, Gender, Class, PaymentType, PaymentStatus, PaymentMethod,
    LeaveType, LeaveStatus, ExpenseCategory, ExpenseStatus, EmploymentStatus, Qualification
)
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
    
    def get_by_name(self, db: Session, name: str) -> Optional[Any]:
        """Get record by name"""
        return db.query(self.model_class).filter(self.model_class.name == name).first()
    
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
        "qualifications": qualification_crud.get_all(db)
    }


async def get_all_metadata_async(db: AsyncSession) -> Dict[str, List[Any]]:
    """Get all metadata for configuration endpoint (async version)"""
    return {
        "user_types": await user_type_crud.get_all_async(db),
        "session_years": await session_year_crud.get_all_async(db),
        "genders": await gender_crud.get_all_async(db),
        "classes": await class_crud.get_all_async(db),
        "payment_types": await payment_type_crud.get_all_async(db),
        "payment_statuses": await payment_status_crud.get_all_async(db),
        "payment_methods": await payment_method_crud.get_all_async(db),
        "leave_types": await leave_type_crud.get_all_async(db),
        "leave_statuses": await leave_status_crud.get_all_async(db),
        "expense_categories": await expense_category_crud.get_all_async(db),
        "expense_statuses": await expense_status_crud.get_all_async(db),
        "employment_statuses": await employment_status_crud.get_all_async(db),
        "qualifications": await qualification_crud.get_all_async(db)
    }


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
            "display_name": getattr(record, 'display_name', record.name),
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
