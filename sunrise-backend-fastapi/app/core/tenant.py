"""
Automatic tenant (school) scoping for SQLAlchemy sessions.

The current school is stored on the session (``session.info``) by the request
dependencies in ``app.api.deps``. Two session events then enforce isolation:

* ``do_orm_execute`` adds ``school_id = <current school>`` criteria for every
  ``TenantMixin`` model in ORM SELECT, UPDATE and DELETE statements. The criteria
  also propagate to relationship and lazy loads.
* ``before_flush`` stamps ``school_id`` on new tenant rows and refuses to write
  a row that belongs to another school.

Both fail closed: touching a tenant model on a session without a school raises
``TenantContextError`` instead of silently returning or writing every school's
data. Code that must work across schools (school lookup, platform admin tasks)
uses ``tenant_bypass``.

Raw SQL (``text()``) cannot be rewritten, so it is checked instead. On a session
bound to a school, a raw statement must filter by the ``:school_id`` parameter;
the parameter is filled in from the session, and a different value passed by the
caller is refused. A raw statement that reads only global tables (fixed system
lists, pure SQL functions) is built with ``global_sql()``. Anything else fails
instead of running unscoped.

Row-level security (PostgreSQL) is the last layer. Every table with a
``school_id`` column has a policy that only shows and accepts rows of the school
in the ``app.school_id`` setting, or every row when ``app.bypass_rls`` is ``on``
(see ``Database/Functions/F900_tenant_row_level_security.sql``). Before a session
runs a statement or flushes, ``_sync_rls_settings`` copies the session's school
and bypass state into those two settings, transaction-local, so a statement that
slips past the checks above still only reaches its own school's rows. Without
either setting a tenant table shows no rows and accepts no writes.
"""
from contextlib import contextmanager
from typing import Iterator, Optional, Union

from sqlalchemy import event, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria
from sqlalchemy.sql.elements import TextClause

from app.models.tenant import TenantMixin

SCHOOL_ID_KEY = "school_id"
BYPASS_KEY = "tenant_bypass"
GLOBAL_SQL_OPTION = "tenant_global"
SCHOOL_PARAM = "school_id"

AnySession = Union[Session, AsyncSession]


class TenantContextError(RuntimeError):
    """Raised when tenant data is accessed without a school context, or across schools."""


def _info(session: AnySession) -> dict:
    return session.info  # AsyncSession.info proxies the underlying Session.info


PLATFORM_KEY = "platform_session"


def bind_platform_session(session: AnySession) -> None:
    """
    Make a request's session a platform session: it works across schools (tenant
    scoping off) for the whole request. Only platform admin routes call this, after
    the platform admin token is verified. A session bound to a school cannot become one.
    """
    info = _info(session)
    if info.get(SCHOOL_ID_KEY) is not None:
        raise TenantContextError("Session is bound to a school and cannot become a platform session")
    info[PLATFORM_KEY] = True
    info[BYPASS_KEY] = True


def is_platform_session(session: AnySession) -> bool:
    return bool(_info(session).get(PLATFORM_KEY))


def set_session_school(session: AnySession, school_id: int) -> None:
    """Bind a session to one school. Rebinding to a different school is refused."""
    info = _info(session)
    if info.get(PLATFORM_KEY):
        raise TenantContextError("A platform session cannot be bound to a school")
    current = info.get(SCHOOL_ID_KEY)
    if current is not None and current != school_id:
        raise TenantContextError(
            f"Session is already bound to school {current}, refusing to rebind to {school_id}"
        )
    info[SCHOOL_ID_KEY] = school_id


def get_session_school(session: AnySession) -> Optional[int]:
    return _info(session).get(SCHOOL_ID_KEY)


@contextmanager
def tenant_bypass(session: AnySession) -> Iterator[None]:
    """Temporarily disable tenant scoping on a session (cross-school system work only)."""
    info = _info(session)
    previous = info.get(BYPASS_KEY, False)
    info[BYPASS_KEY] = True
    try:
        yield
    finally:
        # A platform session stays unscoped for its whole life
        info[BYPASS_KEY] = previous or bool(info.get(PLATFORM_KEY))


def _is_tenant_class(cls) -> bool:
    return isinstance(cls, type) and issubclass(cls, TenantMixin)


def _statement_touches_tenant(state: ORMExecuteState) -> bool:
    try:
        mappers = state.all_mappers
    except Exception:
        mappers = []
    if any(_is_tenant_class(m.class_) for m in mappers):
        return True
    bind_mapper = state.bind_mapper
    return bind_mapper is not None and _is_tenant_class(bind_mapper.class_)


def global_sql(sql: str) -> TextClause:
    """Raw SQL that reads no school data: only fixed system lists or pure functions."""
    return text(sql).execution_options(**{GLOBAL_SQL_OPTION: True})


def _with_school(params: dict, school_id: int) -> dict:
    given = params.get(SCHOOL_PARAM)
    if given is not None and given != school_id:
        raise TenantContextError(
            f"Raw SQL passed school_id={given} on a session bound to school {school_id}"
        )
    return {**params, SCHOOL_PARAM: school_id}


