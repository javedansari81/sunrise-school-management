from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from datetime import datetime, date
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = select(self.model)

        # Filter by is_active if the model has this column
        if hasattr(self.model, 'is_active'):
            query = query.where(self.model.is_active == True)

        # Also exclude soft deleted records if the model has is_deleted column
        if hasattr(self.model, 'is_deleted'):
            query = query.where(
                (self.model.is_deleted == False) | (self.model.is_deleted.is_(None))
            )

        result = await db.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)

        # Convert string dates back to date objects for database insertion
        for key, value in obj_in_data.items():
            if isinstance(value, str) and key in ['date_of_birth', 'joining_date', 'admission_date']:
                try:
                    obj_in_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    # If conversion fails, keep the original value
                    pass

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                value = update_data[field]
                # Convert string dates back to date objects for database insertion
                if isinstance(value, str) and field in ['date_of_birth', 'joining_date', 'admission_date']:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        # If conversion fails, keep the original value
                        pass
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        from datetime import datetime
        obj = await self.get(db, id=id)
        if obj:
            # Soft delete using available columns for compatibility
            if hasattr(obj, 'is_active'):
                obj.is_active = False
            if hasattr(obj, 'is_deleted'):
                obj.is_deleted = True
            if hasattr(obj, 'deleted_date'):
                obj.deleted_date = datetime.utcnow()
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
        return obj
