from __future__ import annotations

from typing import Any

from scoring.dimension_score_v2 import score_phone_dimensions_v2
from scoring.dimension_score_v3 import score_phone_dimensions_v3

PUBLIC_ASPECT_ORDER = [
    "career",
    "wealth",
    "love",
    "health",
    "acad",
    "fortune",
    "investment",
    "travel",
    "social",
    "family",
    "personality",
    "fengshui",
]

DEFAULT_FREE_ASPECT_KEYS = [
    "career",
    "wealth",
    "love",
]
_ASPECT_SHORT_TITLES = {
    "career": "事业",
    "wealth": "财富",
    "love": "感情",
    "health": "健康",
    "acad": "学业",
    "fortune": "运势",
    "investment": "投资",
    "travel": "出行",
    "social": "人际",
    "family": "家庭",
    "personality": "性格",
    "fengshui": "风水",
}
_PALACE_DISPLAY_ORDER = [
    ("xun", "巽", "巽宫", "东南"),
    ("li", "离", "离宫", "正南"),
    ("kun", "坤", "坤宫", "西南"),
    ("zhen", "震", "震宫", "正东"),
    ("center", "中", "中宫", "盘心"),
    ("dui", "兑", "兑宫", "正西"),
    ("gen", "艮", "艮宫", "东北"),
    ("kan", "坎", "坎宫", "正北"),
    ("qian", "乾", "乾宫", "西北"),
]
_PALACE_WUXING_LABELS = {
    "巽": "木",
    "离": "火",
    "坤": "土",
    "震": "木",
    "中": "土",
    "兑": "金",
    "艮": "土",
    "坎": "水",
    "乾": "金",
}


def build_phone_review_product_view(score_result: dict[str, Any], score_template: dict[str, Any]) -> dict[str, Any]:
    product_render = score_template.get("product_render") if isinstance(score_template.get("product_render"), dict) else {}
    phone_summary = score_template.get("phone_summary") if isinstance(score_template.get("phone_summary"), dict) else {}
    if not phone_summary:
        phone_summary = product_render.get("phone_summary") if isinstance(product_render.get("phone_summary"), dict) else {}
    score_summary = score_template.get("score_summary") if isinstance(score_template.get("score_summary"), dict) else {}
    stability_render = _resolve_stability_render(product_render)
    final_score = int(score_summary.get("final_score", 0) or 0)
    dimension_result = _resolve_dimension_result(score_result, score_template)
    aspect_render = score_template.get("product_aspects_render") if isinstance(score_template.get("product_aspects_render"), dict) else {}
    aspects = _build_public_aspects(product_render, aspect_render, dimension_result)

    return {
        "score": final_score,
        "phone_summary": phone_summary,
        "board": _build_board_view(score_result, score_template),
        "stability_detail": {
            "verdict": str(stability_render.get("verdict") or _build_stability_value(score_result, final_score)),
            "content": str(stability_render.get("content") or "").strip(),
            "elements_check": stability_render.get("elements_check") if isinstance(stability_render.get("elements_check"), dict) else {},
        },
        "aspects": aspects,
        "aspect_scores": {
            key: {"score": item["score"]}
            for key, item in dimension_result.get("dimensions", {}).items()
            if key in PUBLIC_ASPECT_ORDER and isinstance(item, dict) and item.get("score") is not None
        },
        "aspect_order": PUBLIC_ASPECT_ORDER.copy(),
    }


def _build_public_aspects(
    product_render: dict[str, Any],
    aspect_render: dict[str, Any],
    dimension_result: dict[str, Any],
) -> list[dict[str, Any]]:
    sections = product_render.get("sections") if isinstance(product_render.get("sections"), dict) else {}
    dimensions = dimension_result.get("dimensions") if isinstance(dimension_result.get("dimensions"), dict) else {}
    aspects: list[dict[str, Any]] = []
    for aspect_id in PUBLIC_ASPECT_ORDER:
        rendered = aspect_render.get(aspect_id) if isinstance(aspect_render.get(aspect_id), dict) else {}
        if not rendered:
            rendered = sections.get(aspect_id) if isinstance(sections.get(aspect_id), dict) else {}
        dimension = dimensions.get(aspect_id) if isinstance(dimensions.get(aspect_id), dict) else {}
        score = rendered.get("score")
        if score is None:
            score = dimension.get("score")
        aspects.append(
            {
                "aspect_key": aspect_id,
                "title": str(rendered.get("title") or _ASPECT_SHORT_TITLES.get(aspect_id, aspect_id)).strip(),
                "short_title": _ASPECT_SHORT_TITLES.get(aspect_id, aspect_id),
                "score": int(score) if score is not None else None,
                "content": str(rendered.get("content") or "").strip() or None,
                "risk": str(rendered.get("risk") or "").strip() or None,
                "elements_check": rendered.get("elements_check") if isinstance(rendered.get("elements_check"), dict) else {},
            }
        )
    return aspects


