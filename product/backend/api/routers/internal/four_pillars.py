from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/four-pillars", tags=["internal-four-pillars"])

router.add_api_route("/summary", handlers.get_internal_four_pillars_summary, methods=["GET"], response_model=handlers.InternalFourPillarsSummaryResponse)
router.add_api_route("/reviews", handlers.get_internal_four_pillars_reviews, methods=["GET"], response_model=handlers.InternalFourPillarsReviewListResponse)
router.add_api_route("/reviews/{review_id}", handlers.get_internal_four_pillars_review_detail, methods=["GET"], response_model=handlers.InternalFourPillarsReviewDetailResponse)
router.add_api_route("/usage-records", handlers.get_internal_usage_records, methods=["GET"], response_model=handlers.UsageRecordListResponse)
router.add_api_route("/usage-records/{usage_record_id}", handlers.get_internal_usage_record_detail, methods=["GET"], response_model=handlers.UsageRecordDetailResponse)
