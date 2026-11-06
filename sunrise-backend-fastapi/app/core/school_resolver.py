"""
Work out which school a request is for.

Order of precedence:

1. ``X-School-Code`` header (set explicitly by the frontend or by tests).
2. The subdomain of the ``Origin`` header. A browser on ``sunrise.<base domain>``
   calling the API on another host always sends this on API (CORS) requests.
3. The subdomain of the forwarded host or ``Host`` header (same-origin deployments).

Only hosts under ``settings.BASE_DOMAIN`` count, and reserved labels such as
``api`` or ``www`` are ignored. When nothing identifies a school, the caller may
fall back to ``settings.DEFAULT_SCHOOL_CODE``.
"""
import re
from typing import Optional
from urllib.parse import urlsplit

from starlette.requests import Request

from app.core.config import settings

SCHOOL_CODE_HEADER = "x-school-code"
_CODE_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_school_code(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    code = value.strip().lower()
    return code if _CODE_RE.match(code) else None


def school_code_from_host(host: Optional[str], base_domain: Optional[str] = None) -> Optional[str]:
    """Return the school code for ``host`` (``sunrise.example.in:443`` -> ``sunrise``)."""
    base = (settings.BASE_DOMAIN if base_domain is None else base_domain).strip().lower().lstrip(".")
    if not host or not base:
        return None
    hostname = host.strip().lower().split(":", 1)[0].rstrip(".")
    suffix = "." + base
    if not hostname.endswith(suffix):
        return None
    label = hostname[: -len(suffix)]
    # Only a single label directly under the base domain is a school
    if not label or "." in label or label in settings.RESERVED_SUBDOMAINS:
        return None
    return normalize_school_code(label)


def _host_of(origin: Optional[str]) -> Optional[str]:
    if not origin or origin == "null":
        return None
    return urlsplit(origin).netloc or None


def resolve_school_code(request: Request) -> Optional[str]:
    """School code named by the request itself, or None if it names none."""
    header_code = normalize_school_code(request.headers.get(SCHOOL_CODE_HEADER))
    if header_code:
        return header_code

    origin_code = school_code_from_host(_host_of(request.headers.get("origin")))
    if origin_code:
        return origin_code

    forwarded = request.headers.get("x-forwarded-host")
    if forwarded:
        forwarded = forwarded.split(",", 1)[0]
    return school_code_from_host(forwarded or request.headers.get("host"))
