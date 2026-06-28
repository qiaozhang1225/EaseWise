from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/phone-qimen", tags=["phone-qimen"])

router.add_api_route("/reviews", handlers.create_review_record, methods=["POST"], response_model=handlers.ReviewRecordResponse)
router.add_api_route("/reviews/stream", handlers.stream_create_review_record, methods=["POST"])
router.add_api_route("/reviews", handlers.list_review_records, methods=["GET"], response_model=handlers.ReviewListResponse)
router.add_api_route("/reviews/{review_id}", handlers.get_review_record, methods=["GET"], response_model=handlers.ReviewRecordResponse)
router.add_api_route("/reviews/{review_id}/aspect-unlocks", handlers.get_review_aspect_unlock_status, methods=["GET"], response_model=handlers.ReviewAspectUnlockListResponse)
router.add_api_route("/reviews/{review_id}/aspect-unlocks", handlers.create_review_aspect_unlock_record, methods=["POST"], response_model=handlers.ReviewAspectUnlockResponse)
router.add_api_route("/reviews/{review_id}/aspect-unlocks/{aspect_key}/stream", handlers.stream_review_aspect_unlock_record, methods=["POST"])
