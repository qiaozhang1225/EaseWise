from __future__ import annotations

from typing import Any

from scoring.dimensions.aspect_scores import build_aspect_scores
from scoring.total_score.labels import COMPONENT_LABELS, COMPONENT_ORDER, _join_or_none
from scoring.total_score.score_facts import build_phone_summary_facts, _build_pattern_check, _build_structure


def _build_components(base_scoring: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"key": key, "label": COMPONENT_LABELS[key], "value": base_scoring["components"][key]}
        for key in COMPONENT_ORDER
    ]


def build_score_template(result: dict[str, Any]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    base_scoring = result["scoring"]
    final_score = base_scoring["score_after_structural_cap"]
    aspect_scores = build_aspect_scores(result)

    return {
        "meta": {
            "phone": result["input"]["phone"],
            "gender": result["input"]["gender"],
            "last7": board["last7"],
            "rules_version": result["rules_version"],
        },
        "score_summary": {
            "code_base_score": base_scoring["raw_score"],
            "score_after_structural_cap": base_scoring["score_after_structural_cap"],
            "structural_cap": base_scoring["structural_cap"],
            "final_score": final_score,
            "confidence": base_scoring["confidence"],
            "tags": base_scoring["tags"],
        },
        "components": _build_components(base_scoring),
        "structure": _build_structure(features, base_scoring),
        "four_harms_check": {
            "emptiness": "有" if harms["emptiness"] else "无",
            "door_pressure": "有" if harms["door_pressure"] else "无",
            "tomb": "有" if harms["tomb"] else "无",
            "punishment_hit": "有" if harms["punishment_hit"] else "无",
        },
        "pattern_check": _build_pattern_check(patterns, features["edge_flags"]),
        "phone_summary_facts": build_phone_summary_facts(result, final_score),
        "aspect_scores": aspect_scores,
        "aspect_templates": {
            key: {"score": value["score"], "grade": value["grade"]}
            for key, value in aspect_scores.items()
        },
        "board_facts": {
            "last7": board["last7"],
            "symbols": board["symbols"],
        },
    }


def _render_score_card(card: dict[str, Any]) -> str:
    score_summary = card["score_summary"]
    structure = card["structure"]
    patterns = card["pattern_check"]

    lines = [
        "号码评估概览",
        f"- 综合评分：{score_summary['final_score']}/100",
        f"- 代码原始分：{score_summary['code_base_score']}",
        f"- 结构封顶后分数：{score_summary['score_after_structural_cap']}",
        f"- 结构封顶上限：{score_summary['structural_cap']}",
        f"- 置信度：{score_summary['confidence']}",
        f"- 风险标签：{_join_or_none(score_summary['tags'])}",
        f"- 宫门关系：{structure['palace_door_relation']}",
        f"- 后两干关系：{structure['stem_pair_relation']}",
        f"- 结构封顶原因：{_join_or_none(structure['structural_cap_reasons'])}",
        f"- 特殊组合：{_join_or_none(patterns['detected'])}",
        f"- 合十格：{_join_or_none(patterns['neutral_pairs'])}",
    ]
    return "\n".join(lines)


def render_score_template(result: dict[str, Any]) -> str:
    return _render_score_card(build_score_template(result))


def build_skill_package(result: dict[str, Any]) -> dict[str, Any]:
    from scoring.total_score.bundle import build_scoring_bundle

    return build_scoring_bundle(result, include_markdown=True)
