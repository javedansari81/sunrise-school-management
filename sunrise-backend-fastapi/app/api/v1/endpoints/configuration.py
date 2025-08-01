"""
Configuration endpoint for metadata-driven architecture
Returns all metadata configuration as singleton for frontend consumption
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
import gzip

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.metadata import ConfigurationResponse
from app.crud import get_all_metadata_async
from app.utils.performance_monitor import ConfigurationPerformanceMonitor, timer

router = APIRouter()

# Global configuration cache
_configuration_cache: Dict[str, Any] = {}
_cache_timestamp: float = 0.0

async def get_metadata_configuration(db: AsyncSession) -> Dict[str, Any]:
    """
    Fetch all metadata configuration from database using the new metadata CRUD
    Returns a comprehensive configuration object for frontend consumption
    """

    # Use the new async metadata CRUD helper
    metadata = await get_all_metadata_async(db)

    configuration = {
        "user_types": [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in metadata["user_types"]],
        "session_years": [{"id": item.id, "name": item.name, "start_date": item.start_date, "end_date": item.end_date, "is_current": item.is_current, "is_active": item.is_active} for item in metadata["session_years"]],
        "genders": [{"id": item.id, "name": item.name, "description": item.description, "is_active": item.is_active} for item in metadata["genders"]],
        "classes": [{"id": item.id, "name": item.name, "display_name": item.display_name, "sort_order": item.sort_order, "is_active": item.is_active} for item in metadata["classes"]],
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


@router.get("/")
async def get_configuration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all metadata configuration for the application (OPTIMIZED)

    This endpoint returns all metadata tables as a single configuration object
    that can be used throughout the frontend application as a singleton.

    PERFORMANCE OPTIMIZATIONS:
    - Single database query instead of 13 separate queries
    - Response compression (gzip) for faster network transfer
    - Optimized caching with 5-minute TTL
    - Database indexes for faster metadata queries

    The configuration includes:
    - User types (admin, teacher, student, etc.)
    - Session years (academic years)
    - Genders
    - Classes (PG, LKG, UKG, Class 1-12)
    - Payment types, statuses, and methods
    - Leave types and statuses
    - Expense categories and statuses
    - Employment statuses
    - Qualifications

    Returns:
        Compressed JSON response containing all metadata configuration
    """

    import time
    global _configuration_cache, _cache_timestamp

    start_time = time.time()

    # Cache for 5 minutes (300 seconds)
    current_time = time.time()
    cache_hit = False

    if current_time - _cache_timestamp > 300 or not _configuration_cache:
        with timer("Database Query", cache_status="MISS"):
            _configuration_cache = await get_metadata_configuration(db)
            _cache_timestamp = current_time
    else:
        cache_hit = True

    # Check if client accepts gzip compression
    accept_encoding = request.headers.get("accept-encoding", "")
    use_compression = "gzip" in accept_encoding.lower()

    # Prepare response data
    response_data = _configuration_cache.copy()
    response_data["metadata"]["cache_hit"] = cache_hit
    response_data["metadata"]["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

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
                "Cache-Control": "public, max-age=300",  # 5 minutes
                "X-Response-Time": f"{response_data['metadata']['response_time_ms']}ms",
                "X-Cache-Status": "HIT" if cache_hit else "MISS",
                "X-Compression-Ratio": f"{round((1 - len(compressed_data)/len(json_str)) * 100, 1)}%"
            }
        )
    else:
        # Return uncompressed response
        return JSONResponse(
            content=response_data,
            headers={
                "Cache-Control": "public, max-age=300",  # 5 minutes
                "X-Response-Time": f"{response_data['metadata']['response_time_ms']}ms",
                "X-Cache-Status": "HIT" if cache_hit else "MISS"
            }
        )


@router.post("/refresh")
async def refresh_configuration(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Force refresh the configuration cache
    
    This endpoint allows administrators to force refresh the configuration cache
    when metadata has been updated.
    
    Requires admin privileges.
    """
    
    # Check if user is admin (using metadata relationship)
    if not current_user.user_type or current_user.user_type.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can refresh configuration"
        )
    
    global _configuration_cache, _cache_timestamp

    try:
        import time
        _configuration_cache = await get_metadata_configuration(db)
        _cache_timestamp = time.time()
        
        return {
            "message": "Configuration cache refreshed successfully",
            "timestamp": _cache_timestamp,
            "records_count": {
                "user_types": len(_configuration_cache.get("user_types", [])),
                "session_years": len(_configuration_cache.get("session_years", [])),
                "genders": len(_configuration_cache.get("genders", [])),
                "classes": len(_configuration_cache.get("classes", [])),
                "payment_types": len(_configuration_cache.get("payment_types", [])),
                "payment_statuses": len(_configuration_cache.get("payment_statuses", [])),
                "payment_methods": len(_configuration_cache.get("payment_methods", [])),
                "leave_types": len(_configuration_cache.get("leave_types", [])),
                "leave_statuses": len(_configuration_cache.get("leave_statuses", [])),
                "expense_categories": len(_configuration_cache.get("expense_categories", [])),
                "expense_statuses": len(_configuration_cache.get("expense_statuses", [])),
                "employment_statuses": len(_configuration_cache.get("employment_statuses", [])),
                "qualifications": len(_configuration_cache.get("qualifications", []))
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh configuration: {str(e)}"
        )
