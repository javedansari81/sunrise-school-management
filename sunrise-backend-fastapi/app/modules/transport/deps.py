"""
Route permissions of the transport module. Assignments create and end fee plan
lines, so they use the fee permissions:

    VIEW_FEES                  read setup, rates, assignments and rosters
    CREATE_FEES + UPDATE_FEES  change setup and rates, assign, change,
                               discontinue and pause
"""
from app.core.permissions import Permission
from app.modules.fees.deps import require

can_view = require(Permission.VIEW_FEES)
can_manage = require(Permission.CREATE_FEES, Permission.UPDATE_FEES)
