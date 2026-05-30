from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/promotion", tags=["internal-promotion"])

router.add_api_route("/applications", handlers.get_internal_promotion_applications, methods=["GET"], response_model=handlers.PromotionApplicationListResponse)
router.add_api_route("/applications/{application_id}", handlers.get_internal_promotion_application_detail, methods=["GET"], response_model=handlers.PromotionApplicationResponse)
router.add_api_route("/applications/{application_id}/review", handlers.post_internal_promotion_application_review, methods=["POST"], response_model=handlers.PromotionApplicationResponse)
router.add_api_route("/commissions", handlers.get_internal_promotion_commissions, methods=["GET"], response_model=handlers.PromotionCommissionListResponse)
router.add_api_route("/commissions/{commission_id}", handlers.get_internal_promotion_commission_detail, methods=["GET"], response_model=handlers.PromotionCommissionResponse)
router.add_api_route("/withdrawals", handlers.get_internal_promotion_withdrawals, methods=["GET"], response_model=handlers.PromotionWithdrawalListResponse)
router.add_api_route("/withdrawals/{withdrawal_id}", handlers.get_internal_promotion_withdrawal_detail, methods=["GET"], response_model=handlers.PromotionWithdrawalResponse)
router.add_api_route("/withdrawals/{withdrawal_id}/review", handlers.post_internal_promotion_withdrawal_review, methods=["POST"], response_model=handlers.PromotionWithdrawalResponse)
router.add_api_route("/withdrawals/{withdrawal_id}/retry-payout", handlers.post_internal_promotion_withdrawal_retry_payout, methods=["POST"], response_model=handlers.PromotionWithdrawalResponse)
router.add_api_route("/withdrawals/{withdrawal_id}/mark-paid", handlers.post_internal_promotion_withdrawal_mark_paid, methods=["POST"], response_model=handlers.PromotionWithdrawalResponse)
router.add_api_route("/rules", handlers.get_internal_promotion_rules, methods=["GET"], response_model=handlers.PromotionRulesResponse)
router.add_api_route("/rules", handlers.put_internal_promotion_rules, methods=["PUT"], response_model=handlers.PromotionRulesResponse)
