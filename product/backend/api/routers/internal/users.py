from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/users", tags=["internal-users"])

router.add_api_route("", handlers.get_internal_users, methods=["GET"], response_model=handlers.InternalUserListResponse)
router.add_api_route("/{user_id}", handlers.get_internal_user_detail, methods=["GET"], response_model=handlers.InternalUserResponse)
router.add_api_route("/{user_id}/admin-summary", handlers.get_internal_user_admin_summary, methods=["GET"], response_model=handlers.InternalUserAdminSummaryResponse)
router.add_api_route("/{user_id}/points/ledger", handlers.get_internal_user_points_ledger, methods=["GET"], response_model=handlers.PointsLedgerListResponse)
router.add_api_route("/{user_id}/points/adjust", handlers.post_internal_user_points_adjust, methods=["POST"], response_model=handlers.ManualPointsAdjustResponse)
router.add_api_route("/{user_id}/rebate-points/adjust", handlers.post_internal_user_rebate_points_adjust, methods=["POST"], response_model=handlers.RebatePointsAdjustResponse)
router.add_api_route("/{user_id}/status", handlers.patch_internal_user_status, methods=["PATCH"], response_model=handlers.InternalUserResponse)
router.add_api_route("/{user_id}/identity", handlers.patch_internal_user_identity, methods=["PATCH"], response_model=handlers.InternalUserResponse)
router.add_api_route("/{user_id}/promoter-parent", handlers.patch_internal_user_promoter_parent, methods=["PATCH"], response_model=handlers.InternalUserResponse)
