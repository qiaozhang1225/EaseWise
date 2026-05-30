from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

router.add_api_route("/guest-session", handlers.create_guest_session, methods=["POST"], response_model=handlers.GuestSessionResponse)
router.add_api_route("/wechat-login", handlers.login_with_wechat, methods=["POST"], response_model=handlers.AuthLoginResponse)
