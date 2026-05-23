"""Deterministic scoring primitives for EaseWise."""

from .engine import load_rules, score_phone
from .services import (
    build_product_bundle,
    build_score_template,
    build_scoring_bundle,
    build_scoring_bundle_from_phone,
    build_skill_package,
    render_score_template,
    score_phone_result,
)

__all__ = [
    "build_product_bundle",
    "build_score_template",
    "build_scoring_bundle",
    "build_scoring_bundle_from_phone",
    "build_skill_package",
    "load_rules",
    "render_score_template",
    "score_phone",
    "score_phone_result",
]
