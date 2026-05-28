from __future__ import annotations

from typing import Any, TypedDict

from scoring.total_score.score_template import build_score_template, render_score_template

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired


class ProductScoringBundle(TypedDict):
    score_result: dict[str, Any]
    score_template: dict[str, Any]


class SkillScoringPackage(ProductScoringBundle, total=False):
    score_markdown: NotRequired[str]


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
