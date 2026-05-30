from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal", tags=["internal-dashboard"])

router.add_api_route("/dashboard", handlers.get_internal_dashboard, methods=["GET"], response_model=handlers.DashboardResponse)
