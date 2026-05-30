from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

router.add_api_route("/recharge-packages", handlers.get_recharge_packages, methods=["GET"], response_model=handlers.RechargePackageListResponse)
router.add_api_route("/recharge-orders", handlers.create_recharge_order_record, methods=["POST"], response_model=handlers.RechargeOrderResponse)
router.add_api_route("/recharge-orders", handlers.get_my_recharge_orders, methods=["GET"], response_model=handlers.RechargeOrderListResponse)
router.add_api_route("/recharge-orders/{order_id}", handlers.get_my_recharge_order_detail, methods=["GET"], response_model=handlers.RechargeOrderResponse)
