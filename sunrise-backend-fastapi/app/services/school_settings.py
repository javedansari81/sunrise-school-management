"""
Per-school settings used outside the fee module (Phase 5).

Every value is read on the request's school-bound session, so the tenant
scoping picks the calling school's row.

    user.email_domain           domain of generated student and teacher emails.
                                Default: "<school code>.<BASE_DOMAIN>", or
                                "<school code>.local" while BASE_DOMAIN is empty.
                                Sunrise is set to "sunrise.com" (migration V005)
                                so existing logins keep working.
    cloudinary.<kind>_folder    Cloudinary folder for uploads of one kind
                                (gallery, inventory, student_photos,
                                teacher_photos). Default: "<school code>/<kind>".
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.tenant import get_session_school
from app.models.school import School, SchoolSetting

EMAIL_DOMAIN = "user.email_domain"

GALLERY = "gallery"
INVENTORY = "inventory"
STUDENT_PHOTOS = "student_photos"
TEACHER_PHOTOS = "teacher_photos"


async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
    value = (await db.execute(select(SchoolSetting.value).where(SchoolSetting.key == key))).scalar_one_or_none()
    return value.strip() if value and value.strip() else None


async def _school(db: AsyncSession) -> School:
    school = await db.get(School, get_session_school(db))
    if school is None:
        raise RuntimeError("School settings need a session bound to a school")
    return school


async def email_domain(db: AsyncSession) -> str:
    domain = await get_setting(db, EMAIL_DOMAIN)
    if domain:
        return domain.lstrip("@").lower()
    code = (await _school(db)).code
    return f"{code}.{settings.BASE_DOMAIN}" if settings.BASE_DOMAIN else f"{code}.local"


async def cloudinary_folder(db: AsyncSession, kind: str) -> str:
    folder = await get_setting(db, f"cloudinary.{kind}_folder")
    if folder:
        return folder.strip("/")
    return f"{(await _school(db)).code}/{kind}"


def cloudinary_public_id(url: str) -> Optional[str]:
    """
    Public id of an uploaded Cloudinary image, from its delivery URL:
    .../image/upload/[transformations/][v123/]<public id>.<format>
    Works for any folder depth, so files uploaded before per-school folders are found too.
    """
    if not url or "/upload/" not in url:
        return None
    parts = url.split("/upload/", 1)[1].split("?", 1)[0].split("/")
    while parts and ("," in parts[0] or "_" in parts[0] and parts[0][:2] in ("w_", "h_", "c_", "q_", "f_")):
        parts.pop(0)  # transformation segments
    if parts and parts[0][:1] == "v" and parts[0][1:].isdigit():
        parts.pop(0)  # version
    if not parts:
        return None
    parts[-1] = parts[-1].rsplit(".", 1)[0]
    return "/".join(parts)
