from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from .config import get_database_path


class InsufficientPointsError(RuntimeError):
    pass

CREATE_REVIEWS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    phone TEXT NOT NULL,
    gender TEXT NOT NULL,
    status TEXT NOT NULL,
    progress_stage TEXT,
    progress_message TEXT,
    score_result_json TEXT,
    score_template_json TEXT,
    score_markdown TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_active_at TEXT NOT NULL
)
"""

CREATE_USER_PROFILES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    nickname TEXT,
    avatar_url TEXT,
    profile_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_USER_WECHAT_IDENTITIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_wechat_identities (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    appid TEXT NOT NULL,
    openid TEXT NOT NULL,
    unionid TEXT,
    session_key TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_login_at TEXT NOT NULL,
    UNIQUE(appid, openid),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_USER_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    device_type TEXT,
    client_version TEXT,
    ip TEXT,
    status TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_POINTS_ACCOUNTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS points_accounts (
    user_id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL,
    frozen_balance INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_POINTS_LEDGERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS points_ledgers (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    change_type TEXT NOT NULL,
    delta INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    biz_type TEXT NOT NULL,
    biz_id TEXT,
    idempotency_key TEXT,
    remark TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(user_id, idempotency_key),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_USAGE_RECORDS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS usage_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    scene TEXT NOT NULL,
    target_id TEXT,
    points_cost INTEGER NOT NULL,
    status TEXT NOT NULL,
    request_payload_summary TEXT,
    result_summary TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_GUEST_IDENTITIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS guest_identities (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    guest_key TEXT,
    appid TEXT,
    openid TEXT,
    unionid TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    UNIQUE(channel, guest_key),
    UNIQUE(appid, openid),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_GUEST_USER_MERGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS guest_user_merges (
    id TEXT PRIMARY KEY,
    guest_user_id TEXT NOT NULL UNIQUE,
    target_user_id TEXT NOT NULL,
    transferred_points INTEGER NOT NULL DEFAULT 0,
    merged_at TEXT NOT NULL,
    FOREIGN KEY(guest_user_id) REFERENCES users(id),
    FOREIGN KEY(target_user_id) REFERENCES users(id)
)
"""

CREATE_RUNTIME_CONFIG_ENTRIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS runtime_config_entries (
    id TEXT PRIMARY KEY,
    scope_type TEXT NOT NULL,
    scope_key TEXT NOT NULL,
    config_key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(scope_type, scope_key, config_key)
)
"""

CREATE_REVIEW_ASPECT_UNLOCKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS review_aspect_unlocks (
    id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    aspect_key TEXT NOT NULL,
    points_cost INTEGER NOT NULL,
    usage_record_id TEXT,
    unlocked_at TEXT NOT NULL,
    UNIQUE(review_id, user_id, aspect_key),
    FOREIGN KEY(review_id) REFERENCES reviews(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_RECHARGE_ORDERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recharge_orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    channel TEXT,
    status TEXT NOT NULL,
    package_key TEXT NOT NULL,
    package_title TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    points_amount INTEGER NOT NULL,
    bonus_points INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL,
    external_order_id TEXT,
    idempotency_key TEXT,
    proof_url TEXT,
    remark TEXT,
    review_note TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    granted_ledger_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, idempotency_key),
    UNIQUE(source, external_order_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(granted_ledger_id) REFERENCES points_ledgers(id)
)
"""

