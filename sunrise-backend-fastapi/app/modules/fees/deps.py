"""
Route permissions of the fee module, taken from app.core.permissions (the same
role mapping the rest of the app uses):

    VIEW_FEES          read fee heads, structures, plans, dues, payments
    CREATE_FEES /
    UPDATE_FEES        configure heads, structures, concessions; generate dues
    PROCESS_PAYMENTS   collect payments, reverse them
    VIEW_FEE_REPORTS   reports
"""
from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.core.permissions import Permission, has_permission
from app.models.user import User, UserTypeEnum

# user_types is a fixed system list (Database/Tables/T100_user_types.sql)
_USER_TYPE_BY_ID = {
    1: UserTypeEnum.ADMIN,
    2: UserTypeEnum.TEACHER,
    3: UserTypeEnum.STUDENT,
    4: UserTypeEnum.STAFF,
    5: UserTypeEnum.PARENT,
    6: UserTypeEnum.SUPER_ADMIN,
}


def user_has(user: User, permission: Permission) -> bool:
    user_type = _USER_TYPE_BY_ID.get(user.user_type_id)
    return user_type is not None and has_permission(user_type, permission)


def require(*permissions: Permission):
    """Dependency: the current user must have every one of the permissions."""

    async def _check(current_user: User = Depends(get_current_active_user)) -> User:
        if not all(user_has(current_user, p) for p in permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user

    return _check


can_view = require(Permission.VIEW_FEES)
can_configure = require(Permission.CREATE_FEES, Permission.UPDATE_FEES)
can_collect = require(Permission.PROCESS_PAYMENTS)
can_report = require(Permission.VIEW_FEE_REPORTS)
