"""Deterministic scoring primitives for EaseWise."""

from .total_score import (
    ProductScoringBundle,
    SkillScoringPackage,
    build_product_bundle,
    build_score_template,
    build_scoring_bundle,
    build_skill_package,
    load_rules,
    render_score_template,
    score_phone,
)
from .dimensions import (
    DIMENSION_ORDER,
    DIMENSION_TITLES,
    build_dimension_scores,
    build_stability_dimension_scores,
    score_phone_dimensions,
    score_phone_stability_dimensions,
)

__all__ = [
    "build_product_bundle",
    "build_dimension_scores",
    "build_score_template",
    "build_scoring_bundle",
    "build_skill_package",
    "build_stability_dimension_scores",
    "DIMENSION_ORDER",
    "DIMENSION_TITLES",
    "ProductScoringBundle",
    "load_rules",
    "render_score_template",
    "score_phone_dimensions",
    "score_phone_stability_dimensions",
    "score_phone",
    "SkillScoringPackage",
]
