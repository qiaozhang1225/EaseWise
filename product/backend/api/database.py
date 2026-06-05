from __future__ import annotations

import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from .config import get_database_path


class InsufficientPointsError(RuntimeError):
    pass


CANONICAL_USER_IDENTITY_LEVELS = {"normal_user", "promoter", "vip_promoter", "svip_promoter"}
USER_IDENTITY_LEVEL_ALIASES = {
    "promotion_ambassador": "promoter",
    "vip_promotion_ambassador": "vip_promoter",
    "senior_promoter": "vip_promoter",
    "senior_promotion_ambassador": "vip_promoter",
    "svip_promotion_ambassador": "svip_promoter",
}

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
    uid TEXT UNIQUE,
    status TEXT NOT NULL,
    identity_level TEXT NOT NULL DEFAULT 'normal_user',
    primary_identity_type TEXT NOT NULL DEFAULT 'unknown',
    registered_channel TEXT,
    promoter_parent_user_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_active_at TEXT NOT NULL,
    FOREIGN KEY(promoter_parent_user_id) REFERENCES users(id)
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

CREATE_USER_PHONE_IDENTITIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_phone_identities (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT '86',
    phone_number TEXT NOT NULL,
    normalized_phone TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 1,
    verified_at TEXT,
    password_hash TEXT,
    password_updated_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_login_at TEXT,
    UNIQUE(country_code, normalized_phone),
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

CREATE_PROMOTION_REBATE_ACCOUNTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS promotion_rebate_accounts (
    user_id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    frozen_balance INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_PROMOTION_WALLET_ACCOUNTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS promotion_wallet_accounts (
    user_id TEXT PRIMARY KEY,
    withdrawable_balance_cents INTEGER NOT NULL DEFAULT 0,
    frozen_commission_cents INTEGER NOT NULL DEFAULT 0,
    withdrawn_amount_cents INTEGER NOT NULL DEFAULT 0,
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

CREATE_ADMIN_OPERATION_LOGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admin_operation_logs (
    id TEXT PRIMARY KEY,
    operator TEXT,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    reason TEXT,
    operator_note TEXT,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL
)
"""

CREATE_USAGE_RECORDS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS usage_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    scene TEXT NOT NULL,
    channel TEXT,
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

CREATE_LLM_API_KEYS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS llm_api_keys (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    display_name TEXT NOT NULL,
    masked_key TEXT NOT NULL,
    secret_ref TEXT NOT NULL,
    secret_value TEXT,
    enabled INTEGER NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 100,
    remark TEXT,
    last_operator TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
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
    paid_at TEXT,
    completed_at TEXT,
    closed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, idempotency_key),
    UNIQUE(source, external_order_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(granted_ledger_id) REFERENCES points_ledgers(id)
)
"""

CREATE_PAYMENT_TRANSACTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS payment_transactions (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    status TEXT NOT NULL,
    provider_transaction_id TEXT,
    prepay_id TEXT,
    idempotency_key TEXT,
    payment_params_json TEXT,
    notify_payload_json TEXT,
    failure_reason TEXT,
    paid_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(order_id, idempotency_key),
    FOREIGN KEY(order_id) REFERENCES recharge_orders(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_REFUND_REQUESTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS refund_requests (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    operator_note TEXT,
    reject_reason TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    failure_reason TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(order_id) REFERENCES recharge_orders(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_PROMOTION_APPLICATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS promotion_applications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    requested_level TEXT NOT NULL,
    status TEXT NOT NULL,
    applicant_name TEXT,
    applicant_phone TEXT,
    reject_reason TEXT,
    review_note TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_PROMOTION_RELATIONSHIPS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS promotion_relationships (
    user_id TEXT PRIMARY KEY,
    promoter_user_id TEXT NOT NULL,
    bind_source TEXT NOT NULL,
    updated_by TEXT,
    reason TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(promoter_user_id) REFERENCES users(id)
)
"""

CREATE_PROMOTION_COMMISSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS promotion_commissions (
    id TEXT PRIMARY KEY,
    promoter_user_id TEXT NOT NULL,
    invited_user_id TEXT,
    order_id TEXT,
    order_amount_cents INTEGER NOT NULL DEFAULT 0,
    commission_rate REAL NOT NULL DEFAULT 0,
    commission_points INTEGER NOT NULL DEFAULT 0,
    commission_type TEXT NOT NULL,
    status TEXT NOT NULL,
    remark TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    settled_at TEXT,
    revoked_at TEXT,
    FOREIGN KEY(promoter_user_id) REFERENCES users(id),
    FOREIGN KEY(invited_user_id) REFERENCES users(id),
    FOREIGN KEY(order_id) REFERENCES recharge_orders(id)
)
"""

CREATE_PROMOTION_WITHDRAWALS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS promotion_withdrawals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL,
    points_used INTEGER NOT NULL DEFAULT 0,
    amount_cents INTEGER NOT NULL DEFAULT 0,
    rebate_points_balance_snapshot INTEGER NOT NULL DEFAULT 0,
    cash_rate_snapshot REAL NOT NULL DEFAULT 1,
    reject_reason TEXT,
    review_note TEXT,
    payout_method TEXT,
    payout_proof TEXT,
    payout_failure_reason TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    paid_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
"""

CREATE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_reviews_user_created_at ON reviews(user_id, created_at DESC)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_uid ON users(uid)",
    "CREATE INDEX IF NOT EXISTS idx_users_identity_type_created_at ON users(primary_identity_type, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_phone_identity_user_id ON user_phone_identities(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_phone_identity_normalized_phone ON user_phone_identities(country_code, normalized_phone)",
    "CREATE INDEX IF NOT EXISTS idx_wechat_identity_user_id ON user_wechat_identities(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_wechat_identity_unionid ON user_wechat_identities(unionid)",
    "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)",
    "CREATE INDEX IF NOT EXISTS idx_points_ledgers_user_created_at ON points_ledgers(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_admin_logs_target_created_at ON admin_operation_logs(target_type, target_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_usage_records_user_created_at ON usage_records(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_usage_records_scene_created_at ON usage_records(scene, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_usage_records_channel_created_at ON usage_records(channel, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_runtime_config_scope_key ON runtime_config_entries(scope_type, scope_key, config_key)",
    "CREATE INDEX IF NOT EXISTS idx_review_aspect_unlocks_review_user ON review_aspect_unlocks(review_id, user_id, unlocked_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_recharge_orders_user_created_at ON recharge_orders(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_recharge_orders_status_created_at ON recharge_orders(status, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_recharge_orders_source_external_order_id ON recharge_orders(source, external_order_id)",
    "CREATE INDEX IF NOT EXISTS idx_payment_transactions_order_created_at ON payment_transactions(order_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_payment_transactions_provider_status ON payment_transactions(provider, status, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_llm_api_keys_enabled_priority ON llm_api_keys(enabled, priority, updated_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_refund_requests_order_created_at ON refund_requests(order_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_promotion_applications_status_created_at ON promotion_applications(status, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_promotion_commissions_promoter_created_at ON promotion_commissions(promoter_user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_promotion_withdrawals_status_created_at ON promotion_withdrawals(status, created_at DESC)",
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


def _ensure_users_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()}
    if "uid" not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN uid TEXT")
    if "identity_level" not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN identity_level TEXT NOT NULL DEFAULT 'normal_user'")
    if "primary_identity_type" not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN primary_identity_type TEXT NOT NULL DEFAULT 'unknown'")
    if "registered_channel" not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN registered_channel TEXT")
    if "promoter_parent_user_id" not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN promoter_parent_user_id TEXT")
    _backfill_missing_user_uids(connection)


def _generate_unique_user_uid(connection: sqlite3.Connection) -> str:
    for _ in range(100):
        uid = f"{secrets.randbelow(90_000_000) + 10_000_000:08d}"
        exists = connection.execute("SELECT 1 FROM users WHERE uid = ? LIMIT 1", (uid,)).fetchone()
        if exists is None:
            return uid
    raise RuntimeError("user_uid_generation_failed")


def _backfill_missing_user_uids(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        "SELECT id FROM users WHERE uid IS NULL OR TRIM(uid) = '' ORDER BY created_at, id"
    ).fetchall()
    for row in rows:
        connection.execute("UPDATE users SET uid = ? WHERE id = ?", (_generate_unique_user_uid(connection), str(row["id"])))


def _ensure_usage_records_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(usage_records)").fetchall()}
    if "channel" not in columns:
        connection.execute("ALTER TABLE usage_records ADD COLUMN channel TEXT")


def _ensure_recharge_orders_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(recharge_orders)").fetchall()}
    if "paid_at" not in columns:
        connection.execute("ALTER TABLE recharge_orders ADD COLUMN paid_at TEXT")
    if "completed_at" not in columns:
        connection.execute("ALTER TABLE recharge_orders ADD COLUMN completed_at TEXT")
    if "closed_at" not in columns:
        connection.execute("ALTER TABLE recharge_orders ADD COLUMN closed_at TEXT")


def _ensure_llm_api_keys_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(llm_api_keys)").fetchall()}
    if "secret_value" not in columns:
        connection.execute("ALTER TABLE llm_api_keys ADD COLUMN secret_value TEXT")
    connection.execute(
        """
        UPDATE llm_api_keys
        SET
            model = 'bailian_api_key',
            display_name = CASE
                WHEN display_name IN ('阿里云 TTS AppKey', '阿里云 NLS TTS AppKey') THEN '阿里云百炼 API Key'
                ELSE display_name
            END,
            secret_ref = 'admin:aliyun:bailian_api_key:' || id
        WHERE provider = 'aliyun'
          AND model = 'tts_app_key'
          AND secret_value LIKE 'sk-%'
        """
    )


def _ensure_promotion_wallet_accounts(connection: sqlite3.Connection) -> None:
    now_text = _utc_now_text()
    rows = connection.execute(
        "SELECT user_id, balance, frozen_balance, created_at, updated_at FROM promotion_rebate_accounts"
    ).fetchall()
    for row in rows:
        connection.execute(
            """
            INSERT OR IGNORE INTO promotion_wallet_accounts
                (user_id, withdrawable_balance_cents, frozen_commission_cents, withdrawn_amount_cents, version, created_at, updated_at)
            VALUES (?, ?, ?, 0, 0, ?, ?)
            """,
            (
                str(row["user_id"]),
                int(row["balance"] or 0),
                int(row["frozen_balance"] or 0),
                str(row["created_at"] or now_text),
                str(row["updated_at"] or now_text),
            ),
        )



def ensure_schema() -> None:
    with open_connection() as connection:
        connection.execute(CREATE_REVIEWS_TABLE_SQL)
        _ensure_reviews_columns(connection)
        connection.execute(CREATE_USERS_TABLE_SQL)
        _ensure_users_columns(connection)
        connection.execute(CREATE_USER_PROFILES_TABLE_SQL)
        connection.execute(CREATE_USER_PHONE_IDENTITIES_TABLE_SQL)
        connection.execute(CREATE_USER_WECHAT_IDENTITIES_TABLE_SQL)
        connection.execute(CREATE_USER_SESSIONS_TABLE_SQL)
        connection.execute(CREATE_POINTS_ACCOUNTS_TABLE_SQL)
        connection.execute(CREATE_PROMOTION_REBATE_ACCOUNTS_TABLE_SQL)
        connection.execute(CREATE_PROMOTION_WALLET_ACCOUNTS_TABLE_SQL)
        _ensure_promotion_wallet_accounts(connection)
        connection.execute(CREATE_POINTS_LEDGERS_TABLE_SQL)
        connection.execute(CREATE_ADMIN_OPERATION_LOGS_TABLE_SQL)
        connection.execute(CREATE_USAGE_RECORDS_TABLE_SQL)
        _ensure_usage_records_columns(connection)
        connection.execute(CREATE_LLM_API_KEYS_TABLE_SQL)
        _ensure_llm_api_keys_columns(connection)
        connection.execute(CREATE_RUNTIME_CONFIG_ENTRIES_TABLE_SQL)
        connection.execute(CREATE_REVIEW_ASPECT_UNLOCKS_TABLE_SQL)
        connection.execute(CREATE_RECHARGE_ORDERS_TABLE_SQL)
        _ensure_recharge_orders_columns(connection)
        connection.execute(CREATE_PAYMENT_TRANSACTIONS_TABLE_SQL)
        connection.execute(CREATE_REFUND_REQUESTS_TABLE_SQL)
        connection.execute(CREATE_PROMOTION_APPLICATIONS_TABLE_SQL)
        connection.execute(CREATE_PROMOTION_RELATIONSHIPS_TABLE_SQL)
        connection.execute(CREATE_PROMOTION_COMMISSIONS_TABLE_SQL)
        connection.execute(CREATE_PROMOTION_WITHDRAWALS_TABLE_SQL)
        for statement in CREATE_INDEX_SQL:
            connection.execute(statement)



def create_review(*, review_id: str, user_id: str | None, phone: str, gender: str, status: str, created_at: str, progress_stage: str | None = None, progress_message: str | None = None) -> None:
    with open_connection() as connection:
        connection.execute(
            "INSERT INTO reviews (id, user_id, phone, gender, status, progress_stage, progress_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (review_id, user_id, phone, gender, status, progress_stage, progress_message, created_at, created_at),
        )



def create_review_with_charge(*, review_id: str, user_id: str | None, phone: str, gender: str, status: str, created_at: str, progress_stage: str | None = None, progress_message: str | None = None, points_cost: int = 0, usage_scene: str | None = None, request_payload_summary: dict[str, Any] | None = None, channel: str | None = None) -> None:
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
                channel=channel,
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


def update_review_generation_payload(
    *,
    review_id: str,
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    score_markdown: str | None,
    progress_stage: str,
    progress_message: str | None,
    updated_at: str,
) -> None:
    with open_connection() as connection:
        connection.execute(
            """
            UPDATE reviews
            SET progress_stage = ?, progress_message = ?, score_result_json = ?, score_template_json = ?, score_markdown = ?, error_message = NULL, updated_at = ?
            WHERE id = ?
            """,
            (
                progress_stage,
                progress_message,
                json.dumps(score_result, ensure_ascii=False),
                json.dumps(score_template, ensure_ascii=False),
                score_markdown,
                updated_at,
                review_id,
            ),
        )


def complete_review_with_message(
    *,
    review_id: str,
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    score_markdown: str | None,
    progress_message: str,
    updated_at: str,
) -> None:
    with open_connection() as connection:
        connection.execute(
            """
            UPDATE reviews
            SET status = ?, progress_stage = ?, progress_message = ?, score_result_json = ?, score_template_json = ?, score_markdown = ?, error_message = NULL, updated_at = ?
            WHERE id = ?
            """,
            (
                "completed",
                "completed",
                progress_message,
                json.dumps(score_result, ensure_ascii=False),
                json.dumps(score_template, ensure_ascii=False),
                score_markdown,
                updated_at,
                review_id,
            ),
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


def update_review_score_template(*, review_id: str, score_template: dict[str, Any], updated_at: str) -> None:
    with open_connection() as connection:
        connection.execute(
            "UPDATE reviews SET score_template_json = ?, updated_at = ? WHERE id = ?",
            (json.dumps(score_template, ensure_ascii=False), updated_at, review_id),
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



def list_reviews(
    limit: int = 20,
    user_id: str | None = None,
    *,
    offset: int = 0,
    status: str | None = None,
    keyword: str | None = None,
    channel: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_offset = max(0, int(offset))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(user_id):
        conditions.append("r.user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(status):
        conditions.append("r.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(channel):
        conditions.append("ur.channel = ?")
        parameters.append(str(channel))
    if _normalize_optional_text(date_from):
        conditions.append("r.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("r.created_at <= ?")
        parameters.append(str(date_to))
    if _normalize_optional_text(keyword):
        like_value = f"%{str(keyword).strip()}%"
        conditions.append("(r.id LIKE ? OR r.phone LIKE ? OR IFNULL(r.user_id, '') LIKE ? OR IFNULL(p.nickname, '') LIKE ?)")
        parameters.extend([like_value, like_value, like_value, like_value])

    sql = (
        "SELECT r.id, r.user_id, r.phone, r.gender, r.status, r.progress_stage, r.progress_message, r.error_message, r.created_at, r.updated_at "
        "FROM reviews r "
        "LEFT JOIN user_profiles p ON p.user_id = r.user_id "
        "LEFT JOIN usage_records ur ON ur.id = r.id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.created_at DESC, r.id DESC LIMIT ? OFFSET ?"
    parameters.extend([normalized_limit, normalized_offset])
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_review_summary_row(row) for row in rows]


def get_internal_phone_qimen_summary() -> dict[str, Any]:
    with open_connection() as connection:
        review_row = connection.execute(
            """
            WITH base_usage AS (
                SELECT COALESCE(NULLIF(target_id, ''), id) AS review_id, SUM(points_cost) AS points_cost
                FROM usage_records
                WHERE scene = 'phone_review_base'
                GROUP BY COALESCE(NULLIF(target_id, ''), id)
            )
            SELECT
                COUNT(r.id) AS total_review_count,
                SUM(CASE WHEN date(datetime(r.created_at), '+8 hours') = date('now', '+8 hours') THEN 1 ELSE 0 END) AS today_review_count,
                SUM(CASE WHEN datetime(r.created_at, '+8 hours') >= date('now', '+8 hours', 'weekday 1', '-7 days') THEN 1 ELSE 0 END) AS week_review_count,
                SUM(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END) AS completed_review_count,
                SUM(CASE WHEN r.status = 'failed' THEN 1 ELSE 0 END) AS failed_review_count,
                AVG(CASE WHEN r.status IN ('completed', 'failed') THEN strftime('%s', r.updated_at) - strftime('%s', r.created_at) END) AS average_generation_seconds,
                COALESCE(SUM(COALESCE(base_usage.points_cost, 0)), 0) AS review_points_cost
            FROM reviews r
            LEFT JOIN base_usage ON base_usage.review_id = r.id
            """
        ).fetchone()
        unlock_row = connection.execute(
            "SELECT COUNT(*) AS unlock_count, COUNT(DISTINCT review_id) AS unlocked_review_count FROM review_aspect_unlocks"
        ).fetchone()
        voice_row = connection.execute(
            "SELECT COUNT(*) AS voice_request_count FROM usage_records WHERE scene = 'voice_tts'"
        ).fetchone()

    total_review_count = int(review_row["total_review_count"] or 0) if review_row else 0
    completed_review_count = int(review_row["completed_review_count"] or 0) if review_row else 0
    unlocked_review_count = int(unlock_row["unlocked_review_count"] or 0) if unlock_row else 0
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "today_review_count": int(review_row["today_review_count"] or 0) if review_row else 0,
        "week_review_count": int(review_row["week_review_count"] or 0) if review_row else 0,
        "total_review_count": total_review_count,
        "completed_review_count": completed_review_count,
        "failed_review_count": int(review_row["failed_review_count"] or 0) if review_row else 0,
        "success_rate": round(completed_review_count / total_review_count * 100, 1) if total_review_count else 0,
        "average_generation_seconds": round(float(review_row["average_generation_seconds"]), 1) if review_row and review_row["average_generation_seconds"] is not None else None,
        "aspect_unlock_count": int(unlock_row["unlock_count"] or 0) if unlock_row else 0,
        "aspect_unlock_rate": round(unlocked_review_count / completed_review_count * 100, 1) if completed_review_count else 0,
        "review_points_cost": int(review_row["review_points_cost"] or 0) if review_row else 0,
        "voice_request_count": int(voice_row["voice_request_count"] or 0) if voice_row else 0,
    }


def _build_internal_phone_qimen_review_conditions(
    *,
    keyword: str | None = None,
    status: str | None = None,
    gender: str | None = None,
    channel: str | None = None,
    user_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    review_id: str | None = None,
) -> tuple[list[str], list[Any]]:
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(review_id):
        conditions.append("r.id = ?")
        parameters.append(str(review_id))
    if _normalize_optional_text(user_id):
        conditions.append("r.user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(status):
        conditions.append("r.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(gender):
        conditions.append("r.gender = ?")
        parameters.append(str(gender))
    if _normalize_optional_text(channel):
        conditions.append("base_usage.channel = ?")
        parameters.append(str(channel))
    if _normalize_optional_text(date_from):
        conditions.append("r.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("r.created_at <= ?")
        parameters.append(str(date_to))
    if _normalize_optional_text(keyword):
        like_value = f"%{str(keyword).strip()}%"
        conditions.append(
            "(r.id LIKE ? OR r.phone LIKE ? OR IFNULL(r.user_id, '') LIKE ? OR IFNULL(u.uid, '') LIKE ? OR IFNULL(p.nickname, '') LIKE ? OR IFNULL(pi.normalized_phone, '') LIKE ?)"
        )
        parameters.extend([like_value, like_value, like_value, like_value, like_value, like_value])
    return conditions, parameters


def _internal_phone_qimen_review_from_clause() -> str:
    return """
        FROM reviews r
        LEFT JOIN users u ON u.id = r.user_id
        LEFT JOIN user_profiles p ON p.user_id = r.user_id
        LEFT JOIN user_phone_identities pi ON pi.user_id = r.user_id AND pi.is_primary = 1
        LEFT JOIN (
            SELECT
                COALESCE(NULLIF(target_id, ''), id) AS review_id,
                MAX(channel) AS channel,
                SUM(points_cost) AS points_cost
            FROM usage_records
            WHERE scene = 'phone_review_base'
            GROUP BY COALESCE(NULLIF(target_id, ''), id)
        ) base_usage ON base_usage.review_id = r.id
        LEFT JOIN (
            SELECT review_id, COUNT(*) AS unlock_count
            FROM review_aspect_unlocks
            GROUP BY review_id
        ) unlocks ON unlocks.review_id = r.id
        LEFT JOIN (
            SELECT
                CASE
                    WHEN target_id LIKE '%:%' THEN substr(target_id, 1, instr(target_id, ':') - 1)
                    ELSE target_id
                END AS review_id,
                COUNT(*) AS voice_count
            FROM usage_records
            WHERE scene = 'voice_tts' AND IFNULL(target_id, '') != ''
            GROUP BY
                CASE
                    WHEN target_id LIKE '%:%' THEN substr(target_id, 1, instr(target_id, ':') - 1)
                    ELSE target_id
                END
        ) voices ON voices.review_id = r.id
    """


def count_internal_phone_qimen_reviews(
    *,
    keyword: str | None = None,
    status: str | None = None,
    gender: str | None = None,
    channel: str | None = None,
    user_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> int:
    conditions, parameters = _build_internal_phone_qimen_review_conditions(
        keyword=keyword,
        status=status,
        gender=gender,
        channel=channel,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    sql = "SELECT COUNT(r.id) AS total " + _internal_phone_qimen_review_from_clause()
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    with open_connection() as connection:
        row = connection.execute(sql, parameters).fetchone()
    return int(row["total"] if row is not None else 0)


def list_internal_phone_qimen_reviews(
    *,
    limit: int = 20,
    offset: int = 0,
    keyword: str | None = None,
    status: str | None = None,
    gender: str | None = None,
    channel: str | None = None,
    user_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_offset = max(0, int(offset))
    conditions, parameters = _build_internal_phone_qimen_review_conditions(
        keyword=keyword,
        status=status,
        gender=gender,
        channel=channel,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    sql = (
        """
        SELECT
            r.id, r.user_id, u.uid AS user_uid, p.nickname AS user_nickname, pi.normalized_phone AS user_phone,
            r.phone, r.gender, r.status, r.progress_stage, r.progress_message, r.error_message,
            base_usage.channel, COALESCE(base_usage.points_cost, 0) AS base_points_cost,
            COALESCE(unlocks.unlock_count, 0) AS unlock_count,
            COALESCE(voices.voice_count, 0) AS voice_count,
            CASE WHEN r.status IN ('completed', 'failed') THEN CAST(strftime('%s', r.updated_at) - strftime('%s', r.created_at) AS INTEGER) ELSE NULL END AS generation_duration_seconds,
            r.created_at, r.updated_at
        """
        + _internal_phone_qimen_review_from_clause()
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.created_at DESC, r.id DESC LIMIT ? OFFSET ?"
    parameters.extend([normalized_limit, normalized_offset])
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_internal_phone_qimen_review_row(row) for row in rows]


def get_internal_phone_qimen_review(review_id: str) -> dict[str, Any] | None:
    conditions, parameters = _build_internal_phone_qimen_review_conditions(review_id=review_id)
    sql = (
        """
        SELECT
            r.id, r.user_id, u.uid AS user_uid, p.nickname AS user_nickname, pi.normalized_phone AS user_phone,
            r.phone, r.gender, r.status, r.progress_stage, r.progress_message, r.error_message,
            base_usage.channel, COALESCE(base_usage.points_cost, 0) AS base_points_cost,
            COALESCE(unlocks.unlock_count, 0) AS unlock_count,
            COALESCE(voices.voice_count, 0) AS voice_count,
            CASE WHEN r.status IN ('completed', 'failed') THEN CAST(strftime('%s', r.updated_at) - strftime('%s', r.created_at) AS INTEGER) ELSE NULL END AS generation_duration_seconds,
            r.created_at, r.updated_at
        """
        + _internal_phone_qimen_review_from_clause()
        + " WHERE "
        + " AND ".join(conditions)
        + " LIMIT 1"
    )
    with open_connection() as connection:
        row = connection.execute(sql, parameters).fetchone()
    return _deserialize_internal_phone_qimen_review_row(row) if row is not None else None


def list_voice_usage_records_for_review(review_id: str) -> list[dict[str, Any]]:
    with open_connection() as connection:
        rows = connection.execute(
            """
            SELECT ur.id, ur.user_id, ur.scene, ur.channel, ur.target_id, ur.points_cost, ur.status,
                   ur.request_payload_summary, ur.result_summary, ur.created_at, ur.updated_at,
                   u.status AS user_status, p.nickname AS user_nickname, p.avatar_url AS user_avatar_url
            FROM usage_records ur
            JOIN users u ON u.id = ur.user_id
            LEFT JOIN user_profiles p ON p.user_id = ur.user_id
            WHERE ur.scene = 'voice_tts'
              AND (ur.target_id = ? OR ur.target_id LIKE ?)
            ORDER BY ur.created_at DESC, ur.id DESC
            """,
            (review_id, f"{review_id}:%"),
        ).fetchall()
    return [_deserialize_usage_record_row(row) for row in rows]



def upsert_wechat_user(*, appid: str, openid: str, unionid: str | None, session_key: str | None, nickname: str | None, avatar_url: str | None, initial_points: int, now_text: str) -> dict[str, Any]:
    normalized_unionid = _normalize_optional_text(unionid)
    normalized_identity_type = "wechat_unionid" if normalized_unionid else "wechat_pending_unionid"
    with open_connection() as connection:
        matched_by_openid = connection.execute(
            """
            SELECT i.id AS identity_id, i.user_id, i.unionid, p.nickname, p.avatar_url
            FROM user_wechat_identities i
            JOIN users u ON u.id = i.user_id
            LEFT JOIN user_profiles p ON p.user_id = u.id
            WHERE i.appid = ? AND i.openid = ?
            """,
            (appid, openid),
        ).fetchone()
        matched_by_unionid = None
        if normalized_unionid:
            matched_by_unionid = connection.execute(
                """
                SELECT i.id AS identity_id, i.user_id, i.unionid, p.nickname, p.avatar_url
                FROM user_wechat_identities i
                JOIN users u ON u.id = i.user_id
                LEFT JOIN user_profiles p ON p.user_id = u.id
                WHERE i.unionid = ?
                ORDER BY i.last_login_at DESC
                LIMIT 1
                """,
                (normalized_unionid,),
            ).fetchone()

        if matched_by_openid is not None and matched_by_unionid is not None and str(matched_by_openid["user_id"]) != str(matched_by_unionid["user_id"]):
            raise ValueError("wechat_identity_conflict")

        existing = matched_by_openid or matched_by_unionid
        if existing is None:
            user_id = uuid4().hex
            user_uid = _generate_unique_user_uid(connection)
            connection.execute(
                "INSERT INTO users (id, uid, status, primary_identity_type, registered_channel, created_at, updated_at, last_active_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_uid, "active", normalized_identity_type, f"wechat:{appid}", now_text, now_text, now_text),
            )
            connection.execute(
                "INSERT INTO user_profiles (user_id, nickname, avatar_url, profile_completed, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, nickname, avatar_url, _profile_completed(nickname, avatar_url), now_text, now_text),
            )
            connection.execute(
                "INSERT INTO user_wechat_identities (id, user_id, appid, openid, unionid, session_key, created_at, updated_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (uuid4().hex, user_id, appid, openid, normalized_unionid, session_key, now_text, now_text, now_text),
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
            final_unionid = normalized_unionid or _normalize_optional_text(existing["unionid"])
            final_identity_type = "wechat_unionid" if final_unionid else normalized_identity_type
            connection.execute(
                "UPDATE users SET primary_identity_type = ?, registered_channel = COALESCE(registered_channel, ?), updated_at = ?, last_active_at = ? WHERE id = ?",
                (final_identity_type, f"wechat:{appid}", now_text, now_text, user_id),
            )
            connection.execute(
                "INSERT OR IGNORE INTO user_profiles (user_id, nickname, avatar_url, profile_completed, created_at, updated_at) VALUES (?, NULL, NULL, 0, ?, ?)",
                (user_id, now_text, now_text),
            )
            connection.execute(
                "UPDATE user_profiles SET nickname = ?, avatar_url = ?, profile_completed = ?, updated_at = ? WHERE user_id = ?",
                (final_nickname, final_avatar_url, _profile_completed(final_nickname, final_avatar_url), now_text, user_id),
            )
            if matched_by_openid is None:
                connection.execute(
                    "INSERT INTO user_wechat_identities (id, user_id, appid, openid, unionid, session_key, created_at, updated_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (uuid4().hex, user_id, appid, openid, final_unionid, session_key, now_text, now_text, now_text),
                )
            else:
                connection.execute(
                    "UPDATE user_wechat_identities SET unionid = ?, session_key = ?, updated_at = ?, last_login_at = ? WHERE id = ?",
                    (final_unionid, session_key, now_text, now_text, str(matched_by_openid["identity_id"])),
                )
            connection.execute(
                "INSERT OR IGNORE INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, 0, 0, 0, ?, ?)",
                (user_id, now_text, now_text),
            )

        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    if row is None:
        raise RuntimeError("user_upsert_failed")
    return _deserialize_user_row(row)


def get_phone_identity_by_normalized_phone(*, normalized_phone: str, country_code: str = "86") -> dict[str, Any] | None:
    normalized_country_code = _normalize_optional_text(country_code) or "86"
    normalized_phone_value = _normalize_optional_text(normalized_phone)
    if not normalized_phone_value:
        return None
    with open_connection() as connection:
        row = connection.execute(
            """
            SELECT id, user_id, country_code, phone_number, normalized_phone, is_primary,
                   verified_at, password_hash, password_updated_at, created_at, updated_at, last_login_at
            FROM user_phone_identities
            WHERE country_code = ? AND normalized_phone = ?
            LIMIT 1
            """,
            (normalized_country_code, normalized_phone_value),
        ).fetchone()
    if row is None:
        return None
    return {
        "identity_id": row["id"],
        "user_id": row["user_id"],
        "country_code": row["country_code"],
        "phone_number": row["phone_number"],
        "normalized_phone": row["normalized_phone"],
        "is_primary": bool(row["is_primary"]),
        "verified_at": row["verified_at"],
        "password_hash": row["password_hash"],
        "password_updated_at": row["password_updated_at"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_login_at": row["last_login_at"],
    }


def get_primary_phone_identity_by_user_id(user_id: str) -> dict[str, Any] | None:
    normalized_user_id = _normalize_optional_text(user_id)
    if not normalized_user_id:
        return None
    with open_connection() as connection:
        row = connection.execute(
            """
            SELECT id, user_id, country_code, phone_number, normalized_phone, is_primary,
                   verified_at, password_hash, password_updated_at, created_at, updated_at, last_login_at
            FROM user_phone_identities
            WHERE user_id = ? AND is_primary = 1
            LIMIT 1
            """,
            (normalized_user_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "identity_id": row["id"],
        "user_id": row["user_id"],
        "country_code": row["country_code"],
        "phone_number": row["phone_number"],
        "normalized_phone": row["normalized_phone"],
        "is_primary": bool(row["is_primary"]),
        "verified_at": row["verified_at"],
        "password_hash": row["password_hash"],
        "password_updated_at": row["password_updated_at"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_login_at": row["last_login_at"],
    }


def create_phone_user(*, normalized_phone: str, password_hash: str, initial_points: int, registered_channel: str | None, now_text: str) -> dict[str, Any]:
    normalized_phone_value = _normalize_optional_text(normalized_phone)
    normalized_password_hash = _normalize_optional_text(password_hash)
    if not normalized_phone_value:
        raise ValueError("invalid_phone_number")
    if not normalized_password_hash:
        raise ValueError("password_hash_required")

    user_id = uuid4().hex
    with open_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM user_phone_identities WHERE country_code = ? AND normalized_phone = ?",
            ("86", normalized_phone_value),
        ).fetchone()
        if existing is not None:
            raise ValueError("phone_already_registered")
        try:
            user_uid = _generate_unique_user_uid(connection)
            connection.execute(
                "INSERT INTO users (id, uid, status, primary_identity_type, registered_channel, created_at, updated_at, last_active_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_uid, "active", "phone", registered_channel or "phone:h5", now_text, now_text, now_text),
            )
            connection.execute(
                "INSERT INTO user_profiles (user_id, nickname, avatar_url, profile_completed, created_at, updated_at) VALUES (?, NULL, NULL, 0, ?, ?)",
                (user_id, now_text, now_text),
            )
            connection.execute(
                """
                INSERT INTO user_phone_identities (
                    id, user_id, country_code, phone_number, normalized_phone, is_primary,
                    verified_at, password_hash, password_updated_at, created_at, updated_at, last_login_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid4().hex,
                    user_id,
                    "86",
                    normalized_phone_value,
                    normalized_phone_value,
                    1,
                    now_text,
                    normalized_password_hash,
                    now_text,
                    now_text,
                    now_text,
                    now_text,
                ),
            )
            _create_points_account_with_initial_grant_in_connection(
                connection,
                user_id=user_id,
                initial_points=initial_points,
                grant_biz_type="signup_bonus",
                grant_idempotency_key=f"signup:phone:86:{normalized_phone_value}",
                remark="initial test points",
                now_text=now_text,
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("phone_already_registered") from exc

        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    if row is None:
        raise RuntimeError("phone_user_create_failed")
    return _deserialize_user_row(row)


def mark_phone_identity_login(*, identity_id: str, now_text: str) -> dict[str, Any] | None:
    normalized_identity_id = _normalize_optional_text(identity_id)
    if not normalized_identity_id:
        return None
    with open_connection() as connection:
        identity = connection.execute("SELECT user_id FROM user_phone_identities WHERE id = ?", (normalized_identity_id,)).fetchone()
        if identity is None:
            return None
        user_id = str(identity["user_id"])
        connection.execute(
            "UPDATE user_phone_identities SET last_login_at = ?, updated_at = ? WHERE id = ?",
            (now_text, now_text, normalized_identity_id),
        )
        connection.execute(
            "UPDATE users SET primary_identity_type = ?, updated_at = ?, last_active_at = ? WHERE id = ?",
            ("phone", now_text, now_text, user_id),
        )
        row = connection.execute(_USER_SELECT_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    return _deserialize_user_row(row) if row is not None else None



def update_phone_identity_password(*, identity_id: str, password_hash: str, now_text: str) -> bool:
    normalized_identity_id = _normalize_optional_text(identity_id)
    normalized_password_hash = _normalize_optional_text(password_hash)
    if not normalized_identity_id or not normalized_password_hash:
        return False
    with open_connection() as connection:
        cursor = connection.execute(
            "UPDATE user_phone_identities SET password_hash = ?, password_updated_at = ?, updated_at = ? WHERE id = ?",
            (normalized_password_hash, now_text, now_text, normalized_identity_id),
        )
    return cursor.rowcount > 0


def create_session(*, user_id: str, token_hash: str, device_type: str | None, client_version: str | None, ip: str | None, expires_at: str, now_text: str) -> dict[str, Any]:
    session_id = uuid4().hex
    with open_connection() as connection:
        connection.execute(
            "INSERT INTO user_sessions (id, user_id, token_hash, device_type, client_version, ip, status, expires_at, last_seen_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, user_id, token_hash, device_type, client_version, ip, "active", expires_at, now_text, now_text),
        )
    return {"session_id": session_id, "expires_at": expires_at}


def revoke_session_by_token_hash(token_hash: str, *, now_text: str) -> bool:
    normalized_token_hash = _normalize_optional_text(token_hash)
    if not normalized_token_hash:
        return False
    with open_connection() as connection:
        cursor = connection.execute(
            "UPDATE user_sessions SET status = ?, last_seen_at = ? WHERE token_hash = ? AND status = ?",
            ("revoked", now_text, normalized_token_hash, "active"),
        )
    return cursor.rowcount > 0



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
        "SELECT u.id AS user_id, u.uid, u.status, u.identity_level, u.primary_identity_type, u.registered_channel, u.promoter_parent_user_id, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance, "
        "COALESCE(pwa.withdrawable_balance_cents, pra.balance, 0) AS withdrawable_balance_cents, COALESCE(pwa.frozen_commission_cents, pra.frozen_balance, 0) AS frozen_commission_cents, COALESCE(pwa.withdrawn_amount_cents, 0) AS withdrawn_amount_cents, "
        "pra.balance AS rebate_points_balance, pra.frozen_balance AS rebate_frozen_balance, "
        "MAX(pi.normalized_phone) AS primary_phone, MAX(pi.verified_at) AS phone_verified_at, MAX(w.unionid) AS primary_unionid, "
        "MIN(pi.verified_at) AS phone_registered_at, MIN(CASE WHEN w.unionid IS NOT NULL THEN COALESCE(w.updated_at, w.created_at) END) AS unionid_registered_at, "
        "MAX(w.openid) AS openid, MAX(w.unionid) AS unionid "
        "FROM users u "
        "LEFT JOIN user_profiles p ON p.user_id = u.id "
        "LEFT JOIN points_accounts pa ON pa.user_id = u.id "
        "LEFT JOIN user_phone_identities pi ON pi.user_id = u.id AND pi.is_primary = 1 "
        "LEFT JOIN promotion_rebate_accounts pra ON pra.user_id = u.id "
        "LEFT JOIN promotion_wallet_accounts pwa ON pwa.user_id = u.id "
        "LEFT JOIN user_wechat_identities w ON w.user_id = u.id "
        "WHERE u.id = ? "
        "GROUP BY u.id, u.uid, u.status, u.identity_level, u.primary_identity_type, u.registered_channel, u.promoter_parent_user_id, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance, pra.balance, pra.frozen_balance, pwa.withdrawable_balance_cents, pwa.frozen_commission_cents, pwa.withdrawn_amount_cents"
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


def list_users(
    *,
    limit: int = 20,
    offset: int = 0,
    query: str | None = None,
    keyword: str | None = None,
    status: str | None = None,
    identity_level: str | None = None,
    channel: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_offset = max(0, int(offset))
    normalized_query = _normalize_optional_text(keyword) or _normalize_optional_text(query)
    sql = (
        "SELECT u.id AS user_id, u.uid, u.status, u.identity_level, u.primary_identity_type, u.registered_channel, u.promoter_parent_user_id, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance, "
        "COALESCE(pwa.withdrawable_balance_cents, pra.balance, 0) AS withdrawable_balance_cents, COALESCE(pwa.frozen_commission_cents, pra.frozen_balance, 0) AS frozen_commission_cents, COALESCE(pwa.withdrawn_amount_cents, 0) AS withdrawn_amount_cents, "
        "pra.balance AS rebate_points_balance, pra.frozen_balance AS rebate_frozen_balance, "
        "MAX(pi.normalized_phone) AS primary_phone, MAX(pi.verified_at) AS phone_verified_at, MAX(w.unionid) AS primary_unionid, "
        "MIN(pi.verified_at) AS phone_registered_at, MIN(CASE WHEN w.unionid IS NOT NULL THEN COALESCE(w.updated_at, w.created_at) END) AS unionid_registered_at, "
        "MAX(w.openid) AS openid, MAX(w.unionid) AS unionid "
        "FROM users u "
        "LEFT JOIN user_profiles p ON p.user_id = u.id "
        "LEFT JOIN points_accounts pa ON pa.user_id = u.id "
        "LEFT JOIN user_phone_identities pi ON pi.user_id = u.id AND pi.is_primary = 1 "
        "LEFT JOIN promotion_rebate_accounts pra ON pra.user_id = u.id "
        "LEFT JOIN promotion_wallet_accounts pwa ON pwa.user_id = u.id "
        "LEFT JOIN user_wechat_identities w ON w.user_id = u.id"
    )
    conditions: list[str] = []
    parameters: list[Any] = []
    if normalized_query:
        conditions.append("(u.id LIKE ? OR IFNULL(u.uid, '') LIKE ? OR IFNULL(p.nickname, '') LIKE ? OR IFNULL(pi.normalized_phone, '') LIKE ? OR IFNULL(w.unionid, '') LIKE ? OR IFNULL(w.openid, '') LIKE ?)")
        like_value = f"%{normalized_query}%"
        parameters.extend([like_value, like_value, like_value, like_value, like_value, like_value])
    if _normalize_optional_text(status):
        try:
            normalized_filter_status = _normalize_user_status(status)
        except ValueError:
            normalized_filter_status = str(status)
        if normalized_filter_status == "disabled":
            conditions.append("u.status != 'active'")
        else:
            conditions.append("u.status = ?")
            parameters.append(normalized_filter_status)
    normalized_identity_filter = _normalize_optional_text(identity_level)
    if normalized_identity_filter:
        canonical_identity_filter = _normalize_user_identity_for_output(normalized_identity_filter)
        identity_aliases = [
            value
            for value, canonical_value in USER_IDENTITY_LEVEL_ALIASES.items()
            if canonical_value == canonical_identity_filter
        ]
        identity_values = [canonical_identity_filter, *identity_aliases]
        conditions.append("u.identity_level IN (" + ", ".join("?" for _ in identity_values) + ")")
        parameters.extend(identity_values)
    if _normalize_optional_text(channel):
        conditions.append("u.registered_channel = ?")
        parameters.append(str(channel))
    if _normalize_optional_text(date_from):
        conditions.append("u.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("u.created_at <= ?")
        parameters.append(str(date_to))
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " GROUP BY u.id, u.uid, u.status, u.identity_level, u.primary_identity_type, u.registered_channel, u.promoter_parent_user_id, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance, pra.balance, pra.frozen_balance, pwa.withdrawable_balance_cents, pwa.frozen_commission_cents, pwa.withdrawn_amount_cents ORDER BY u.last_active_at DESC LIMIT ? OFFSET ?"
    parameters.extend([normalized_limit, normalized_offset])
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_internal_user_row(row) for row in rows]


def count_users(
    *,
    query: str | None = None,
    keyword: str | None = None,
    status: str | None = None,
    identity_level: str | None = None,
    channel: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> int:
    normalized_query = _normalize_optional_text(keyword) or _normalize_optional_text(query)
    sql = (
        "SELECT COUNT(DISTINCT u.id) AS total "
        "FROM users u "
        "LEFT JOIN user_profiles p ON p.user_id = u.id "
        "LEFT JOIN user_phone_identities pi ON pi.user_id = u.id AND pi.is_primary = 1 "
        "LEFT JOIN user_wechat_identities w ON w.user_id = u.id"
    )
    conditions: list[str] = []
    parameters: list[Any] = []
    if normalized_query:
        conditions.append("(u.id LIKE ? OR IFNULL(u.uid, '') LIKE ? OR IFNULL(p.nickname, '') LIKE ? OR IFNULL(pi.normalized_phone, '') LIKE ? OR IFNULL(w.unionid, '') LIKE ? OR IFNULL(w.openid, '') LIKE ?)")
        like_value = f"%{normalized_query}%"
        parameters.extend([like_value, like_value, like_value, like_value, like_value, like_value])
    if _normalize_optional_text(status):
        try:
            normalized_filter_status = _normalize_user_status(status)
        except ValueError:
            normalized_filter_status = str(status)
        if normalized_filter_status == "disabled":
            conditions.append("u.status != 'active'")
        else:
            conditions.append("u.status = ?")
            parameters.append(normalized_filter_status)
    normalized_identity_filter = _normalize_optional_text(identity_level)
    if normalized_identity_filter:
        canonical_identity_filter = _normalize_user_identity_for_output(normalized_identity_filter)
        identity_aliases = [
            value
            for value, canonical_value in USER_IDENTITY_LEVEL_ALIASES.items()
            if canonical_value == canonical_identity_filter
        ]
        identity_values = [canonical_identity_filter, *identity_aliases]
        conditions.append("u.identity_level IN (" + ", ".join("?" for _ in identity_values) + ")")
        parameters.extend(identity_values)
    if _normalize_optional_text(channel):
        conditions.append("u.registered_channel = ?")
        parameters.append(str(channel))
    if _normalize_optional_text(date_from):
        conditions.append("u.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("u.created_at <= ?")
        parameters.append(str(date_to))
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    with open_connection() as connection:
        row = connection.execute(sql, parameters).fetchone()
    return int(row["total"] if row is not None else 0)



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


def adjust_rebate_points(*, user_id: str, delta: int, reason: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    normalized_delta = int(delta)
    if normalized_delta == 0:
        raise ValueError("delta_must_not_be_zero")
    with open_connection() as connection:
        before_row = _get_rebate_account_row(connection, user_id=user_id, now_text=now_text)
        before_balance = int(before_row["balance"])
        balance_after = before_balance + normalized_delta
        connection.execute(
            "UPDATE promotion_rebate_accounts SET balance = ?, version = version + 1, updated_at = ? WHERE user_id = ?",
            (balance_after, now_text, user_id),
        )
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action="rebate_points_adjust",
            target_type="user",
            target_id=user_id,
            reason=reason,
            operator_note=operator_note,
            before={"rebate_points_balance": before_balance},
            after={"rebate_points_balance": balance_after, "delta": normalized_delta},
            created_at=now_text,
        )
        row = _get_rebate_account_row(connection, user_id=user_id, now_text=now_text)
    return _deserialize_rebate_account_row(row)


def update_user_status(*, user_id: str, status: str, reason: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_status = _normalize_user_status(status)
    with open_connection() as connection:
        before = connection.execute("SELECT id, status FROM users WHERE id = ?", (user_id,)).fetchone()
        if before is None:
            return None
        connection.execute("UPDATE users SET status = ?, updated_at = ? WHERE id = ?", (normalized_status, now_text, user_id))
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action="user_status_update",
            target_type="user",
            target_id=user_id,
            reason=reason,
            operator_note=operator_note,
            before={"status": before["status"]},
            after={"status": normalized_status},
            created_at=now_text,
        )
    return get_internal_user(user_id)


def update_user_identity(*, user_id: str, identity_level: str, reason: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_identity = _normalize_user_identity_for_storage(identity_level)
    with open_connection() as connection:
        before = connection.execute("SELECT id, identity_level FROM users WHERE id = ?", (user_id,)).fetchone()
        if before is None:
            return None
        connection.execute("UPDATE users SET identity_level = ?, updated_at = ? WHERE id = ?", (normalized_identity, now_text, user_id))
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action="user_identity_update",
            target_type="user",
            target_id=user_id,
            reason=reason,
            operator_note=operator_note,
            before={"identity_level": before["identity_level"]},
            after={"identity_level": normalized_identity},
            created_at=now_text,
        )
    return get_internal_user(user_id)


def update_user_promoter_parent(*, user_id: str, promoter_parent_user_id: str | None, reason: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_parent_id = _normalize_optional_text(promoter_parent_user_id)
    if normalized_parent_id == user_id:
        raise ValueError("promoter_parent_must_not_be_self")
    with open_connection() as connection:
        before = connection.execute("SELECT id, promoter_parent_user_id FROM users WHERE id = ?", (user_id,)).fetchone()
        if before is None:
            return None
        if normalized_parent_id:
            parent = connection.execute("SELECT id FROM users WHERE id = ?", (normalized_parent_id,)).fetchone()
            if parent is None:
                raise ValueError("promoter_parent_not_found")
        connection.execute("UPDATE users SET promoter_parent_user_id = ?, updated_at = ? WHERE id = ?", (normalized_parent_id, now_text, user_id))
        if normalized_parent_id:
            connection.execute(
                """
                INSERT INTO promotion_relationships (user_id, promoter_user_id, bind_source, updated_by, reason, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET promoter_user_id = excluded.promoter_user_id, bind_source = excluded.bind_source, updated_by = excluded.updated_by, reason = excluded.reason, updated_at = excluded.updated_at
                """,
                (user_id, normalized_parent_id, "admin_manual", operator, reason, now_text, now_text),
            )
        else:
            connection.execute("DELETE FROM promotion_relationships WHERE user_id = ?", (user_id,))
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action="promoter_parent_update",
            target_type="user",
            target_id=user_id,
            reason=reason,
            operator_note=operator_note,
            before={"promoter_parent_user_id": before["promoter_parent_user_id"]},
            after={"promoter_parent_user_id": normalized_parent_id},
            created_at=now_text,
        )
    return get_internal_user(user_id)



def refund_points(*, user_id: str, points_amount: int, biz_type: str, biz_id: str | None, idempotency_key: str | None, remark: str | None, now_text: str) -> dict[str, Any] | None:
    normalized_points_amount = max(0, int(points_amount))
    if normalized_points_amount == 0:
        return None
    with open_connection() as connection:
        return _credit_points_in_connection(connection, user_id=user_id, points_amount=normalized_points_amount, change_type="refund", biz_type=biz_type, biz_id=biz_id, idempotency_key=idempotency_key, remark=remark, now_text=now_text)



def get_usage_record(usage_record_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT ur.id, ur.user_id, ur.scene, ur.channel, ur.target_id, ur.points_cost, ur.status, ur.request_payload_summary, ur.result_summary, ur.created_at, ur.updated_at, u.status AS user_status, p.nickname AS user_nickname, p.avatar_url AS user_avatar_url "
            "FROM usage_records ur "
            "JOIN users u ON u.id = ur.user_id "
            "LEFT JOIN user_profiles p ON p.user_id = ur.user_id "
            "WHERE ur.id = ?",
            (usage_record_id,),
        ).fetchone()
    return _deserialize_usage_record_row(row) if row is not None else None


def create_usage_record(*, usage_record_id: str, user_id: str, scene: str, channel: str | None, target_id: str | None, points_cost: int, status: str, request_payload_summary: dict[str, Any] | None, result_summary: dict[str, Any] | None, created_at: str) -> dict[str, Any]:
    with open_connection() as connection:
        _create_usage_record_in_connection(
            connection,
            usage_record_id=usage_record_id,
            user_id=user_id,
            scene=scene,
            channel=channel,
            target_id=target_id,
            points_cost=max(0, int(points_cost)),
            status=status,
            request_payload_summary=request_payload_summary,
            result_summary=result_summary,
            created_at=created_at,
            updated_at=created_at,
        )
    usage_record = get_usage_record(usage_record_id)
    if usage_record is None:
        raise RuntimeError("usage_record_create_failed")
    return usage_record


def list_usage_records(
    *,
    limit: int = 20,
    offset: int = 0,
    user_id: str | None = None,
    feature_key: str | None = None,
    scene: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    channel: str | None = None,
    target_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_offset = max(0, int(offset))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(user_id):
        conditions.append("ur.user_id = ?")
        parameters.append(str(user_id))
    normalized_scene = _normalize_optional_text(feature_key) or _normalize_optional_text(scene)
    if normalized_scene:
        conditions.append("ur.scene = ?")
        parameters.append(normalized_scene)
    if _normalize_optional_text(status):
        conditions.append("ur.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(channel):
        conditions.append("ur.channel = ?")
        parameters.append(str(channel))
    if _normalize_optional_text(target_id):
        conditions.append("ur.target_id = ?")
        parameters.append(str(target_id))
    if _normalize_optional_text(date_from):
        conditions.append("ur.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("ur.created_at <= ?")
        parameters.append(str(date_to))
    if _normalize_optional_text(keyword):
        like_value = f"%{str(keyword).strip()}%"
        conditions.append(
            "("
            "ur.id LIKE ? OR ur.user_id LIKE ? OR ur.scene LIKE ? OR IFNULL(ur.target_id, '') LIKE ? "
            "OR IFNULL(ur.channel, '') LIKE ? OR IFNULL(p.nickname, '') LIKE ? "
            "OR IFNULL(ur.request_payload_summary, '') LIKE ? OR IFNULL(ur.result_summary, '') LIKE ?"
            ")"
        )
        parameters.extend([like_value, like_value, like_value, like_value, like_value, like_value, like_value, like_value])
    sql = (
        "SELECT ur.id, ur.user_id, ur.scene, ur.channel, ur.target_id, ur.points_cost, ur.status, ur.request_payload_summary, ur.result_summary, ur.created_at, ur.updated_at, "
        "u.status AS user_status, p.nickname AS user_nickname, p.avatar_url AS user_avatar_url "
        "FROM usage_records ur "
        "JOIN users u ON u.id = ur.user_id "
        "LEFT JOIN user_profiles p ON p.user_id = ur.user_id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY ur.created_at DESC, ur.id DESC LIMIT ? OFFSET ?"
    parameters.extend([normalized_limit, normalized_offset])
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


def list_recharge_orders(
    *,
    limit: int = 20,
    offset: int = 0,
    user_id: str | None = None,
    status: str | None = None,
    source: str | None = None,
    channel: str | None = None,
    keyword: str | None = None,
    amount_min: int | None = None,
    amount_max: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_offset = max(0, int(offset))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(user_id):
        conditions.append("r.user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(status):
        conditions.append("r.status = ?")
        parameters.append(_storage_recharge_order_status(str(status)))
    if _normalize_optional_text(source):
        conditions.append("r.source = ?")
        parameters.append(str(source))
    if _normalize_optional_text(channel):
        conditions.append("r.channel = ?")
        parameters.append(str(channel))
    if amount_min is not None:
        conditions.append("r.amount_cents >= ?")
        parameters.append(int(amount_min))
    if amount_max is not None:
        conditions.append("r.amount_cents <= ?")
        parameters.append(int(amount_max))
    if _normalize_optional_text(date_from):
        conditions.append("r.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("r.created_at <= ?")
        parameters.append(str(date_to))
    if _normalize_optional_text(keyword):
        like_value = f"%{str(keyword).strip()}%"
        conditions.append("(r.id LIKE ? OR r.user_id LIKE ? OR IFNULL(p.nickname, '') LIKE ? OR IFNULL(r.external_order_id, '') LIKE ? OR r.package_title LIKE ?)")
        parameters.extend([like_value, like_value, like_value, like_value, like_value])

    sql = (
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.paid_at, r.completed_at, r.closed_at, r.granted_ledger_id, r.created_at, r.updated_at "
        "FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.created_at DESC, r.id DESC LIMIT ? OFFSET ?"
    parameters.extend([normalized_limit, normalized_offset])
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_recharge_order_row(row) for row in rows]


def create_payment_transaction(
    *,
    transaction_id: str,
    order_id: str,
    user_id: str,
    provider: str,
    payment_method: str,
    amount_cents: int,
    status: str,
    provider_transaction_id: str | None,
    prepay_id: str | None,
    idempotency_key: str | None,
    payment_params: dict[str, Any] | None,
    failure_reason: str | None,
    now_text: str,
) -> dict[str, Any]:
    normalized_provider = (_normalize_optional_text(provider) or "wechat_h5").lower()
    normalized_payment_method = (_normalize_optional_text(payment_method) or normalized_provider).lower()
    normalized_status = (_normalize_optional_text(status) or "pending").lower()
    normalized_idempotency_key = _normalize_optional_text(idempotency_key)

    with open_connection() as connection:
        if normalized_idempotency_key:
            existing = _get_payment_transaction_by_order_idempotency_key_in_connection(
                connection,
                order_id=order_id,
                idempotency_key=normalized_idempotency_key,
            )
            if existing is not None:
                return existing
        try:
            connection.execute(
                """
                INSERT INTO payment_transactions (
                    id, order_id, user_id, provider, payment_method, amount_cents, status,
                    provider_transaction_id, prepay_id, idempotency_key, payment_params_json,
                    failure_reason, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction_id,
                    order_id,
                    user_id,
                    normalized_provider,
                    normalized_payment_method,
                    max(0, int(amount_cents)),
                    normalized_status,
                    _normalize_optional_text(provider_transaction_id),
                    _normalize_optional_text(prepay_id),
                    normalized_idempotency_key,
                    _serialize_json_value(payment_params or {}),
                    _normalize_optional_text(failure_reason),
                    now_text,
                    now_text,
                ),
            )
        except sqlite3.IntegrityError:
            if normalized_idempotency_key:
                existing = _get_payment_transaction_by_order_idempotency_key_in_connection(
                    connection,
                    order_id=order_id,
                    idempotency_key=normalized_idempotency_key,
                )
                if existing is not None:
                    return existing
            raise

        transaction = _get_payment_transaction_in_connection(connection, transaction_id=transaction_id)
    if transaction is None:
        raise RuntimeError("payment_transaction_create_failed")
    return transaction


def get_payment_transaction(transaction_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        return _get_payment_transaction_in_connection(connection, transaction_id=transaction_id)


def get_latest_payment_transaction_for_order(order_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            """
            SELECT id, order_id, user_id, provider, payment_method, amount_cents, status,
                   provider_transaction_id, prepay_id, idempotency_key, payment_params_json,
                   notify_payload_json, failure_reason, paid_at, created_at, updated_at
            FROM payment_transactions
            WHERE order_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (order_id,),
        ).fetchone()
    return _deserialize_payment_transaction_row(row) if row is not None else None


def list_payment_transactions_for_order(order_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    with open_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, order_id, user_id, provider, payment_method, amount_cents, status,
                   provider_transaction_id, prepay_id, idempotency_key, payment_params_json,
                   notify_payload_json, failure_reason, paid_at, created_at, updated_at
            FROM payment_transactions
            WHERE order_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (order_id, normalized_limit),
        ).fetchall()
    return [_deserialize_payment_transaction_row(row) for row in rows]


def settle_payment_transaction(*, transaction_id: str, provider_transaction_id: str | None, notify_payload: dict[str, Any] | None, now_text: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    with open_connection() as connection:
        transaction = _get_payment_transaction_in_connection(connection, transaction_id=transaction_id)
        if transaction is None:
            raise RuntimeError("payment_transaction_not_found")
        order = _get_recharge_order_in_connection(connection, order_id=str(transaction["order_id"]))
        if order is None:
            raise RuntimeError("recharge_order_not_found")

        raw_order_status = str(order.get("raw_status") or order.get("status") or "").lower()
        if raw_order_status in {"approved", "rejected", "refunded", "refund_pending", "closed"}:
            raise ValueError("recharge_order_not_payable")
        existing_payment_ledger = _get_points_ledger_by_idempotency_key(
            connection,
            user_id=str(order["user_id"]),
            idempotency_key=f"recharge:payment:{order['order_id']}",
        )
        if raw_order_status in {"paid", "completed"} and existing_payment_ledger is None and order.get("granted_ledger_id"):
            raise ValueError("recharge_order_already_paid")

        ledger = existing_payment_ledger or _credit_points_in_connection(
            connection,
            user_id=str(order["user_id"]),
            points_amount=int(order["points_amount"]) + int(order["bonus_points"]),
            change_type="recharge",
            biz_type="recharge_order",
            biz_id=str(order["order_id"]),
            idempotency_key=f"recharge:payment:{order['order_id']}",
            remark=f"recharge_order:{order['package_key']}",
            now_text=now_text,
        )
        connection.execute(
            """
            UPDATE payment_transactions
            SET status = ?, provider_transaction_id = COALESCE(?, provider_transaction_id),
                notify_payload_json = ?, paid_at = COALESCE(paid_at, ?), updated_at = ?
            WHERE id = ?
            """,
            (
                "paid",
                _normalize_optional_text(provider_transaction_id),
                _serialize_json_value(notify_payload or {}),
                now_text,
                now_text,
                transaction_id,
            ),
        )
        if raw_order_status not in {"completed"}:
            connection.execute(
                """
                UPDATE recharge_orders
                SET status = ?, paid_at = COALESCE(paid_at, ?), granted_ledger_id = COALESCE(granted_ledger_id, ?), updated_at = ?
                WHERE id = ?
                """,
                ("paid", now_text, ledger["ledger_id"], now_text, str(order["order_id"])),
            )
        refreshed_transaction = _get_payment_transaction_in_connection(connection, transaction_id=transaction_id)
        refreshed_order = _get_recharge_order_in_connection(connection, order_id=str(order["order_id"]))
    if refreshed_transaction is None or refreshed_order is None:
        raise RuntimeError("payment_transaction_settle_failed")
    return refreshed_transaction, refreshed_order, ledger


def complete_recharge_order_manually(
    *,
    order_id: str,
    payment_method: str | None,
    payment_reference: str | None,
    operator_note: str | None,
    operator: str | None,
    now_text: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    normalized_payment_method = _normalize_optional_text(payment_method)
    normalized_payment_reference = _normalize_optional_text(payment_reference)
    normalized_operator_note = _normalize_optional_text(operator_note)
    normalized_operator = _normalize_optional_text(operator)
    idempotency_key = f"recharge:manual_complete:{order_id}"

    with open_connection() as connection:
        order = _get_recharge_order_in_connection(connection, order_id=order_id)
        if order is None:
            raise RuntimeError("recharge_order_not_found")

        current_status = str(order.get("raw_status") or order.get("status") or "").lower()
        existing_ledger = _get_points_ledger_by_idempotency_key(
            connection,
            user_id=str(order["user_id"]),
            idempotency_key=idempotency_key,
        )
        if current_status == "completed":
            if existing_ledger is not None:
                return order, existing_ledger
            raise ValueError("recharge_order_already_completed")
        if current_status not in {"pending", "unpaid"}:
            raise ValueError("recharge_order_not_manual_completable")

        before_order = dict(order)
        ledger = existing_ledger or _credit_points_in_connection(
            connection,
            user_id=str(order["user_id"]),
            points_amount=int(order["points_amount"]) + int(order["bonus_points"]),
            change_type="recharge",
            biz_type="recharge_order",
            biz_id=order_id,
            idempotency_key=idempotency_key,
            remark=f"recharge_order:{order['package_key']}:manual_complete",
            now_text=now_text,
        )
        connection.execute(
            """
            UPDATE recharge_orders
            SET status = ?,
                external_order_id = COALESCE(external_order_id, ?),
                review_note = COALESCE(?, review_note),
                reviewed_by = COALESCE(reviewed_by, ?),
                reviewed_at = COALESCE(reviewed_at, ?),
                paid_at = COALESCE(paid_at, ?),
                completed_at = COALESCE(completed_at, ?),
                granted_ledger_id = COALESCE(granted_ledger_id, ?),
                updated_at = ?
            WHERE id = ?
            """,
            (
                "completed",
                normalized_payment_reference,
                normalized_operator_note,
                normalized_operator,
                now_text,
                now_text,
                now_text,
                ledger["ledger_id"],
                now_text,
                order_id,
            ),
        )
        refreshed_order = _get_recharge_order_in_connection(connection, order_id=order_id)
        if refreshed_order is None:
            raise RuntimeError("recharge_order_manual_complete_failed")
        _insert_admin_operation_log(
            connection,
            operator=normalized_operator,
            action="recharge_order_manual_complete",
            target_type="recharge_order",
            target_id=order_id,
            reason="offline_payment_confirmed",
            operator_note=normalized_operator_note,
            before=before_order,
            after={
                **refreshed_order,
                "manual_payment_method": normalized_payment_method,
                "manual_payment_reference": normalized_payment_reference,
                "granted_ledger_id": ledger["ledger_id"],
            },
            created_at=now_text,
        )
    return refreshed_order, ledger


def get_dashboard_summary(*, date_from: str | None = None, date_to: str | None = None, channel: str | None = None) -> dict[str, Any]:
    with open_connection() as connection:
        now_text = _utc_now_text()
        total_users = int(connection.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"])
        today_new_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE date(datetime(created_at), '+8 hours') = date('now', '+8 hours')").fetchone()["total"])
        yesterday_new_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE date(datetime(created_at), '+8 hours') = date('now', '+8 hours', '-1 day')").fetchone()["total"])
        week_new_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE datetime(created_at, '+8 hours') >= date('now', '+8 hours', 'weekday 1', '-7 days')").fetchone()["total"])
        last_week_new_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE datetime(created_at, '+8 hours') >= date('now', '+8 hours', 'weekday 1', '-14 days') AND datetime(created_at, '+8 hours') < date('now', '+8 hours', 'weekday 1', '-7 days')").fetchone()["total"])
        month_new_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE strftime('%Y-%m', datetime(created_at), '+8 hours') = strftime('%Y-%m', 'now', '+8 hours')").fetchone()["total"])
        last_month_new_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE strftime('%Y-%m', datetime(created_at), '+8 hours') = strftime('%Y-%m', 'now', '+8 hours', '-1 month')").fetchone()["total"])
        daily_active_users = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE date(datetime(last_active_at), '+8 hours') = date('now', '+8 hours')").fetchone()["total"])
        active_users_7d = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE datetime(last_active_at) >= datetime('now', '-7 day')").fetchone()["total"])
        active_users_30d = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE datetime(last_active_at) >= datetime('now', '-30 day')").fetchone()["total"])
        normal_promoters = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE identity_level IN ('promoter', 'promotion_ambassador')").fetchone()["total"])
        vip_promoters = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE identity_level IN ('vip_promoter', 'vip_promotion_ambassador', 'senior_promoter', 'senior_promotion_ambassador')").fetchone()["total"])
        svip_promoters = int(connection.execute("SELECT COUNT(*) AS total FROM users WHERE identity_level IN ('svip_promoter', 'svip_promotion_ambassador')").fetchone()["total"])
        total_promoters = normal_promoters + vip_promoters + svip_promoters
        total_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders").fetchone()["total"])
        today_paid_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND date(COALESCE(paid_at, reviewed_at, created_at)) = date('now')").fetchone()["total"])
        today_paid_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND date(COALESCE(paid_at, reviewed_at, created_at)) = date('now')").fetchone()["total"])
        yesterday_paid_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND date(COALESCE(paid_at, reviewed_at, created_at)) = date('now', '-1 day')").fetchone()["total"])
        month_paid_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND strftime('%Y-%m', COALESCE(paid_at, reviewed_at, created_at)) = strftime('%Y-%m', 'now')").fetchone()["total"])
        last_month_paid_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND strftime('%Y-%m', COALESCE(paid_at, reviewed_at, created_at)) = strftime('%Y-%m', 'now', '-1 month')").fetchone()["total"])
        year_paid_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND strftime('%Y', COALESCE(paid_at, reviewed_at, created_at)) = strftime('%Y', 'now')").fetchone()["total"])
        last_year_paid_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed') AND strftime('%Y', COALESCE(paid_at, reviewed_at, created_at)) = strftime('%Y', 'now', '-1 year')").fetchone()["total"])
        pending_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status IN ('pending', 'unpaid')").fetchone()["total"])
        paid_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status IN ('approved', 'paid')").fetchone()["total"])
        completed_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status = 'completed'").fetchone()["total"])
        refund_pending_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status = 'refund_pending'").fetchone()["total"])
        refunded_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status IN ('rejected', 'refunded')").fetchone()["total"])
        closed_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status = 'closed'").fetchone()["total"])
        refund_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('rejected', 'refunded')").fetchone()["total"])
        users_with_points = int(connection.execute("SELECT COUNT(*) AS total FROM points_accounts WHERE balance > 0").fetchone()["total"])
        total_points_balance = int(connection.execute("SELECT COALESCE(SUM(balance), 0) AS total FROM points_accounts").fetchone()["total"])
        total_recharge_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed')").fetchone()["total"])
        total_approved_orders = int(connection.execute("SELECT COUNT(*) AS total FROM recharge_orders WHERE status IN ('approved', 'paid', 'completed')").fetchone()["total"])
        total_commission_amount_cents = int(connection.execute("SELECT COALESCE(SUM(commission_points), 0) AS total FROM promotion_commissions WHERE status IN ('pending', 'settled')").fetchone()["total"])
        total_withdraw_amount_cents = int(connection.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM promotion_withdrawals WHERE status IN ('paid', 'paying')").fetchone()["total"])
        pending_applications = int(connection.execute("SELECT COUNT(*) AS total FROM promotion_applications WHERE status = 'pending'").fetchone()["total"])
        pending_withdrawals = int(connection.execute("SELECT COUNT(*) AS total FROM promotion_withdrawals WHERE status = 'pending'").fetchone()["total"])
        payout_failed_withdrawals = int(connection.execute("SELECT COUNT(*) AS total FROM promotion_withdrawals WHERE status = 'payout_failed'").fetchone()["total"])
        total_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records").fetchone()["total"])
        today_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE date(datetime(created_at), '+8 hours') = date('now', '+8 hours')").fetchone()["total"])
        yesterday_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE date(datetime(created_at), '+8 hours') = date('now', '+8 hours', '-1 day')").fetchone()["total"])
        week_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE datetime(created_at, '+8 hours') >= date('now', '+8 hours', 'weekday 1', '-7 days')").fetchone()["total"])
        month_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE strftime('%Y-%m', datetime(created_at), '+8 hours') = strftime('%Y-%m', 'now', '+8 hours')").fetchone()["total"])
        phone_review_base_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE scene = 'phone_review_base'").fetchone()["total"])
        phone_review_unlock_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE scene = 'phone_review_aspect_unlock'").fetchone()["total"])
        phone_review_usage_records = phone_review_base_usage_records + phone_review_unlock_usage_records
        agent_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE scene = 'agent_reply'").fetchone()["total"])
        almanac_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE scene = 'almanac_query'").fetchone()["total"])
        five_elements_usage_records = int(connection.execute("SELECT COUNT(*) AS total FROM usage_records WHERE scene = 'five_elements_query'").fetchone()["total"])
        feature_scene_labels = {
            "phone_review_base": "手机号评测",
            "phone_review_aspect_unlock": "维度解锁",
            "agent_reply": "智能体玄学技能",
            "almanac_query": "黄历查询",
            "five_elements_query": "五行属性查询",
        }
        feature_usage_window_metrics: list[dict[str, Any]] = []
        feature_usage_window_conditions = [
            ("今日使用", "date(datetime(created_at), '+8 hours') = date('now', '+8 hours')"),
            ("昨日使用", "date(datetime(created_at), '+8 hours') = date('now', '+8 hours', '-1 day')"),
            ("本周使用", "datetime(created_at, '+8 hours') >= date('now', '+8 hours', 'weekday 1', '-7 days')"),
            ("本月使用", "strftime('%Y-%m', datetime(created_at), '+8 hours') = strftime('%Y-%m', 'now', '+8 hours')"),
        ]
        for window_label, window_condition in feature_usage_window_conditions:
            rows = connection.execute(
                f"""
                SELECT scene, COUNT(*) AS total
                FROM usage_records
                WHERE {window_condition}
                GROUP BY scene
                ORDER BY total DESC, scene ASC
                LIMIT 5
                """
            ).fetchall()
            for row in rows:
                scene = str(row["scene"] or "unknown")
                count = int(row["total"])
                feature_name = feature_scene_labels.get(scene, scene)
                feature_usage_window_metrics.append(
                    {
                        "label": f"{window_label}·{feature_name}",
                        "value": count,
                        "display_value": str(count),
                        "unit": "条",
                    }
                )
        llm_enabled_keys = int(connection.execute("SELECT COUNT(*) AS total FROM llm_api_keys WHERE enabled = 1").fetchone()["total"])
        llm_total_keys = int(connection.execute("SELECT COUNT(*) AS total FROM llm_api_keys").fetchone()["total"])

    revenue_block = {
        "yesterday_amount_cents": yesterday_paid_amount_cents,
        "current_month_amount_cents": month_paid_amount_cents,
        "last_month_amount_cents": last_month_paid_amount_cents,
        "current_year_amount_cents": year_paid_amount_cents,
        "last_year_amount_cents": last_year_paid_amount_cents,
        "total_amount_cents": total_recharge_amount_cents,
        "commission_amount_cents": total_commission_amount_cents,
        "commission_points": total_commission_amount_cents,
        "withdrawn_amount_cents": total_withdraw_amount_cents,
        "net_revenue_cents": max(0, total_recharge_amount_cents - total_withdraw_amount_cents),
        "refund_amount_cents": refund_amount_cents,
    }
    users_block = {
        "total_users": total_users,
        "today_new_users": today_new_users,
        "yesterday_new_users": yesterday_new_users,
        "week_new_users": week_new_users,
        "last_week_new_users": last_week_new_users,
        "month_new_users": month_new_users,
        "last_month_new_users": last_month_new_users,
        "daily_active_users": daily_active_users,
        "active_users_7d": active_users_7d,
        "active_users_30d": active_users_30d,
        "monthly_active_users": active_users_30d,
        "promoter_count": total_promoters,
        "normal_promoter_count": normal_promoters,
        "vip_promoter_count": vip_promoters,
        "svip_promoter_count": svip_promoters,
        "senior_promoter_count": vip_promoters,
        "users_with_points": users_with_points,
        "total_points_balance": total_points_balance,
    }
    orders_block = {
        "total_orders": total_orders,
        "today_paid_orders": today_paid_orders,
        "today_paid_amount_cents": today_paid_amount_cents,
        "unpaid_orders": pending_orders,
        "paid_orders": paid_orders,
        "completed_orders": completed_orders,
        "refund_pending_orders": refund_pending_orders,
        "refunded_orders": refunded_orders,
        "closed_orders": closed_orders,
    }
    promotion_block = {
        "promoter_count": total_promoters,
        "normal_promoter_count": normal_promoters,
        "vip_promoter_count": vip_promoters,
        "svip_promoter_count": svip_promoters,
        "senior_promoter_count": vip_promoters,
        "pending_applications": pending_applications,
        "pending_withdrawals": pending_withdrawals,
        "payout_failed_withdrawals": payout_failed_withdrawals,
        "commission_amount_cents": total_commission_amount_cents,
        "commission_points": total_commission_amount_cents,
        "withdrawn_amount_cents": total_withdraw_amount_cents,
    }

    dashboard = {
        "generated_at": now_text,
        "revenue": revenue_block,
        "users": users_block,
        "orders": orders_block,
        "promotion": promotion_block,
        "sections": [
            {
                "title": "收益",
                "summary": "围绕支付、返佣、提现和退款构成核心经营口径",
                "metrics": [
                    {"label": "累计支付", "value": total_recharge_amount_cents, "display_value": _format_money_cents(total_recharge_amount_cents), "unit": "元"},
                    {"label": "昨日收益", "value": yesterday_paid_amount_cents, "display_value": _format_money_cents(yesterday_paid_amount_cents), "unit": "元"},
                    {"label": "本月收益", "value": month_paid_amount_cents, "display_value": _format_money_cents(month_paid_amount_cents), "unit": "元"},
                    {"label": "上月收益", "value": last_month_paid_amount_cents, "display_value": _format_money_cents(last_month_paid_amount_cents), "unit": "元"},
                    {"label": "本年度收益", "value": year_paid_amount_cents, "display_value": _format_money_cents(year_paid_amount_cents), "unit": "元"},
                    {"label": "上年度收益", "value": last_year_paid_amount_cents, "display_value": _format_money_cents(last_year_paid_amount_cents), "unit": "元"},
                    {"label": "累计总收益", "value": total_recharge_amount_cents, "display_value": _format_money_cents(total_recharge_amount_cents), "unit": "元"},
                    {"label": "今日支付", "value": today_paid_amount_cents, "display_value": _format_money_cents(today_paid_amount_cents), "unit": "元"},
                    {"label": "已完成订单", "value": total_approved_orders, "display_value": str(total_approved_orders), "unit": "单"},
                    {"label": "已产生返佣金额", "value": total_commission_amount_cents, "display_value": _format_money_cents(total_commission_amount_cents), "unit": "元"},
                    {"label": "已提现金额", "value": total_withdraw_amount_cents, "display_value": _format_money_cents(total_withdraw_amount_cents), "unit": "元"},
                    {"label": "净收益", "value": revenue_block["net_revenue_cents"], "display_value": _format_money_cents(revenue_block["net_revenue_cents"]), "unit": "元"},
                    {"label": "退款金额", "value": refund_amount_cents, "display_value": _format_money_cents(refund_amount_cents), "unit": "元"},
                ],
            },
            {
                "title": "用户",
                "summary": "查看总用户、活跃用户、推广用户和积分概况",
                "metrics": [
                    {"label": "总用户", "value": total_users, "display_value": str(total_users), "unit": "人"},
                    {"label": "今日新增", "value": today_new_users, "display_value": str(today_new_users), "unit": "人"},
                    {"label": "昨日新增", "value": yesterday_new_users, "display_value": str(yesterday_new_users), "unit": "人"},
                    {"label": "本周新增", "value": week_new_users, "display_value": str(week_new_users), "unit": "人"},
                    {"label": "上周新增", "value": last_week_new_users, "display_value": str(last_week_new_users), "unit": "人"},
                    {"label": "本月新增", "value": month_new_users, "display_value": str(month_new_users), "unit": "人"},
                    {"label": "上月新增", "value": last_month_new_users, "display_value": str(last_month_new_users), "unit": "人"},
                    {"label": "日活", "value": daily_active_users, "display_value": str(daily_active_users), "unit": "人"},
                    {"label": "7日活跃", "value": active_users_7d, "display_value": str(active_users_7d), "unit": "人"},
                    {"label": "月活", "value": active_users_30d, "display_value": str(active_users_30d), "unit": "人"},
                    {"label": "30日活跃", "value": active_users_30d, "display_value": str(active_users_30d), "unit": "人"},
                    {"label": "推广用户", "value": total_promoters, "display_value": str(total_promoters), "unit": "人"},
                    {"label": "推广大使", "value": normal_promoters, "display_value": str(normal_promoters), "unit": "人"},
                    {"label": "VIP 推广大使", "value": vip_promoters, "display_value": str(vip_promoters), "unit": "人"},
                    {"label": "SVIP 推广大使", "value": svip_promoters, "display_value": str(svip_promoters), "unit": "人"},
                    {"label": "有积分用户", "value": users_with_points, "display_value": str(users_with_points), "unit": "人"},
                    {"label": "积分余额", "value": total_points_balance, "display_value": str(total_points_balance), "unit": "积分"},
                ],
            },
            {
                "title": "订单",
                "summary": "订单状态、支付量与退款情况的概览",
                "metrics": [
                    {"label": "订单总数", "value": total_orders, "display_value": str(total_orders), "unit": "单"},
                    {"label": "总订单数量", "value": total_orders, "display_value": str(total_orders), "unit": "单"},
                    {"label": "今日支付", "value": today_paid_orders, "display_value": str(today_paid_orders), "unit": "单"},
                    {"label": "待支付", "value": pending_orders, "display_value": str(pending_orders), "unit": "单"},
                    {"label": "待完成订单", "value": paid_orders, "display_value": str(paid_orders), "unit": "单"},
                    {"label": "退款中", "value": refund_pending_orders, "display_value": str(refund_pending_orders), "unit": "单"},
                    {"label": "已退款", "value": refunded_orders, "display_value": str(refunded_orders), "unit": "单"},
                    {"label": "已关闭", "value": closed_orders, "display_value": str(closed_orders), "unit": "单"},
                ],
            },
            {
                "title": "推广合作",
                "summary": "申请、提现和返佣记录的可见状态",
                "metrics": [
                    {"label": "推广大使", "value": normal_promoters, "display_value": str(normal_promoters), "unit": "人"},
                    {"label": "VIP 推广大使", "value": vip_promoters, "display_value": str(vip_promoters), "unit": "人"},
                    {"label": "SVIP 推广大使", "value": svip_promoters, "display_value": str(svip_promoters), "unit": "人"},
                    {"label": "待审核申请", "value": pending_applications, "display_value": str(pending_applications), "unit": "条"},
                    {"label": "待提现申请", "value": pending_withdrawals, "display_value": str(pending_withdrawals), "unit": "笔"},
                    {"label": "打款失败", "value": payout_failed_withdrawals, "display_value": str(payout_failed_withdrawals), "unit": "笔"},
                ],
            },
            {
                "title": "功能使用",
                "summary": "功能调用按自然日、自然周、自然月和功能类型排名统计",
                "metrics": [
                    {"label": "使用记录", "value": total_usage_records, "display_value": str(total_usage_records), "unit": "条"},
                    {"label": "今日使用", "value": today_usage_records, "display_value": str(today_usage_records), "unit": "条"},
                    {"label": "昨日使用", "value": yesterday_usage_records, "display_value": str(yesterday_usage_records), "unit": "条"},
                    {"label": "本周使用", "value": week_usage_records, "display_value": str(week_usage_records), "unit": "条"},
                    {"label": "本月使用", "value": month_usage_records, "display_value": str(month_usage_records), "unit": "条"},
                    {"label": "手机号评测", "value": phone_review_base_usage_records, "display_value": str(phone_review_base_usage_records), "unit": "条"},
                    {"label": "维度解锁", "value": phone_review_unlock_usage_records, "display_value": str(phone_review_unlock_usage_records), "unit": "条"},
                    {"label": "智能体", "value": agent_usage_records, "display_value": str(agent_usage_records), "unit": "条"},
                    {"label": "黄历查询", "value": almanac_usage_records, "display_value": str(almanac_usage_records), "unit": "条"},
                    {"label": "五行查询", "value": five_elements_usage_records, "display_value": str(five_elements_usage_records), "unit": "条"},
                    *feature_usage_window_metrics,
                    {"label": "启用密钥", "value": llm_enabled_keys, "display_value": str(llm_enabled_keys), "unit": "个"},
                    {"label": "密钥总数", "value": llm_total_keys, "display_value": str(llm_total_keys), "unit": "个"},
                ],
            },
        ],
    }

    return dashboard


def create_refund_request(*, order_id: str, reason: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    with open_connection() as connection:
        order = _get_recharge_order_in_connection(connection, order_id=order_id)
        if order is None:
            raise RuntimeError("recharge_order_not_found")
        if str(order["status"]) not in {"paid", "completed"}:
            raise ValueError("order_not_refundable")
        existing = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE order_id = ? AND status IN ('pending', 'approved', 'processing') ORDER BY created_at DESC LIMIT 1",
            (order_id,),
        ).fetchone()
        if existing is not None:
            return _deserialize_refund_request_row(existing)
        refund_id = uuid4().hex
        connection.execute(
            "INSERT INTO refund_requests (id, order_id, user_id, status, reason, operator_note, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (refund_id, order_id, str(order["user_id"]), "pending", _normalize_optional_text(reason), _normalize_optional_text(operator_note), now_text, now_text),
        )
        connection.execute("UPDATE recharge_orders SET status = ?, updated_at = ? WHERE id = ?", ("refund_pending", now_text, order_id))
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action="refund_create",
            target_type="refund",
            target_id=refund_id,
            reason=reason,
            operator_note=operator_note,
            before={"order_status": order.get("status")},
            after={"order_status": "refund_pending", "refund_status": "pending"},
            created_at=now_text,
        )
        row = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE id = ?",
            (refund_id,),
        ).fetchone()
    if row is None:
        raise RuntimeError("refund_request_create_failed")
    return _deserialize_refund_request_row(row)


def review_refund_request(*, refund_id: str, action: str, reject_reason: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    normalized_action = action.strip().lower()
    if normalized_action not in {"approve", "reject"}:
        raise ValueError("invalid_refund_review_action")
    if normalized_action == "reject" and not _normalize_optional_text(reject_reason):
        raise ValueError("reject_reason_required")
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE id = ?",
            (refund_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError("refund_request_not_found")
        current = _deserialize_refund_request_row(row)
        if str(current["status"]) not in {"pending", "processing"}:
            raise ValueError("refund_request_already_reviewed")
        next_status = "approved" if normalized_action == "approve" else "rejected"
        order_status = "refunded" if normalized_action == "approve" else "paid"
        connection.execute(
            "UPDATE refund_requests SET status = ?, reject_reason = ?, operator_note = COALESCE(?, operator_note), reviewed_by = ?, reviewed_at = ?, updated_at = ? WHERE id = ?",
            (next_status, _normalize_optional_text(reject_reason), _normalize_optional_text(operator_note), operator, now_text, now_text, refund_id),
        )
        connection.execute("UPDATE recharge_orders SET status = ?, updated_at = ? WHERE id = ?", (_storage_recharge_order_status(order_status), now_text, str(current["order_id"])))
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action=f"refund_{normalized_action}",
            target_type="refund",
            target_id=refund_id,
            reason=reject_reason,
            operator_note=operator_note,
            before={"refund_status": current["status"]},
            after={"refund_status": next_status, "order_status": order_status},
            created_at=now_text,
        )
        refreshed = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE id = ?",
            (refund_id,),
        ).fetchone()
    if refreshed is None:
        raise RuntimeError("refund_request_review_failed")
    return _deserialize_refund_request_row(refreshed)


def retry_refund_request(*, refund_id: str, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE id = ?",
            (refund_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError("refund_request_not_found")
        current = _deserialize_refund_request_row(row)
        connection.execute(
            "UPDATE refund_requests SET status = ?, retry_count = retry_count + 1, operator_note = COALESCE(?, operator_note), failure_reason = NULL, updated_at = ? WHERE id = ?",
            ("processing", _normalize_optional_text(operator_note), now_text, refund_id),
        )
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action="refund_retry",
            target_type="refund",
            target_id=refund_id,
            reason=None,
            operator_note=operator_note,
            before={"refund_status": current["status"]},
            after={"refund_status": "processing"},
            created_at=now_text,
        )
        refreshed = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE id = ?",
            (refund_id,),
        ).fetchone()
    if refreshed is None:
        raise RuntimeError("refund_request_retry_failed")
    return _deserialize_refund_request_row(refreshed)


def list_recent_recharge_orders_for_user(*, user_id: str, limit: int = 5) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 20))
    with open_connection() as connection:
        rows = connection.execute(
            "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.paid_at, r.completed_at, r.closed_at, r.granted_ledger_id, r.created_at, r.updated_at "
            "FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id "
            "WHERE r.user_id = ? ORDER BY r.created_at DESC, r.id DESC LIMIT ?",
            (user_id, normalized_limit),
        ).fetchall()
    return [_deserialize_recharge_order_row(row) for row in rows]


def list_promotion_applications(*, limit: int = 20, status: str | None = None, user_id: str | None = None, keyword: str | None = None) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(status):
        conditions.append("pa.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(user_id):
        conditions.append("pa.user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(keyword):
        like_value = f"%{str(keyword).strip()}%"
        conditions.append("(pa.id LIKE ? OR pa.user_id LIKE ? OR IFNULL(up.nickname, '') LIKE ? OR IFNULL(pa.applicant_name, '') LIKE ? OR IFNULL(pa.applicant_phone, '') LIKE ?)")
        parameters.extend([like_value, like_value, like_value, like_value, like_value])
    sql = (
        "SELECT pa.id, pa.user_id, up.nickname AS user_nickname, u.identity_level AS current_identity_level, pa.requested_level, pa.status, pa.applicant_name, pa.applicant_phone, pa.reject_reason, pa.review_note, pa.reviewed_by, pa.reviewed_at, pa.created_at, pa.updated_at "
        "FROM promotion_applications pa JOIN users u ON u.id = pa.user_id LEFT JOIN user_profiles up ON up.user_id = pa.user_id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY pa.created_at DESC, pa.id DESC LIMIT ?"
    parameters.append(normalized_limit)
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_promotion_application_row(row) for row in rows]


def get_promotion_application(application_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT pa.id, pa.user_id, up.nickname AS user_nickname, u.identity_level AS current_identity_level, pa.requested_level, pa.status, pa.applicant_name, pa.applicant_phone, pa.reject_reason, pa.review_note, pa.reviewed_by, pa.reviewed_at, pa.created_at, pa.updated_at "
            "FROM promotion_applications pa JOIN users u ON u.id = pa.user_id LEFT JOIN user_profiles up ON up.user_id = pa.user_id WHERE pa.id = ?",
            (application_id,),
        ).fetchone()
    return _deserialize_promotion_application_row(row) if row is not None else None


def review_promotion_application(*, application_id: str, action: str, reject_reason: str | None, review_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    normalized_action = action.strip().lower()
    if normalized_action not in {"approve", "reject"}:
        raise ValueError("invalid_promotion_review_action")
    if normalized_action == "reject" and not _normalize_optional_text(reject_reason):
        raise ValueError("reject_reason_required")
    with open_connection() as connection:
        row = connection.execute("SELECT id, user_id, requested_level, status FROM promotion_applications WHERE id = ?", (application_id,)).fetchone()
        if row is None:
            raise RuntimeError("promotion_application_not_found")
        if str(row["status"]) != "pending":
            raise ValueError("promotion_application_already_reviewed")
        next_status = "approved" if normalized_action == "approve" else "rejected"
        connection.execute(
            "UPDATE promotion_applications SET status = ?, reject_reason = ?, review_note = ?, reviewed_by = ?, reviewed_at = ?, updated_at = ? WHERE id = ?",
            (next_status, _normalize_optional_text(reject_reason), _normalize_optional_text(review_note), operator, now_text, now_text, application_id),
        )
        if normalized_action == "approve":
            approved_identity = _normalize_user_identity_for_storage(str(row["requested_level"]))
            connection.execute(
                "UPDATE users SET identity_level = ?, updated_at = ? WHERE id = ?",
                (approved_identity, now_text, str(row["user_id"])),
            )
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action=f"promotion_application_{normalized_action}",
            target_type="promotion_application",
            target_id=application_id,
            reason=reject_reason,
            operator_note=review_note,
            before={"status": row["status"]},
            after={"status": next_status, "identity_level": _normalize_user_identity_for_output(row["requested_level"]) if normalized_action == "approve" else None},
            created_at=now_text,
        )
    refreshed = get_promotion_application(application_id)
    if refreshed is None:
        raise RuntimeError("promotion_application_review_failed")
    return refreshed


def list_promotion_commissions(*, limit: int = 20, user_id: str | None = None, promoter_user_id: str | None = None, order_id: str | None = None, status: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(promoter_user_id) or _normalize_optional_text(user_id):
        conditions.append("pc.promoter_user_id = ?")
        parameters.append(str(promoter_user_id or user_id))
    if _normalize_optional_text(order_id):
        conditions.append("pc.order_id = ?")
        parameters.append(str(order_id))
    if _normalize_optional_text(status):
        conditions.append("pc.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(date_from):
        conditions.append("pc.created_at >= ?")
        parameters.append(str(date_from))
    if _normalize_optional_text(date_to):
        conditions.append("pc.created_at <= ?")
        parameters.append(str(date_to))
    sql = (
        "SELECT pc.id, pc.promoter_user_id, promoter_profile.nickname AS promoter_nickname, pc.invited_user_id, invited_profile.nickname AS invited_user_nickname, pc.order_id, pc.order_amount_cents, pc.commission_rate, pc.commission_points, pc.commission_type, pc.status, pc.remark, pc.created_at, pc.updated_at, pc.settled_at, pc.revoked_at "
        "FROM promotion_commissions pc "
        "LEFT JOIN user_profiles promoter_profile ON promoter_profile.user_id = pc.promoter_user_id "
        "LEFT JOIN user_profiles invited_profile ON invited_profile.user_id = pc.invited_user_id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY pc.created_at DESC, pc.id DESC LIMIT ?"
    parameters.append(normalized_limit)
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_promotion_commission_row(row) for row in rows]


def get_promotion_commission(commission_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT pc.id, pc.promoter_user_id, promoter_profile.nickname AS promoter_nickname, pc.invited_user_id, invited_profile.nickname AS invited_user_nickname, pc.order_id, pc.order_amount_cents, pc.commission_rate, pc.commission_points, pc.commission_type, pc.status, pc.remark, pc.created_at, pc.updated_at, pc.settled_at, pc.revoked_at "
            "FROM promotion_commissions pc "
            "LEFT JOIN user_profiles promoter_profile ON promoter_profile.user_id = pc.promoter_user_id "
            "LEFT JOIN user_profiles invited_profile ON invited_profile.user_id = pc.invited_user_id WHERE pc.id = ?",
            (commission_id,),
        ).fetchone()
    return _deserialize_promotion_commission_row(row) if row is not None else None


def list_promotion_withdrawals(*, limit: int = 20, user_id: str | None = None, status: str | None = None, keyword: str | None = None) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 100))
    conditions: list[str] = []
    parameters: list[Any] = []
    if _normalize_optional_text(user_id):
        conditions.append("pw.user_id = ?")
        parameters.append(str(user_id))
    if _normalize_optional_text(status):
        conditions.append("pw.status = ?")
        parameters.append(str(status))
    if _normalize_optional_text(keyword):
        like_value = f"%{str(keyword).strip()}%"
        conditions.append("(pw.id LIKE ? OR pw.user_id LIKE ? OR IFNULL(up.nickname, '') LIKE ?)")
        parameters.extend([like_value, like_value, like_value])
    sql = (
        "SELECT pw.id, pw.user_id, up.nickname AS user_nickname, u.identity_level, pw.status, pw.points_used, pw.amount_cents, pw.rebate_points_balance_snapshot, pw.cash_rate_snapshot, pw.reject_reason, pw.review_note, pw.payout_method, pw.payout_proof, pw.payout_failure_reason, pw.reviewed_by, pw.reviewed_at, pw.paid_at, pw.created_at, pw.updated_at "
        "FROM promotion_withdrawals pw JOIN users u ON u.id = pw.user_id LEFT JOIN user_profiles up ON up.user_id = pw.user_id"
    )
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY pw.created_at DESC, pw.id DESC LIMIT ?"
    parameters.append(normalized_limit)
    with open_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [_deserialize_promotion_withdrawal_row(row) for row in rows]


def get_promotion_withdrawal(withdrawal_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT pw.id, pw.user_id, up.nickname AS user_nickname, u.identity_level, pw.status, pw.points_used, pw.amount_cents, pw.rebate_points_balance_snapshot, pw.cash_rate_snapshot, pw.reject_reason, pw.review_note, pw.payout_method, pw.payout_proof, pw.payout_failure_reason, pw.reviewed_by, pw.reviewed_at, pw.paid_at, pw.created_at, pw.updated_at "
            "FROM promotion_withdrawals pw JOIN users u ON u.id = pw.user_id LEFT JOIN user_profiles up ON up.user_id = pw.user_id WHERE pw.id = ?",
            (withdrawal_id,),
        ).fetchone()
    return _deserialize_promotion_withdrawal_row(row) if row is not None else None


def review_promotion_withdrawal(*, withdrawal_id: str, action: str, reject_reason: str | None, review_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    normalized_action = action.strip().lower()
    if normalized_action not in {"approve", "reject"}:
        raise ValueError("invalid_withdrawal_review_action")
    if normalized_action == "reject" and not _normalize_optional_text(reject_reason):
        raise ValueError("reject_reason_required")
    with open_connection() as connection:
        row = connection.execute("SELECT id, status FROM promotion_withdrawals WHERE id = ?", (withdrawal_id,)).fetchone()
        if row is None:
            raise RuntimeError("promotion_withdrawal_not_found")
        if str(row["status"]) != "pending":
            raise ValueError("promotion_withdrawal_already_reviewed")
        next_status = "paying" if normalized_action == "approve" else "rejected"
        connection.execute(
            "UPDATE promotion_withdrawals SET status = ?, reject_reason = ?, review_note = ?, reviewed_by = ?, reviewed_at = ?, updated_at = ? WHERE id = ?",
            (next_status, _normalize_optional_text(reject_reason), _normalize_optional_text(review_note), operator, now_text, now_text, withdrawal_id),
        )
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action=f"promotion_withdrawal_{normalized_action}",
            target_type="promotion_withdrawal",
            target_id=withdrawal_id,
            reason=reject_reason,
            operator_note=review_note,
            before={"status": row["status"]},
            after={"status": next_status},
            created_at=now_text,
        )
    refreshed = get_promotion_withdrawal(withdrawal_id)
    if refreshed is None:
        raise RuntimeError("promotion_withdrawal_review_failed")
    return refreshed


def retry_promotion_withdrawal_payout(*, withdrawal_id: str, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    return _update_promotion_withdrawal_payout_status(
        withdrawal_id=withdrawal_id,
        status="paying",
        payout_method=None,
        payout_proof=None,
        payout_failure_reason=None,
        operator_note=operator_note,
        operator=operator,
        action="promotion_withdrawal_retry_payout",
        now_text=now_text,
    )


def mark_promotion_withdrawal_paid(*, withdrawal_id: str, payout_method: str | None, payout_proof: str | None, operator_note: str | None, operator: str | None, now_text: str) -> dict[str, Any]:
    return _update_promotion_withdrawal_payout_status(
        withdrawal_id=withdrawal_id,
        status="paid",
        payout_method=payout_method,
        payout_proof=payout_proof,
        payout_failure_reason=None,
        operator_note=operator_note,
        operator=operator,
        action="promotion_withdrawal_mark_paid",
        now_text=now_text,
    )


def _update_promotion_withdrawal_payout_status(
    *,
    withdrawal_id: str,
    status: str,
    payout_method: str | None,
    payout_proof: str | None,
    payout_failure_reason: str | None,
    operator_note: str | None,
    operator: str | None,
    action: str,
    now_text: str,
) -> dict[str, Any]:
    with open_connection() as connection:
        row = connection.execute("SELECT id, status FROM promotion_withdrawals WHERE id = ?", (withdrawal_id,)).fetchone()
        if row is None:
            raise RuntimeError("promotion_withdrawal_not_found")
        paid_at_expr = now_text if status == "paid" else None
        connection.execute(
            "UPDATE promotion_withdrawals SET status = ?, payout_method = COALESCE(?, payout_method), payout_proof = COALESCE(?, payout_proof), payout_failure_reason = ?, paid_at = COALESCE(?, paid_at), review_note = COALESCE(?, review_note), updated_at = ? WHERE id = ?",
            (status, _normalize_optional_text(payout_method), _normalize_optional_text(payout_proof), _normalize_optional_text(payout_failure_reason), paid_at_expr, _normalize_optional_text(operator_note), now_text, withdrawal_id),
        )
        _insert_admin_operation_log(
            connection,
            operator=operator,
            action=action,
            target_type="promotion_withdrawal",
            target_id=withdrawal_id,
            reason=None,
            operator_note=operator_note,
            before={"status": row["status"]},
            after={"status": status},
            created_at=now_text,
        )
    refreshed = get_promotion_withdrawal(withdrawal_id)
    if refreshed is None:
        raise RuntimeError("promotion_withdrawal_update_failed")
    return refreshed


def list_refund_requests_for_order(order_id: str) -> list[dict[str, Any]]:
    with open_connection() as connection:
        rows = connection.execute(
            "SELECT id, order_id, user_id, status, reason, operator_note, reject_reason, reviewed_by, reviewed_at, retry_count, failure_reason, created_at, updated_at FROM refund_requests WHERE order_id = ? ORDER BY created_at DESC, id DESC",
            (order_id,),
        ).fetchall()
    return [_deserialize_refund_request_row(row) for row in rows]


def get_promotion_rules() -> dict[str, Any]:
    entries = list_runtime_config_entries(scope_type="global", scope_key="default")
    values = {str(entry["config_key"]): entry.get("value") for entry in entries}
    return {
        "normal_threshold_cents": int(values.get("promotion.normal_threshold_cents") or 39800),
        "senior_threshold_cents": int(values.get("promotion.senior_threshold_cents") or 398000),
        "normal_commission_rate": float(values.get("promotion.normal_commission_rate") or 0.1),
        "senior_commission_rate": float(values.get("promotion.senior_commission_rate") or 0.2),
        "min_withdraw_cents": int(values.get("promotion.min_withdraw_cents") or 3000),
        "order_completion_days": int(values.get("promotion.order_completion_days") or 7),
    }


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

        current_status = str(order.get("raw_status") or order["status"])
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
                "UPDATE recharge_orders SET status = ?, review_note = ?, reviewed_by = ?, reviewed_at = ?, paid_at = COALESCE(paid_at, ?), granted_ledger_id = ?, updated_at = ? WHERE id = ?",
                ("approved", normalized_review_note, normalized_reviewed_by, now_text, now_text, ledger["ledger_id"], now_text, order_id),
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


def create_review_aspect_unlock(*, review_id: str, user_id: str, aspect_key: str, points_cost: int, usage_scene: str, request_payload_summary: dict[str, Any] | None, now_text: str, channel: str | None = None) -> dict[str, Any]:
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
            channel=channel,
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


def update_initial_points_config(
    *,
    old_initial_grant: int,
    new_initial_grant: int,
    apply_scope: str,
    reason: str | None,
    updated_at: str,
) -> dict[str, Any]:
    normalized_old_initial = max(0, int(old_initial_grant))
    normalized_new_initial = max(0, int(new_initial_grant))
    normalized_scope = _normalize_optional_text(apply_scope) or "future_users"
    if normalized_scope not in {"future_users", "all_users"}:
        raise ValueError("invalid_initial_points_apply_scope")

    delta = normalized_new_initial - normalized_old_initial
    target_user_count = 0
    affected_user_count = 0
    adjusted_points_total = 0
    zeroed_user_count = 0
    operation_id = uuid4().hex
    normalized_reason = _normalize_optional_text(reason)

    with open_connection() as connection:
        connection.execute(
            """
            INSERT INTO runtime_config_entries (id, scope_type, scope_key, config_key, value_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(scope_type, scope_key, config_key)
            DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at
            """,
            (uuid4().hex, "global", "default", "points.initial_grant", _serialize_json_value(normalized_new_initial), updated_at),
        )

        if normalized_scope == "all_users" and delta != 0:
            rows = connection.execute(
                """
                SELECT u.id AS user_id, COALESCE(pa.balance, 0) AS balance
                FROM users u
                LEFT JOIN points_accounts pa ON pa.user_id = u.id
                WHERE u.status IN ('active', 'disabled')
                  AND u.primary_identity_type IN ('phone', 'wechat_unionid', 'wechat_pending_unionid')
                ORDER BY u.created_at ASC, u.id ASC
                """
            ).fetchall()
            target_user_count = len(rows)
            for row in rows:
                user_id = str(row["user_id"])
                current_balance = max(0, int(row["balance"] or 0))
                next_balance = max(0, current_balance + delta)
                actual_delta = next_balance - current_balance
                if actual_delta == 0:
                    continue
                _ensure_points_account_row(connection, user_id=user_id, now_text=updated_at)
                connection.execute(
                    "UPDATE points_accounts SET balance = ?, version = version + 1, updated_at = ? WHERE user_id = ?",
                    (next_balance, updated_at, user_id),
                )
                connection.execute(
                    """
                    INSERT INTO points_ledgers (id, user_id, change_type, delta, balance_after, biz_type, biz_id, idempotency_key, remark, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uuid4().hex,
                        user_id,
                        "initial_grant_rebase",
                        actual_delta,
                        next_balance,
                        "initial_points_rebase",
                        operation_id,
                        f"initial_points_rebase:{operation_id}:{user_id}",
                        normalized_reason or f"initial points changed {normalized_old_initial}->{normalized_new_initial}",
                        updated_at,
                    ),
                )
                affected_user_count += 1
                adjusted_points_total += actual_delta
                if actual_delta < 0 and next_balance == 0:
                    zeroed_user_count += 1

        entry_row = connection.execute(
            "SELECT id, scope_type, scope_key, config_key, value_json, updated_at FROM runtime_config_entries WHERE scope_type = ? AND scope_key = ? AND config_key = ?",
            ("global", "default", "points.initial_grant"),
        ).fetchone()

    if entry_row is None:
        raise RuntimeError("initial_points_config_update_failed")
    return {
        "previous_initial_grant": normalized_old_initial,
        "initial_grant": normalized_new_initial,
        "delta": delta,
        "apply_scope": normalized_scope,
        "target_user_count": target_user_count,
        "affected_user_count": affected_user_count,
        "adjusted_points_total": adjusted_points_total,
        "zeroed_user_count": zeroed_user_count,
        "operation_id": operation_id,
        "entry": _deserialize_runtime_config_entry_row(entry_row),
    }



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



def _create_usage_record_in_connection(connection: sqlite3.Connection, *, usage_record_id: str, user_id: str, scene: str, channel: str | None, target_id: str | None, points_cost: int, status: str, request_payload_summary: dict[str, Any] | None, result_summary: dict[str, Any] | None, created_at: str, updated_at: str) -> None:
    connection.execute(
        "INSERT INTO usage_records (id, user_id, scene, channel, target_id, points_cost, status, request_payload_summary, result_summary, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (usage_record_id, user_id, scene, channel, target_id, points_cost, status, _serialize_json_value(request_payload_summary), _serialize_json_value(result_summary), created_at, updated_at),
    )



def _ensure_points_account_row(connection: sqlite3.Connection, *, user_id: str, now_text: str) -> None:
    connection.execute("INSERT OR IGNORE INTO points_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, 0, 0, 0, ?, ?)", (user_id, now_text, now_text))


def _get_rebate_account_row(connection: sqlite3.Connection, *, user_id: str, now_text: str) -> sqlite3.Row:
    connection.execute(
        "INSERT OR IGNORE INTO promotion_rebate_accounts (user_id, balance, frozen_balance, version, created_at, updated_at) VALUES (?, 0, 0, 0, ?, ?)",
        (user_id, now_text, now_text),
    )
    row = connection.execute(
        "SELECT user_id, balance, frozen_balance, version, created_at, updated_at FROM promotion_rebate_accounts WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError("rebate_account_not_found")
    return row


def _deserialize_rebate_account_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "user_id": row["user_id"],
        "balance": int(row["balance"] or 0),
        "frozen_balance": int(row["frozen_balance"] or 0),
        "version": int(row["version"] or 0),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _insert_admin_operation_log(
    connection: sqlite3.Connection,
    *,
    operator: str | None,
    action: str,
    target_type: str,
    target_id: str,
    reason: str | None,
    operator_note: str | None,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    created_at: str,
) -> None:
    connection.execute(
        "INSERT INTO admin_operation_logs (id, operator, action, target_type, target_id, reason, operator_note, before_json, after_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            uuid4().hex,
            _normalize_optional_text(operator),
            action,
            target_type,
            target_id,
            _normalize_optional_text(reason),
            _normalize_optional_text(operator_note),
            _serialize_json_value(before),
            _serialize_json_value(after),
            created_at,
        ),
    )



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
    points_cost = int(row["points_cost"])
    return {
        "usage_record_id": row["id"],
        "user_id": row["user_id"],
        "scene": row["scene"],
        "feature_key": row["scene"],
        "feature_name": _scene_to_feature_name(str(row["scene"])),
        "channel": row["channel"] if "channel" in row.keys() else None,
        "target_id": row["target_id"],
        "points_cost": points_cost,
        "normal_points_cost": points_cost,
        "rebate_points_cost": 0,
        "status": row["status"],
        "user_status": row["user_status"] if "user_status" in row.keys() else None,
        "user_nickname": row["user_nickname"] if "user_nickname" in row.keys() else None,
        "user_avatar_url": row["user_avatar_url"] if "user_avatar_url" in row.keys() else None,
        "request_payload_summary": json.loads(row["request_payload_summary"]) if row["request_payload_summary"] else None,
        "result_summary": json.loads(row["result_summary"]) if row["result_summary"] else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }



def _serialize_json_value(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _deserialize_json_value(value: Any, *, default: Any = None) -> Any:
    if value is None:
        return default
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _deserialize_runtime_config_entry_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "entry_id": row["id"],
        "scope_type": row["scope_type"],
        "scope_key": row["scope_key"],
        "config_key": row["config_key"],
        "value": json.loads(row["value_json"]),
        "updated_at": row["updated_at"],
    }


def _deserialize_refund_request_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "refund_id": row["id"],
        "order_id": row["order_id"],
        "user_id": row["user_id"],
        "status": row["status"],
        "reason": row["reason"],
        "operator_note": row["operator_note"],
        "reject_reason": row["reject_reason"],
        "reviewed_by": row["reviewed_by"],
        "reviewed_at": row["reviewed_at"],
        "retry_count": int(row["retry_count"] or 0),
        "failure_reason": row["failure_reason"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _deserialize_promotion_application_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "application_id": row["id"],
        "user_id": row["user_id"],
        "user_nickname": row["user_nickname"] if "user_nickname" in row.keys() else None,
        "current_identity_level": _normalize_user_identity_for_output(row["current_identity_level"]) if "current_identity_level" in row.keys() else None,
        "requested_level": _normalize_user_identity_for_output(row["requested_level"]),
        "status": row["status"],
        "applicant_name": row["applicant_name"],
        "applicant_phone": row["applicant_phone"],
        "reject_reason": row["reject_reason"],
        "review_note": row["review_note"],
        "reviewed_by": row["reviewed_by"],
        "reviewed_at": row["reviewed_at"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _deserialize_promotion_commission_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "commission_id": row["id"],
        "promoter_user_id": row["promoter_user_id"],
        "promoter_nickname": row["promoter_nickname"] if "promoter_nickname" in row.keys() else None,
        "invited_user_id": row["invited_user_id"],
        "invited_user_nickname": row["invited_user_nickname"] if "invited_user_nickname" in row.keys() else None,
        "order_id": row["order_id"],
        "order_amount_cents": int(row["order_amount_cents"] or 0),
        "commission_rate": float(row["commission_rate"] or 0),
        "commission_amount_cents": int(row["commission_amount_cents"] or row["commission_points"] or 0) if "commission_amount_cents" in row.keys() else int(row["commission_points"] or 0),
        "commission_points": int(row["commission_points"] or 0),
        "commission_type": row["commission_type"],
        "status": row["status"],
        "remark": row["remark"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "settled_at": row["settled_at"],
        "revoked_at": row["revoked_at"],
    }


def _deserialize_promotion_withdrawal_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "withdrawal_id": row["id"],
        "user_id": row["user_id"],
        "user_nickname": row["user_nickname"] if "user_nickname" in row.keys() else None,
        "identity_level": _normalize_user_identity_for_output(row["identity_level"]) if "identity_level" in row.keys() else None,
        "status": row["status"],
        "withdrawable_balance_snapshot_cents": int(row["withdrawable_balance_snapshot_cents"] or row["rebate_points_balance_snapshot"] or 0) if "withdrawable_balance_snapshot_cents" in row.keys() else int(row["rebate_points_balance_snapshot"] or 0),
        "frozen_commission_snapshot_cents": int(row["frozen_commission_snapshot_cents"] or 0) if "frozen_commission_snapshot_cents" in row.keys() else 0,
        "points_used": int(row["points_used"] or 0),
        "amount_cents": int(row["amount_cents"] or 0),
        "rebate_points_balance_snapshot": int(row["rebate_points_balance_snapshot"] or 0),
        "cash_rate_snapshot": float(row["cash_rate_snapshot"] or 1),
        "reject_reason": row["reject_reason"],
        "review_note": row["review_note"],
        "payout_method": row["payout_method"],
        "payout_proof": row["payout_proof"],
        "payout_failure_reason": row["payout_failure_reason"],
        "reviewed_by": row["reviewed_by"],
        "reviewed_at": row["reviewed_at"],
        "paid_at": row["paid_at"],
        "created_at": row["created_at"],
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


def _deserialize_internal_phone_qimen_review_row(row: sqlite3.Row) -> dict[str, Any]:
    duration = row["generation_duration_seconds"]
    return {
        "review_id": row["id"],
        "user_id": row["user_id"],
        "user_uid": row["user_uid"],
        "user_nickname": row["user_nickname"],
        "user_phone": row["user_phone"],
        "phone": row["phone"],
        "gender": row["gender"],
        "status": row["status"],
        "progress_stage": row["progress_stage"],
        "progress_message": row["progress_message"],
        "error_message": row["error_message"],
        "channel": row["channel"],
        "base_points_cost": int(row["base_points_cost"] or 0),
        "unlock_count": int(row["unlock_count"] or 0),
        "voice_count": int(row["voice_count"] or 0),
        "generation_duration_seconds": int(duration) if duration is not None else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }



def _deserialize_user_row(row: sqlite3.Row) -> dict[str, Any]:
    return {"user_id": row["user_id"], "uid": row["uid"] if "uid" in row.keys() else None, "status": _normalize_user_status_for_output(row["status"]), "identity_level": _normalize_user_identity_for_output(row["identity_level"] if "identity_level" in row.keys() else "normal_user"), "nickname": row["nickname"], "avatar_url": row["avatar_url"], "profile_completed": bool(row["profile_completed"]), "points_balance": int(row["balance"] or 0), "frozen_balance": int(row["frozen_balance"] or 0), "created_at": row["created_at"], "updated_at": row["updated_at"], "last_active_at": row["last_active_at"]}


def _deserialize_internal_user_row(row: sqlite3.Row) -> dict[str, Any]:
    identity_registered_candidates = [
        value
        for value in (
            row["phone_registered_at"] if "phone_registered_at" in row.keys() else None,
            row["unionid_registered_at"] if "unionid_registered_at" in row.keys() else None,
        )
        if value
    ]
    registered_at = min(identity_registered_candidates) if identity_registered_candidates else row["created_at"]
    return {
        "user_id": row["user_id"],
        "uid": row["uid"] if "uid" in row.keys() else None,
        "status": _normalize_user_status_for_output(row["status"]),
        "identity_level": _normalize_user_identity_for_output(row["identity_level"] if "identity_level" in row.keys() else "normal_user"),
        "primary_identity_type": row["primary_identity_type"] if "primary_identity_type" in row.keys() else "unknown",
        "registered_channel": row["registered_channel"] if "registered_channel" in row.keys() else None,
        "promoter_parent_user_id": row["promoter_parent_user_id"] if "promoter_parent_user_id" in row.keys() else None,
        "nickname": row["nickname"],
        "avatar_url": row["avatar_url"],
        "profile_completed": bool(row["profile_completed"]),
        "points_balance": int(row["balance"] or 0),
        "frozen_balance": int(row["frozen_balance"] or 0),
        "withdrawable_balance_cents": int(row["withdrawable_balance_cents"] or 0) if "withdrawable_balance_cents" in row.keys() else 0,
        "frozen_commission_cents": int(row["frozen_commission_cents"] or 0) if "frozen_commission_cents" in row.keys() else 0,
        "withdrawn_amount_cents": int(row["withdrawn_amount_cents"] or 0) if "withdrawn_amount_cents" in row.keys() else 0,
        "rebate_points_balance": int(row["rebate_points_balance"] or 0) if "rebate_points_balance" in row.keys() else 0,
        "rebate_frozen_balance": int(row["rebate_frozen_balance"] or 0) if "rebate_frozen_balance" in row.keys() else 0,
        "primary_phone": row["primary_phone"] if "primary_phone" in row.keys() else None,
        "phone_verified_at": row["phone_verified_at"] if "phone_verified_at" in row.keys() else None,
        "primary_unionid": row["primary_unionid"] if "primary_unionid" in row.keys() else None,
        "first_login_at": row["created_at"],
        "registered_at": registered_at,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_active_at": row["last_active_at"],
        "openid": row["openid"],
        "unionid": row["unionid"],
    }



def _deserialize_recharge_order_row(row: sqlite3.Row) -> dict[str, Any]:
    points_amount = int(row["points_amount"] or 0)
    bonus_points = int(row["bonus_points"] or 0)
    raw_status = str(row["status"])
    paid_at = row["paid_at"] if "paid_at" in row.keys() else row["reviewed_at"]
    completed_at = row["completed_at"] if "completed_at" in row.keys() else None
    closed_at = row["closed_at"] if "closed_at" in row.keys() else None
    return {
        "order_id": row["id"],
        "user_id": row["user_id"],
        "user_status": row["user_status"] if "user_status" in row.keys() else None,
        "user_nickname": row["user_nickname"] if "user_nickname" in row.keys() else None,
        "channel": row["channel"],
        "status": _normalize_recharge_order_status(raw_status),
        "raw_status": raw_status,
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
        "paid_at": paid_at,
        "completed_at": completed_at,
        "closed_at": closed_at,
        "granted_ledger_id": row["granted_ledger_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _deserialize_payment_transaction_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "transaction_id": row["id"],
        "order_id": row["order_id"],
        "user_id": row["user_id"],
        "provider": row["provider"],
        "payment_method": row["payment_method"],
        "amount_cents": int(row["amount_cents"] or 0),
        "status": row["status"],
        "provider_transaction_id": row["provider_transaction_id"],
        "prepay_id": row["prepay_id"],
        "idempotency_key": row["idempotency_key"],
        "payment_params": _deserialize_json_value(row["payment_params_json"], default={}),
        "notify_payload": _deserialize_json_value(row["notify_payload_json"], default={}),
        "failure_reason": row["failure_reason"],
        "paid_at": row["paid_at"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _normalize_recharge_order_status(status: str) -> str:
    normalized_status = status.strip().lower()
    status_map = {
        "pending": "unpaid",
        "approved": "paid",
        "rejected": "refunded",
        "unpaid": "unpaid",
        "paid": "paid",
        "completed": "completed",
        "refund_pending": "refund_pending",
        "refunded": "refunded",
        "closed": "closed",
    }
    return status_map.get(normalized_status, normalized_status or "unpaid")


def _storage_recharge_order_status(status: str) -> str:
    normalized_status = status.strip().lower()
    status_map = {
        "unpaid": "pending",
        "paid": "approved",
        "refunded": "rejected",
    }
    return status_map.get(normalized_status, normalized_status)


def _scene_to_feature_name(scene: str) -> str | None:
    normalized_scene = scene.strip().lower()
    scene_map = {
        "phone_review_base": "手机号评测",
        "phone_review_aspect_unlock": "维度解锁",
        "agent_reply": "智能体对话",
        "almanac_query": "黄历查询",
        "five_elements_query": "五行属性查询",
        "recharge": "充值",
        "ambassador_apply": "推广大使申请",
        "withdraw_apply": "提现申请",
    }
    return scene_map.get(normalized_scene)


def list_llm_api_keys() -> list[dict[str, Any]]:
    with open_connection() as connection:
        rows = connection.execute(
            "SELECT id, provider, model, display_name, masked_key, secret_ref, CASE WHEN IFNULL(secret_value, '') != '' THEN 1 ELSE 0 END AS secret_configured, enabled, priority, remark, last_operator, created_at, updated_at FROM llm_api_keys ORDER BY enabled DESC, priority ASC, updated_at DESC, id DESC"
        ).fetchall()
    return [_deserialize_llm_api_key_row(row) for row in rows]


def get_llm_api_key(key_id: str) -> dict[str, Any] | None:
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, provider, model, display_name, masked_key, secret_ref, secret_value, CASE WHEN IFNULL(secret_value, '') != '' THEN 1 ELSE 0 END AS secret_configured, enabled, priority, remark, last_operator, created_at, updated_at FROM llm_api_keys WHERE id = ?",
            (key_id,),
        ).fetchone()
    return _deserialize_llm_api_key_row(row, include_secret=True) if row is not None else None


def get_enabled_llm_api_key(*, provider: str, model: str | None = None) -> dict[str, Any] | None:
    normalized_provider = _normalize_optional_text(provider)
    normalized_model = _normalize_optional_text(model)
    if not normalized_provider:
        return None
    conditions = ["provider = ?", "enabled = 1", "IFNULL(secret_value, '') != ''"]
    parameters: list[Any] = [normalized_provider]
    if normalized_model:
        conditions.append("model = ?")
        parameters.append(normalized_model)
    with open_connection() as connection:
        row = connection.execute(
            "SELECT id, provider, model, display_name, masked_key, secret_ref, secret_value, CASE WHEN IFNULL(secret_value, '') != '' THEN 1 ELSE 0 END AS secret_configured, enabled, priority, remark, last_operator, created_at, updated_at FROM llm_api_keys WHERE "
            + " AND ".join(conditions)
            + " ORDER BY priority ASC, updated_at DESC, id DESC LIMIT 1",
            parameters,
        ).fetchone()
    return _deserialize_llm_api_key_row(row, include_secret=True) if row is not None else None


def upsert_llm_api_key(*, key_id: str | None, provider: str, model: str, display_name: str, masked_key: str, secret_ref: str, secret_value: str | None, enabled: bool, priority: int, remark: str | None, last_operator: str | None, now_text: str) -> dict[str, Any]:
    normalized_key_id = _normalize_optional_text(key_id) or uuid4().hex
    normalized_secret_value = _normalize_optional_text(secret_value)
    if normalized_secret_value is None and key_id:
        existing = get_llm_api_key(key_id)
        normalized_secret_value = str(existing.get("secret_value") or "") if existing else None
    if not normalized_secret_value:
        raise ValueError("secret_value_required")
    with open_connection() as connection:
        connection.execute(
            """
            INSERT INTO llm_api_keys (id, provider, model, display_name, masked_key, secret_ref, secret_value, enabled, priority, remark, last_operator, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id)
            DO UPDATE SET
                provider = excluded.provider,
                model = excluded.model,
                display_name = excluded.display_name,
                masked_key = excluded.masked_key,
                secret_ref = excluded.secret_ref,
                secret_value = excluded.secret_value,
                enabled = excluded.enabled,
                priority = excluded.priority,
                remark = excluded.remark,
                last_operator = excluded.last_operator,
                updated_at = excluded.updated_at
            """,
            (
                normalized_key_id,
                provider,
                model,
                display_name,
                masked_key,
                secret_ref,
                normalized_secret_value,
                int(bool(enabled)),
                int(priority),
                remark,
                last_operator,
                now_text,
                now_text,
            ),
        )
        row = connection.execute(
            "SELECT id, provider, model, display_name, masked_key, secret_ref, CASE WHEN IFNULL(secret_value, '') != '' THEN 1 ELSE 0 END AS secret_configured, enabled, priority, remark, last_operator, created_at, updated_at FROM llm_api_keys WHERE id = ?",
            (normalized_key_id,),
        ).fetchone()
    if row is None:
        raise RuntimeError("llm_api_key_upsert_failed")
    return _deserialize_llm_api_key_row(row)


def delete_llm_api_key(key_id: str) -> None:
    with open_connection() as connection:
        connection.execute("DELETE FROM llm_api_keys WHERE id = ?", (key_id,))


def _deserialize_llm_api_key_row(row: sqlite3.Row, *, include_secret: bool = False) -> dict[str, Any]:
    output = {
        "key_id": row["id"],
        "provider": row["provider"],
        "model": row["model"],
        "display_name": row["display_name"],
        "masked_key": row["masked_key"],
        "secret_ref": row["secret_ref"],
        "secret_configured": bool(row["secret_configured"]) if "secret_configured" in row.keys() else False,
        "enabled": bool(row["enabled"]),
        "priority": int(row["priority"]),
        "remark": row["remark"],
        "last_operator": row["last_operator"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    if include_secret:
        output["secret_value"] = row["secret_value"] if "secret_value" in row.keys() else None
    return output


def _get_recharge_order_in_connection(connection: sqlite3.Connection, *, order_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.paid_at, r.completed_at, r.closed_at, r.granted_ledger_id, r.created_at, r.updated_at FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id WHERE r.id = ?",
        (order_id,),
    ).fetchone()
    return _deserialize_recharge_order_row(row) if row is not None else None


def _get_recharge_order_by_user_idempotency_key_in_connection(connection: sqlite3.Connection, *, user_id: str, idempotency_key: str | None) -> dict[str, Any] | None:
    normalized_idempotency_key = _normalize_optional_text(idempotency_key)
    if not normalized_idempotency_key:
        return None
    row = connection.execute(
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.paid_at, r.completed_at, r.closed_at, r.granted_ledger_id, r.created_at, r.updated_at FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id WHERE r.user_id = ? AND r.idempotency_key = ?",
        (user_id, normalized_idempotency_key),
    ).fetchone()
    return _deserialize_recharge_order_row(row) if row is not None else None


def _get_recharge_order_by_source_external_order_id_in_connection(connection: sqlite3.Connection, *, source: str, external_order_id: str | None) -> dict[str, Any] | None:
    normalized_source = _normalize_optional_text(source)
    normalized_external_order_id = _normalize_optional_text(external_order_id)
    if not normalized_source or not normalized_external_order_id:
        return None
    row = connection.execute(
        "SELECT r.id, r.user_id, u.status AS user_status, p.nickname AS user_nickname, r.channel, r.status, r.package_key, r.package_title, r.amount_cents, r.points_amount, r.bonus_points, r.source, r.external_order_id, r.proof_url, r.remark, r.review_note, r.reviewed_by, r.reviewed_at, r.paid_at, r.completed_at, r.closed_at, r.granted_ledger_id, r.created_at, r.updated_at FROM recharge_orders r JOIN users u ON u.id = r.user_id LEFT JOIN user_profiles p ON p.user_id = u.id WHERE r.source = ? AND r.external_order_id = ?",
        (normalized_source, normalized_external_order_id),
    ).fetchone()
    return _deserialize_recharge_order_row(row) if row is not None else None


def _get_payment_transaction_in_connection(connection: sqlite3.Connection, *, transaction_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT id, order_id, user_id, provider, payment_method, amount_cents, status,
               provider_transaction_id, prepay_id, idempotency_key, payment_params_json,
               notify_payload_json, failure_reason, paid_at, created_at, updated_at
        FROM payment_transactions
        WHERE id = ?
        """,
        (transaction_id,),
    ).fetchone()
    return _deserialize_payment_transaction_row(row) if row is not None else None


def _get_payment_transaction_by_order_idempotency_key_in_connection(connection: sqlite3.Connection, *, order_id: str, idempotency_key: str | None) -> dict[str, Any] | None:
    normalized_idempotency_key = _normalize_optional_text(idempotency_key)
    if not normalized_idempotency_key:
        return None
    row = connection.execute(
        """
        SELECT id, order_id, user_id, provider, payment_method, amount_cents, status,
               provider_transaction_id, prepay_id, idempotency_key, payment_params_json,
               notify_payload_json, failure_reason, paid_at, created_at, updated_at
        FROM payment_transactions
        WHERE order_id = ? AND idempotency_key = ?
        """,
        (order_id, normalized_idempotency_key),
    ).fetchone()
    return _deserialize_payment_transaction_row(row) if row is not None else None


def _profile_completed(nickname: str | None, avatar_url: str | None) -> int:
    return int(bool(_normalize_optional_text(nickname)) and bool(_normalize_optional_text(avatar_url)))



def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_user_status(status: str | None) -> str:
    normalized_status = (_normalize_optional_text(status) or "").lower()
    if normalized_status == "active":
        return "active"
    if normalized_status in {"disabled", "blocked", "inactive"}:
        return "disabled"
    if not normalized_status:
        raise ValueError("status_required")
    raise ValueError("invalid_user_status")


def _normalize_user_status_for_output(status: Any) -> str:
    try:
        return _normalize_user_status(str(status))
    except ValueError:
        return "disabled"


def _normalize_user_identity_for_storage(identity_level: str | None) -> str:
    normalized_identity = (_normalize_optional_text(identity_level) or "").lower()
    if not normalized_identity:
        raise ValueError("identity_level_required")
    normalized_identity = USER_IDENTITY_LEVEL_ALIASES.get(normalized_identity, normalized_identity)
    if normalized_identity not in CANONICAL_USER_IDENTITY_LEVELS:
        raise ValueError("invalid_identity_level")
    return normalized_identity


def _normalize_user_identity_for_output(identity_level: Any) -> str:
    try:
        return _normalize_user_identity_for_storage(str(identity_level))
    except ValueError:
        return "normal_user"


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _format_money_cents(value: int) -> str:
    amount = max(0, int(value)) / 100
    return f"{amount:.2f}"


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


_USER_SELECT_SQL = """
SELECT u.id AS user_id, u.uid, u.status, u.identity_level, u.created_at, u.updated_at, u.last_active_at, p.nickname, p.avatar_url, p.profile_completed, pa.balance, pa.frozen_balance
FROM users u
LEFT JOIN user_profiles p ON p.user_id = u.id
LEFT JOIN points_accounts pa ON pa.user_id = u.id
"""

_SESSION_USER_SELECT_SQL = """
SELECT s.id AS session_id, s.user_id, s.status, s.expires_at
FROM user_sessions s
WHERE s.token_hash = ?
"""
