from typing import List, Dict, Any
from enum import Enum
import logging

from app.schemas.user import UserTypeEnum
from app.core.logging import log_permission_check


class Permission(str, Enum):
    # Student Management
    VIEW_STUDENTS = "view_students"
    CREATE_STUDENTS = "create_students"
    UPDATE_STUDENTS = "update_students"
    DELETE_STUDENTS = "delete_students"
    
    # Teacher Management
    VIEW_TEACHERS = "view_teachers"
    CREATE_TEACHERS = "create_teachers"
    UPDATE_TEACHERS = "update_teachers"
    DELETE_TEACHERS = "delete_teachers"
    
    # Fee Management
    VIEW_FEES = "view_fees"
    CREATE_FEES = "create_fees"
    UPDATE_FEES = "update_fees"
    PROCESS_PAYMENTS = "process_payments"
    VIEW_FEE_REPORTS = "view_fee_reports"
    
    # Leave Management
    VIEW_LEAVES = "view_leaves"
    CREATE_LEAVES = "create_leaves"
    UPDATE_LEAVES = "update_leaves"
    APPROVE_LEAVES = "approve_leaves"
    VIEW_LEAVE_REPORTS = "view_leave_reports"
    
    # Expense Management
    VIEW_EXPENSES = "view_expenses"
    CREATE_EXPENSES = "create_expenses"
    UPDATE_EXPENSES = "update_expenses"
    APPROVE_EXPENSES = "approve_expenses"
    DELETE_EXPENSES = "delete_expenses"
    VIEW_EXPENSE_REPORTS = "view_expense_reports"
    
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"
    
    # Profile Access
    VIEW_OWN_PROFILE = "view_own_profile"
    UPDATE_OWN_PROFILE = "update_own_profile"
    VIEW_STUDENT_PROFILE = "view_student_profile"
    VIEW_TEACHER_PROFILE = "view_teacher_profile"
    
    # Dashboard Access
    VIEW_ADMIN_DASHBOARD = "view_admin_dashboard"
    VIEW_TEACHER_DASHBOARD = "view_teacher_dashboard"
    VIEW_STUDENT_DASHBOARD = "view_student_dashboard"


# Role-based permissions mapping
ROLE_PERMISSIONS: Dict[UserTypeEnum, List[Permission]] = {
    UserTypeEnum.ADMIN: [
        # Full access to everything
        Permission.VIEW_STUDENTS,
        Permission.CREATE_STUDENTS,
        Permission.UPDATE_STUDENTS,
        Permission.DELETE_STUDENTS,
        Permission.VIEW_TEACHERS,
        Permission.CREATE_TEACHERS,
        Permission.UPDATE_TEACHERS,
        Permission.DELETE_TEACHERS,
        Permission.VIEW_FEES,
        Permission.CREATE_FEES,
        Permission.UPDATE_FEES,
        Permission.PROCESS_PAYMENTS,
        Permission.VIEW_FEE_REPORTS,
        Permission.VIEW_LEAVES,
        Permission.CREATE_LEAVES,
        Permission.UPDATE_LEAVES,
        Permission.APPROVE_LEAVES,
        Permission.VIEW_LEAVE_REPORTS,
        Permission.VIEW_EXPENSES,
        Permission.CREATE_EXPENSES,
        Permission.UPDATE_EXPENSES,
        Permission.APPROVE_EXPENSES,
        Permission.DELETE_EXPENSES,
        Permission.VIEW_EXPENSE_REPORTS,
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.UPDATE_USERS,
        Permission.DELETE_USERS,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_STUDENT_PROFILE,
        Permission.VIEW_TEACHER_PROFILE,
        Permission.VIEW_ADMIN_DASHBOARD,
    ],
    
    UserTypeEnum.TEACHER: [
        # Limited access for teachers
        Permission.VIEW_STUDENTS,
        Permission.VIEW_TEACHERS,
        Permission.VIEW_FEES,
        Permission.VIEW_LEAVES,
        Permission.CREATE_LEAVES,
        Permission.UPDATE_LEAVES,
        Permission.VIEW_EXPENSES,
        Permission.CREATE_EXPENSES,
        Permission.UPDATE_EXPENSES,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_STUDENT_PROFILE,
        Permission.VIEW_TEACHER_PROFILE,
        Permission.VIEW_TEACHER_DASHBOARD,
    ],
    
    UserTypeEnum.STUDENT: [
        # Very limited access for students
        Permission.VIEW_LEAVES,
        Permission.CREATE_LEAVES,
        Permission.UPDATE_LEAVES,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_STUDENT_DASHBOARD,
    ],
    
    UserTypeEnum.STAFF: [
        # Staff access similar to teachers but more limited
        Permission.VIEW_STUDENTS,
        Permission.VIEW_TEACHERS,
        Permission.VIEW_FEES,
        Permission.VIEW_LEAVES,
        Permission.VIEW_EXPENSES,
        Permission.CREATE_EXPENSES,
        Permission.UPDATE_EXPENSES,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
    ],
    
    UserTypeEnum.PARENT: [
        # Parent access to their child's information only
        Permission.VIEW_LEAVES,
        Permission.CREATE_LEAVES,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_STUDENT_PROFILE,  # Only their child's profile
    ],

    UserTypeEnum.SUPER_ADMIN: [
        # Full access to everything - identical to ADMIN
        # SUPER_ADMIN serves as foundation for future enhanced privileges
        Permission.VIEW_STUDENTS,
        Permission.CREATE_STUDENTS,
        Permission.UPDATE_STUDENTS,
        Permission.DELETE_STUDENTS,
        Permission.VIEW_TEACHERS,
        Permission.CREATE_TEACHERS,
        Permission.UPDATE_TEACHERS,
        Permission.DELETE_TEACHERS,
        Permission.VIEW_FEES,
        Permission.CREATE_FEES,
        Permission.UPDATE_FEES,
        Permission.PROCESS_PAYMENTS,
        Permission.VIEW_FEE_REPORTS,
        Permission.VIEW_LEAVES,
        Permission.CREATE_LEAVES,
        Permission.UPDATE_LEAVES,
        Permission.APPROVE_LEAVES,
        Permission.VIEW_LEAVE_REPORTS,
        Permission.VIEW_EXPENSES,
        Permission.CREATE_EXPENSES,
        Permission.UPDATE_EXPENSES,
        Permission.APPROVE_EXPENSES,
        Permission.DELETE_EXPENSES,
        Permission.VIEW_EXPENSE_REPORTS,
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.UPDATE_USERS,
        Permission.DELETE_USERS,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_STUDENT_PROFILE,
        Permission.VIEW_TEACHER_PROFILE,
        Permission.VIEW_ADMIN_DASHBOARD,
    ],
}


