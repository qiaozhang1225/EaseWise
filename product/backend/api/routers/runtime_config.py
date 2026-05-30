from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/runtime-config", tags=["runtime-config"])

router.add_api_route("/public", handlers.get_public_runtime_config, methods=["GET"], response_model=handlers.PublicRuntimeConfigResponse)
