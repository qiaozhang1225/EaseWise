from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import allow_mock_wechat_login


@dataclass(frozen=True)
class PaymentCreateResult:
    provider: str
    payment_method: str
    status: str
    payment_params: dict[str, Any] = field(default_factory=dict)
    prepay_id: str | None = None
    provider_transaction_id: str | None = None
    failure_reason: str | None = None
    client_message: str | None = None


def create_payment_request(*, provider: str, payment_method: str | None, order: dict[str, Any], return_url: str | None, client_context: dict[str, Any] | None) -> PaymentCreateResult:
    normalized_provider = (provider or "wechat_h5").strip().lower()
    normalized_method = (payment_method or normalized_provider).strip().lower()
    base_params = {
        "order_id": order["order_id"],
        "amount_cents": order["amount_cents"],
        "return_url": return_url,
        "client_context": client_context or {},
    }

    if normalized_provider == "mock" and allow_mock_wechat_login():
        return PaymentCreateResult(
            provider="mock",
            payment_method=normalized_method,
            status="pending",
            payment_params={
                **base_params,
                "mode": "mock",
                "next_step": "call_mock_notify",
            },
            client_message="当前为本地模拟支付交易，可通过 mock notify 推进到账；不会发起真实扣款。",
        )

    return PaymentCreateResult(
        provider=normalized_provider,
        payment_method=normalized_method,
        status="provider_unconfigured",
        payment_params={
            **base_params,
            "mode": "placeholder",
            "provider": normalized_provider,
        },
        failure_reason="payment_provider_not_configured",
        client_message="支付渠道适配层已创建订单交易，但真实支付参数尚未接入。当前不会发起扣款。",
    )
