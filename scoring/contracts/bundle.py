from __future__ import annotations

from typing import Any, TypedDict

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired


class BaseScoringBundle(TypedDict):
    score_result: dict[str, Any]
    score_template: dict[str, Any]


class ProductScoringBundle(BaseScoringBundle):
    pass


class SkillScoringPackage(BaseScoringBundle, total=False):
    score_markdown: NotRequired[str]
