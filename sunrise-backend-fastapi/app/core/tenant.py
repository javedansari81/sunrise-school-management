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

Raw SQL (``text()``) is NOT scoped by these events. Queries written that way
must filter by ``school_id`` themselves (see Phase 5 of the redesign plan).
"""
from contextlib import contextmanager
from typing import Iterator, Optional, Union

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from app.models.tenant import TenantMixin

SCHOOL_ID_KEY = "school_id"
BYPASS_KEY = "tenant_bypass"

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


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_criteria(state: ORMExecuteState) -> None:
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
