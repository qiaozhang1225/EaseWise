from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/almanac", tags=["internal-almanac"])

router.add_api_route("/usage-records", handlers.get_internal_usage_records, methods=["GET"], response_model=handlers.UsageRecordListResponse)
router.add_api_route("/usage-records/{usage_record_id}", handlers.get_internal_usage_record_detail, methods=["GET"], response_model=handlers.UsageRecordDetailResponse)
