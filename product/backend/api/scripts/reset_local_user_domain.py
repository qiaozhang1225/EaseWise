from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DB_PATH = REPO_ROOT / "product" / "backend" / "api" / "data" / "app.db"

USER_DOMAIN_TABLES = (
    "review_aspect_unlocks",
    "usage_records",
    "reviews",
    "payment_transactions",
    "refund_requests",
    "promotion_commissions",
    "promotion_withdrawals",
    "promotion_applications",
    "promotion_relationships",
    "recharge_orders",
    "points_ledgers",
    "points_accounts",
    "promotion_wallet_accounts",
    "promotion_rebate_accounts",
    "user_sessions",
    "user_phone_identities",
    "user_wechat_identities",
    "guest_user_merges",
    "guest_identities",
    "user_profiles",
    "admin_operation_logs",
    "users",
)

OBSOLETE_CONFIG_KEYS = (
    "points.guest_initial_grant",
)


def resolve_db_path(raw_path: str | None) -> Path:
    if raw_path:
        return Path(raw_path).expanduser().resolve()
    env_path = os.getenv("EASEWISE_DB_PATH", "").strip()
    if env_path:
        return Path(env_path).expanduser().resolve()
    return DEFAULT_DB_PATH.resolve()


def existing_tables(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {str(row[0]) for row in rows}


def reset_user_domain(db_path: Path) -> list[str]:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    deleted_tables: list[str] = []
    with sqlite3.connect(db_path) as connection:
        tables = existing_tables(connection)
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN")
        try:
            for table_name in USER_DOMAIN_TABLES:
                if table_name not in tables:
                    continue
                connection.execute(f"DELETE FROM {table_name}")
                deleted_tables.append(table_name)

            if "runtime_config_entries" in tables:
                connection.executemany(
                    "DELETE FROM runtime_config_entries WHERE config_key = ?",
                    [(config_key,) for config_key in OBSOLETE_CONFIG_KEYS],
                )

            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.execute("PRAGMA foreign_keys = ON")
    return deleted_tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset local EaseWise user-domain data while preserving system configuration.")
    parser.add_argument("--db", dest="db_path", default=None, help="SQLite database path. Defaults to EASEWISE_DB_PATH or product/backend/api/data/app.db.")
    args = parser.parse_args()

    db_path = resolve_db_path(args.db_path)
    deleted_tables = reset_user_domain(db_path)
    print(f"Reset user-domain data in {db_path}")
    print("Cleared tables: " + (", ".join(deleted_tables) if deleted_tables else "none"))


if __name__ == "__main__":
    main()
