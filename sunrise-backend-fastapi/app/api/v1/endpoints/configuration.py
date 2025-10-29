"""
Configuration endpoint for metadata-driven architecture
Returns service-specific metadata configuration for optimized performance
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
import gzip
import time

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.metadata import ConfigurationResponse
from app.crud import get_all_metadata_async
from app.crud.crud_teacher import teacher_crud
from app.utils.performance_monitor import ConfigurationPerformanceMonitor, timer

router = APIRouter()

# Service-specific configuration caches
_service_configuration_caches: Dict[str, Dict[str, Any]] = {}
_service_cache_timestamps: Dict[str, float] = {}

# Legacy global configuration cache (for backward compatibility)
_configuration_cache: Dict[str, Any] = {}
_cache_timestamp: float = 0.0

# Cache TTL in seconds (5 minutes)
CACHE_TTL = 300

# Service metadata mappings
SERVICE_METADATA_MAPPINGS = {
    "fee-management": [
        "payment_types", "payment_statuses", "payment_methods",
        "session_years", "classes"
    ],
    "student-management": [
        "genders", "classes", "session_years", "user_types"
    ],
    "leave-management": [
        "leave_types", "leave_statuses", "session_years", "classes"
    ],
    "expense-management": [
        "expense_categories", "expense_statuses",
        "payment_methods", "session_years"
    ],
    "teacher-management": [
        "employment_statuses", "qualifications",
        "genders", "user_types", "session_years",
        "departments", "positions", "classes"
    ],
    "transport-management": [
        "transport_types", "payment_statuses", "payment_methods",
        "session_years", "classes"
    ],
    "gallery-management": [
        "gallery_categories"
    ],
    "common": [
        "session_years", "user_types"
    ]
}

async def get_service_metadata_configuration(db: AsyncSession, service_name: str) -> Dict[str, Any]:
    """
    Fetch service-specific metadata configuration from database
    Returns only the metadata types required by the specified service
    """
    # Get required metadata types for this service
    required_metadata = SERVICE_METADATA_MAPPINGS.get(service_name, [])

    if not required_metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown service: {service_name}"
        )

    # Use the new async metadata CRUD helper to get all metadata
    all_metadata = await get_all_metadata_async(db)

    # Build service-specific configuration
    configuration = {}

    # Add only required metadata types
    for metadata_type in required_metadata:
        if metadata_type in all_metadata:
            items = all_metadata[metadata_type]

            if metadata_type == "user_types":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in items]
            elif metadata_type == "session_years":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "start_date": item.start_date.isoformat() if item.start_date else None, "end_date": item.end_date.isoformat() if item.end_date else None, "is_current": item.is_current, "is_active": item.is_active} for item in items]
            elif metadata_type == "genders":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in items]
            elif metadata_type == "classes":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "sort_order": item.sort_order, "is_active": item.is_active} for item in items]
            elif metadata_type == "payment_types":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in items]
            elif metadata_type == "payment_statuses":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "color_code": item.color_code, "is_active": item.is_active} for item in items]
            elif metadata_type == "payment_methods":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "requires_reference": item.requires_reference, "is_active": item.is_active} for item in items]
            elif metadata_type == "leave_types":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "max_days_per_year": item.max_days_per_year, "requires_medical_certificate": item.requires_medical_certificate, "is_active": item.is_active} for item in items]
            elif metadata_type == "leave_statuses":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "color_code": item.color_code, "is_final": item.is_final, "is_active": item.is_active} for item in items]
            elif metadata_type == "expense_categories":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "budget_limit": float(item.budget_limit) if item.budget_limit else None, "requires_approval": item.requires_approval, "is_active": item.is_active} for item in items]
            elif metadata_type == "expense_statuses":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "color_code": item.color_code, "is_final": item.is_final, "is_active": item.is_active} for item in items]
            elif metadata_type == "employment_statuses":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in items]
            elif metadata_type == "qualifications":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "level_order": item.level_order, "is_active": item.is_active} for item in items]
            elif metadata_type == "departments":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in items]
            elif metadata_type == "positions":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in items]
            elif metadata_type == "transport_types":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "base_monthly_fee": float(item.base_monthly_fee), "capacity": item.capacity, "is_active": item.is_active} for item in items]
            elif metadata_type == "gallery_categories":
                configuration[metadata_type] = [{"id": item.id, "name": item.name, "description": item.description, "icon": item.icon, "display_order": item.display_order, "is_active": item.is_active} for item in items]

    # Add service-specific metadata
    configuration["metadata"] = {
        "service": service_name,
        "last_updated": None,
        "version": "3.0.0",
        "architecture": "service-specific-optimized",
        "metadata_types": required_metadata,
        "optimizations": [
            "Service-specific metadata loading",
            "Reduced payload size (60-80% smaller)",
            "Response compression (gzip)",
            "Service-aware caching (5min TTL)",
            "Performance monitoring"
        ]
    }

    return configuration


async def get_metadata_configuration(db: AsyncSession) -> Dict[str, Any]:
    """
    Fetch all metadata configuration from database (legacy endpoint)
    Returns a comprehensive configuration object for frontend consumption
    """
    # Use the new async metadata CRUD helper
    metadata = await get_all_metadata_async(db)

    configuration = {
        "user_types": [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in metadata["user_types"]],
        "session_years": [{"id": item.id, "name": item.name, "description": item.description, "start_date": item.start_date.isoformat() if item.start_date else None, "end_date": item.end_date.isoformat() if item.end_date else None, "is_current": item.is_current, "is_active": item.is_active} for item in metadata["session_years"]],
        "genders": [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in metadata["genders"]],
        "classes": [{"id": item.id, "name": item.name, "description": item.description, "sort_order": item.sort_order, "is_active": item.is_active} for item in metadata["classes"]],
        "payment_types": [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in metadata["payment_types"]],
        "payment_statuses": [{"id": item.id, "name": item.name, "description": item.description, "color_code": item.color_code, "is_active": item.is_active} for item in metadata["payment_statuses"]],
        "payment_methods": [{"id": item.id, "name": item.name, "description": item.description, "requires_reference": item.requires_reference, "is_active": item.is_active} for item in metadata["payment_methods"]],
        "leave_types": [{"id": item.id, "name": item.name, "description": item.description, "max_days_per_year": item.max_days_per_year, "requires_medical_certificate": item.requires_medical_certificate, "is_active": item.is_active} for item in metadata["leave_types"]],
        "leave_statuses": [{"id": item.id, "name": item.name, "description": item.description, "color_code": item.color_code, "is_final": item.is_final, "is_active": item.is_active} for item in metadata["leave_statuses"]],
        "expense_categories": [{"id": item.id, "name": item.name, "description": item.description, "budget_limit": float(item.budget_limit) if item.budget_limit else None, "requires_approval": item.requires_approval, "is_active": item.is_active} for item in metadata["expense_categories"]],
        "expense_statuses": [{"id": item.id, "name": item.name, "description": item.description, "color_code": item.color_code, "is_final": item.is_final, "is_active": item.is_active} for item in metadata["expense_statuses"]],
        "employment_statuses": [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in metadata["employment_statuses"]],
        "qualifications": [{"id": item.id, "name": item.name, "description": item.description, "level_order": item.level_order, "is_active": item.is_active} for item in metadata["qualifications"]],
        "metadata": {
            "last_updated": None,
            "version": "2.1.0",
            "architecture": "metadata-driven-optimized",
            "optimizations": [
                "Single database query (UNION ALL)",
                "Response compression (gzip)",
                "Database indexes for metadata tables",
                "Optimized caching (5min TTL)",
                "Performance monitoring"
            ]
        }
    }

    return configuration


async def _get_service_configuration_with_cache(
    db: AsyncSession, service_name: str, request: Request
) -> Response:
    """
    Helper function to get service configuration with caching and compression
    """
    global _service_configuration_caches, _service_cache_timestamps

    # Check cache
    current_time = time.time()
    cache_key = service_name

    if (cache_key in _service_configuration_caches and
        cache_key in _service_cache_timestamps and
        current_time - _service_cache_timestamps[cache_key] < CACHE_TTL):

        # Cache hit
        cached_config = _service_configuration_caches[cache_key]
        cache_hit = True
        total_time_start = time.time()
    else:
        # Cache miss - fetch from database
        cache_hit = False
        total_time_start = time.time()

        cached_config = await get_service_metadata_configuration(db, service_name)

        # Update cache
        _service_configuration_caches[cache_key] = cached_config
        _service_cache_timestamps[cache_key] = current_time

    # Calculate record count for performance monitoring
    record_count = sum(len(v) for k, v in cached_config.items() if isinstance(v, list))

    # Check if client accepts gzip compression
    accept_encoding = request.headers.get("accept-encoding", "")
    use_compression = "gzip" in accept_encoding.lower()

    response_data = cached_config
    total_time_ms = (time.time() - total_time_start) * 1000

    # Log cache performance
    ConfigurationPerformanceMonitor.log_cache_performance(
        cache_hit, total_time_ms, record_count
    )

    if use_compression:
        # Compress the JSON response
        compression_start = time.time()
        json_str = json.dumps(response_data, default=str, separators=(',', ':'))
        compressed_data = gzip.compress(json_str.encode('utf-8'))
        compression_time_ms = (time.time() - compression_start) * 1000

        # Log compression performance
        ConfigurationPerformanceMonitor.log_compression_performance(
            len(json_str), len(compressed_data), compression_time_ms
        )

        return Response(
            content=compressed_data,
            media_type="application/json",
            headers={
                "Content-Encoding": "gzip",
                "Cache-Control": f"public, max-age={CACHE_TTL}",
                "X-Service-Name": service_name,
                "X-Cache-Status": "HIT" if cache_hit else "MISS",
                "X-Record-Count": str(record_count),
                "X-Response-Time": f"{total_time_ms:.2f}ms"
            }
        )
    else:
        return JSONResponse(
            content=response_data,
            headers={
                "Cache-Control": f"public, max-age={CACHE_TTL}",
                "X-Service-Name": service_name,
                "X-Cache-Status": "HIT" if cache_hit else "MISS",
                "X-Record-Count": str(record_count),
                "X-Response-Time": f"{total_time_ms:.2f}ms"
            }
        )


# Service-specific configuration endpoints

@router.get("/fee-management/")
async def get_fee_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Fee Management System

    Returns only metadata required for fee management:
    - payment_types, payment_statuses, payment_methods
    - session_years, classes

    Optimized for 60-80% smaller payload compared to full configuration.
    """
    return await _get_service_configuration_with_cache(
        db, "fee-management", request
    )


