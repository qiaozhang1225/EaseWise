from __future__ import annotations

from typing import Any

from scoring.engine import load_rules, score_phone
from scoring.services.bundle_service import build_scoring_bundle


def score_phone_result(phone: str, gender: str, *, rules: dict[str, Any] | None = None) -> dict[str, Any]:
    active_rules = rules or load_rules()
    return score_phone(phone, gender, active_rules)


def build_scoring_bundle_from_phone(
    phone: str,
    gender: str,
    *,
    rules: dict[str, Any] | None = None,
    include_markdown: bool = False,
) -> dict[str, Any]:
    result = score_phone_result(phone, gender, rules=rules)
    return build_scoring_bundle(result, include_markdown=include_markdown)