def get_user_permissions(user_type: UserTypeEnum) -> List[str]:
    """Get list of permissions for a user type"""
    try:
        log_permission_check(f"Getting permissions for user type: {user_type}",
                           user_type=str(user_type))
        permissions = ROLE_PERMISSIONS.get(user_type, [])
        permission_values = [perm.value for perm in permissions]
        log_permission_check(f"Found {len(permission_values)} permissions",
                           user_type=str(user_type), count=len(permission_values))
        return permission_values
    except Exception as perm_error:
        log_permission_check(f"Error getting permissions: {str(perm_error)}",
                           "error", user_type=str(user_type), error_type=type(perm_error).__name__)
        logging.exception("Full permissions error traceback:")
        # Return empty list as fallback
        return []


def has_permission(user_type: UserTypeEnum, permission: Permission) -> bool:
    """Check if a user type has a specific permission"""
    user_permissions = ROLE_PERMISSIONS.get(user_type, [])
    return permission in user_permissions


def get_dashboard_permissions(user_type: UserTypeEnum) -> Dict[str, Any]:
    """Get dashboard-specific permissions and features for a user type"""
    log_permission_check(f"Getting dashboard permissions for user type: {user_type}", user_type=str(user_type))

    permissions = get_user_permissions(user_type)

    dashboard_config = {
        "user_type": user_type.value,
        "permissions": permissions,
        "features": {
            "student_management": has_permission(user_type, Permission.VIEW_STUDENTS),
            "teacher_management": has_permission(user_type, Permission.VIEW_TEACHERS),
            "fee_management": has_permission(user_type, Permission.VIEW_FEES),
            "leave_management": has_permission(user_type, Permission.VIEW_LEAVES),
            "expense_management": has_permission(user_type, Permission.VIEW_EXPENSES),
            "user_management": has_permission(user_type, Permission.VIEW_USERS),
            "reports": has_permission(user_type, Permission.VIEW_FEE_REPORTS) or 
                     has_permission(user_type, Permission.VIEW_LEAVE_REPORTS) or
                     has_permission(user_type, Permission.VIEW_EXPENSE_REPORTS),
        },
        "actions": {
            "can_create_students": has_permission(user_type, Permission.CREATE_STUDENTS),
            "can_create_teachers": has_permission(user_type, Permission.CREATE_TEACHERS),
            "can_process_payments": has_permission(user_type, Permission.PROCESS_PAYMENTS),
            "can_approve_leaves": has_permission(user_type, Permission.APPROVE_LEAVES),
            "can_approve_expenses": has_permission(user_type, Permission.APPROVE_EXPENSES),
        }
    }

    log_permission_check(f"Dashboard config created with {len(dashboard_config['features'])} features",
                       feature_count=len(dashboard_config['features']))
    return dashboard_config


def filter_menu_items(user_type: UserTypeEnum) -> List[Dict[str, Any]]:
    """Filter menu items based on user permissions"""
    log_permission_check(f"Filtering menu items for user type: {user_type}", user_type=str(user_type))

    all_menu_items = [
        {
            "name": "Dashboard",
            "path": "/dashboard",
            "icon": "dashboard",
            "permission": None  # Always visible
        },
        {
            "name": "Students",
            "path": "/students",
            "icon": "students",
            "permission": Permission.VIEW_STUDENTS
        },
        {
            "name": "Teachers",
            "path": "/teachers",
            "icon": "teachers",
            "permission": Permission.VIEW_TEACHERS
        },
        {
            "name": "Fees",
            "path": "/fees",
            "icon": "fees",
            "permission": Permission.VIEW_FEES
        },
        {
            "name": "Leaves",
            "path": "/leaves",
            "icon": "leaves",
            "permission": Permission.VIEW_LEAVES
        },
        {
            "name": "Expenses",
            "path": "/expenses",
            "icon": "expenses",
            "permission": Permission.VIEW_EXPENSES
        },
        {
            "name": "Users",
            "path": "/users",
            "icon": "users",
            "permission": Permission.VIEW_USERS
        },
        {
            "name": "Profile",
            "path": "/profile",
            "icon": "profile",
            "permission": Permission.VIEW_OWN_PROFILE
        }
    ]
    
    # Filter menu items based on permissions
    filtered_menu = []
    for item in all_menu_items:
        if item["permission"] is None or has_permission(user_type, item["permission"]):
            filtered_menu.append(item)
            log_permission_check(f"Menu item included: {item['name']}",
                               item_name=item['name'], permission=str(item['permission']))
        else:
            log_permission_check(f"Menu item excluded: {item['name']}",
                               "warning", item_name=item['name'], permission=str(item['permission']))

    log_permission_check(f"Total menu items returned: {len(filtered_menu)}", count=len(filtered_menu))
    return filtered_menu
