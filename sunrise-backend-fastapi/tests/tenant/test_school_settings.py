"""
Per-school settings outside the fee module (Phase 5): generated email domain
and Cloudinary upload folders. Settings are inserted inside the test
transaction, so these tests do not depend on migration V005 being applied.
"""
from datetime import date

import pytest

from app.core.config import settings
from app.models.school import SchoolSetting
from app.services import school_settings
from app.utils.email_generator import generate_student_email, generate_teacher_email


async def _set(make_session, school_id, key, value):
    async with make_session(school_id) as session:
        session.add(SchoolSetting(key=key, value=value))
        await session.commit()


async def test_generated_emails_use_the_schools_domain(make_session, schools, monkeypatch):
    monkeypatch.setattr(settings, "BASE_DOMAIN", "")
    async with make_session(schools["sunrise_id"]) as session:
        await session.execute(SchoolSetting.__table__.delete().where(
            SchoolSetting.school_id == schools["sunrise_id"], SchoolSetting.key == school_settings.EMAIL_DOMAIN))
        await session.commit()
    await _set(make_session, schools["sunrise_id"], school_settings.EMAIL_DOMAIN, "sunrise.com")

    async with make_session(schools["sunrise_id"]) as session:
        email = await generate_student_email(session, "Asha", "Verma", date(2015, 3, 15))
    assert email == "asha.verma.1503@sunrise.com"

    # No setting: <code>.local until BASE_DOMAIN is configured, then <code>.<BASE_DOMAIN>
    async with make_session(schools["other_id"]) as session:
        assert await generate_teacher_email(session, "Ravi", "Kumar", date(1990, 7, 1)) == "ravi.kumar.0107@oakridge.local"
        monkeypatch.setattr(settings, "BASE_DOMAIN", "myschools.in")
        assert await school_settings.email_domain(session) == "oakridge.myschools.in"


async def test_teacher_email_suffix_keeps_the_schools_domain(make_session, schools, monkeypatch):
    """A taken address gets .2, .3 ... before the @, whatever the domain is."""
    monkeypatch.setattr(settings, "BASE_DOMAIN", "")
    from app.models.user import User

    async with make_session(schools["other_id"]) as session:
        session.add(User(email="ravi.kumar.0107@oakridge.local", password="x", first_name="Ravi",
                         last_name="Kumar", user_type_id=2, is_active=True))
        await session.commit()
        assert await generate_teacher_email(session, "Ravi", "Kumar", date(1990, 7, 1)) == "ravi.kumar.0107.2@oakridge.local"


async def test_cloudinary_folders_are_per_school(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        assert await school_settings.cloudinary_folder(session, school_settings.GALLERY) == "oakridge/gallery"
        assert await school_settings.cloudinary_folder(session, school_settings.STUDENT_PHOTOS) == "oakridge/student_photos"
    await _set(make_session, schools["other_id"], "cloudinary.gallery_folder", "/oak-media/gallery/")
    async with make_session(schools["other_id"]) as session:
        assert await school_settings.cloudinary_folder(session, school_settings.GALLERY) == "oak-media/gallery"
    async with make_session(schools["sunrise_id"]) as session:
        assert await school_settings.cloudinary_folder(session, school_settings.GALLERY) != "oak-media/gallery"


@pytest.mark.parametrize("url, expected", [
    ("https://res.cloudinary.com/demo/image/upload/v1712/inventory/item_3_Shirt.jpg", "inventory/item_3_Shirt"),
    ("https://res.cloudinary.com/demo/image/upload/c_fill,h_400,w_400/q_auto/v1712/sunrise/inventory/item_3.png",
     "sunrise/inventory/item_3"),
    ("https://res.cloudinary.com/demo/image/upload/sunrise/inventory/item_3.webp", "sunrise/inventory/item_3"),
    ("", None),
    ("https://example.com/item.png", None),
])
def test_cloudinary_public_id(url, expected):
    assert school_settings.cloudinary_public_id(url) == expected
