from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

router.add_api_route("/recharge-packages", handlers.get_recharge_packages, methods=["GET"], response_model=handlers.RechargePackageListResponse)
router.add_api_route("/recharge-orders", handlers.create_recharge_order_record, methods=["POST"], response_model=handlers.RechargeOrderResponse)
router.add_api_route("/recharge-orders", handlers.get_my_recharge_orders, methods=["GET"], response_model=handlers.RechargeOrderListResponse)
router.add_api_route("/recharge-orders/{order_id}", handlers.get_my_recharge_order_detail, methods=["GET"], response_model=handlers.RechargeOrderResponse)
router.add_api_route("/recharge-orders/{order_id}/payments", handlers.create_recharge_order_payment, methods=["POST"], response_model=handlers.PaymentTransactionResponse)
router.add_api_route("/recharge-orders/{order_id}/payment-status", handlers.get_recharge_order_payment_status, methods=["GET"], response_model=handlers.RechargeOrderPaymentStatusResponse)
router.add_api_route("/payments/{provider}/notify", handlers.post_payment_notify, methods=["POST"], response_model=handlers.PaymentNotifyResponse)
