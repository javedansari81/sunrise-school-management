"""
Step B: fee heads and fee structures (draft, publish, archive, copy) over HTTP.
"""
from sqlalchemy import select

from app.modules.fees.models import FeeAuditLog


# ---------------------------------------------------------------------------
# Fee heads
# ---------------------------------------------------------------------------

async def test_list_and_create_fee_head(admin_api):
    r = await admin_api.get("/fee-heads")
    assert r.status_code == 200
    assert "TUITION" in [h["code"] for h in r.json()]

    r = await admin_api.post("/fee-heads", json={"code": "COMPUTER", "name": "Computer Fee", "default_frequency": "MONTHLY"})
    assert r.status_code == 201, r.text
    assert r.json()["is_system"] is False

    dup = await admin_api.post("/fee-heads", json={"code": "COMPUTER", "name": "Another name"})
    assert dup.status_code == 409
    bad_code = await admin_api.post("/fee-heads", json={"code": "computer fee", "name": "x"})
    assert bad_code.status_code == 422


async def test_system_heads_are_protected(admin_api, refs):
    transport = refs["heads"]["TRANSPORT"]
    assert (await admin_api.patch(f"/fee-heads/{transport}", json={"code": "BUS"})).status_code == 422
    assert (await admin_api.patch(f"/fee-heads/{transport}", json={"is_active": False})).status_code == 422
    assert (await admin_api.delete(f"/fee-heads/{transport}")).status_code == 422
    # Renaming is fine
    r = await admin_api.patch(f"/fee-heads/{transport}", json={"name": "Bus Fee"})
    assert r.status_code == 200 and r.json()["name"] == "Bus Fee"


async def test_head_in_use_cannot_be_deleted(admin_api, refs):
    r = await admin_api.post("/fee-heads", json={"code": "SPORTS", "name": "Sports Fee"})
    sports = r.json()["id"]
    await admin_api.post("/fee-structures", json={
        "session_year_id": refs["year_id"], "name": "Uses sports",
        "items": [{"fee_head_id": sports, "amount": "100.00", "frequency": "ANNUAL"}],
    })
    assert (await admin_api.delete(f"/fee-heads/{sports}")).status_code == 409

    unused = (await admin_api.post("/fee-heads", json={"code": "UNUSED", "name": "Unused"})).json()["id"]
    assert (await admin_api.delete(f"/fee-heads/{unused}")).status_code == 204
    assert unused not in [h["id"] for h in (await admin_api.get("/fee-heads?include_inactive=true")).json()]


async def test_staff_can_view_but_not_configure(staff_api):
    assert (await staff_api.get("/fee-heads")).status_code == 200
    assert (await staff_api.post("/fee-heads", json={"code": "X", "name": "X"})).status_code == 403


async def test_fee_heads_are_per_school(admin_api, other_api):
    created = await admin_api.post("/fee-heads", json={"code": "COMPUTER", "name": "Computer Fee"})
    head_id = created.json()["id"]
    # Oakridge sees none of Sunrise's heads and gets 404 for Sunrise's head id
    assert (await other_api.get("/fee-heads")).json() == []
    assert (await other_api.patch(f"/fee-heads/{head_id}", json={"name": "Hijack"})).status_code == 404
    # The same code is free in another school
    assert (await other_api.post("/fee-heads", json={"code": "COMPUTER", "name": "Computer Fee"})).status_code == 201


# ---------------------------------------------------------------------------
# Fee structures
# ---------------------------------------------------------------------------

def _items(refs, tuition="1500.00"):
    c1, c2 = refs["class_ids"]
    h = refs["heads"]
    return [
        {"fee_head_id": h["TUITION"], "class_id": c1, "amount": tuition, "frequency": "MONTHLY"},
        {"fee_head_id": h["TUITION"], "class_id": c2, "amount": "1700.00", "frequency": "MONTHLY"},
        {"fee_head_id": h["EXAM"], "amount": "800.00", "frequency": "HALF_YEARLY", "billing_months": [9, 3]},
        {"fee_head_id": h["ADMISSION"], "amount": "5000.00", "frequency": "ONE_TIME", "applies_to": "NEW_STUDENTS"},
    ]


async def _create(api, refs, name="2026-27 fees", items=None):
    r = await api.post("/fee-structures", json={
        "session_year_id": refs["year_id"], "name": name, "items": _items(refs) if items is None else items,
    })
    assert r.status_code == 201, r.text
    return r.json()


