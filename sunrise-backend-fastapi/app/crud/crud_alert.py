"""
CRUD operations for Alert system
Following established patterns from crud_leave.py and crud_fee.py
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, func, desc, update, text
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.alert import Alert, AlertType, AlertStatus
from app.schemas.alert import AlertCreate, AlertUpdate, AlertFilters


class CRUDAlert(CRUDBase[Alert, AlertCreate, AlertUpdate]):
    """
    CRUD operations for Alerts with role-based access
    
    Alert Status IDs:
    - 1: UNREAD
    - 2: READ
    - 3: ACKNOWLEDGED
    - 4: DISMISSED
    - 5: EXPIRED
    """

    async def create_alert(
        self,
        db: AsyncSession,
        *,
        alert_type_id: int,
        title: str,
        message: str,
        entity_type: str,
        entity_id: int,
        actor_user_id: Optional[int] = None,
        actor_type: Optional[str] = None,
        actor_name: Optional[str] = None,
        entity_display_name: Optional[str] = None,
        target_role: Optional[str] = None,
        target_user_id: Optional[int] = None,
        alert_metadata: Optional[Dict[str, Any]] = None,
        priority_level: int = 2,
        expires_at: Optional[datetime] = None,
        auto_commit: bool = True
    ) -> Alert:
        """Create a new alert with all necessary context"""
        alert = Alert(
            alert_type_id=alert_type_id,
            alert_status_id=1,  # UNREAD
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            actor_type=actor_type,
            actor_name=actor_name,
            entity_display_name=entity_display_name,
            target_role=target_role,
            target_user_id=target_user_id,
            alert_metadata=alert_metadata or {},
            priority_level=priority_level,
            expires_at=expires_at
        )
        db.add(alert)
        if auto_commit:
            await db.commit()
            await db.refresh(alert)
        else:
            await db.flush()
        return alert

    async def get_alerts_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        user_role: str,
        filters: Optional[AlertFilters] = None,
        skip: int = 0,
        limit: int = 25
    ) -> Tuple[List[Alert], int]:
        """Get alerts visible to a specific user/role with filtering and pagination"""

        # Base query with relationships
        # Alert visibility logic:
        # 1. If target_user_id is set, ONLY that specific user should see it
        # 2. If target_user_id is NULL and target_role is set, all users with that role see it
        # 3. If both target_role and target_user_id are NULL, it's a broadcast (everyone sees it)
        query = (
            select(Alert)
            .options(
                joinedload(Alert.alert_type),
                joinedload(Alert.alert_status)
            )
            .where(
                and_(
                    or_(Alert.is_deleted == False, Alert.is_deleted.is_(None)),
                    or_(
                        # Case 1: Targeted to specific user (ignore role, only user_id matters)
                        Alert.target_user_id == user_id,
                        # Case 2: Targeted to role only (no specific user)
                        and_(
                            Alert.target_role == user_role,
                            Alert.target_user_id.is_(None)
                        ),
                        # Case 3: Broadcast - visible to everyone (both NULL)
                        and_(
                            Alert.target_role.is_(None),
                            Alert.target_user_id.is_(None)
                        )
                    )
                )
            )
        )

        # Apply filters if provided
        if filters:
            if filters.alert_type_id:
                query = query.where(Alert.alert_type_id == filters.alert_type_id)
            if filters.alert_status_id:
                query = query.where(Alert.alert_status_id == filters.alert_status_id)
            if filters.entity_type:
                query = query.where(Alert.entity_type == filters.entity_type)
            if filters.priority_level:
                query = query.where(Alert.priority_level == filters.priority_level)
            if filters.from_date:
                query = query.where(Alert.created_at >= filters.from_date)
            if filters.to_date:
                query = query.where(Alert.created_at <= filters.to_date)
            if filters.is_read is not None:
                if filters.is_read:
                    query = query.where(Alert.alert_status_id != 1)
                else:
                    query = query.where(Alert.alert_status_id == 1)
            if filters.category:
                # Join with alert_type to filter by category
                query = query.join(AlertType, Alert.alert_type_id == AlertType.id).where(
                    AlertType.category == filters.category
                )

        # Get total count before pagination
        count_subquery = query.with_only_columns(func.count(Alert.id)).order_by(None)
        total_result = await db.execute(count_subquery)
        total = total_result.scalar() or 0

        # Apply ordering and pagination
        query = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        alerts = result.unique().scalars().all()

        return list(alerts), total

    async def get_with_details(self, db: AsyncSession, id: int) -> Optional[Alert]:
        """Get a single alert with all relationship details"""
        query = (
            select(Alert)
            .options(
                joinedload(Alert.alert_type),
                joinedload(Alert.alert_status)
            )
            .where(Alert.id == id)
        )
        result = await db.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_unread_count(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        user_role: str
    ) -> int:
        """Get count of unread alerts for a user"""
        # Same visibility logic as get_alerts_for_user
        query = select(func.count(Alert.id)).where(
            and_(
                or_(Alert.is_deleted == False, Alert.is_deleted.is_(None)),
                Alert.alert_status_id == 1,  # UNREAD
                or_(
                    # Case 1: Targeted to specific user
                    Alert.target_user_id == user_id,
                    # Case 2: Targeted to role only (no specific user)
                    and_(
                        Alert.target_role == user_role,
                        Alert.target_user_id.is_(None)
                    ),
                    # Case 3: Broadcast - visible to everyone
                    and_(
                        Alert.target_role.is_(None),
                        Alert.target_user_id.is_(None)
                    )
                )
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def mark_as_read(
        self,
        db: AsyncSession,
        *,
        alert_id: int,
        user_id: int
    ) -> Optional[Alert]:
        """Mark an alert as read"""
        alert = await self.get(db, id=alert_id)
        if alert and alert.alert_status_id == 1:  # Only update if UNREAD
            alert.alert_status_id = 2  # READ
            alert.read_at = datetime.utcnow()
            alert.read_by = user_id
            alert.updated_at = datetime.utcnow()
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
        return alert

    async def mark_all_as_read(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        user_role: str
    ) -> int:
        """Mark all unread alerts as read for a user"""
        # Same visibility logic as get_alerts_for_user
        stmt = (
            update(Alert)
            .where(
                and_(
                    or_(Alert.is_deleted == False, Alert.is_deleted.is_(None)),
                    Alert.alert_status_id == 1,  # UNREAD
                    or_(
                        # Case 1: Targeted to specific user
                        Alert.target_user_id == user_id,
                        # Case 2: Targeted to role only (no specific user)
                        and_(
                            Alert.target_role == user_role,
                            Alert.target_user_id.is_(None)
                        ),
                        # Case 3: Broadcast - visible to everyone
                        and_(
                            Alert.target_role.is_(None),
                            Alert.target_user_id.is_(None)
                        )
                    )
                )
            )
            .values(
                alert_status_id=2,  # READ
                read_at=datetime.utcnow(),
                read_by=user_id,
                updated_at=datetime.utcnow()
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def acknowledge_alert(
        self,
        db: AsyncSession,
        *,
        alert_id: int,
        user_id: int
    ) -> Optional[Alert]:
        """Acknowledge an alert (for alerts that require acknowledgment)"""
        alert = await self.get(db, id=alert_id)
        if alert:
            alert.alert_status_id = 3  # ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            alert.updated_at = datetime.utcnow()
            # Also mark as read if not already
            if not alert.read_at:
                alert.read_at = datetime.utcnow()
                alert.read_by = user_id
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
        return alert

    async def dismiss_alert(
        self,
        db: AsyncSession,
        *,
        alert_id: int,
        user_id: int
    ) -> Optional[Alert]:
        """Dismiss/soft-delete an alert"""
        alert = await self.get(db, id=alert_id)
        if alert:
            alert.is_deleted = True
            alert.deleted_date = datetime.utcnow()
            alert.alert_status_id = 4  # DISMISSED
            alert.updated_at = datetime.utcnow()
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
        return alert

    async def get_alert_stats(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        user_role: str
    ) -> Dict[str, Any]:
        """Get alert statistics for dashboard"""

        # Base filter for user's visible alerts (same visibility logic as get_alerts_for_user)
        base_filter = and_(
            or_(Alert.is_deleted == False, Alert.is_deleted.is_(None)),
            or_(
                # Case 1: Targeted to specific user
                Alert.target_user_id == user_id,
                # Case 2: Targeted to role only (no specific user)
                and_(
                    Alert.target_role == user_role,
                    Alert.target_user_id.is_(None)
                ),
                # Case 3: Broadcast - visible to everyone
                and_(
                    Alert.target_role.is_(None),
                    Alert.target_user_id.is_(None)
                )
            )
        )

        # Total alerts
        total_query = select(func.count(Alert.id)).where(base_filter)
        total_result = await db.execute(total_query)
        total_alerts = total_result.scalar() or 0

        # Unread count
        unread_query = select(func.count(Alert.id)).where(
            and_(base_filter, Alert.alert_status_id == 1)
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar() or 0

        # By category
        category_query = (
            select(AlertType.category, func.count(Alert.id))
            .join(AlertType, Alert.alert_type_id == AlertType.id)
            .where(base_filter)
            .group_by(AlertType.category)
        )
        category_result = await db.execute(category_query)
        by_category = {row[0]: row[1] for row in category_result.fetchall()}

        # By priority
        priority_query = (
            select(Alert.priority_level, func.count(Alert.id))
            .where(base_filter)
            .group_by(Alert.priority_level)
        )
        priority_result = await db.execute(priority_query)
        by_priority = {str(row[0]): row[1] for row in priority_result.fetchall()}

        # Recent (last 24 hours)
        recent_query = select(func.count(Alert.id)).where(
            and_(
                base_filter,
                Alert.created_at >= datetime.utcnow() - timedelta(hours=24)
            )
        )
        recent_result = await db.execute(recent_query)
        recent_count = recent_result.scalar() or 0

        return {
            "total_alerts": total_alerts,
            "unread_count": unread_count,
            "by_category": by_category,
            "by_priority": by_priority,
            "recent_count": recent_count
        }


# Create singleton instance
alert_crud = CRUDAlert(Alert)

