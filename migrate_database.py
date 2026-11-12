"""
Apply pending migrations from Database/Versioning/ to an existing schema, once each.

Every applied migration is recorded in <schema>.schema_migrations with a SHA-256
checksum of its file. A migration that is already recorded is never run again, and
the runner stops if an applied file was edited afterwards (its checksum changed).

Each migration runs in its own transaction: if it fails, that migration is rolled
back, nothing is recorded, and the runner stops so later migrations do not run on
top of a half-applied change. A database lock stops two runs at the same time.

Usage (from the repository root):
    python migrate_database.py --status      # list applied and pending migrations, change nothing
    python migrate_database.py               # apply pending migrations (asks first)
    python migrate_database.py --yes         # apply without asking

DATABASE_URL and DB_SCHEMA come from sunrise-backend-fastapi/.env unless given with
--database-url / --schema. Only local databases are allowed unless --allow-remote is given.

Writing a migration: see Database/Versioning/README.md.
"""
import argparse
import asyncio
import sys
import time
from pathlib import Path

import asyncpg

from redeploy_database import (
    VERSIONING_DIR,
    _print,
    file_checksum,
    migration_files,
    prepare_sql,
    resolve_target,
)


async def _applied(conn, schema: str) -> dict:
    exists = await conn.fetchval("SELECT to_regclass($1) IS NOT NULL", f'"{schema}".schema_migrations')
    if not exists:
        raise SystemExit(
            f"Schema {schema} has no schema_migrations table. Deploy it first with: python redeploy_database.py"
        )
    rows = await conn.fetch(
        f'SELECT version, filename, checksum, kind, applied_at FROM "{schema}".schema_migrations'
    )
    return {r["version"]: r for r in rows}


def _plan(files: list, applied: dict):
    """Split migration files into applied, pending and edited-after-applying."""
    done, pending, edited = [], [], []
    for version, path, description in files:
        row = applied.get(version)
        if row is None:
            pending.append((version, path, description))
        elif row["checksum"] and row["checksum"] != file_checksum(path):
            edited.append((version, path, row))
        else:
            done.append((version, path, row))
    known = {v for v, _, _ in files}
    missing = sorted(v for v, row in applied.items() if row["kind"] != "BASELINE" and v not in known)
    return done, pending, edited, missing


async def run(database_url: str, schema: str, directory: Path, status_only: bool, assume_yes: bool) -> int:
    files = migration_files(directory)
    conn = await asyncpg.connect(database_url)
    try:
        # Migrations work across schools: row-level security must not hide rows from them
        await conn.execute("SET app.bypass_rls = on")
        # One runner per schema at a time
        await conn.execute("SELECT pg_advisory_lock(hashtext($1))", f"migrations:{schema}")
        applied = await _applied(conn, schema)
        done, pending, edited, missing = _plan(files, applied)

        baseline = [r for r in applied.values() if r["kind"] == "BASELINE"]
        if baseline:
            _print(f"Baseline: {baseline[0]['version']} (deployed {baseline[0]['applied_at']:%Y-%m-%d %H:%M})")
        for version, path, row in done:
            how = "in baseline" if row["kind"] == "INCLUDED_IN_BASELINE" else f"applied {row['applied_at']:%Y-%m-%d %H:%M}"
            _print(f"  done     {path.name}  ({how})")
        for version, path, row in edited:
            _print(f"  EDITED   {path.name}  (file changed after it was applied)")
        for version, path, _ in pending:
            _print(f"  pending  {path.name}")
        for version in missing:
            _print(f"  missing  {version}  (recorded in the database, file not found)")
        if not files:
            _print("  (no migrations in Database/Versioning/)")
        _print()

        if edited:
            _print("Stopping: an applied migration was edited. Never change an applied migration;")
            _print("restore the file and put the change in a new migration instead.")
            return 2
        if status_only:
            _print(f"{len(pending)} pending migration(s).")
            return 0
        if not pending:
            _print("Schema is up to date.")
            return 0
        if not assume_yes:
            answer = input(f"Apply {len(pending)} migration(s) to schema {schema}? (yes/no): ").strip().lower()
            if answer != "yes":
                _print("Cancelled.")
                return 1

        for version, path, description in pending:
            started = time.monotonic()
            try:
                async with conn.transaction():
                    await conn.execute(f'SET LOCAL search_path TO "{schema}"')
                    await conn.execute(prepare_sql(path))
                    await conn.execute(
                        "INSERT INTO schema_migrations (version, filename, description, checksum, kind, execution_ms) "
                        "VALUES ($1, $2, $3, $4, 'MIGRATION', $5)",
                        version, path.name, description, file_checksum(path),
                        int((time.monotonic() - started) * 1000),
                    )
            except Exception as error:
                _print(f"  FAILED   {path.name}")
                _print(f"           {type(error).__name__}: {error}")
                _print()
                _print(f"{path.name} was rolled back and not recorded. Later migrations were not run.")
                return 1
            _print(f"  applied  {path.name}  ({int((time.monotonic() - started) * 1000)} ms)")
        _print()
        _print("Schema is up to date.")
        return 0
    finally:
        await conn.close()  # also releases the advisory lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--status", action="store_true", help="Only list applied and pending migrations")
    parser.add_argument("--database-url", help="PostgreSQL URL. Default: DATABASE_URL from sunrise-backend-fastapi/.env")
    parser.add_argument("--schema", help="Schema to migrate. Default: DB_SCHEMA from .env, else school")
    parser.add_argument("--yes", action="store_true", help="Do not ask for confirmation")
    parser.add_argument("--allow-remote", action="store_true", help="Allow a database that is not on this machine")
    parser.add_argument("--dir", type=Path, default=VERSIONING_DIR, help=argparse.SUPPRESS)  # tests only
    args = parser.parse_args()

    database_url, schema, target = resolve_target(args)
    _print(f"Target: {target}, schema {schema}")
    return asyncio.run(run(database_url, schema, args.dir, args.status, args.yes))


if __name__ == "__main__":
    sys.exit(main())
