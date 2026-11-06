"""
Drop the application schema and redeploy it, directly (no backend server).

The application lives in ONE schema (DB_SCHEMA, default "school") of a database
that may be shared with other applications (for example warsi_db, which also holds
"mart"). This script only ever drops and recreates that one schema.

The SQL files and their order come from Database/deploy_database.sql, the same list
psql uses, so there is one source of truth. Everything runs in a single transaction:
if any file fails, the database is left exactly as it was.

Usage (from the repository root):
    python redeploy_database.py                 # DATABASE_URL and DB_SCHEMA from sunrise-backend-fastapi/.env
    python redeploy_database.py --schema school --database-url postgresql://user:pass@localhost:5432/warsi_db
    python redeploy_database.py --yes           # skip the confirmation prompt

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
DEFAULT_SCHEMA = "school"
PROTECTED_SCHEMAS = {"public", "information_schema"}
_SCHEMA_RE = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")

# Lines that only make sense in psql, or that would end our single transaction
_SKIP_LINE = re.compile(r"^\s*(\\|BEGIN\s*;\s*$|COMMIT\s*;\s*$)", re.IGNORECASE)


def _print(text: str = "") -> None:
    # Windows consoles may not be UTF-8
    print(text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))


def _env_file_value(key: str):
    if not BACKEND_ENV.exists():
        return None
    for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(f"{key}=") and not line.startswith("#"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def setting(key: str, cli_value: str = None, default: str = None):
    return cli_value or os.getenv(key) or _env_file_value(key) or default


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


def prepare_sql(path: Path) -> str:
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if not _SKIP_LINE.match(line))


VERSIONING_DIR = DATABASE_DIR / "Versioning"
_MIGRATION_NAME = re.compile(r"^(V\d{3,})_([A-Za-z0-9_]+)\.sql$")


def migration_files(directory: Path = VERSIONING_DIR) -> list:
    """(version, path, description) for every V###_name.sql in directory, sorted by version number."""
    found = []
    for path in directory.glob("*.sql"):
        match = _MIGRATION_NAME.match(path.name)
        if not match:
            raise SystemExit(f"Migration file name must look like V001_short_description.sql: {path.name}")
        found.append((match.group(1), path, match.group(2).replace("_", " ")))
    found.sort(key=lambda item: int(item[0][1:]))
    versions = [v for v, _, _ in found]
    duplicates = sorted({v for v in versions if versions.count(v) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate migration versions: {', '.join(duplicates)}")
    return found


def file_checksum(path: Path) -> str:
    import hashlib
    # Normalise line endings so a Windows checkout and a Linux checkout agree
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_schema_name(schema: str) -> str:
    schema = schema.strip().lower()
    if not _SCHEMA_RE.match(schema) or schema in PROTECTED_SCHEMAS or schema.startswith("pg_"):
        raise SystemExit(f"Refusing to use schema {schema!r}")
    return schema


def resolve_target(args):
    """DATABASE_URL, schema and printable target from CLI arguments and .env, with the local-only guard."""
    database_url = setting("DATABASE_URL", args.database_url)
    if not database_url:
        raise SystemExit("DATABASE_URL not found. Pass --database-url or set it in sunrise-backend-fastapi/.env")
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]
    if not database_url.startswith("postgresql://"):
        raise SystemExit("Only PostgreSQL databases are supported")
    schema = validate_schema_name(setting("DB_SCHEMA", args.schema, DEFAULT_SCHEMA))
    parts = urlsplit(database_url)
    host = parts.hostname or "localhost"
    target = f"{host}:{parts.port or 5432}/{parts.path.lstrip('/')}"
    if host not in LOCAL_HOSTS and not args.allow_remote:
        raise SystemExit(f"Refusing to use non-local database {target}. Use --allow-remote if you really mean it.")
    return database_url, schema, target


async def show_counts(conn: asyncpg.Connection, schema: str) -> None:
    tables = await conn.fetchval(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = $1 AND table_type = 'BASE TABLE'",
        schema,
    )
    _print(f"Tables in {schema}: {tables}")
    for table in ("schools", "users", "user_types", "classes", "session_years"):
        exists = await conn.fetchval("SELECT to_regclass($1) IS NOT NULL", f'"{schema}"."{table}"')
        if exists:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
            _print(f"  {table}: {count} rows")


async def redeploy(database_url: str, schema: str) -> bool:
    files = deployment_files()
    conn = await asyncpg.connect(database_url)
    try:
        async with conn.transaction():
            _print(f"Dropping schema {schema} (other schemas are not touched) ...")
            await conn.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
            await conn.execute(f'CREATE SCHEMA "{schema}"')
            # Session-level only: the database-wide search_path is never changed
            await conn.execute(f'SET LOCAL search_path TO "{schema}"')
            for index, path in enumerate(files, start=1):
                name = path.relative_to(DATABASE_DIR).as_posix()
                try:
                    await conn.execute(prepare_sql(path))
                except Exception as error:  # report which file failed, then roll back
                    _print(f"[{index:>2}/{len(files)}] FAILED  {name}")
                    _print(f"         {type(error).__name__}: {error}")
                    raise
                _print(f"[{index:>2}/{len(files)}] ok      {name}")

            # The baseline already contains every migration in Versioning/ (each
            # migration is also folded into its Tables/ script), so record them as
            # applied: migrate_database.py must never run them on this schema.
            included = migration_files()
            for version, path, description in included:
                await conn.execute(
                    "INSERT INTO schema_migrations (version, filename, description, checksum, kind) "
                    "VALUES ($1, $2, $3, $4, 'INCLUDED_IN_BASELINE')",
                    version, path.name, description, file_checksum(path),
                )
            if included:
                _print(f"Recorded {len(included)} migration(s) as included in the baseline: "
                       + ", ".join(v for v, _, _ in included))
    except Exception:
        _print()
        _print("Deployment FAILED. The transaction was rolled back, so the database is unchanged.")
        return False
    finally:
        if not conn.is_closed():
            try:
                _print()
                await show_counts(conn, schema)
            except Exception:
                pass
            await conn.close()

    _print()
    _print("Deployment SUCCESSFUL.")
    _print("Admin logins: see Database/Init/02_create_admin_user.sql and 03_create_super_admin_user.sql.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database-url", help="PostgreSQL URL. Default: DATABASE_URL from sunrise-backend-fastapi/.env")
    parser.add_argument("--schema", help=f"Schema to redeploy. Default: DB_SCHEMA from .env, else {DEFAULT_SCHEMA}")
    parser.add_argument("--yes", action="store_true", help="Do not ask for confirmation")
    parser.add_argument("--allow-remote", action="store_true", help="Allow a database that is not on this machine")
    args = parser.parse_args()

    database_url, schema, target = resolve_target(args)

    _print("=" * 60)
    _print("SCHOOL DATABASE REDEPLOYMENT")
    _print("=" * 60)
    _print(f"Target: {target}, schema {schema}")
    _print(f"Files:  {len(deployment_files())} from Database/deploy_database.sql")
    _print()
    _print(f"WARNING: this DROPS the {schema} schema and ALL its data, for every school.")
    _print("Other schemas in the database are not touched.")
    if not args.yes:
        answer = input(f"Type the schema name ({schema}) to continue: ").strip()
        if answer != schema:
            _print("Cancelled.")
            return 1
    _print()

    return 0 if asyncio.run(redeploy(database_url, schema)) else 1


if __name__ == "__main__":
    sys.exit(main())
