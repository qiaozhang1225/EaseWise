from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/almanac", tags=["almanac"])

router.add_api_route("/today", handlers.get_today_almanac, methods=["GET"], response_model=handlers.AlmanacResponse)
router.add_api_route("/days/{date_text}", handlers.get_almanac_by_date, methods=["GET"], response_model=handlers.AlmanacResponse)
