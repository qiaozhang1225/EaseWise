from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

router.add_api_route("/wechat-login", handlers.login_with_wechat, methods=["POST"], response_model=handlers.AuthLoginResponse)
router.add_api_route("/phone/status", handlers.get_phone_registration_status, methods=["POST"], response_model=handlers.PhoneStatusResponse)
router.add_api_route("/phone/register", handlers.register_with_phone_password, methods=["POST"], response_model=handlers.AuthLoginResponse)
router.add_api_route("/phone/login", handlers.login_with_phone_password, methods=["POST"], response_model=handlers.AuthLoginResponse)
router.add_api_route("/logout", handlers.logout_user, methods=["POST"])
