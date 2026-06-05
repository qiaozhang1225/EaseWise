from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/billing", tags=["internal-billing"])

router.add_api_route("/recharge-orders", handlers.get_internal_recharge_orders, methods=["GET"], response_model=handlers.RechargeOrderListResponse)
router.add_api_route("/recharge-orders/{order_id}", handlers.get_internal_recharge_order_detail, methods=["GET"], response_model=handlers.RechargeOrderResponse)
router.add_api_route("/recharge-orders/{order_id}/review", handlers.post_internal_recharge_order_review, methods=["POST"], response_model=handlers.RechargeOrderReviewResponse)
router.add_api_route("/recharge-orders/{order_id}/manual-complete", handlers.post_internal_recharge_order_manual_complete, methods=["POST"], response_model=handlers.RechargeOrderManualCompleteResponse)
router.add_api_route("/recharge-orders/{order_id}/refunds", handlers.post_internal_recharge_order_refund, methods=["POST"], response_model=handlers.RefundRequestResponse)
router.add_api_route("/refunds/{refund_id}/review", handlers.post_internal_refund_review, methods=["POST"], response_model=handlers.RefundRequestResponse)
router.add_api_route("/refunds/{refund_id}/retry", handlers.post_internal_refund_retry, methods=["POST"], response_model=handlers.RefundRequestResponse)
