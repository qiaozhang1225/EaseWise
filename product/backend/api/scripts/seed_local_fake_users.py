from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from product.backend.api.config import get_database_path
from product.backend.api.database import ensure_schema, open_connection


FAKE_COUNT = 25
FAKE_PREFIX = "local_fake_pagination"
FAKE_CHANNEL = "local_pagination_seed"


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def table_columns(connection: Any, table: str) -> dict[str, Any]:
    return {str(row["name"]): row for row in connection.execute(f"PRAGMA table_info({quote_identifier(table)})").fetchall()}


def default_value_for_column(name: str, now_text: str) -> Any:
    lowered = name.lower()
    if lowered in {"id", "user_id"} or lowered.endswith("_id"):
        return f"{FAKE_PREFIX}_{lowered}"
    if lowered.endswith("_at") or lowered in {"created_time", "updated_time"}:
        return now_text
    if lowered.startswith("is_") or lowered.endswith("_enabled") or lowered in {"enabled", "profile_completed"}:
        return 1
    if any(part in lowered for part in ("balance", "amount", "count", "version", "priority", "sort_order")):
        return 0
    if lowered == "status":
        return "active"
    if lowered == "identity_level":
        return "normal_user"
    if lowered == "primary_identity_type":
        return "phone"
    return ""


def complete_required_values(columns: dict[str, Any], values: dict[str, Any], now_text: str) -> dict[str, Any]:
    completed = {key: value for key, value in values.items() if key in columns}
    for name, column in columns.items():
        has_default = column["dflt_value"] is not None
        is_required = bool(column["notnull"]) and not bool(column["pk"]) and not has_default
        if is_required and name not in completed:
            completed[name] = default_value_for_column(name, now_text)
    return completed


def upsert_row(connection: Any, table: str, key_column: str, key_value: Any, values: dict[str, Any], now_text: str) -> None:
    columns = table_columns(connection, table)
    filtered = complete_required_values(columns, values, now_text)
    if key_column not in columns:
        raise RuntimeError(f"{table}.{key_column} does not exist")
    if key_column not in filtered:
        filtered[key_column] = key_value
    if "id" in columns and "id" not in values:
        filtered["id"] = f"{FAKE_PREFIX}_{table}_{key_value}"

    exists = connection.execute(
        f"SELECT 1 FROM {quote_identifier(table)} WHERE {quote_identifier(key_column)} = ? LIMIT 1",
        (key_value,),
    ).fetchone()
    if exists:
        update_columns = [name for name in filtered if name != key_column]
        if not update_columns:
            return
        assignments = ", ".join(f"{quote_identifier(name)} = ?" for name in update_columns)
        connection.execute(
            f"UPDATE {quote_identifier(table)} SET {assignments} WHERE {quote_identifier(key_column)} = ?",
            [filtered[name] for name in update_columns] + [key_value],
        )
        return

    insert_columns = list(filtered.keys())
    placeholders = ", ".join("?" for _ in insert_columns)
    connection.execute(
        f"INSERT INTO {quote_identifier(table)} ({', '.join(quote_identifier(name) for name in insert_columns)}) VALUES ({placeholders})",
        [filtered[name] for name in insert_columns],
    )


def insert_phone_identity(connection: Any, user_id: str, phone: str, now_text: str) -> None:
    columns = table_columns(connection, "user_phone_identities")
    if not columns:
        return
    delete_conditions = []
    delete_params: list[Any] = []
    if "user_id" in columns:
        delete_conditions.append("user_id = ?")
        delete_params.append(user_id)
    if "normalized_phone" in columns:
        delete_conditions.append("normalized_phone = ?")
        delete_params.append(phone)
    if delete_conditions:
        connection.execute(
            f"DELETE FROM user_phone_identities WHERE {' OR '.join(delete_conditions)}",
            delete_params,
        )

    values = complete_required_values(
        columns,
        {
            "id": f"{FAKE_PREFIX}_phone_{phone}",
            "user_id": user_id,
            "phone": phone,
            "phone_number": phone,
            "raw_phone": phone,
            "normalized_phone": phone,
            "password_hash": "local_fake_password_hash",
            "is_primary": 1,
            "verified_at": now_text,
            "created_at": now_text,
            "updated_at": now_text,
        },
        now_text,
    )
    insert_columns = list(values.keys())
    placeholders = ", ".join("?" for _ in insert_columns)
    connection.execute(
        f"INSERT INTO user_phone_identities ({', '.join(quote_identifier(name) for name in insert_columns)}) VALUES ({placeholders})",
        [values[name] for name in insert_columns],
    )


def seed_fake_users() -> None:
    ensure_schema()
    base_time = datetime.now(timezone.utc).replace(microsecond=0)
    identities = ["normal_user", "promoter", "vip_promoter", "svip_promoter"]
    statuses = ["active", "active", "active", "disabled"]

    with open_connection() as connection:
        for index in range(1, FAKE_COUNT + 1):
            created_at = base_time - timedelta(days=index)
            updated_at = created_at + timedelta(hours=2)
            last_active_at = base_time - timedelta(minutes=index * 11)
            created_text = created_at.isoformat().replace("+00:00", "Z")
            updated_text = updated_at.isoformat().replace("+00:00", "Z")
            active_text = last_active_at.isoformat().replace("+00:00", "Z")
            user_id = f"{FAKE_PREFIX}_{index:02d}"
            uid = f"9900{index:04d}"
            phone = f"1889900{index:04d}"
            identity_level = identities[(index - 1) % len(identities)]
            status = statuses[(index - 1) % len(statuses)]

            upsert_row(
                connection,
                "users",
                "id",
                user_id,
                {
                    "id": user_id,
                    "uid": uid,
                    "status": status,
                    "identity_level": identity_level,
                    "primary_identity_type": "phone",
                    "registered_channel": FAKE_CHANNEL,
                    "promoter_parent_user_id": None,
                    "first_login_at": created_text,
                    "registered_at": created_text,
                    "created_at": created_text,
                    "updated_at": updated_text,
                    "last_active_at": active_text,
                },
                created_text,
            )
            upsert_row(
                connection,
                "user_profiles",
                "user_id",
                user_id,
                {
                    "user_id": user_id,
                    "nickname": f"本地分页测试用户 {index:02d}",
                    "avatar_url": None,
                    "profile_completed": 1,
                    "created_at": created_text,
                    "updated_at": updated_text,
                },
                created_text,
            )
            upsert_row(
                connection,
                "points_accounts",
                "user_id",
                user_id,
                {
                    "user_id": user_id,
                    "balance": 10000 + index * 37,
                    "frozen_balance": index % 3 * 10,
                    "version": 1,
                    "created_at": created_text,
                    "updated_at": updated_text,
                },
                created_text,
            )
            insert_phone_identity(connection, user_id, phone, created_text)

    print(f"Seeded {FAKE_COUNT} fake users into {get_database_path()}")


if __name__ == "__main__":
    seed_fake_users()