def _scope_raw_sql(state: ORMExecuteState):
    info = state.session.info
    if info.get(BYPASS_KEY):
        return None
    references_school = SCHOOL_PARAM in state.statement._bindparams
    if state.execution_options.get(GLOBAL_SQL_OPTION):
        if references_school:
            raise TenantContextError("global_sql() must not filter by :school_id; use text()")
        return None

    school_id = info.get(SCHOOL_ID_KEY)
    if school_id is None:
        raise TenantContextError(
            "Raw SQL run on a session without a school. Use a tenant-aware dependency, "
            "global_sql() for system lists, or tenant_bypass for cross-school work."
        )
    if not references_school:
        raise TenantContextError(
            "Raw SQL on a school session must filter by :school_id "
            "(or use global_sql() if it reads no school data)."
        )
    params = state.parameters
    if isinstance(params, (list, tuple)):
        scoped = [_with_school(dict(p), school_id) for p in params]
    else:
        if params is None:
            # invoke_statement() cannot merge into a call made without parameters
            state.parameters = {}
        scoped = _with_school(dict(params or {}), school_id)
    return state.invoke_statement(params=scoped)


# ---------------------------------------------------------------------------
# Row-level security settings
# ---------------------------------------------------------------------------

RLS_SCHOOL_SETTING = "app.school_id"
RLS_BYPASS_SETTING = "app.bypass_rls"
_RLS_APPLIED_KEY = "tenant_rls_applied"  # in Connection.info: the (school, bypass) set in this transaction


def _desired_rls_state(info: dict) -> tuple:
    school_id = info.get(SCHOOL_ID_KEY)
    return ("" if school_id is None else str(int(school_id)), "on" if info.get(BYPASS_KEY) else "off")


def _sync_rls_settings(session: Session) -> None:
    """
    Put the session's school and bypass state into the connection's RLS settings.
    The settings are transaction-local (set_config(..., true)), so they end with the
    transaction; they are only sent again when they change or the transaction did.
    """
    connection = session.connection()
    if connection.dialect.name != "postgresql":
        return
    desired = _desired_rls_state(session.info)
    if connection.info.get(_RLS_APPLIED_KEY) == desired:
        return
    school, bypass = desired  # school is digits or empty, bypass is on/off: safe to inline
    connection.exec_driver_sql(
        f"SELECT set_config('{RLS_SCHOOL_SETTING}', '{school}', true), "
        f"set_config('{RLS_BYPASS_SETTING}', '{bypass}', true)"
    )
    connection.info[_RLS_APPLIED_KEY] = desired


def _forget_rls_settings(conn, *args) -> None:
    conn.info.pop(_RLS_APPLIED_KEY, None)


@event.listens_for(Session, "after_begin")
def _new_transaction_has_no_rls_settings(session, transaction, connection) -> None:
    _forget_rls_settings(connection)


# A transaction (or savepoint) that ends takes its local settings with it
for _name in ("commit", "rollback", "rollback_savepoint"):
    event.listen(Connection, _name, _forget_rls_settings)


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_criteria(state: ORMExecuteState):
    _sync_rls_settings(state.session)
    if isinstance(state.statement, TextClause):
        return _scope_raw_sql(state)
    if not (state.is_select or state.is_update or state.is_delete):
        return
    # Column and relationship loads inherit the criteria from the parent query
    # through propagate_to_loaders, so they need no option of their own.
    if state.is_column_load or state.is_relationship_load:
        return

    info = state.session.info
    if info.get(BYPASS_KEY):
        return

    school_id = info.get(SCHOOL_ID_KEY)
    if school_id is None:
        if _statement_touches_tenant(state):
            raise TenantContextError(
                "Tenant data queried on a session without a school. "
                "Use a tenant-aware dependency (get_current_user / get_current_school) "
                "or tenant_bypass for cross-school system work."
            )
        return

    state.statement = state.statement.options(
        with_loader_criteria(
            TenantMixin,
            lambda cls: cls.school_id == school_id,
            include_aliases=True,
        )
    )


@event.listens_for(Session, "before_flush")
def _stamp_and_guard_school(session: Session, flush_context, instances) -> None:
    _sync_rls_settings(session)
    info = session.info
    if info.get(BYPASS_KEY):
        return
    school_id = info.get(SCHOOL_ID_KEY)

    for obj in session.new:
        if not isinstance(obj, TenantMixin):
            continue
        if obj.school_id is None:
            if school_id is None:
                raise TenantContextError(
                    f"Cannot create {type(obj).__name__} without a school context"
                )
            obj.school_id = school_id
        elif school_id is not None and obj.school_id != school_id:
            raise TenantContextError(
                f"Refusing to create {type(obj).__name__} for school {obj.school_id} "
                f"from a session bound to school {school_id}"
            )

    for obj in list(session.dirty) + list(session.deleted):
        if not isinstance(obj, TenantMixin):
            continue
        if school_id is None:
            raise TenantContextError(
                f"Cannot modify {type(obj).__name__} without a school context"
            )
        if obj.school_id != school_id:
            raise TenantContextError(
                f"Refusing to modify {type(obj).__name__} of school {obj.school_id} "
                f"from a session bound to school {school_id}"
            )
