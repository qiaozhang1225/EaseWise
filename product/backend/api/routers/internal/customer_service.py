from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/customer-service", tags=["internal-customer-service"])

router.add_api_route("/qr-code", handlers.post_internal_customer_service_qr_code, methods=["POST"], response_model=handlers.RuntimeConfigEntryResponse)
router.add_api_route("/qr-code", handlers.delete_internal_customer_service_qr_code, methods=["DELETE"], response_model=handlers.RuntimeConfigEntryResponse)