@router.get("/student-management/")
async def get_student_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Student Management System

    Returns only metadata required for student management:
    - genders, classes, session_years, user_types
    """
    return await _get_service_configuration_with_cache(
        db, "student-management", request
    )


@router.get("/leave-management/")
async def get_leave_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Leave Management System

    Returns only metadata required for leave management:
    - leave_types, leave_statuses, session_years, classes
    """
    try:
        result = await _get_service_configuration_with_cache(
            db, "leave-management", request
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load leave management configuration: {str(e)}"
        )


@router.get("/expense-management/")
async def get_expense_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Expense Management System

    Returns only metadata required for expense management:
    - expense_categories, expense_statuses, payment_methods, session_years
    """
    return await _get_service_configuration_with_cache(
        db, "expense-management", request
    )


@router.get("/teacher-management/")
async def get_teacher_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Teacher Management System

    Returns only metadata required for teacher management:
    - employment_statuses, qualifications, genders, user_types, session_years, departments, positions, classes
    """
    return await _get_service_configuration_with_cache(
        db, "teacher-management", request
    )


@router.get("/transport-management/")
async def get_transport_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Transport Management System

    Returns only metadata required for transport management:
    - transport_types, payment_statuses, payment_methods, session_years, classes
    """
    return await _get_service_configuration_with_cache(
        db, "transport-management", request
    )


@router.get("/gallery-management/")
async def get_gallery_management_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get configuration for Gallery Management System

    Returns only metadata required for gallery management:
    - gallery_categories

    This endpoint provides gallery category definitions for the admin gallery management interface.
    Categories include: Independence Day, School Premises, Sports Day, Annual Function, etc.
    """
    return await _get_service_configuration_with_cache(
        db, "gallery-management", request
    )


