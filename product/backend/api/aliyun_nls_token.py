from __future__ import annotations

import json
import threading
import time

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from .config import get_aliyun_nls_access_key_id, get_aliyun_nls_access_key_secret, get_aliyun_tts_token

TOKEN_REFRESH_SKEW_SECONDS = 300

_TOKEN_LOCK = threading.Lock()
_TOKEN_CACHE: dict[str, int | str] = {
    "token": "",
    "expires_at": 0,
}


class AliyunNlsTokenError(RuntimeError):
    pass


def resolve_aliyun_nls_token() -> str:
    static_token = get_aliyun_tts_token()
    if static_token:
        return static_token
    access_key_id = get_aliyun_nls_access_key_id()
    access_key_secret = get_aliyun_nls_access_key_secret()
    if not access_key_id or not access_key_secret:
        return ""
    return get_cached_aliyun_nls_token(access_key_id=access_key_id, access_key_secret=access_key_secret)


def get_cached_aliyun_nls_token(*, access_key_id: str, access_key_secret: str) -> str:
    now = int(time.time())
    cached_token = str(_TOKEN_CACHE.get("token") or "")
    cached_expires_at = int(_TOKEN_CACHE.get("expires_at") or 0)
    if cached_token and cached_expires_at - now > TOKEN_REFRESH_SKEW_SECONDS:
        return cached_token

    with _TOKEN_LOCK:
        cached_token = str(_TOKEN_CACHE.get("token") or "")
        cached_expires_at = int(_TOKEN_CACHE.get("expires_at") or 0)
        if cached_token and cached_expires_at - now > TOKEN_REFRESH_SKEW_SECONDS:
            return cached_token

        token, expires_at = fetch_aliyun_nls_token(access_key_id=access_key_id, access_key_secret=access_key_secret)
        _TOKEN_CACHE["token"] = token
        _TOKEN_CACHE["expires_at"] = expires_at
        return token


def fetch_aliyun_nls_token(*, access_key_id: str, access_key_secret: str) -> tuple[str, int]:
    try:
        client = AcsClient(access_key_id, access_key_secret, "cn-shanghai")
        request = CommonRequest()
        request.set_method("POST")
        request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
        request.set_version("2019-02-28")
        request.set_action_name("CreateToken")
        response = client.do_action_with_exception(request)
        payload = json.loads(response.decode("utf-8") if isinstance(response, bytes) else str(response))
    except Exception as exc:
        raise AliyunNlsTokenError("aliyun_nls_token_fetch_failed") from exc

    token_payload = payload.get("Token")
    if not isinstance(token_payload, dict):
        raise AliyunNlsTokenError("aliyun_nls_token_missing")
    token = str(token_payload.get("Id") or "").strip()
    expires_at = int(token_payload.get("ExpireTime") or 0)
    if not token or expires_at <= int(time.time()):
        raise AliyunNlsTokenError("aliyun_nls_token_invalid")
    return token, expires_at
