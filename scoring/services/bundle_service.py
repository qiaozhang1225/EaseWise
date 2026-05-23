from __future__ import annotations

from typing import Any

from scoring.contracts.bundle import ProductScoringBundle, SkillScoringPackage
from scoring.services.template_service import build_score_template, render_score_template


def build_scoring_bundle(result: dict[str, Any], *, include_markdown: bool = False) -> ProductScoringBundle | SkillScoringPackage:
    bundle: ProductScoringBundle | SkillScoringPackage = {
        "score_result": result,
        "score_template": build_score_template(result),
    }
    if include_markdown:
        bundle["score_markdown"] = render_score_template(result)
    return bundle


def build_product_bundle(result: dict[str, Any]) -> ProductScoringBundle:
    return build_scoring_bundle(result)
