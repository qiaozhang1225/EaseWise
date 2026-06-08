from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/points-claims", tags=["points-claims"])

router.add_api_route("/{claim_code}", handlers.get_public_points_claim_link, methods=["GET"], response_model=handlers.PublicPointsClaimLinkResponse)
router.add_api_route("/{claim_code}/claim", handlers.post_public_points_claim, methods=["POST"], response_model=handlers.PointsClaimSubmitResponse)
