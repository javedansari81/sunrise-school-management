"""
Step A: unified fee module schema, defaults and tenant isolation.
"""
from datetime import date

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app.core.tenant import TenantContextError, tenant_bypass
from app.models.metadata import Class, SessionYear
from app.models.school import SchoolSetting
from app.models.tenant import TenantMixin
from app.modules.fees import models as m
from app.modules.fees.provisioning import seed_fee_defaults

from .conftest import add_student

FEE_MODELS = [
    m.FeeHead, m.FeeStructure, m.FeeStructureItem, m.ConcessionRule, m.StudentFeePlan,
    m.StudentConcession, m.StudentDue, m.ReceiptSequence, m.Payment, m.PaymentAllocation, m.FeeAuditLog,
]


def test_every_fee_model_is_tenant_scoped():
    assert all(issubclass(model, TenantMixin) for model in FEE_MODELS)


async def test_sunrise_has_fee_defaults(sunrise_session):
    async with sunrise_session() as session:
        codes = set((await session.execute(select(m.FeeHead.code))).scalars())
        assert {"TUITION", "TRANSPORT", "LATE_FEE", "ADMISSION", "EXAM"} <= codes
        system = set((await session.execute(select(m.FeeHead.code).where(m.FeeHead.is_system))).scalars())
        assert system == {"TRANSPORT", "LATE_FEE"}

        rule = (await session.execute(
            select(m.ConcessionRule).where(m.ConcessionRule.concession_type == "SIBLING")
        )).scalar_one()
        tuition_id = (await session.execute(select(m.FeeHead.id).where(m.FeeHead.code == "TUITION"))).scalar_one()
        assert rule.fee_head_ids == [tuition_id]
        assert len(rule.tiers) == 4

        prefix = (await session.execute(
            select(SchoolSetting.value).where(SchoolSetting.key == "fee.receipt_prefix")
        )).scalar_one()
        assert prefix == "SUN"


async def test_fee_heads_are_isolated_per_school(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        # Oakridge was added by the test fixture without defaults: it sees no heads, not Sunrise's
        assert (await session.execute(select(func.count()).select_from(m.FeeHead))).scalar_one() == 0
        session.add(m.FeeHead(code="TUITION", name="Tuition Fee"))
        await session.flush()
        head = (await session.execute(select(m.FeeHead))).scalar_one()
        assert head.school_id == schools["other_id"]

    async with make_session() as session:
        with pytest.raises(TenantContextError):
            await session.execute(select(m.FeeHead))


async def test_seed_defaults_for_new_school_copies_template(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            created = await seed_fee_defaults(
                session, school_id=schools["other_id"], school_code=schools["other_code"],
                template_school_id=schools["sunrise_id"],
            )
            await session.commit()
    assert created == {"fee_heads": 10, "concession_rules": 1}

    async with make_session(schools["other_id"]) as session:
        heads = {h.code: h.id for h in (await session.execute(select(m.FeeHead))).scalars()}
        rule = (await session.execute(select(m.ConcessionRule))).scalar_one()
        # The rule points at the NEW school's tuition head
        assert rule.fee_head_ids == [heads["TUITION"]]
        settings = dict((await session.execute(select(SchoolSetting.key, SchoolSetting.value))).all())
        assert settings["fee.receipt_prefix"] == "OAK"
        assert settings["fee.late_fee.grace_days"] == "7"


async def test_seed_defaults_without_template(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            created = await seed_fee_defaults(
                session, school_id=schools["other_id"], school_code=schools["other_code"], template_school_id=None,
            )
    assert created == {"fee_heads": 10, "concession_rules": 0}


async def _sunrise_refs(session):
    head = (await session.execute(select(m.FeeHead).where(m.FeeHead.code == "TUITION"))).scalar_one()
    cls = (await session.execute(select(Class).order_by(Class.sort_order).limit(1))).scalar_one()
    year = (await session.execute(select(SessionYear).where(SessionYear.name == "2026-27"))).scalar_one()
    return head, cls, year


async def test_a_regular_due_is_unique_per_period_until_cancelled(sunrise_session):
    async with sunrise_session() as session:
        head, cls, year = await _sunrise_refs(session)
        student = await add_student(session, class_id=cls.id, session_year_id=year.id)

        def due(**kw):
            values = dict(student_id=student.id, session_year_id=year.id, fee_head_id=head.id,
                          period=date(2026, 4, 1), due_date=date(2026, 4, 10),
                          gross_amount=1000, concession_amount=0, net_amount=1000)
            values.update(kw)
            return m.StudentDue(**values)

        first = due()
        session.add(first)
        await session.flush()

        async with session.begin_nested():
            session.add(due())
            with pytest.raises(IntegrityError):
                await session.flush()

        # A manual line for the same period is allowed, and so is a new line once the first is cancelled
        session.add(due(line_type="MANUAL"))
        first.status = "CANCELLED"
        await session.flush()
        session.add(due())
        await session.flush()


async def test_payment_shape_is_enforced(sunrise_session):
    async with sunrise_session() as session:
        _, cls, year = await _sunrise_refs(session)
        student = await add_student(session, class_id=cls.id, session_year_id=year.id)
        async with session.begin_nested():
            # A payment needs a method and a positive amount
            session.add(m.Payment(student_id=student.id, session_year_id=year.id, amount=-10))
            with pytest.raises(IntegrityError):
                await session.flush()


async def test_legacy_fee_structures_table_renamed(sunrise_session):
    async with sunrise_session() as session:
        names = set((await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema() "
            "AND table_name IN ('fee_structures', 'legacy_fee_structures')"
        ))).scalars())
        assert names == {"fee_structures", "legacy_fee_structures"}
        cols = set((await session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = current_schema() "
            "AND table_name = 'fee_structures'"
        ))).scalars())
        assert "status" in cols and "tuition_fee" not in cols
