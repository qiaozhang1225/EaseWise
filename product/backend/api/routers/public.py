from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter()

router.add_api_route("/", handlers.index, methods=["GET"], include_in_schema=False)
router.add_api_route("/h5/wechat-openid-test", handlers.h5_wechat_openid_test, methods=["GET"], include_in_schema=False)
router.add_api_route("/health", handlers.health, methods=["GET"])