def _build_board_view(score_result: dict[str, Any], score_template: dict[str, Any]) -> dict[str, Any]:
    board = score_result["board"]
    symbols = board["symbols"]
    board_payload = score_template.get("board_description_payload") if isinstance(score_template.get("board_description_payload"), dict) else {}
    basis = board_payload.get("board_basis") if isinstance(board_payload.get("board_basis"), dict) else {}
    structure = score_template.get("structure") if isinstance(score_template.get("structure"), dict) else {}
    harms = score_template.get("four_harms_check") if isinstance(score_template.get("four_harms_check"), dict) else {}
    patterns = score_template.get("pattern_check") if isinstance(score_template.get("pattern_check"), dict) else {}
    palace_direction_map = {
        palace_key: direction
        for _, palace_key, _, direction in _PALACE_DISPLAY_ORDER
    }
    cells: list[dict[str, Any]] = []

    for slot_id, palace_key, title, direction in _PALACE_DISPLAY_ORDER:
        cells.append(
            {
                "slot_id": slot_id,
                "palace_key": palace_key,
                "palace_name": title,
                "direction": direction,
                "wuxing": _PALACE_WUXING_LABELS.get(palace_key),
                "is_active": slot_id != "center" and symbols["palace"] == palace_key,
            }
        )

    return {
        "center_basis": {
            "trigger": str(basis.get("trigger") or symbols["trigger"]),
        },
        "active_basis": {
            "palace": str(basis.get("palace") or symbols["palace"]),
            "direction": palace_direction_map.get(str(basis.get("palace") or symbols["palace"])),
            "god": str(basis.get("god") or symbols["god"]),
            "star": str(basis.get("star") or symbols["star"]),
            "door": str(basis.get("door") or symbols["door"]),
            "heaven_stem": str(basis.get("heaven_stem") or symbols["heaven_stem"]),
            "earth_stem": str(basis.get("earth_stem") or symbols["earth_stem"]),
        },
        "grid_cells": cells,
        "relations": {
            "palace_door_relation": str(structure.get("palace_door_relation") or "") or None,
            "stem_pair_relation": str(structure.get("stem_pair_relation") or "") or None,
        },
        "risks": {
            "four_harms": {
                "emptiness": str(harms.get("emptiness") or "无"),
                "door_pressure": str(harms.get("door_pressure") or "无"),
                "tomb": str(harms.get("tomb") or "无"),
                "punishment_hit": str(harms.get("punishment_hit") or "无"),
            },
            "pattern_flags": [str(item) for item in patterns.get("detected", []) if str(item).strip()],
            "risk_pairs": [str(item) for item in patterns.get("risk_pairs", []) if str(item).strip()],
            "structural_cap_reasons": [str(item) for item in structure.get("structural_cap_reasons", []) if str(item).strip()],
        },
    }


def _resolve_stability_render(product_render: dict[str, Any]) -> dict[str, Any]:
    sections = product_render.get("sections") if isinstance(product_render.get("sections"), dict) else {}
    stability = sections.get("stability") if isinstance(sections.get("stability"), dict) else {}
    if stability:
        return stability
    direct = product_render.get("stability") if isinstance(product_render.get("stability"), dict) else {}
    return direct


def _resolve_dimension_result(score_result: dict[str, Any], score_template: dict[str, Any]) -> dict[str, Any]:
    existing = score_template.get("dimension_score_v3") if isinstance(score_template.get("dimension_score_v3"), dict) else {}
    if isinstance(existing.get("dimensions"), dict):
        return existing

    existing = score_template.get("dimension_score_v2") if isinstance(score_template.get("dimension_score_v2"), dict) else {}
    if isinstance(existing.get("dimensions"), dict):
        return existing
    try:
        input_payload = score_result.get("input") if isinstance(score_result.get("input"), dict) else {}
        phone = str(input_payload.get("phone") or "").strip()
        gender = str(input_payload.get("gender") or "").strip()
        if phone and gender:
            return score_phone_dimensions_v3(phone, gender)
    except Exception:
        return {"dimensions": {}}
    return {"dimensions": {}}


def _build_stability_value(score_result: dict[str, Any], final_score: int) -> str:
    try:
        dimensions = score_phone_dimensions_v2(score_result["input"]["phone"], score_result["input"]["gender"])
        stability = dimensions["dimensions"]["stability"]
        stability_score = int(stability["score"])
        caps = set(stability["caps"]["applied"])
        harms = dimensions["features"]["harms"]
    except Exception:
        stability_score = final_score
        caps = set()
        harms = score_result["features"]["harms"]

    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    if stability_score >= 85 and heavy_harm_count == 0 and not caps:
        return "适合长期使用"
    if stability_score >= 72 and heavy_harm_count <= 1 and len(caps) <= 1:
        return "可以继续使用，但要注意使用方式"
    if stability_score >= 60 or heavy_harm_count <= 2:
        return "不建议继续长期主用"
    return "不建议长期使用，请尽快调整"
