from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from urllib import parse, request
from urllib.error import HTTPError, URLError

from fastapi import HTTPException

from .config import get_public_base_url, get_wechat_oa_app_id, get_wechat_oa_app_secret

WECHAT_OAUTH_AUTHORIZE_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"
WECHAT_OAUTH_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
STATE_COOKIE_NAME = "easewise_wechat_h5_state"


@dataclass
class WeChatH5OpenIdResult:
    openid: str
    scope: str | None
    unionid: str | None


def is_wechat_browser(user_agent: str | None) -> bool:
    return "micromessenger" in (user_agent or "").lower()


def build_oauth_state() -> str:
    return secrets.token_urlsafe(18)


def build_wechat_oauth_authorize_url(state: str) -> str:
    public_base_url = get_public_base_url()
    appid = get_wechat_oa_app_id()
    redirect_uri = f"{public_base_url}/h5/wechat-openid-test"
    query = parse.urlencode(
        {
            "appid": appid,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_base",
            "state": state,
        }
    )
    return f"{WECHAT_OAUTH_AUTHORIZE_URL}?{query}#wechat_redirect"


def exchange_h5_oauth_code(code: str) -> WeChatH5OpenIdResult:
    appid = get_wechat_oa_app_id()
    secret = get_wechat_oa_app_secret()
    if not appid or not secret:
        raise HTTPException(status_code=503, detail="wechat_h5_oauth_not_configured")

    query = parse.urlencode(
        {
            "appid": appid,
            "secret": secret,
            "code": code,
            "grant_type": "authorization_code",
        }
    )
    exchange_url = f"{WECHAT_OAUTH_ACCESS_TOKEN_URL}?{query}"
    try:
        with request.urlopen(exchange_url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail="wechat_h5_oauth_exchange_unavailable") from exc

    errcode = payload.get("errcode", 0)
    if errcode:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "wechat_h5_oauth_exchange_failed",
                "wechat_errcode": errcode,
                "wechat_errmsg": payload.get("errmsg", "unknown_error"),
            },
        )

    openid = str(payload.get("openid", "")).strip()
    if not openid:
        raise HTTPException(status_code=502, detail="wechat_h5_openid_missing")
    return WeChatH5OpenIdResult(
        openid=openid,
        scope=str(payload.get("scope", "")).strip() or None,
        unionid=str(payload.get("unionid", "")).strip() or None,
    )


def h5_oauth_is_configured() -> bool:
    return bool(get_public_base_url() and get_wechat_oa_app_id() and get_wechat_oa_app_secret())
