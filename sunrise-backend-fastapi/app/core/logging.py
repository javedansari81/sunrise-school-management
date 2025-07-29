import logging
import sys
from typing import Dict, Any
from datetime import datetime

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the application
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout,
        force=True
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Create application logger
    app_logger = logging.getLogger("sunrise_app")
    app_logger.setLevel(level)
    
    return app_logger

# Create loggers for different modules
auth_logger = logging.getLogger("sunrise_app.auth")
crud_logger = logging.getLogger("sunrise_app.crud")
permissions_logger = logging.getLogger("sunrise_app.permissions")
db_logger = logging.getLogger("sunrise_app.database")

def log_auth_step(step: str, message: str, level: str = "info", **kwargs) -> None:
    """Log authentication steps with consistent formatting"""
    log_message = f"[{step}] {message}"
    if kwargs:
        log_message += f" | Data: {kwargs}"
    
    getattr(auth_logger, level.lower())(log_message)

def log_crud_operation(operation: str, message: str, level: str = "info", **kwargs) -> None:
    """Log CRUD operations with consistent formatting"""
    log_message = f"[{operation}] {message}"
    if kwargs:
        log_message += f" | Data: {kwargs}"
    
    getattr(crud_logger, level.lower())(log_message)

def log_permission_check(message: str, level: str = "info", **kwargs) -> None:
    """Log permission checks with consistent formatting"""
    log_message = f"[PERMISSIONS] {message}"
    if kwargs:
        log_message += f" | Data: {kwargs}"
    
    getattr(permissions_logger, level.lower())(log_message)

def log_database_operation(message: str, level: str = "info", **kwargs) -> None:
    """Log database operations with consistent formatting"""
    log_message = f"[DATABASE] {message}"
    if kwargs:
        log_message += f" | Data: {kwargs}"
    
    getattr(db_logger, level.lower())(log_message)