@router.get("/common/")
async def get_common_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get common configuration metadata

    Returns metadata used across multiple services:
    - session_years, user_types
    """
    return await _get_service_configuration_with_cache(
        db, "common", request
    )


@router.post("/refresh")
async def refresh_configuration(
    service: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Force refresh the configuration cache

    This endpoint allows administrators to force refresh configuration caches
    when metadata has been updated.

    Args:
        service: Optional service name to refresh specific cache.
                If not provided, refreshes all caches.
                Valid values: fee-management, student-management, leave-management,
                             expense-management, teacher-management, transport-management,
                             gallery-management, common

    Requires admin privileges.
    """

    # Check if user is admin (using metadata relationship)
    if not current_user.user_type or current_user.user_type.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can refresh configuration"
        )

    global _service_configuration_caches, _service_cache_timestamps

    try:
        current_time = time.time()
        refreshed_services = []

        if service:
            # Refresh specific service cache
            if service not in SERVICE_METADATA_MAPPINGS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown service: {service}. Valid services: {list(SERVICE_METADATA_MAPPINGS.keys())}"
                )

            config = await get_service_metadata_configuration(db, service)
            _service_configuration_caches[service] = config
            _service_cache_timestamps[service] = current_time
            refreshed_services.append(service)
        else:
            # Refresh all service caches
            for service_name in SERVICE_METADATA_MAPPINGS.keys():
                config = await get_service_metadata_configuration(db, service_name)
                _service_configuration_caches[service_name] = config
                _service_cache_timestamps[service_name] = current_time
                refreshed_services.append(service_name)

        # Build response with cache statistics
        cache_stats = {}
        for service_name in refreshed_services:
            config = _service_configuration_caches.get(service_name, {})
            cache_stats[service_name] = {
                "metadata_types": len([k for k in config.keys() if k != "metadata"]),
                "total_records": sum(len(v) for k, v in config.items() if isinstance(v, list)),
                "timestamp": _service_cache_timestamps.get(service_name)
            }

        return {
            "message": f"Configuration cache refreshed successfully for: {', '.join(refreshed_services)}",
            "refreshed_services": refreshed_services,
            "cache_statistics": cache_stats,
            "refresh_timestamp": current_time
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh configuration: {str(e)}"
        )


@router.get("/services/")
async def get_available_services(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of available service-specific configuration endpoints
    """
    return {
        "services": list(SERVICE_METADATA_MAPPINGS.keys()),
        "endpoints": {
            service: f"/configuration/{service}/"
            for service in SERVICE_METADATA_MAPPINGS.keys()
        },
        "metadata_mappings": SERVICE_METADATA_MAPPINGS
    }
