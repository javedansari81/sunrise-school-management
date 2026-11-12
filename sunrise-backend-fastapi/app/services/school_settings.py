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
    module.shop.enabled         School Shop (uniform and book sales, stock,
                                pricing). Default: off for every school; a
                                school admin turns it on in Settings.

SETTINGS_CATALOG lists every setting a school admin may change on the Settings
screen, with its type and the default used while no value is stored.
"""
from dataclasses import asdict, dataclass, field
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.tenant import get_session_school
from app.models.school import School, SchoolSetting

EMAIL_DOMAIN = "user.email_domain"
SHOP_ENABLED = "module.shop.enabled"

TRUE_VALUES = ("true", "1", "yes", "on")

GALLERY = "gallery"
INVENTORY = "inventory"
STUDENT_PHOTOS = "student_photos"
TEACHER_PHOTOS = "teacher_photos"


async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
    value = (await db.execute(select(SchoolSetting.value).where(SchoolSetting.key == key))).scalar_one_or_none()
    return value.strip() if value and value.strip() else None


async def get_bool(db: AsyncSession, key: str, default: bool = False) -> bool:
    value = await get_setting(db, key)
    return default if value is None else value.lower() in TRUE_VALUES


async def shop_enabled(db: AsyncSession) -> bool:
    return await get_bool(db, SHOP_ENABLED, default=False)


async def features(db: AsyncSession) -> dict:
    """Optional modules this school uses; the frontend shows only these."""
    return {"shop": await shop_enabled(db)}


@dataclass(frozen=True)
class SettingSpec:
    key: str
    label: str
    group: str
    type: str  # bool, int, decimal, text, choice
    default: Optional[str] = None
    help: str = ""
    choices: tuple = field(default_factory=tuple)
    min: Optional[float] = None
    max: Optional[float] = None

    def as_dict(self) -> dict:
        data = asdict(self)
        data["choices"] = list(self.choices)
        return data


SETTINGS_CATALOG = (
    SettingSpec(SHOP_ENABLED, "School Shop", "Modules", "bool", "false",
                "Sell uniforms and books, track stock and prices. Off by default."),
    SettingSpec("fee.receipt_prefix", "Receipt prefix", "Fees", "text", None,
                "Start of every receipt number, e.g. SUN in SUN/2026-27/000123. Default: first 3 letters of the school code."),
    SettingSpec("fee.late_fee.enabled", "Late fee", "Fees", "bool", "false",
                "Add a Late fee due automatically after the grace days."),
    SettingSpec("fee.late_fee.mode", "Late fee type", "Fees", "choice", "FIXED",
                "A fixed amount, or a percent of the overdue amount.", ("FIXED", "PERCENT")),
    SettingSpec("fee.late_fee.value", "Late fee amount or percent", "Fees", "decimal", "0",
                "Charged once per overdue month.", min=0),
    SettingSpec("fee.late_fee.grace_days", "Grace days", "Fees", "int", "7",
                "Days after the due date before a late fee is added.", min=0, max=60),
    SettingSpec("fee.transport.cutoff_day", "Transport cut-off day", "Transport", "int", "15",
                "Transport started after this day of the month is billed from the next month.", min=1, max=31),
    SettingSpec("fee.transport.due_day", "Transport due day", "Transport", "int", "10",
                "Day of the month transport fees fall due.", min=1, max=28),
    SettingSpec("whatsapp.receipts_enabled", "Send receipts on WhatsApp", "Receipts", "bool", "true",
                "Send the receipt PDF to the parent's WhatsApp after each payment."),
    SettingSpec("whatsapp.media_receipt_template_sid", "WhatsApp receipt template", "Receipts", "text", None,
                "Twilio content template id used for receipt messages."),
    SettingSpec("receipt.logo", "Receipt logo", "Receipts", "text", None,
                "Image URL of the logo printed on receipts. Default: the school logo."),
    SettingSpec(EMAIL_DOMAIN, "Login email domain", "Accounts", "text", None,
                "Domain of the login emails made for new students and teachers. Existing logins keep theirs."),
)
SETTINGS_BY_KEY = {spec.key: spec for spec in SETTINGS_CATALOG}


def validate_value(spec: SettingSpec, value: Optional[str]) -> Optional[str]:
    """Normalised value to store, or ValueError with a message for the user."""
    if value is None or not str(value).strip():
        return None
    value = str(value).strip()
    if spec.type == "bool":
        if value.lower() not in TRUE_VALUES + ("false", "0", "no", "off"):
            raise ValueError(f"{spec.label}: use true or false")
        return "true" if value.lower() in TRUE_VALUES else "false"
    if spec.type in ("int", "decimal"):
        try:
            number = int(value) if spec.type == "int" else float(value)
        except ValueError:
            raise ValueError(f"{spec.label}: enter a {'whole ' if spec.type == 'int' else ''}number")
        if spec.min is not None and number < spec.min:
            raise ValueError(f"{spec.label}: must be at least {spec.min:g}")
        if spec.max is not None and number > spec.max:
            raise ValueError(f"{spec.label}: must be at most {spec.max:g}")
        return str(number)
    if spec.type == "choice":
        if value.upper() not in spec.choices:
            raise ValueError(f"{spec.label}: choose one of {', '.join(spec.choices)}")
        return value.upper()
    return value[:1000]


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
