"""
Drop the sunrise schema and redeploy the whole database, directly (no backend server).

The SQL files and their order come from Database/deploy_database.sql, the same list
psql uses, so there is one source of truth. Everything runs in a single transaction:
if any file fails, the database is left exactly as it was.

Usage (from the repository root):
    python redeploy_database.py                       # uses DATABASE_URL from sunrise-backend-fastapi/.env
    python redeploy_database.py --database-url postgresql://user:pass@localhost:5432/sunrise_school_db
    python redeploy_database.py --yes                 # skip the confirmation prompt

Only local databases (localhost, 127.0.0.1, ::1) are allowed unless --allow-remote is given.
"""
import argparse
import asyncio
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import asyncpg

REPO_ROOT = Path(__file__).resolve().parent
DATABASE_DIR = REPO_ROOT / "Database"
MASTER_SCRIPT = DATABASE_DIR / "deploy_database.sql"
BACKEND_ENV = REPO_ROOT / "sunrise-backend-fastapi" / ".env"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
SCHEMA = "sunrise"

# Lines that only make sense in psql, or that would end our single transaction
_SKIP_LINE = re.compile(r"^\s*(\\|BEGIN\s*;\s*$|COMMIT\s*;\s*$)", re.IGNORECASE)


def _print(text: str = "") -> None:
    # Windows consoles may not be UTF-8
    print(text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))


def load_database_url(cli_value: str = None) -> str:
    if cli_value:
        return cli_value
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("DATABASE_URL not found. Pass --database-url or set it in sunrise-backend-fastapi/.env")


def deployment_files() -> list:
    """SQL files named by the \\ir lines of deploy_database.sql, in order."""
    files = []
    for line in MASTER_SCRIPT.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*\\ir\s+(\S+)", line)
        if match:
            files.append(DATABASE_DIR / match.group(1))
    missing = [str(f.relative_to(REPO_ROOT)) for f in files if not f.exists()]
    if missing:
        raise SystemExit("Files listed in deploy_database.sql are missing:\n  " + "\n  ".join(missing))
    return files


def prepare_sql(path: Path, database_name: str) -> str:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not _SKIP_LINE.match(line)]
    return "\n".join(lines).replace("sunrise_school_db", database_name)


async def show_counts(conn: asyncpg.Connection) -> None:
    tables = await conn.fetchval(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = $1 AND table_type = 'BASE TABLE'",
        SCHEMA,
    )
    _print(f"Tables in {SCHEMA}: {tables}")
    for table in ("schools", "users", "user_types", "classes", "session_years"):
        exists = await conn.fetchval("SELECT to_regclass($1) IS NOT NULL", f"{SCHEMA}.{table}")
        if exists:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {SCHEMA}."{table}"')
            _print(f"  {table}: {count} rows")


async def redeploy(database_url: str) -> bool:
    parts = urlsplit(database_url)
    database_name = parts.path.lstrip("/").split("?")[0]
    files = deployment_files()

    conn = await asyncpg.connect(database_url)
    try:
        async with conn.transaction():
            _print(f"Dropping schema {SCHEMA} ...")
            await conn.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
            for index, path in enumerate(files, start=1):
                name = path.relative_to(DATABASE_DIR).as_posix()
                try:
                    await conn.execute(prepare_sql(path, database_name))
                except Exception as error:  # report which file failed, then roll back
                    _print(f"[{index:>2}/{len(files)}] FAILED  {name}")
                    _print(f"         {type(error).__name__}: {error}")
                    raise
                _print(f"[{index:>2}/{len(files)}] ok      {name}")
    except Exception:
        _print()
        _print("Deployment FAILED. The transaction was rolled back, so the database is unchanged.")
        return False
    finally:
        if not conn.is_closed():
            try:
                _print()
                await show_counts(conn)
            except Exception:
                pass
            await conn.close()

    _print()
    _print("Deployment SUCCESSFUL.")
    _print("Admin login: see Database/Init/02_create_admin_user.sql for the credentials.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database-url", help="PostgreSQL URL. Default: DATABASE_URL from sunrise-backend-fastapi/.env")
    parser.add_argument("--yes", action="store_true", help="Do not ask for confirmation")
    parser.add_argument("--allow-remote", action="store_true", help="Allow a database that is not on this machine")
    args = parser.parse_args()

    database_url = load_database_url(args.database_url)
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]
    if not database_url.startswith("postgresql://"):
        raise SystemExit("Only PostgreSQL databases are supported")

    parts = urlsplit(database_url)
    host = parts.hostname or "localhost"
    target = f"{host}:{parts.port or 5432}/{parts.path.lstrip('/')}"
    if host not in LOCAL_HOSTS and not args.allow_remote:
        raise SystemExit(f"Refusing to redeploy non-local database {target}. Use --allow-remote if you really mean it.")

    _print("=" * 60)
    _print("SUNRISE SCHOOL DATABASE REDEPLOYMENT")
    _print("=" * 60)
    _print(f"Target: {target}")
    _print(f"Files:  {len(deployment_files())} from Database/deploy_database.sql")
    _print()
    _print(f"WARNING: this DROPS the {SCHEMA} schema and ALL its data, for every school.")
    if not args.yes:
        answer = input(f"Type the database name ({parts.path.lstrip('/')}) to continue: ").strip()
        if answer != parts.path.lstrip("/"):
            _print("Cancelled.")
            return 1
    _print()

    return 0 if asyncio.run(redeploy(database_url)) else 1


if __name__ == "__main__":
    sys.exit(main())
