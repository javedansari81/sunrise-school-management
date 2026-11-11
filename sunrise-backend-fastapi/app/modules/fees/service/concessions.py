"""
Concessions: rules (one SIBLING rule per school, plus staff, scholarship and
custom rules) and concessions granted to individual students.

Sibling concession (decision 8, changed by decision 13): siblings are linked by
hand. A student's position is worked out at billing time among the linked
siblings enrolled in the same session, eldest first by date of birth (ties:
admission number). The SIBLING rule's tiers give the percent for that position.
Nothing about birth order is stored.

How concessions combine on one due: every applicable percent is added up and
every fixed amount is added, and the total is capped at the due's gross amount.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Iterable, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_student_sibling import student_sibling_crud
from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import AuditAction, ConcessionType, PositionBasis, ValueType
from app.modules.fees.errors import Conflict, Invalid
from app.modules.fees.models import ConcessionRule, StudentConcession
from app.modules.fees.periods import month_start
from app.modules.fees.schemas import (
    ConcessionRuleCreate, ConcessionRuleUpdate, StudentConcessionCreate,
)

RULE_ENTITY = "concession_rule"
STUDENT_ENTITY = "student_concession"
RULE_FIELDS = ("name", "description", "concession_type", "value_type", "value", "fee_head_ids", "tiers", "is_active")
CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

async def list_rules(db: AsyncSession, *, include_inactive: bool = False) -> List[ConcessionRule]:
    query = select(ConcessionRule).order_by(ConcessionRule.concession_type, ConcessionRule.name)
    if not include_inactive:
        query = query.where(ConcessionRule.is_active)
    return list((await db.execute(query)).scalars())


async def _check_heads(db: AsyncSession, head_ids: Optional[Sequence[int]]) -> None:
    if head_ids is None:
        return
    if not head_ids:
        raise Invalid("fee_head_ids must not be empty; leave it out to cover every fee head")
    found = await repo.heads_by_id(db, head_ids)
    missing = sorted(set(head_ids) - set(found))
    if missing:
        raise Invalid(f"Fee heads not found: {missing}")


async def _active_sibling_rule(db: AsyncSession, exclude_id: Optional[int] = None) -> Optional[ConcessionRule]:
    query = select(ConcessionRule).where(
        ConcessionRule.concession_type == ConcessionType.SIBLING.value, ConcessionRule.is_active
    )
    if exclude_id is not None:
        query = query.where(ConcessionRule.id != exclude_id)
    return (await db.execute(query)).scalars().first()


async def _check_name(db: AsyncSession, name: Optional[str], exclude_id: Optional[int] = None) -> None:
    if name is None:
        return
    query = select(ConcessionRule.id).where(ConcessionRule.name == name)
    if exclude_id is not None:
        query = query.where(ConcessionRule.id != exclude_id)
    if (await db.execute(query)).first():
        raise Conflict(f"A concession rule named '{name}' already exists")


async def create_rule(db: AsyncSession, data: ConcessionRuleCreate, *, user_id: int) -> ConcessionRule:
    await _check_heads(db, data.fee_head_ids)
    await _check_name(db, data.name)
    if data.concession_type == ConcessionType.SIBLING and data.is_active and await _active_sibling_rule(db):
        raise Conflict("The school already has an active sibling rule; edit it or deactivate it first")
    rule = ConcessionRule(**data.model_dump(mode="json"))
    db.add(rule)
    await db.flush()
    await audit.record(db, entity_type=RULE_ENTITY, entity_id=rule.id, action=AuditAction.CREATE.value,
                       performed_by=user_id, new=audit.snapshot(rule, RULE_FIELDS))
    return rule


async def update_rule(db: AsyncSession, rule_id: int, data: ConcessionRuleUpdate, *, user_id: int) -> ConcessionRule:
    rule = await repo.get_or_404(db, ConcessionRule, rule_id, "Concession rule")
    changes = data.model_dump(mode="json", exclude_unset=True)
    if "fee_head_ids" in changes:
        await _check_heads(db, changes["fee_head_ids"])
    await _check_name(db, changes.get("name"), exclude_id=rule.id)
    is_sibling = rule.concession_type == ConcessionType.SIBLING.value
    if is_sibling:
        if "tiers" in changes and not changes["tiers"]:
            raise Invalid("A SIBLING rule needs tiers")
        if changes.get("is_active") and not rule.is_active and await _active_sibling_rule(db, exclude_id=rule.id):
            raise Conflict("The school already has an active sibling rule")
    elif changes.get("tiers"):
        raise Invalid("Only SIBLING rules have tiers")
    value_type = changes.get("value_type", rule.value_type)
    value = Decimal(str(changes.get("value", rule.value)))
    if not is_sibling and value_type == ValueType.PERCENT.value and value > 100:
        raise Invalid("A percent must be 0 to 100")

    old = audit.snapshot(rule, RULE_FIELDS)
    for key, value in changes.items():
        setattr(rule, key, value)
    await db.flush()
    await audit.record(db, entity_type=RULE_ENTITY, entity_id=rule.id, action=AuditAction.UPDATE.value,
                       performed_by=user_id, old=old, new=audit.snapshot(rule, RULE_FIELDS))
    return rule


# ---------------------------------------------------------------------------
# Student concessions
# ---------------------------------------------------------------------------

async def list_student_concessions(
    db: AsyncSession, student_id: int, *, session_year_id: Optional[int] = None, include_inactive: bool = False
) -> List[StudentConcession]:
    await repo.student_or_404(db, student_id)
    query = select(StudentConcession).where(StudentConcession.student_id == student_id).order_by(StudentConcession.id)
    if session_year_id is not None:
        query = query.where(StudentConcession.session_year_id == session_year_id)
    if not include_inactive:
        query = query.where(StudentConcession.is_active)
    return list((await db.execute(query)).scalars())


async def grant_concession(
    db: AsyncSession, student_id: int, data: StudentConcessionCreate, *, user_id: int
) -> StudentConcession:
    """Grant a concession to a student, from a rule (its values are copied) or with explicit values."""
    await repo.student_or_404(db, student_id)
    await repo.session_year_or_404(db, data.session_year_id)
    values = dict(
        concession_type=data.concession_type.value if data.concession_type else None,
        value_type=data.value_type.value if data.value_type else None,
        value=data.value, fee_head_ids=data.fee_head_ids,
    )
    if data.concession_rule_id is not None:
        rule = await repo.get_or_404(db, ConcessionRule, data.concession_rule_id, "Concession rule")
        if rule.concession_type == ConcessionType.SIBLING.value:
            raise Invalid("Sibling concessions are applied automatically from linked siblings")
        if not rule.is_active:
            raise Invalid(f"Concession rule {rule.id} is inactive")
        for key in values:
            if values[key] is None:
                values[key] = getattr(rule, key)
    if values["concession_type"] in (None, ConcessionType.SIBLING.value):
        raise Invalid("concession_type must be STAFF, SCHOLARSHIP or CUSTOM")
    if values["value_type"] is None or values["value"] is None:
        raise Invalid("value_type and value are required without a concession rule")
    if values["value_type"] == ValueType.PERCENT.value and Decimal(str(values["value"])) > 100:
        raise Invalid("A percent must be 0 to 100")
    await _check_heads(db, values["fee_head_ids"])
    start = month_start(data.start_period) if data.start_period else None
    end = month_start(data.end_period) if data.end_period else None
    if start and end and end < start:
        raise Invalid("end_period must not be before start_period")

    concession = StudentConcession(
        student_id=student_id, session_year_id=data.session_year_id, concession_rule_id=data.concession_rule_id,
        start_period=start, end_period=end, reason=data.reason,
        approved_by=user_id, approved_at=datetime.now(timezone.utc), created_by=user_id, **values,
    )
    db.add(concession)
    await db.flush()
    await audit.record(db, entity_type=STUDENT_ENTITY, entity_id=concession.id, action=AuditAction.CREATE.value,
                       performed_by=user_id,
                       new=audit.snapshot(concession, ("student_id", "session_year_id", "concession_type",
                                                       "value_type", "value", "fee_head_ids", "reason")))
    return concession


async def revoke_concession(db: AsyncSession, concession_id: int, *, user_id: int, reason: Optional[str]) -> StudentConcession:
    concession = await repo.get_or_404(db, StudentConcession, concession_id, "Student concession")
    if not concession.is_active:
        raise Conflict(f"Student concession {concession_id} is already revoked")
    concession.is_active = False
    await db.flush()
    await audit.record(db, entity_type=STUDENT_ENTITY, entity_id=concession.id, action=AuditAction.DELETE.value,
                       performed_by=user_id, remarks=reason)
    return concession


# ---------------------------------------------------------------------------
# Sibling position
# ---------------------------------------------------------------------------

@dataclass
class SiblingStanding:
    family_size: int  # enrolled siblings in the session, the student included
    position_from_eldest: int
    percent: Decimal
    sibling_ids: List[int] = field(default_factory=list)  # eldest first, the student included

    @property
    def position_from_youngest(self) -> int:
        return self.family_size - self.position_from_eldest + 1


def tier_percent(tiers: Iterable[dict], family_size: int, position_from_eldest: int) -> Decimal:
    """Highest percent of the tiers matching a family size and position (0 when none match)."""
    best = Decimal("0")
    from_youngest = family_size - position_from_eldest + 1
    for t in tiers or []:
        if family_size < t["min_siblings"]:
            continue
        if t.get("max_siblings") is not None and family_size > t["max_siblings"]:
            continue
        position = from_youngest if t.get("position_basis") == PositionBasis.YOUNGEST.value else position_from_eldest
        if position < t["position_from"]:
            continue
        if t.get("position_to") is not None and position > t["position_to"]:
            continue
        best = max(best, Decimal(str(t["percent"])))
    return money(best)


async def sibling_standing(
    db: AsyncSession, student_id: int, session_year_id: int, rule: Optional[ConcessionRule]
) -> SiblingStanding:
    family_ids = await student_sibling_crud.get_all_family_members(db, student_id)
    enrolled = [s for s, _ in await repo.enrolled_students(db, session_year_id, student_ids=family_ids)]
    if student_id not in {s.id for s in enrolled}:
        # Not enrolled in this session: rank among the enrolled siblings anyway
        enrolled.append(await repo.student_or_404(db, student_id))
    ordered = sorted(enrolled, key=lambda s: (s.date_of_birth, s.admission_number))
    ids = [s.id for s in ordered]
    position = ids.index(student_id) + 1
    percent = tier_percent(rule.tiers, len(ids), position) if rule is not None and len(ids) > 1 else Decimal("0")
    return SiblingStanding(family_size=len(ids), position_from_eldest=position, percent=percent, sibling_ids=ids)


# ---------------------------------------------------------------------------
# Calculator used by dues generation
# ---------------------------------------------------------------------------

@dataclass
class _Grant:
    value_type: str
    value: Decimal
    fee_head_ids: Optional[List[int]]
    start: Optional[date] = None
    end: Optional[date] = None

    def covers(self, head_id: int, period: date) -> bool:
        if self.fee_head_ids is not None and head_id not in self.fee_head_ids:
            return False
        if self.start is not None and period < self.start:
            return False
        return self.end is None or period <= self.end


class ConcessionCalculator:
    """Concession amount for any (student, head, period, gross) of one session. Loads lazily per student."""

    def __init__(self, db: AsyncSession, session_year_id: int):
        self.db = db
        self.session_year_id = session_year_id
        self._sibling_rule: Optional[ConcessionRule] = None
        self._loaded_rule = False
        self._grants: Dict[int, List[_Grant]] = {}

    async def _rule(self) -> Optional[ConcessionRule]:
        if not self._loaded_rule:
            self._sibling_rule = await _active_sibling_rule(self.db)
            self._loaded_rule = True
        return self._sibling_rule

    async def grants_for(self, student_id: int) -> List[_Grant]:
        if student_id not in self._grants:
            grants: List[_Grant] = []
            rule = await self._rule()
            if rule is not None:
                standing = await sibling_standing(self.db, student_id, self.session_year_id, rule)
                if standing.percent > 0:
                    grants.append(_Grant(ValueType.PERCENT.value, standing.percent, rule.fee_head_ids))
            rows = (await self.db.execute(
                select(StudentConcession).where(
                    StudentConcession.student_id == student_id,
                    StudentConcession.session_year_id == self.session_year_id,
                    StudentConcession.is_active,
                )
            )).scalars().all()
            grants += [_Grant(r.value_type, Decimal(r.value), r.fee_head_ids, r.start_period, r.end_period) for r in rows]
            self._grants[student_id] = grants
        return self._grants[student_id]

    async def amount(self, student_id: int, head_id: int, period: date, gross: Decimal) -> Decimal:
        percent = Decimal("0")
        fixed = Decimal("0")
        for g in await self.grants_for(student_id):
            if not g.covers(head_id, period):
                continue
            if g.value_type == ValueType.PERCENT.value:
                percent += g.value
            else:
                fixed += g.value
        total = money(gross * min(percent, Decimal("100")) / 100 + fixed)
        return min(total, money(gross))


async def sibling_preview(db: AsyncSession, student_id: int, session_year_id: int) -> dict:
    """What the sibling rule gives a student in a session, for the student screen."""
    await repo.student_or_404(db, student_id)
    await repo.session_year_or_404(db, session_year_id)
    rule = await _active_sibling_rule(db)
    standing = await sibling_standing(db, student_id, session_year_id, rule)
    return {
        "student_id": student_id,
        "session_year_id": session_year_id,
        "family_size": standing.family_size,
        "position_from_eldest": standing.position_from_eldest,
        "position_from_youngest": standing.position_from_youngest,
        "sibling_ids_eldest_first": standing.sibling_ids,
        "rule_id": rule.id if rule else None,
        "fee_head_ids": rule.fee_head_ids if rule else None,
        "percent": standing.percent,
    }

