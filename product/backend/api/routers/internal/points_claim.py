from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/points-claims", tags=["internal-points-claims"])

router.add_api_route("", handlers.get_internal_points_claim_links, methods=["GET"], response_model=handlers.PointsClaimLinkListResponse)
router.add_api_route("", handlers.post_internal_points_claim_link, methods=["POST"], response_model=handlers.PointsClaimLinkResponse)
router.add_api_route("/{claim_link_id}", handlers.get_internal_points_claim_link_detail, methods=["GET"], response_model=handlers.PointsClaimLinkResponse)
router.add_api_route("/{claim_link_id}/disable", handlers.post_internal_points_claim_link_disable, methods=["POST"], response_model=handlers.PointsClaimLinkResponse)
router.add_api_route("/{claim_link_id}/records", handlers.get_internal_points_claim_records, methods=["GET"], response_model=handlers.PointsClaimRecordListResponse)
