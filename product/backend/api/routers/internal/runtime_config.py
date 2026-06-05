from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/runtime-config", tags=["internal-runtime-config"])

router.add_api_route("", handlers.get_internal_runtime_config, methods=["GET"], response_model=handlers.RuntimeConfigListResponse)
router.add_api_route("", handlers.put_internal_runtime_config, methods=["PUT"], response_model=handlers.RuntimeConfigListResponse)
router.add_api_route("/initial-points", handlers.post_internal_initial_points_config, methods=["POST"], response_model=handlers.RuntimeInitialPointsUpdateResponse)
router.add_api_route("/schema", handlers.get_internal_runtime_config_schema, methods=["GET"], response_model=handlers.RuntimeConfigSchemaResponse)
