"""
Fee module defaults for a newly created school.

Existing schools got theirs from Database/Init/04_fee_module_defaults.sql (fresh
deployments) or migration V002. A school created later through the platform API
copies the template school's fee heads, concession rules and fee settings, so a
school group can set them up once. Without a template it gets the built-in
defaults below. Runs on a platform session (tenant scoping off), so school_id is
set explicitly on every row.
"""
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.school import SchoolSetting
from app.modules.fees import constants as c
from app.modules.fees.models import ConcessionRule, FeeHead

DEFAULT_HEADS = [
    # code, name, category, frequency, is_system, sort_order
    ("TUITION", "Tuition Fee", "ACADEMIC", "MONTHLY", False, 10),
    ("ADMISSION", "Admission Fee", "ONE_TIME", "ONE_TIME", False, 20),
    ("DEVELOPMENT", "Development Fee", "ACADEMIC", "ANNUAL", False, 30),
    ("ACTIVITY", "Activity Fee", "ACADEMIC", "ANNUAL", False, 40),
    ("LIBRARY", "Library Fee", "ACADEMIC", "ANNUAL", False, 50),
    ("LAB", "Lab Fee", "ACADEMIC", "ANNUAL", False, 60),
    ("EXAM", "Exam Fee", "ACADEMIC", "ANNUAL", False, 70),
    (c.HEAD_TRANSPORT, "Transport Fee", "TRANSPORT", "MONTHLY", True, 80),
    (c.HEAD_LATE_FEE, "Late Fee", "PENALTY", "ONE_TIME", True, 90),
    ("OTHER", "Other Charges", "OTHER", "ONE_TIME", False, 100),
]

DEFAULT_SETTINGS = {
    c.SETTING_LATE_FEE_ENABLED: ("false", "Add a Late fee due automatically after the grace days"),
    c.SETTING_LATE_FEE_MODE: ("FIXED", "FIXED amount or PERCENT of the overdue amount"),
    c.SETTING_LATE_FEE_VALUE: ("0", "Late fee amount or percent per overdue month"),
    c.SETTING_LATE_FEE_GRACE_DAYS: ("7", "Days after the due date before a late fee is added"),
    c.SETTING_TRANSPORT_CUTOFF_DAY: ("15", "Transport started after this day of the month is billed from the next month"),
    c.SETTING_TRANSPORT_DUE_DAY: ("10", "Day of the month transport dues fall due (1-28)"),
}


def default_receipt_prefix(school_code: str) -> str:
    return (school_code or "RCP")[:3].upper()


async def seed_fee_defaults(
    db: AsyncSession, *, school_id: int, school_code: str, template_school_id: Optional[int]
) -> Dict[str, int]:
    """Create fee heads, concession rules and fee settings for a new school. Returns rows created per table."""
    head_ids_by_code: Dict[str, int] = {}
    template_head_codes: Dict[int, str] = {}

    template_heads = []
    if template_school_id is not None:
        template_heads = (
            await db.execute(select(FeeHead).where(FeeHead.school_id == template_school_id).order_by(FeeHead.id))
        ).scalars().all()

    if template_heads:
        for h in template_heads:
            template_head_codes[h.id] = h.code
            new = FeeHead(
                school_id=school_id, code=h.code, name=h.name, description=h.description,
                category=h.category, default_frequency=h.default_frequency, is_system=h.is_system,
                sort_order=h.sort_order, is_active=h.is_active,
            )
            db.add(new)
            await db.flush()
            head_ids_by_code[h.code] = new.id

    # Built-in heads: all of them without a template, and the system heads in any case
    for code, name, category, frequency, is_system, order in DEFAULT_HEADS:
        if code in head_ids_by_code or (template_heads and not is_system):
            continue
        new = FeeHead(
            school_id=school_id, code=code, name=name, category=category,
            default_frequency=frequency, is_system=is_system, sort_order=order,
        )
        db.add(new)
        await db.flush()
        head_ids_by_code[code] = new.id

    rules_created = 0
    if template_school_id is not None:
        rules = (
            await db.execute(
                select(ConcessionRule).where(ConcessionRule.school_id == template_school_id).order_by(ConcessionRule.id)
            )
        ).scalars().all()
        for r in rules:
            heads = None
            if r.fee_head_ids is not None:
                heads = [head_ids_by_code[template_head_codes[i]] for i in r.fee_head_ids if i in template_head_codes]
            db.add(ConcessionRule(
                school_id=school_id, name=r.name, description=r.description,
                concession_type=r.concession_type, value_type=r.value_type, value=r.value,
                fee_head_ids=heads, tiers=r.tiers, is_active=r.is_active,
            ))
            rules_created += 1

    settings = {k: v for k, v in DEFAULT_SETTINGS.items()}
    if template_school_id is not None:
        rows = (
            await db.execute(
                select(SchoolSetting).where(
                    SchoolSetting.school_id == template_school_id, SchoolSetting.key.like("fee.%")
                )
            )
        ).scalars().all()
        for s in rows:
            if s.key != c.SETTING_RECEIPT_PREFIX:
                settings[s.key] = (s.value, s.description)
    settings[c.SETTING_RECEIPT_PREFIX] = (
        default_receipt_prefix(school_code), "Receipt number prefix, e.g. SUN in SUN/2026-27/000123"
    )
    for key, (value, description) in settings.items():
        db.add(SchoolSetting(school_id=school_id, key=key, value=value, description=description))

    await db.flush()
    return {"fee_heads": len(head_ids_by_code), "concession_rules": rules_created}
