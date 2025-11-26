"""
Password configuration settings for the application.

This module defines password-related constants and settings used throughout
the authentication system, including default passwords for resets and
password validation rules.
"""


class PasswordConfig:
    """Password configuration constants"""
    
    # Default password for admin-assisted resets
    DEFAULT_PASSWORD = "Sunrise@001"
    
    # Password validation rules
    MIN_LENGTH = 6
    MAX_LENGTH = 72  # bcrypt byte limit
    
    # Password change settings
    FORCE_CHANGE_ON_RESET = False  # Users can optionally change password
    
    # Future: Password expiry settings (not implemented)
    PASSWORD_EXPIRY_DAYS = None  # None = never expires


# Export for easy access
DEFAULT_PASSWORD = PasswordConfig.DEFAULT_PASSWORD
MIN_PASSWORD_LENGTH = PasswordConfig.MIN_LENGTH
MAX_PASSWORD_LENGTH = PasswordConfig.MAX_LENGTH

