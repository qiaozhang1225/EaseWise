from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/four-pillars", tags=["four-pillars"])

router.add_api_route("/reviews", handlers.create_four_pillars_review_record, methods=["POST"], response_model=handlers.FourPillarsReviewRecordResponse)
router.add_api_route("/input/locations", handlers.list_four_pillars_birth_locations, methods=["GET"])
router.add_api_route("/input/resolve", handlers.resolve_four_pillars_input, methods=["POST"])
router.add_api_route("/reviews", handlers.list_four_pillars_review_records, methods=["GET"], response_model=handlers.FourPillarsReviewListResponse)
router.add_api_route("/reviews/{review_id}", handlers.get_four_pillars_review_record, methods=["GET"], response_model=handlers.FourPillarsReviewRecordResponse)
router.add_api_route("/reviews/{review_id}/aspect-unlocks", handlers.get_four_pillars_review_aspect_unlock_status, methods=["GET"], response_model=handlers.FourPillarsAspectUnlockListResponse)
router.add_api_route("/reviews/{review_id}/aspect-unlocks", handlers.create_four_pillars_review_aspect_unlock_record, methods=["POST"], response_model=handlers.FourPillarsAspectUnlockResponse)
router.add_api_route("/reviews/{review_id}/luck-cycles", handlers.get_four_pillars_luck_cycles, methods=["GET"], response_model=handlers.FourPillarsLuckCycleListResponse)
router.add_api_route("/reviews/{review_id}/luck-cycles/{cycle_key}/summary", handlers.create_four_pillars_luck_cycle_summary, methods=["POST"], response_model=handlers.FourPillarsLuckRenderRecordResponse)
router.add_api_route("/reviews/{review_id}/luck-cycles/{cycle_key}/summary", handlers.get_four_pillars_luck_cycle_summary, methods=["GET"], response_model=handlers.FourPillarsLuckRenderRecordResponse)
router.add_api_route("/reviews/{review_id}/luck-cycles/{cycle_key}/years/{year}", handlers.create_four_pillars_luck_year_summary, methods=["POST"], response_model=handlers.FourPillarsLuckRenderRecordResponse)
router.add_api_route("/reviews/{review_id}/luck-cycles/{cycle_key}/years/{year}", handlers.get_four_pillars_luck_year_summary, methods=["GET"], response_model=handlers.FourPillarsLuckRenderRecordResponse)
