from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/account", tags=["account"])

router.add_api_route("/me", handlers.get_me, methods=["GET"], response_model=handlers.CurrentUserResponse)
router.add_api_route("/profile", handlers.patch_me_profile, methods=["PATCH"], response_model=handlers.UserResponse)
router.add_api_route("/points", handlers.get_my_points, methods=["GET"], response_model=handlers.PointsAccountResponse)
router.add_api_route("/points/ledger", handlers.get_my_points_ledger, methods=["GET"], response_model=handlers.PointsLedgerListResponse)