CREATE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_reviews_user_created_at ON reviews(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_wechat_identity_user_id ON user_wechat_identities(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_wechat_identity_unionid ON user_wechat_identities(unionid)",
    "CREATE INDEX IF NOT EXISTS idx_guest_identity_user_id ON guest_identities(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_guest_identity_guest_key ON guest_identities(channel, guest_key)",
    "CREATE INDEX IF NOT EXISTS idx_guest_identity_openid ON guest_identities(appid, openid)",
    "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)",
    "CREATE INDEX IF NOT EXISTS idx_points_ledgers_user_created_at ON points_ledgers(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_usage_records_user_created_at ON usage_records(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_runtime_config_scope_key ON runtime_config_entries(scope_type, scope_key, config_key)",
    "CREATE INDEX IF NOT EXISTS idx_review_aspect_unlocks_review_user ON review_aspect_unlocks(review_id, user_id, unlocked_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_recharge_orders_user_created_at ON recharge_orders(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_recharge_orders_status_created_at ON recharge_orders(status, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_recharge_orders_source_external_order_id ON recharge_orders(source, external_order_id)",
)


@contextmanager
def open_connection() -> Iterator[sqlite3.Connection]:
    database_path = get_database_path()
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def _ensure_reviews_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(reviews)").fetchall()}
    if "user_id" not in columns:
        connection.execute("ALTER TABLE reviews ADD COLUMN user_id TEXT")
    if "progress_stage" not in columns:
        connection.execute("ALTER TABLE reviews ADD COLUMN progress_stage TEXT")
    if "progress_message" not in columns:
        connection.execute("ALTER TABLE reviews ADD COLUMN progress_message TEXT")



def ensure_schema() -> None:
    with open_connection() as connection:
        connection.execute(CREATE_REVIEWS_TABLE_SQL)
        _ensure_reviews_columns(connection)
        connection.execute(CREATE_USERS_TABLE_SQL)
        connection.execute(CREATE_USER_PROFILES_TABLE_SQL)
        connection.execute(CREATE_USER_WECHAT_IDENTITIES_TABLE_SQL)
        connection.execute(CREATE_GUEST_IDENTITIES_TABLE_SQL)
        connection.execute(CREATE_GUEST_USER_MERGES_TABLE_SQL)
        connection.execute(CREATE_USER_SESSIONS_TABLE_SQL)
        connection.execute(CREATE_POINTS_ACCOUNTS_TABLE_SQL)
        connection.execute(CREATE_POINTS_LEDGERS_TABLE_SQL)
        connection.execute(CREATE_USAGE_RECORDS_TABLE_SQL)
        connection.execute(CREATE_RUNTIME_CONFIG_ENTRIES_TABLE_SQL)
        connection.execute(CREATE_REVIEW_ASPECT_UNLOCKS_TABLE_SQL)
        connection.execute(CREATE_RECHARGE_ORDERS_TABLE_SQL)
        for statement in CREATE_INDEX_SQL:
            connection.execute(statement)



def create_review(*, review_id: str, user_id: str | None, phone: str, gender: str, status: str, created_at: str, progress_stage: str | None = None, progress_message: str | None = None) -> None:
    with open_connection() as connection:
        connection.execute(
            "INSERT INTO reviews (id, user_id, phone, gender, status, progress_stage, progress_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (review_id, user_id, phone, gender, status, progress_stage, progress_message, created_at, created_at),
        )



def create_review_with_charge(*, review_id: str, user_id: str | None, phone: str, gender: str, status: str, created_at: str, progress_stage: str | None = None, progress_message: str | None = None, points_cost: int = 0, usage_scene: str | None = None, request_payload_summary: dict[str, Any] | None = None) -> None:
    normalized_points_cost = max(0, int(points_cost))
    with open_connection() as connection:
        connection.execute(
            "INSERT INTO reviews (id, user_id, phone, gender, status, progress_stage, progress_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (review_id, user_id, phone, gender, status, progress_stage, progress_message, created_at, created_at),
        )
        if user_id and usage_scene and normalized_points_cost > 0:
            _spend_points_in_connection(
                connection,
                user_id=user_id,
                points_cost=normalized_points_cost,
                biz_type=usage_scene,
                biz_id=review_id,
                idempotency_key=f"review:create:{review_id}",
                remark="phone_review_base_charge",
                now_text=created_at,
            )
            _create_usage_record_in_connection(
                connection,
                usage_record_id=review_id,
                user_id=user_id,
                scene=usage_scene,
                target_id=review_id,
                points_cost=normalized_points_cost,
                status="processing",
                request_payload_summary=request_payload_summary,
                result_summary=None,
                created_at=created_at,
                updated_at=created_at,
            )



def update_review_progress(*, review_id: str, progress_stage: str, progress_message: str | None, updated_at: str) -> None:
    with open_connection() as connection:
        connection.execute(
            "UPDATE reviews SET progress_stage = ?, progress_message = ?, updated_at = ? WHERE id = ?",
            (progress_stage, progress_message, updated_at, review_id),
        )



def complete_review(*, review_id: str, status: str, score_result: dict[str, Any], score_template: dict[str, Any], score_markdown: str | None, updated_at: str) -> None:
    with open_connection() as connection:
        connection.execute(
            """
            UPDATE reviews
            SET status = ?, progress_stage = ?, progress_message = ?, score_result_json = ?, score_template_json = ?, score_markdown = ?, error_message = NULL, updated_at = ?
            WHERE id = ?
            """,
            (status, "completed", "评测结果已生成", json.dumps(score_result, ensure_ascii=False), json.dumps(score_template, ensure_ascii=False), score_markdown, updated_at, review_id),
        )



def fail_review(*, review_id: str, error_message: str, updated_at: str) -> None:
    with open_connection() as connection:
        connection.execute(
            "UPDATE reviews SET status = ?, progress_stage = ?, progress_message = ?, error_message = ?, updated_at = ? WHERE id = ?",
            ("failed", "failed", error_message, error_message, updated_at, review_id),
        )



def get_review(review_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, user_id, phone, gender, status, progress_stage, progress_message, score_result_json, score_template_json, score_markdown, error_message, created_at, updated_at FROM reviews WHERE id = ?",
            (review_id,),
        ).fetchone()
    return _deserialize_review_row(row) if row is not None else None



def list_reviews(limit: int = 20, user_id: str | None = None) -> list[dict[str, Any]]:
    with open_connection() as connection:
        if user_id:
            rows = connection.execute(
                "SELECT id, user_id, phone, gender, status, progress_stage, progress_message, error_message, created_at, updated_at FROM reviews WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT id, user_id, phone, gender, status, progress_stage, progress_message, error_message, created_at, updated_at FROM reviews ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [_deserialize_review_summary_row(row) for row in rows]



def upsert_wechat_user(*, appid: str, openid: str, unionid: str | None, session_key: str | None, nickname: str | None, avatar_url: str | None, initial_points: int, now_text: str) -> dict[str, Any]:
    with open_connection() as connection:
        existing = connection.execute(
            """
            SELECT i.id AS identity_id, i.user_id, i.unionid, p.nickname, p.avatar_url
            FROM user_wechat_identities i
            JOIN users u ON u.id = i.user_id
            LEFT JOIN user_profiles p ON p.user_id = u.id
            WHERE i.appid = ? AND i.openid = ?
            """,
            (appid, openid),
        ).fetchone()

        if existing is None:
            user_id = uuid4().hex
            connection.execute("INSERT INTO users (id, status, created_at, updated_at, last_active_at) VALUES (?, ?, ?, ?, ?)", (user_id, "active", now_text, now_text, now_text))
            connection.execute(
                "INSERT INTO user_profiles (user_id, nickname, avatar_url, profile_completed, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, nickname, avatar_url, _profile_completed(nickname, avatar_url), now_text, now_text),
            )
            connection.execute(
                "INSERT INTO user_wechat_identities (id, user_id, appid, openid, unionid, session_key, created_at, updated_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (uuid4().hex, user_id, appid, openid, unionid, session_key, now_text, now_text, now_text),
            )
            connection.execute(
                "INSERT INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, ?, 0, 0, ?, ?)",
                (user_id, initial_points, now_text, now_text),
            )
            if initial_points > 0:
                connection.execute(
                    "INSERT INTO points_ledgers (id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (uuid4().hex, user_id, "gift", initial_points, initial_points, "signup_bonus", user_id, f"signup:{appid}:{openid}", "initial test points", now_text),
                )
        else:
            user_id = str(existing["user_id"])
            final_nickname = _normalize_optional_text(nickname) or _normalize_optional_text(existing["nickname"])
            final_avatar_url = _normalize_optional_text(avatar_url) or _normalize_optional_text(existing["avatar_url"])
            final_unionid = _normalize_optional_text(unionid) or _normalize_optional_text(existing["unionid"])
            connection.execute("UPDATE users SET updated_at = ?, last_active_at = ? WHERE id = ?", (now_text, now_text, user_id))
            connection.execute(
                "INSERT OR IGNORE INTO user_profiles (user_id, nickname, avatar_url, profile_completed, created_at, updated_at) VALUES (?, NULL, NULL, 0, ?, ?)",
                (user_id, now_text, now_text),
            )
            connection.execute(
                "UPDATE user_profiles SET nickname = ?, avatar_url = ?, profile_completed = ?, updated_at = ? WHERE user_id = ?",
                (final_nickname, final_avatar_url, _profile_completed(final_nickname, final_avatar_url), now_text, user_id),
            )
            connection.execute(
                "UPDATE user_wechat_identities SET unionid = ?, session_key = ?, updated_at = ?, last_login_at = ? WHERE id = ?",
                (final_unionid, session_key, now_text, now_text, str(existing["identity_id"])),
            )
            connection.execute(
                "INSERT OR IGNORE INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, 0, 0, 0, ?, ?)",
                (user_id, now_text, now_text),
            )

        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    if row is None:
        raise RuntimeError("user_upsert_failed")
    return _deserialize_user_row(row)



def upsert_guest_user(*, channel: str, guest_key: str | None, appid: str | None, openid: str | None, unionid: str | None, initial_points: int, now_text: str) -> dict[str, Any]:
    normalized_channel = _normalize_optional_text(channel) or "h5"
    normalized_guest_key = _normalize_optional_text(guest_key) or uuid4().hex
    normalized_appid = _normalize_optional_text(appid)
    normalized_openid = _normalize_optional_text(openid)
    normalized_unionid = _normalize_optional_text(unionid)

    with open_connection() as connection:
        matched_by_guest_key = _get_guest_identity_by_guest_key_in_connection(connection, channel=normalized_channel, guest_key=normalized_guest_key)
        matched_by_openid = _get_guest_identity_by_openid_in_connection(connection, appid=normalized_appid, openid=normalized_openid)

        if matched_by_guest_key is not None and matched_by_openid is not None and str(matched_by_guest_key["user_id"]) != str(matched_by_openid["user_id"]):
            raise ValueError("guest_identity_conflict")

        matched_identity = matched_by_openid or matched_by_guest_key
        if matched_identity is None:
            user_id = uuid4().hex
            connection.execute("INSERT INTO users (id, status, created_at, updated_at, last_active_at) VALUES (?, ?, ?, ?, ?)", (user_id, "guest", now_text, now_text, now_text))
            connection.execute(
                "INSERT INTO user_profiles (user_id, nickname, avatar_url, profile_completed, created_at, updated_at) VALUES (?, NULL, NULL, 0, ?, ?)",
                (user_id, now_text, now_text),
            )
            _create_points_account_with_initial_grant_in_connection(connection, user_id=user_id, initial_points=initial_points, grant_biz_type="guest_bonus", grant_idempotency_key=f"guest-signup:{normalized_channel}:{normalized_guest_key}", remark="guest initial points", now_text=now_text)
            guest_identity_id = uuid4().hex
            connection.execute(
                "INSERT INTO guest_identities (id, user_id, channel, guest_key, appid, openid, unionid, created_at, updated_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (guest_identity_id, user_id, normalized_channel, normalized_guest_key, normalized_appid, normalized_openid, normalized_unionid, now_text, now_text, now_text),
            )
        else:
            if str(matched_identity["status"]) != "guest":
                raise ValueError("guest_identity_bound_to_registered_user")
            user_id = str(matched_identity["user_id"])
            final_guest_key = _normalize_optional_text(matched_identity.get("guest_key")) or normalized_guest_key
            final_appid = normalized_appid or _normalize_optional_text(matched_identity.get("guest_appid"))
            final_openid = normalized_openid or _normalize_optional_text(matched_identity.get("guest_openid"))
            final_unionid = normalized_unionid or _normalize_optional_text(matched_identity.get("guest_unionid"))
            connection.execute("UPDATE users SET updated_at = ?, last_active_at = ? WHERE id = ?", (now_text, now_text, user_id))
            connection.execute(
                "UPDATE guest_identities SET channel = ?, guest_key = ?, appid = ?, openid = ?, unionid = ?, updated_at = ?, last_seen_at = ? WHERE id = ?",
                (normalized_channel, final_guest_key, final_appid, final_openid, final_unionid, now_text, now_text, str(matched_identity["guest_identity_id"])),
            )
            connection.execute(
                "INSERT OR IGNORE INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, 0, 0, 0, ?, ?)",
                (user_id, now_text, now_text),
            )
            normalized_guest_key = final_guest_key

        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    if row is None:
        raise RuntimeError("guest_user_upsert_failed")
    return {"user": _deserialize_user_row(row), "channel": normalized_channel, "guest_key": normalized_guest_key}



def merge_guest_user_into_user(*, guest_user_id: str, target_user_id: str, now_text: str) -> dict[str, Any]:
    if guest_user_id == target_user_id:
        return {"guest_user_id": guest_user_id, "target_user_id": target_user_id, "transferred_points": 0}

    with open_connection() as connection:
        guest_user = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (guest_user_id,)).fetchone()
        target_user = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (target_user_id,)).fetchone()
        if guest_user is None or target_user is None:
            raise RuntimeError("guest_merge_user_not_found")
        if str(guest_user["status"]) != "guest":
            raise ValueError("guest_user_required")

        already_merged = connection.execute("SELECT id FROM guest_user_merges WHERE guest_user_id = ?", (guest_user_id,)).fetchone()
        if already_merged is not None:
            return {"guest_user_id": guest_user_id, "target_user_id": target_user_id, "transferred_points": 0}

        account_row = connection.execute("SELECT balance FROM points_accounts WHERE user_id = ?", (guest_user_id,)).fetchone()
        transferred_points = int(account_row["balance"]) if account_row is not None else 0
        if transferred_points > 0:
            _spend_points_in_connection(
                connection,
                user_id=guest_user_id,
                points_cost=transferred_points,
                biz_type="guest_merge_transfer_out",
                biz_id=target_user_id,
                idempotency_key=f"guest-merge:out:{guest_user_id}:{target_user_id}",
                remark="guest_points_merged_out",
                now_text=now_text,
            )
            _credit_points_in_connection(
                connection,
                user_id=target_user_id,
                points_amount=transferred_points,
                change_type="merge_transfer",
                biz_type="guest_merge_transfer_in",
                biz_id=guest_user_id,
                idempotency_key=f"guest-merge:in:{guest_user_id}:{target_user_id}",
                remark="guest_points_merged_in",
                now_text=now_text,
            )

        connection.execute("UPDATE reviews SET user_id = ? WHERE user_id = ?", (target_user_id, guest_user_id))
        connection.execute("UPDATE usage_records SET user_id = ? WHERE user_id = ?", (target_user_id, guest_user_id))
        connection.execute("UPDATE review_aspect_unlocks SET user_id = ? WHERE user_id = ?", (target_user_id, guest_user_id))
        connection.execute("UPDATE user_sessions SET status = ? WHERE user_id = ? AND status = ?", ("merged", guest_user_id, "active"))
        connection.execute("DELETE FROM guest_identities WHERE user_id = ?", (guest_user_id,))
        connection.execute(
            "INSERT INTO guest_user_merges (id, guest_user_id, target_user_id, transferred_points, merged_at) VALUES (?, ?, ?, ?, ?)",
            (uuid4().hex, guest_user_id, target_user_id, transferred_points, now_text),
        )
        connection.execute("UPDATE users SET status = ?, updated_at = ?, last_active_at = ? WHERE id = ?", ("merged", now_text, now_text, guest_user_id))
        connection.execute("UPDATE users SET updated_at = ?, last_active_at = ? WHERE id = ?", (now_text, now_text, target_user_id))

    return {"guest_user_id": guest_user_id, "target_user_id": target_user_id, "transferred_points": transferred_points}



