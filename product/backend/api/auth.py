from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib import parse, request
from urllib.error import HTTPError, URLError

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import allow_mock_wechat_login, get_auth_token_ttl_hours, get_internal_admin_token, get_wechat_app_id, get_wechat_app_secret
from .database import get_session_user_by_token_hash

WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"
MOCK_CODE_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
TOKEN_PREFIX = "ew_"
PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 260_000
security = HTTPBearer(auto_error=False)


@dataclass
class WeChatCodeExchangeResult:
    appid: str
    openid: str
    unionid: str | None
    session_key: str | None
    is_mock: bool


def exchange_wechat_code(code: str) -> WeChatCodeExchangeResult:
    normalized_code = code.strip()
    if not normalized_code:
        raise HTTPException(status_code=422, detail="wechat_code_required")
    if allow_mock_wechat_login() and normalized_code.startswith("mock:"):
        return _build_mock_exchange_result(normalized_code)

    appid = get_wechat_app_id()
    secret = get_wechat_app_secret()
    if not appid or not secret:
        raise HTTPException(status_code=503, detail="wechat_login_not_configured")

    query = parse.urlencode({"appid": appid, "secret": secret, "js_code": normalized_code, "grant_type": "authorization_code"})
    try:
        with request.urlopen(f"{WECHAT_CODE2SESSION_URL}?{query}", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail="wechat_code_exchange_unavailable") from exc

    errcode = payload.get("errcode", 0)
    if errcode:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "wechat_code_exchange_failed", "wechat_errcode": errcode, "wechat_errmsg": payload.get("errmsg", "unknown_error")},
        )

    openid = str(payload.get("openid", "")).strip()
    if not openid:
        raise HTTPException(status_code=502, detail="wechat_openid_missing")
    return WeChatCodeExchangeResult(
        appid=appid,
        openid=openid,
        unionid=str(payload.get("unionid", "")).strip() or None,
        session_key=str(payload.get("session_key", "")).strip() or None,
        is_mock=False,
    )


def issue_access_token() -> str:
    return TOKEN_PREFIX + secrets.token_urlsafe(32)


def hash_access_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"{PASSWORD_HASH_ALGORITHM}${PASSWORD_HASH_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        algorithm, iterations_text, salt, expected_digest = password_hash.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False
    if algorithm != PASSWORD_HASH_ALGORITHM or iterations <= 0 or not salt or not expected_digest:
        return False
    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return hmac.compare_digest(actual_digest, expected_digest)


def build_session_expiry(now_text: str) -> str:
    return (datetime.fromisoformat(now_text) + timedelta(hours=get_auth_token_ttl_hours())).replace(microsecond=0).isoformat()


async def resolve_authenticated_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, object] | None:
    if credentials is None:
        return None
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth_required")
    user = get_session_user_by_token_hash(hash_access_token(credentials.credentials), now_text=_utc_now(), ip=request.client.host if request.client else None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_or_expired_token")
    if str(user.get("status") or "").strip().lower() != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="account_disabled")
    return user


async def require_authenticated_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, object]:
    user = await resolve_authenticated_user(request, credentials)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth_required")
    return user


async def require_authenticated_user_with_token_hash(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> tuple[dict[str, object], str]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth_required")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth_required")
    token_hash = hash_access_token(credentials.credentials)
    user = get_session_user_by_token_hash(token_hash, now_text=_utc_now(), ip=request.client.host if request.client else None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_or_expired_token")
    if str(user.get("status") or "").strip().lower() != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="account_disabled")
    return user, token_hash


async def require_registered_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, object]:
    user = await require_authenticated_user(request, credentials)
    return user


def require_internal_admin_access(x_internal_admin_token: str | None = Header(default=None, alias="X-Internal-Admin-Token")) -> None:
    configured_token = get_internal_admin_token()
    if not configured_token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="internal_admin_token_not_configured")
    if x_internal_admin_token != configured_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_internal_admin_token")


def _build_mock_exchange_result(code: str) -> WeChatCodeExchangeResult:
    suffix = code.split(":", 1)[1].strip()
    if not suffix or not MOCK_CODE_PATTERN.fullmatch(suffix):
        raise HTTPException(status_code=422, detail="invalid_mock_code")
    return WeChatCodeExchangeResult(
        appid=get_wechat_app_id() or "mock-mini-program-appid",
        openid=f"mock-openid-{suffix}",
        unionid=f"mock-unionid-{suffix}",
        session_key=f"mock-session-{suffix}",
        is_mock=True,
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
