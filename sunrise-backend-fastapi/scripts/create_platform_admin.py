"""
Create a platform admin login (manages schools; belongs to no school).

Run once per environment to create the first platform admin. The password is
asked for interactively unless --password is given.

Usage, from sunrise-backend-fastapi/:
    ..\\.venv\\Scripts\\python scripts\\create_platform_admin.py --email platform@yourdomain.com --first-name Javed --last-name Ansari

Uses DATABASE_URL and DB_SCHEMA from .env. Refuses non-local databases unless
--allow-remote is given (for DigitalOcean, later).
"""
import argparse
import asyncio
import getpass
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncpg  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.user import PLATFORM_ADMIN_USER_TYPE_ID  # noqa: E402


async def main(args) -> int:
    host = urlsplit(settings.ASYNCPG_DSN).hostname
    if host not in ("localhost", "127.0.0.1", "::1") and not args.allow_remote:
        print(f"Refusing to run against non-local database host {host}. Use --allow-remote if you mean it.")
        return 1
    password = args.password or getpass.getpass("Password (8+ characters): ")
    if len(password) < 8:
        print("Password must be at least 8 characters")
        return 1

    conn = await asyncpg.connect(
        settings.ASYNCPG_DSN, ssl=settings.DB_SSL, server_settings={"search_path": settings.DB_SCHEMA}
    )
    try:
        has_type = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM user_types WHERE id = $1)", PLATFORM_ADMIN_USER_TYPE_ID)
        if not has_type:
            print("The PLATFORM_ADMIN user type is missing. Apply migrations first: python migrate_database.py")
            return 1
        exists = await conn.fetchval(
            "SELECT id FROM users WHERE email = $1 AND school_id IS NULL AND (is_deleted IS NOT TRUE)", args.email
        )
        if exists:
            print(f"A platform admin with email {args.email} already exists (user id {exists})")
            return 1
        user_id = await conn.fetchval(
            """INSERT INTO users (school_id, email, password, first_name, last_name, user_type_id, is_active)
               VALUES (NULL, $1, $2, $3, $4, $5, TRUE) RETURNING id""",
            args.email, get_password_hash(password), args.first_name, args.last_name, PLATFORM_ADMIN_USER_TYPE_ID,
        )
    finally:
        await conn.close()
    print(f"Created platform admin {args.email} (user id {user_id}). Log in at POST /api/v1/platform/auth/login")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--email", required=True)
    parser.add_argument("--first-name", default="Platform")
    parser.add_argument("--last-name", default="Admin")
    parser.add_argument("--password", help="Omit to be asked interactively")
    parser.add_argument("--allow-remote", action="store_true")
    sys.exit(asyncio.run(main(parser.parse_args())))