def create_session(*, user_id: str, token_hash: str, device_type: str | None, client_version: str | None, ip: str | None, expires_at: str, now_text: str) -> dict[str, Any]:
    session_id = uuid4().hex
    with open_connection() as connection:
        connection.execute(
            "INSERT INTO user_sessions (id, user_id, token_hash, device_type, client_version, ip, status, expires_at, last_seen_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, user_id, token_hash, device_type, client_version, ip, "active", expires_at, now_text, now_text),
        )
    return {"session_id": session_id, "expires_at": expires_at}



def get_session_user_by_token_hash(token_hash: str, *, now_text: str, ip: str | None) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(_SESSION_USER_SELECT_SQL, (token_hash,)).fetchone()
        if row is None:
            return None
        if str(row["status"]) != "active" or str(row["expires_at"]) <= now_text:
            connection.execute("UPDATE user_sessions SET status = ? WHERE id = ?", ("expired", str(row["session_id"])))
            return None
        connection.execute("UPDATE user_sessions SET last_seen_at = ?, ip = COALESCE(?, ip) WHERE id = ?", (now_text, ip, str(row["session_id"])))
        connection.execute("UPDATE users SET last_active_at = ?, updated_at = ? WHERE id = ?", (now_text, now_text, str(row["user_id"])))
        refreshed = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (str(row["user_id"]),)).fetchone()
    return _deserialize_user_row(refreshed) if refreshed is not None else None



