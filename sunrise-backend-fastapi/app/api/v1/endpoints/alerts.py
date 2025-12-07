"""
Alert/Notification API Endpoints
Provides endpoints for managing user alerts/notifications
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.crud.crud_alert import alert_crud
from app.schemas.alert import (
    AlertResponse, AlertListResponse, AlertWithDetails,
    AlertFilters, AlertStats, AlertUnreadCountResponse, AlertActionResponse
)

router = APIRouter()


def get_user_role(current_user: User) -> str:
    """Helper to get user role string from User model"""
    if current_user.user_type:
        return current_user.user_type.name
    return "ADMIN"


@router.get("/", response_model=AlertListResponse)
@router.get("", response_model=AlertListResponse)
async def get_alerts(
    alert_type_id: Optional[int] = Query(None, description="Filter by alert type ID"),
    alert_status_id: Optional[int] = Query(None, description="Filter by alert status ID"),
    category: Optional[str] = Query(None, description="Filter by category (LEAVE_MANAGEMENT, FINANCIAL, etc.)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (LEAVE_REQUEST, FEE_PAYMENT, etc.)"),
    priority_level: Optional[int] = Query(None, ge=1, le=4, description="Filter by priority (1-4)"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get alerts for the current user with filtering and pagination.
    
    Alerts are filtered based on:
    - User's role (ADMIN, TEACHER, STUDENT)
    - Specific user targeting
    - Various filter parameters
    """
    user_role = get_user_role(current_user)
    
    # Build filters
    filters = AlertFilters(
        alert_type_id=alert_type_id,
        alert_status_id=alert_status_id,
        category=category,
        entity_type=entity_type,
        priority_level=priority_level,
        is_read=is_read
    )
    
    skip = (page - 1) * per_page
    alerts, total = await alert_crud.get_alerts_for_user(
        db,
        user_id=current_user.id,
        user_role=user_role,
        filters=filters,
        skip=skip,
        limit=per_page
    )
    
    # Get unread count
    unread_count = await alert_crud.get_unread_count(
        db, user_id=current_user.id, user_role=user_role
    )
    
    # Enrich alerts with metadata names
    enriched_alerts = []
    for alert in alerts:
        alert_dict = {
            "id": alert.id,
            "alert_type_id": alert.alert_type_id,
            "alert_status_id": alert.alert_status_id,
            "title": alert.title,
            "message": alert.message,
            "entity_type": alert.entity_type,
            "entity_id": alert.entity_id,
            "entity_display_name": alert.entity_display_name,
            "target_role": alert.target_role,
            "target_user_id": alert.target_user_id,
            "metadata": alert.metadata,
            "priority_level": alert.priority_level,
            "actor_user_id": alert.actor_user_id,
            "actor_type": alert.actor_type,
            "actor_name": alert.actor_name,
            "read_at": alert.read_at,
            "read_by": alert.read_by,
            "acknowledged_at": alert.acknowledged_at,
            "acknowledged_by": alert.acknowledged_by,
            "expires_at": alert.expires_at,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at,
            # Enriched fields from relationships
            "alert_type_name": alert.alert_type.name if alert.alert_type else None,
            "alert_type_icon": alert.alert_type.icon if alert.alert_type else None,
            "alert_type_color": alert.alert_type.color_code if alert.alert_type else None,
            "alert_type_category": alert.alert_type.category if alert.alert_type else None,
            "alert_status_name": alert.alert_status.name if alert.alert_status else None,
            "alert_status_color": alert.alert_status.color_code if alert.alert_status else None,
        }
        enriched_alerts.append(AlertResponse(**alert_dict))
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return AlertListResponse(
        alerts=enriched_alerts,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        unread_count=unread_count
    )


@router.get("/unread-count", response_model=AlertUnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread alerts for the current user"""
    user_role = get_user_role(current_user)
    count = await alert_crud.get_unread_count(
        db, user_id=current_user.id, user_role=user_role
    )
    return AlertUnreadCountResponse(unread_count=count)


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert statistics for dashboard"""
    user_role = get_user_role(current_user)
    stats = await alert_crud.get_alert_stats(
        db, user_id=current_user.id, user_role=user_role
    )
    return AlertStats(**stats)


@router.get("/{alert_id}", response_model=AlertWithDetails)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific alert by ID"""
    alert = await alert_crud.get_with_details(db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Check if user has access to this alert
    user_role = get_user_role(current_user)
    has_access = (
        alert.target_role is None or
        alert.target_role == user_role or
        alert.target_user_id == current_user.id
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )

    return alert


@router.patch("/{alert_id}/read", response_model=AlertActionResponse)
async def mark_alert_as_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a specific alert as read"""
    alert = await alert_crud.mark_as_read(
        db, alert_id=alert_id, user_id=current_user.id
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return AlertActionResponse(message="Alert marked as read", alert_id=alert_id)


@router.patch("/mark-all-read", response_model=AlertActionResponse)
async def mark_all_alerts_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all alerts as read for the current user"""
    user_role = get_user_role(current_user)
    count = await alert_crud.mark_all_as_read(
        db, user_id=current_user.id, user_role=user_role
    )
    return AlertActionResponse(message=f"Marked {count} alerts as read", count=count)


@router.patch("/{alert_id}/acknowledge", response_model=AlertActionResponse)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge an alert (for alerts requiring acknowledgment)"""
    alert = await alert_crud.acknowledge_alert(
        db, alert_id=alert_id, user_id=current_user.id
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return AlertActionResponse(message="Alert acknowledged", alert_id=alert_id)


@router.delete("/{alert_id}", response_model=AlertActionResponse)
async def dismiss_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Dismiss/soft-delete an alert"""
    alert = await alert_crud.dismiss_alert(
        db, alert_id=alert_id, user_id=current_user.id
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return AlertActionResponse(message="Alert dismissed", alert_id=alert_id)

