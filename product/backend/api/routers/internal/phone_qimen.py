from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/phone-qimen", tags=["internal-phone-qimen"])

router.add_api_route("/reviews", handlers.get_internal_reviews, methods=["GET"], response_model=handlers.ReviewListResponse)
router.add_api_route("/reviews/{review_id}", handlers.get_internal_review_detail, methods=["GET"], response_model=handlers.ReviewRecordResponse)
router.add_api_route("/usage-records", handlers.get_internal_usage_records, methods=["GET"], response_model=handlers.UsageRecordListResponse)
router.add_api_route("/usage-records/{usage_record_id}", handlers.get_internal_usage_record_detail, methods=["GET"], response_model=handlers.UsageRecordDetailResponse)