def get_user(user_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    return _deserialize_user_row(row) if row is not None else None



def get_internal_user(user_id: str) -> dict[str, Any] | None:
    sql = (
        "SELECT u.id AS user_id, u.status, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance, "
        "MAX(w.openid) AS openid, MAX(w.unionid) AS unionid, "
        "MAX(g.channel) AS guest_channel, MAX(g.guest_key) AS guest_key, MAX(g.appid) AS guest_appid, MAX(g.openid) AS guest_openid, MAX(g.unionid) AS guest_unionid "
        "FROM users u "
        "LEFT JOIN user_profiles p ON p.user_id = u.id "
        "LEFT JOIN points_accounts pa ON pa.user_id = u.id "
        "LEFT JOIN user_wechat_identities w ON w.user_id = u.id "
        "LEFT JOIN guest_identities g ON g.user_id = u.id "
        "WHERE u.id = ? "
        "GROUP BY u.id, u.status, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance"
    )
    with open_connection() as connection:
        row = connection.execute(sql, (user_id,)).fetchone()
    return _deserialize_internal_user_row(row) if row is not None else None



def update_user_profile(*, user_id: str, nickname: str | None, avatar_url: str | None, now_text: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        existing = connection.execute("SELECT nickname, avatar_url FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()
        if existing is None:
            return None
        final_nickname = _normalize_optional_text(nickname) or _normalize_optional_text(existing["nickname"])
        final_avatar_url = _normalize_optional_text(avatar_url) or _normalize_optional_text(existing["avatar_url"])
        connection.execute(
            "UPDATE user_profiles SET nickname = ?, avatar_url = ?, profile_completed = ?, updated_at = ? WHERE user_id = ?",
            (final_nickname, final_avatar_url, _profile_completed(final_nickname, final_avatar_url), now_text, user_id),
        )
        connection.execute("UPDATE users SET updated_at = ?, last_active_at = ? WHERE id = ?", (now_text, now_text, user_id))
        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    return _deserialize_user_row(row) if row is not None else None



def get_points_account(user_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT user_id, balance, frozen_balance, version, created_at, updated_at FROM points_accounts WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        return None
    return {"user_id": row["user_id"], "balance": row["balance"], "frozen_balance": row["frozen_balance"], "version": row["version"], "created_at": row["created_at"], "updated_at": row["updated_at"]}



def list_points_ledger(user_id: str, limit: int = 20) -> list[dict[str, Any]]:
    with open_connection() as connection:
        rows = connection.execute(
            "SELECT id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at FROM points_ledgers WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [_deserialize_points_ledger_row(row) for row in rows]


def list_users(*, limit: int = 20, query: str | None = None) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_query = _normalize_optional_text(query)
    sql = (
        "SELECT u.id AS user_id, u.status, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance, "
        "MAX(w.openid) AS openid, MAX(w.unionid) AS unionid, "
        "MAX(g.channel) AS guest_channel, MAX(g.guest_key) AS guest_key, MAX(g.appid) AS guest_appid, MAX(g.openid) AS guest_openid, MAX(g.unionid) AS guest_unionid "
        "FROM users u "
        "LEFT JOIN user_profiles p ON p.user_id = u.id "
        "LEFT JOIN points_accounts pa ON pa.user_id = u.id "
        "LEFT JOIN user_wechat_identities w ON w.user_id = u.id "
        "LEFT JOIN guest_identities g ON g.user_id = u.id"
    )
    parameters: list[Any] = []
    if normalized_query:
        sql += " WHERE u.id LIKE ? OR IFNULL(p.nickname, '') LIKE ? OR IFNULL(w.openid, '') LIKE ? OR IFNULL(w.unionid, '') LIKE ? OR IFNULL(g.guest_key, '') LIKE ? OR IFNULL(g.openid, '') LIKE ?"
        like_value = f"%{normalized_query}%"
        parameters.extend([like_value, like_value, like_value, like_value, like_value, like_value])
    sql += " GROUP BY u.id, u.status, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance ORDER BY u.last_active_at DESC LIMIT ?"
    parameters.append(normalized_limit)
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_internal_user_row(row) for row in rows]



def spend_points(*, user_id: str, points_cost: int, biz_type: str, biz_id: str | None, idempotency_key: str | None, remark: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_points_cost = max(0, int(points_cost))
    if normalized_points_cost == 0:
        return None
    with open_connection() as connection:
        return _spend_points_in_connection(connection, user_id=user_id, points_cost=normalized_points_cost, biz_type=biz_type, biz_id=biz_id, idempotency_key=idempotency_key, remark=remark, now_text=now_text)


def adjust_points(*, user_id: str, delta: int, biz_type: str, biz_id: str | None, idempotency_key: str | None, remark: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_delta = int(delta)
    if normalized_delta == 0:
        return None
    with open_connection() as connection:
        if normalized_delta > 0:
            return _credit_points_in_connection(connection, user_id=user_id, points_amount=normalized_delta, change_type="manual_adjust", biz_type=biz_type, biz_id=biz_id, idempotency_key=idempotency_key, remark=remark, now_text=now_text)
        return _spend_points_in_connection(connection, user_id=user_id, points_cost=abs(normalized_delta), biz_type=biz_type, biz_id=biz_id, idempotency_key=idempotency_key, remark=remark, now_text=now_text)



def refund_points(*, user_id: str, points_amount: int, biz_type: str, biz_id: str | None, idempotency_key: str | None, remark: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_points_amount = max(0, int(points_amount))
    if normalized_points_amount == 0:
        return None
    with open_connection() as connection:
        return _credit_points_in_connection(connection, user_id=user_id, points_amount=normalized_points_amount, change_type="refund", biz_type=biz_type, biz_id=biz_id, idempotency_key=idempotency_key, remark=remark, now_text=now_text)



def get_usage_record(usage_record_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, user_id, scene, target_id, points_cost, status, request_payload_summary, result_summary, created_at, updated_at FROM usage_records WHERE id = ?",
            (usage_record_id,),
        ).fetchone()
    return _deserialize_usage_record_row(row) if row is not None else None


def list_usage_records(*, limit: int = 20, user_id: str | None = None, scene: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(user_id):
        conditions.append("user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(scene):
        conditions.append("scene = ?")
        parameters.append(str(scene))
    if _normalize_optional_text(status):
        conditions.append("status = ?")
        parameters.append(str(status))
    sql = "SELECT id, user_id, scene, target_id, points_cost, status, request_payload_summary, result_summary, created_at, updated_at FROM usage_records"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
    parameters.append(normalized_limit)
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_usage_record_row(row) for row in rows]


def create_recharge_order(*, order_id: str, user_id: str, channel: str | None, package_key: str, package_title: str, amount_cents: int, points_amount: int, bonus_points: int, source: str, external_order_id: str | None, idempotency_key: str | None, proof_url: str | None, remark: str | None, created_at: str) -> dict[str, Any]:
    normalized_source = _normalize_optional_text(source) or "customer_service_h5"
    normalized_external_order_id = _normalize_optional_text(external_order_id)
    normalized_idempotency_key = _normalize_optional_text(idempotency_key)
    normalized_proof_url = _normalize_optional_text(proof_url)
    normalized_remark = _normalize_optional_text(remark)
    normalized_channel = _normalize_optional_text(channel)
    normalized_amount_cents = max(0, int(amount_cents))
    normalized_points_amount = max(0, int(points_amount))
    normalized_bonus_points = max(0, int(bonus_points))

    with open_connection() as connection:
        if normalized_idempotency_key:
            existing = _get_recharge_order_by_user_idempotency_key_in_connection(connection, user_id=user_id, idempotency_key=normalized_idempotency_key)
            if existing is not None:
                return existing
        if normalized_external_order_id:
            existing = _get_recharge_order_by_source_external_order_id_in_connection(connection, source=normalized_source, external_order_id=normalized_external_order_id)
            if existing is not None:
                if str(existing.get("user_id") or "") != user_id:
                    raise ValueError("recharge_order_external_order_conflict")
                return existing
        try:
            connection.execute(
                "INSERT INTO recharge_orders (id, user_id, channel, status, package_key, package_title, amount_cents, points_amount, bonus_points, source, external_order_id, idempotency_key, proof_url, remark, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order_id, user_id, normalized_channel, "pending", package_key, package_title, normalized_amount_cents, normalized_points_amount, normalized_bonus_points, normalized_source, normalized_external_order_id, normalized_idempotency_key, normalized_proof_url, normalized_remark, created_at, created_at),
            )
        except sqlite3.IntegrityError:
            if normalized_idempotency_key:
                existing = _get_recharge_order_by_user_idempotency_key_in_connection(connection, user_id=user_id, idempotency_key=normalized_idempotency_key)
                if existing is not None:
                    return existing
            if normalized_external_order_id:
                existing = _get_recharge_order_by_source_external_order_id_in_connection(connection, source=normalized_source, external_order_id=normalized_external_order_id)
                if existing is not None:
                    if str(existing.get("user_id") or "") != user_id:
                        raise ValueError("recharge_order_external_order_conflict")
                    return existing
            raise
        created_order = _get_recharge_order_in_connection(connection, order_id=order_id)
    if created_order is None:
        raise RuntimeError("recharge_order_create_failed")
    return created_order


def get_recharge_order(order_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        return _get_recharge_order_in_connection(connection, order_id=order_id)


def list_recharge_orders(*, limit: int = 20, user_id: str | None = None, status: str | None = None, source: str | None = None, channel: str | None = None) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(user_id):
        conditions.append("r.user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(status):
        conditions.append("r.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(source):
        conditions.append("r.source = ?")
        parameters.append(str(source))
    if _normalize_optional_text(channel):
        conditions.append("r.channel = ?")
        parameters.append(str(channel))

    sql = (
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.granted_ledger_id, r.created_at, r.updated_at "
        "FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.created_at DESC, r.id DESC LIMIT ?"
    parameters.append(normalized_limit)
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_recharge_order_row(row) for row in rows]


def review_recharge_order(*, order_id: str, action: str, review_note: str | None, reviewed_by: str | None, now_text: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    normalized_action = action.strip().lower()
    if normalized_action not in {"approve", "reject"}:
        raise ValueError("invalid_recharge_review_action")
    normalized_review_note = _normalize_optional_text(review_note)
    normalized_reviewed_by = _normalize_optional_text(reviewed_by)

    with open_connection() as connection:
        order = _get_recharge_order_in_connection(connection, order_id=order_id)
        if order is None:
            raise RuntimeError("recharge_order_not_found")

        current_status = str(order["status"])
        if current_status == "approved":
            if normalized_action != "approve":
                raise ValueError("recharge_order_already_reviewed")
            return order, _get_points_ledger_by_idempotency_key(connection, user_id=str(order["user_id"]), idempotency_key=f"recharge:approve:{order_id}")
        if current_status == "rejected":
            if normalized_action != "reject":
                raise ValueError("recharge_order_already_reviewed")
            return order, None
        if current_status != "pending":
            raise ValueError("recharge_order_already_reviewed")

        ledger: dict[str, Any] | None = None
        if normalized_action == "approve":
            ledger = _credit_points_in_connection(
                connection,
                user_id=str(order["user_id"]),
                points_amount=int(order["points_amount"]) + int(order["bonus_points"]),
                change_type="recharge",
                biz_type="recharge_order",
                biz_id=order_id,
                idempotency_key=f"recharge:approve:{order_id}",
                remark=f"recharge_order:{order['package_key']}",
                now_text=now_text,
            )
            connection.execute(
                "UPDATE recharge_orders SET status = ?, review_note = ?, reviewed_by = ?, reviewed_at = ?, granted_ledger_id = ?, updated_at = ? WHERE id = ?",
                ("approved", normalized_review_note, normalized_reviewed_by, now_text, ledger["ledger_id"], now_text, order_id),
            )
        else:
            connection.execute(
                "UPDATE recharge_orders SET status = ?, review_note = ?, reviewed_by = ?, reviewed_at = ?, updated_at = ? WHERE id = ?",
                ("rejected", normalized_review_note, normalized_reviewed_by, now_text, now_text, order_id),
            )

        refreshed_order = _get_recharge_order_in_connection(connection, order_id=order_id)
    if refreshed_order is None:
        raise RuntimeError("recharge_order_review_failed")
    return refreshed_order, ledger


def create_review_aspect_unlock(*, review_id: str, user_id: str, aspect_key: str, points_cost: int, usage_scene: str, request_payload_summary: dict[str, Any] | None, now_text: str) -> dict[str, Any]:
    normalized_points_cost = max(0, int(points_cost))
    usage_record_id = uuid4().hex
    with open_connection() as connection:
        existing = _get_review_aspect_unlock_in_connection(connection, review_id=review_id, user_id=user_id, aspect_key=aspect_key)
        if existing is not None:
            return existing
        if normalized_points_cost > 0:
            _spend_points_in_connection(
                connection,
                user_id=user_id,
                points_cost=normalized_points_cost,
                biz_type=usage_scene,
                biz_id=review_id,
                idempotency_key=f"review:aspect_unlock:{review_id}:{aspect_key}",
                remark=f"phone_review_aspect_unlock:{aspect_key}",
                now_text=now_text,
            )
        connection.execute(
            "INSERT INTO review_aspect_unlocks (id, review_id, user_id, aspect_key, points_cost, usage_record_id, unlocked_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (uuid4().hex, review_id, user_id, aspect_key, normalized_points_cost, usage_record_id, now_text),
        )
        _create_usage_record_in_connection(
            connection,
            usage_record_id=usage_record_id,
            user_id=user_id,
            scene=usage_scene,
            target_id=review_id,
            points_cost=normalized_points_cost,
            status="completed",
            request_payload_summary=request_payload_summary,
            result_summary={"status": "completed", "aspect_key": aspect_key},
            created_at=now_text,
            updated_at=now_text,
        )
        row = connection.execute(
            "SELECT id, review_id, user_id, aspect_key, points_cost, usage_record_id, unlocked_at FROM review_aspect_unlocks WHERE review_id = ? AND user_id = ? AND aspect_key = ?",
            (review_id, user_id, aspect_key),
        ).fetchone()
    if row is None:
        raise RuntimeError("review_aspect_unlock_create_failed")
    return _deserialize_review_aspect_unlock_row(row)


def list_review_aspect_unlocks(*, review_id: str, user_id: str) -> list[dict[str, Any]]:
    with open_connection() as connection:
        rows = connection.execute(
            "SELECT id, review_id, user_id, aspect_key, points_cost, usage_record_id, unlocked_at FROM review_aspect_unlocks WHERE review_id = ? AND user_id = ? ORDER BY unlocked_at DESC, id DESC",
            (review_id, user_id),
        ).fetchall()
    return [_deserialize_review_aspect_unlock_row(row) for row in rows]


def get_runtime_config_entry(*, scope_type: str, scope_key: str, config_key: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, scope_type, scope_key, config_key, value_json, updated_at FROM runtime_config_entries WHERE scope_type = ? AND scope_key = ? AND config_key = ?",
            (scope_type, scope_key, config_key),
        ).fetchone()
    return _deserialize_runtime_config_entry_row(row) if row is not None else None


def list_runtime_config_entries(*, scope_type: str | None = None, scope_key: str | None = None) -> list[dict[str, Any]]:
    query = "SELECT id, scope_type, scope_key, config_key, value_json, updated_at FROM runtime_config_entries"
    conditions: list[str] = []
    parameters: list[Any] = []
    if scope_type:
        conditions.append("scope_type = ?")
        parameters.append(scope_type)
    if scope_key:
        conditions.append("scope_key = ?")
        parameters.append(scope_key)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY scope_type ASC, scope_key ASC, config_key ASC"
    with open_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [_deserialize_runtime_config_entry_row(row) for row in rows]


def upsert_runtime_config_entry(*, scope_type: str, scope_key: str, config_key: str, value: Any, updated_at: str) -> dict[str, Any]:
    with open_connection() as connection:
        connection.execute(
            """
            INSERT INTO runtime_config_entries (id, scope_type, scope_key, config_key, value_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(scope_type, scope_key, config_key)
            DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at
            """,
            (uuid4().hex, scope_type, scope_key, config_key, _serialize_json_value(value), updated_at),
        )
        row = connection.execute(
            "SELECT id, scope_type, scope_key, config_key, value_json, updated_at FROM runtime_config_entries WHERE scope_type = ? AND scope_key = ? AND config_key = ?",
            (scope_type, scope_key, config_key),
        ).fetchone()
    if row is None:
        raise RuntimeError("runtime_config_upsert_failed")
    return _deserialize_runtime_config_entry_row(row)



def complete_usage_record(*, usage_record_id: str, result_summary: dict[str, Any] | None, updated_at: str) -> None:
    with open_connection() as connection:
        connection.execute(
            "UPDATE usage_records SET status = ?, result_summary = ?, updated_at = ? WHERE id = ?",
            ("completed", _serialize_json_value(result_summary), updated_at, usage_record_id),
        )



def fail_usage_record(*, usage_record_id: str, result_summary: dict[str, Any] | None, updated_at: str) -> None:
    with open_connection() as connection:
        connection.execute(
            "UPDATE usage_records SET status = ?, result_summary = ?, updated_at = ? WHERE id = ?",
            ("failed", _serialize_json_value(result_summary), updated_at, usage_record_id),
        )



def _spend_points_in_connection(connection: sqlite3.Connection, *, user_id: str, points_cost: int, biz_type: str, biz_id: str | None, idempotency_key: str | None, remark: str | None, now_text: str) -> dict[str, Any]:
    existing = _get_points_ledger_by_idempotency_key(connection, user_id=user_id, idempotency_key=idempotency_key)
    if existing is not None:
        return existing

    _ensure_points_account_row(connection, user_id=user_id, now_text=now_text)
    account_row = connection.execute("SELECT balance FROM points_accounts WHERE user_id = ?", (user_id,)).fetchone()
    if account_row is None or int(account_row["balance"]) < points_cost:
        raise InsufficientPointsError("insufficient_points")

    balance_after = int(account_row["balance"]) - points_cost
    connection.execute("UPDATE points_accounts SET balance = ?, version = version + 1, updated_at = ? WHERE user_id = ?", (balance_after, now_text, user_id))
    ledger_id = uuid4().hex
    try:
        connection.execute(
            "INSERT INTO points_ledgers (id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ledger_id, user_id, "consume", -points_cost, balance_after, biz_type, biz_id, idempotency_key, remark, now_text),
        )
    except sqlite3.IntegrityError:
        existing = _get_points_ledger_by_idempotency_key(connection, user_id=user_id, idempotency_key=idempotency_key)
        if existing is not None:
            return existing
        raise

    return {"ledger_id": ledger_id, "user_id": user_id, "change_type": "consume", "delta": -points_cost, "balance_after": balance_after, "biz_type": biz_type, "biz_id": biz_id, "idempotency_key": idempotency_key, "remark": remark, "created_at": now_text}



def _credit_points_in_connection(connection: sqlite3.Connection, *, user_id: str, points_amount: int, change_type: str, biz_type: str, biz_id: str | None, idempotency_key: str | None, remark: str | None, now_text: str) -> dict[str, Any]:
    existing = _get_points_ledger_by_idempotency_key(connection, user_id=user_id, idempotency_key=idempotency_key)
    if existing is not None:
        return existing

    _ensure_points_account_row(connection, user_id=user_id, now_text=now_text)
    account_row = connection.execute("SELECT balance FROM points_accounts WHERE user_id = ?", (user_id,)).fetchone()
    current_balance = int(account_row["balance"]) if account_row is not None else 0
    balance_after = current_balance + points_amount
    connection.execute("UPDATE points_accounts SET balance = ?, version = version + 1, updated_at = ? WHERE user_id = ?", (balance_after, now_text, user_id))
    ledger_id = uuid4().hex
    try:
        connection.execute(
            "INSERT INTO points_ledgers (id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ledger_id, user_id, change_type, points_amount, balance_after, biz_type, biz_id, idempotency_key, remark, now_text),
        )
    except sqlite3.IntegrityError:
        existing = _get_points_ledger_by_idempotency_key(connection, user_id=user_id, idempotency_key=idempotency_key)
        if existing is not None:
            return existing
        raise

    return {"ledger_id": ledger_id, "user_id": user_id, "change_type": change_type, "delta": points_amount, "balance_after": balance_after, "biz_type": biz_type, "biz_id": biz_id, "idempotency_key": idempotency_key, "remark": remark, "created_at": now_text}



def _create_usage_record_in_connection(connection: sqlite3.Connection, *, usage_record_id: str, user_id: str, scene: str, target_id: str | None, points_cost: int, status: str, request_payload_summary: dict[str, Any] | None, result_summary: dict[str, Any] | None, created_at: str, updated_at: str) -> None:
    connection.execute(
        "INSERT INTO usage_records (id, user_id, scene, target_id, points_cost, status, request_payload_summary, result_summary, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (usage_record_id, user_id, scene, target_id, points_cost, status, _serialize_json_value(request_payload_summary), _serialize_json_value(result_summary), created_at, updated_at),
    )



def _ensure_points_account_row(connection: sqlite3.Connection, *, user_id: str, now_text: str) -> None:
    connection.execute("INSERT OR IGNORE INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, 0, 0, 0, ?, ?)", (user_id, now_text, now_text))



def _get_points_ledger_by_idempotency_key(connection: sqlite3.Connection, *, user_id: str, idempotency_key: str | None) -> dict[str, Any] | None:
    if not idempotency_key:
        return None
    row = connection.execute(
        "SELECT id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at FROM points_ledgers WHERE user_id = ? AND idempotency_key = ?",
        (user_id, idempotency_key),
    ).fetchone()
    return _deserialize_points_ledger_row(row) if row is not None else None



def _deserialize_points_ledger_row(row: sqlite3.Row) -> dict[str, Any]:
    return {"ledger_id": row["id"], "user_id": row["user_id"], "change_type": row["change_type"], "delta": row["delta"], "balance_after": row["balance_after"], "biz_type": row["biz_type"], "biz_id": row["biz_id"], "idempotency_key": row["idempotency_key"], "remark": row["remark"], "created_at": row["created_at"]}



def _deserialize_usage_record_row(row: sqlite3.Row) -> dict[str, Any]:
    return {"usage_record_id": row["id"], "user_id": row["user_id"], "scene": row["scene"], "target_id": row["target_id"], "points_cost": row["points_cost"], "status": row["status"], "request_payload_summary": json.loads(row["request_payload_summary"]) if row["request_payload_summary"] else None, "result_summary": json.loads(row["result_summary"]) if row["result_summary"] else None, "created_at": row["created_at"], "updated_at": row["updated_at"]}



def _serialize_json_value(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _deserialize_runtime_config_entry_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "entry_id": row["id"],
        "scope_type": row["scope_type"],
        "scope_key": row["scope_key"],
        "config_key": row["config_key"],
        "value": json.loads(row["value_json"]),
        "updated_at": row["updated_at"],
    }


def _deserialize_review_aspect_unlock_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "unlock_id": row["id"],
        "review_id": row["review_id"],
        "user_id": row["user_id"],
        "aspect_key": row["aspect_key"],
        "points_cost": row["points_cost"],
        "usage_record_id": row["usage_record_id"],
        "unlocked_at": row["unlocked_at"],
    }



def _deserialize_review_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "phone": row["phone"],
        "gender": row["gender"],
        "status": row["status"],
        "progress_stage": row["progress_stage"],
        "progress_message": row["progress_message"],
        "score_result": json.loads(row["score_result_json"]) if row["score_result_json"] else None,
        "score_template": json.loads(row["score_template_json"]) if row["score_template_json"] else None,
        "score_markdown": row["score_markdown"],
        "error_message": row["error_message"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }



def _deserialize_review_summary_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "phone": row["phone"],
        "gender": row["gender"],
        "status": row["status"],
        "progress_stage": row["progress_stage"],
        "progress_message": row["progress_message"],
        "error_message": row["error_message"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }



def _deserialize_user_row(row: sqlite3.Row) -> dict[str, Any]:
    return {"user_id": row["user_id"], "status": row["status"], "nickname": row["nickname"], "avatar_url": row["avatar_url"], "profile_completed": bool(row["profile_completed"]), "points_balance": int(row["balance"] or 0), "frozen_balance": int(row["frozen_balance"] or 0), "created_at": row["created_at"], "updated_at": row["updated_at"], "last_active_at": row["last_active_at"]}


def _deserialize_internal_user_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "user_id": row["user_id"],
        "status": row["status"],
        "nickname": row["nickname"],
        "avatar_url": row["avatar_url"],
        "profile_completed": bool(row["profile_completed"]),
        "points_balance": int(row["balance"] or 0),
        "frozen_balance": int(row["frozen_balance"] or 0),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_active_at": row["last_active_at"],
        "openid": row["openid"],
        "unionid": row["unionid"],
        "guest_channel": row["guest_channel"],
        "guest_key": row["guest_key"],
        "guest_appid": row["guest_appid"],
        "guest_openid": row["guest_openid"],
        "guest_unionid": row["guest_unionid"],
    }



def _deserialize_recharge_order_row(row: sqlite3.Row) -> dict[str, Any]:
    points_amount = int(row["points_amount"] or 0)
    bonus_points = int(row["bonus_points"] or 0)
    return {
        "order_id": row["id"],
        "user_id": row["user_id"],
        "user_status": row["user_status"] if "user_status" in row.keys() else None,
        "user_nickname": row["user_nickname"] if "user_nickname" in row.keys() else None,
        "channel": row["channel"],
        "status": row["status"],
        "package_key": row["package_key"],
        "package_title": row["package_title"],
        "amount_cents": int(row["amount_cents"] or 0),
        "points_amount": points_amount,
        "bonus_points": bonus_points,
        "total_points": points_amount + bonus_points,
        "source": row["source"],
        "external_order_id": row["external_order_id"],
        "proof_url": row["proof_url"],
        "remark": row["remark"],
        "review_note": row["review_note"],
        "reviewed_by": row["reviewed_by"],
        "reviewed_at": row["reviewed_at"],
        "granted_ledger_id": row["granted_ledger_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _get_recharge_order_in_connection(connection: sqlite3.Connection, *, order_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.granted_ledger_id, r.created_at, r.updated_at FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id WHERE r.id = ?",
        (order_id,),
    ).fetchone()
    return _deserialize_recharge_order_row(row) if row is not None else None


def _get_recharge_order_by_user_idempotency_key_in_connection(connection: sqlite3.Connection, *, user_id: str, idempotency_key: str | None) -> dict[str, Any] | None:
    normalized_idempotency_key = _normalize_optional_text(idempotency_key)
    if not normalized_idempotency_key:
        return None
    row = connection.execute(
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.granted_ledger_id, r.created_at, r.updated_at FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id WHERE r.user_id = ? AND r.idempotency_key = ?",
        (user_id, normalized_idempotency_key),
    ).fetchone()
    return _deserialize_recharge_order_row(row) if row is not None else None


def _get_recharge_order_by_source_external_order_id_in_connection(connection: sqlite3.Connection, *, source: str, external_order_id: str | None) -> dict[str, Any] | None:
    normalized_source = _normalize_optional_text(source)
    normalized_external_order_id = _normalize_optional_text(external_order_id)
    if not normalized_source or not normalized_external_order_id:
        return None
    row = connection.execute(
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.granted_ledger_id, r.created_at, r.updated_at FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id WHERE r.source = ? AND r.external_order_id = ?",
        (normalized_source, normalized_external_order_id),
    ).fetchone()
    return _deserialize_recharge_order_row(row) if row is not None else None


def _profile_completed(nickname: str | None, avatar_url: str | None) -> int:
    return int(bool(_normalize_optional_text(nickname)) and bool(_normalize_optional_text(avatar_url)))



def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _create_points_account_with_initial_grant_in_connection(connection: sqlite3.Connection, *, user_id: str, initial_points: int, grant_biz_type: str, grant_idempotency_key: str, remark: str, now_text: str) -> None:
    normalized_initial_points = max(0, int(initial_points))
    connection.execute(
        "INSERT INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, ?, 0, 0, ?, ?)",
        (user_id, normalized_initial_points, now_text, now_text),
    )
    if normalized_initial_points > 0:
        connection.execute(
            "INSERT INTO points_ledgers (id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (uuid4().hex, user_id, "gift", normalized_initial_points, normalized_initial_points, grant_biz_type, user_id, grant_idempotency_key, remark, now_text),
        )


def _get_review_aspect_unlock_in_connection(connection: sqlite3.Connection, *, review_id: str, user_id: str, aspect_key: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT id, review_id, user_id, aspect_key, points_cost, usage_record_id, unlocked_at FROM review_aspect_unlocks WHERE review_id = ? AND user_id = ? AND aspect_key = ?",
        (review_id, user_id, aspect_key),
    ).fetchone()
    return _deserialize_review_aspect_unlock_row(row) if row is not None else None


def _get_guest_identity_by_guest_key_in_connection(connection: sqlite3.Connection, *, channel: str, guest_key: str | None) -> dict[str, Any] | None:
    normalized_channel = _normalize_optional_text(channel)
    normalized_guest_key = _normalize_optional_text(guest_key)
    if not normalized_channel or not normalized_guest_key:
        return None
    row = connection.execute(
        """
        SELECT g.id AS guest_identity_id, g.user_id, g.channel, g.guest_key, g.appid AS guest_appid, g.openid AS guest_openid, g.unionid AS guest_unionid, u.status
        FROM guest_identities g
        JOIN users u ON u.id = g.user_id
        WHERE g.channel = ? AND g.guest_key = ?
        """,
        (normalized_channel, normalized_guest_key),
    ).fetchone()
    return _deserialize_guest_identity_row(row) if row is not None else None


def _get_guest_identity_by_openid_in_connection(connection: sqlite3.Connection, *, appid: str | None, openid: str | None) -> dict[str, Any] | None:
    normalized_appid = _normalize_optional_text(appid)
    normalized_openid = _normalize_optional_text(openid)
    if not normalized_appid or not normalized_openid:
        return None
    row = connection.execute(
        """
        SELECT g.id AS guest_identity_id, g.user_id, g.channel, g.guest_key, g.appid AS guest_appid, g.openid AS guest_openid, g.unionid AS guest_unionid, u.status
        FROM guest_identities g
        JOIN users u ON u.id = g.user_id
        WHERE g.appid = ? AND g.openid = ?
        """,
        (normalized_appid, normalized_openid),
    ).fetchone()
    return _deserialize_guest_identity_row(row) if row is not None else None


def _deserialize_guest_identity_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "guest_identity_id": row["guest_identity_id"],
        "user_id": row["user_id"],
        "status": row["status"],
        "channel": row["channel"],
        "guest_key": row["guest_key"],
        "guest_appid": row["guest_appid"],
        "guest_openid": row["guest_openid"],
        "guest_unionid": row["guest_unionid"],
    }


_USER_SELECT_SQL = """
SELECT u.id AS user_id, u.status, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance
FROM users u
LEFT JOIN user_profiles p ON p.user_id = u.id
LEFT JOIN points_accounts pa ON pa.user_id = u.id
"""

_SESSION_USER_SELECT_SQL = """
SELECT s.id AS session_id, s.user_id, s.status, s.expires_at
FROM user_sessions s
WHERE s.token_hash = ?
"""