async def test_structure_draft_publish_and_lock(admin_api, refs):
    s = await _create(admin_api, refs)
    assert s["status"] == "DRAFT" and len(s["items"]) == 4

    # A draft can be renamed and its lines replaced
    assert (await admin_api.patch(f"/fee-structures/{s['id']}", json={"name": "Renamed"})).json()["name"] == "Renamed"
    r = await admin_api.put(f"/fee-structures/{s['id']}/items", json=_items(refs, tuition="1600.00"))
    assert r.status_code == 200, r.text
    assert sorted(i["amount"] for i in r.json()["items"])[0] == "1600.00"

    r = await admin_api.post(f"/fee-structures/{s['id']}/publish")
    assert r.status_code == 200 and r.json()["status"] == "PUBLISHED" and r.json()["published_at"]

    # Published: locked
    assert (await admin_api.patch(f"/fee-structures/{s['id']}", json={"name": "x"})).status_code == 409
    assert (await admin_api.put(f"/fee-structures/{s['id']}/items", json=_items(refs))).status_code == 409
    assert (await admin_api.delete(f"/fee-structures/{s['id']}")).status_code == 409


async def test_publishing_a_new_version_archives_the_old_one(admin_api, refs):
    first = await _create(admin_api, refs, name="v1")
    await admin_api.post(f"/fee-structures/{first['id']}/publish")

    copy = await admin_api.post(f"/fee-structures/{first['id']}/copy", json={"name": "v2"})
    assert copy.status_code == 201
    v2 = copy.json()
    assert v2["status"] == "DRAFT" and v2["copied_from_id"] == first["id"] and len(v2["items"]) == 4

    await admin_api.put(f"/fee-structures/{v2['id']}/items", json=_items(refs, tuition="1900.00"))
    assert (await admin_api.post(f"/fee-structures/{v2['id']}/publish")).status_code == 200

    statuses = {s["id"]: s["status"] for s in (await admin_api.get(f"/fee-structures?session_year_id={refs['year_id']}")).json()}
    assert statuses[first["id"]] == "ARCHIVED" and statuses[v2["id"]] == "PUBLISHED"
    published = (await admin_api.get("/fee-structures?status=PUBLISHED")).json()
    assert [s["id"] for s in published] == [v2["id"]]


async def test_structure_item_validation(admin_api, refs):
    h = refs["heads"]
    cases = [
        [{"fee_head_id": 999999, "amount": "1"}],  # unknown head
        [{"fee_head_id": h["TUITION"], "class_id": 999999, "amount": "1"}],  # unknown class
        [{"fee_head_id": h["EXAM"], "amount": "1", "frequency": "ANNUAL", "billing_months": [4, 10]}],
        [{"fee_head_id": h["EXAM"], "amount": "1", "billing_months": [13]}],
        [{"fee_head_id": h["TUITION"], "amount": "1"}, {"fee_head_id": h["TUITION"], "amount": "2"}],  # twice
    ]
    for items in cases:
        r = await admin_api.post("/fee-structures", json={"session_year_id": refs["year_id"], "name": "bad", "items": items})
        assert r.status_code == 422, (items, r.text)
    neg = await admin_api.post("/fee-structures", json={
        "session_year_id": refs["year_id"], "name": "neg", "items": [{"fee_head_id": h["TUITION"], "amount": "-5"}]})
    assert neg.status_code == 422


async def test_empty_structure_cannot_be_published(admin_api, refs):
    s = await _create(admin_api, refs, items=[])
    assert (await admin_api.post(f"/fee-structures/{s['id']}/publish")).status_code == 422


async def test_draft_can_be_deleted_and_changes_are_audited(admin_api, refs, sunrise_session):
    s = await _create(admin_api, refs)
    assert (await admin_api.delete(f"/fee-structures/{s['id']}")).status_code == 204
    assert (await admin_api.get(f"/fee-structures/{s['id']}")).status_code == 404
    async with sunrise_session() as session:
        actions = (await session.execute(
            select(FeeAuditLog.action).where(FeeAuditLog.entity_type == "fee_structure", FeeAuditLog.entity_id == s["id"])
            .order_by(FeeAuditLog.id)
        )).scalars().all()
    assert actions == ["CREATE", "DELETE"]


async def test_structures_are_per_school(admin_api, other_api, refs):
    s = await _create(admin_api, refs)
    assert (await other_api.get(f"/fee-structures/{s['id']}")).status_code == 404
    assert (await other_api.post(f"/fee-structures/{s['id']}/publish")).status_code == 404
    assert (await other_api.get("/fee-structures")).json() == []
    # Oakridge cannot price Sunrise's heads or use Sunrise's session year
    r = await other_api.post("/fee-structures", json={
        "session_year_id": refs["year_id"], "name": "x", "items": []})
    assert r.status_code == 404
