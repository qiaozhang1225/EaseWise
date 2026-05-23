from __future__ import annotations

from typing import Any

from scoring.aspect_scores import build_aspect_scores
from scoring.payloads.board_description import (
    _build_board_description_payload,
    _build_four_harms_check,
    _build_pattern_check,
    _build_structure,
)
from scoring.payloads.career import _build_career_payload
from scoring.payloads.fortune import _build_fortune_payload
from scoring.payloads.health import _build_health_payload
from scoring.payloads.learning import _build_learning_payload
from scoring.payloads.marriage import _build_marriage_payload
from scoring.payloads.personality import build_personality_payload
from scoring.payloads.relationship import _build_relationship_payload
from scoring.payloads.stability import _build_stability_payload
from scoring.payloads.suitable_job import _build_suitable_job_payload
from scoring.payloads.wealth import _build_wealth_payload
from scoring.payloads.shared import (
    CAP_REASON_LABELS,
    COMPONENT_LABELS,
    COMPONENT_ORDER,
    RELATION_LABELS,
    _humanize_harm,
    _join_or_none,
)


def _aspect(key: str, title: str, summary: str, signals: list[str]) -> dict[str, Any]:
    return {
        "key": key,
        "title": title,
        "summary": summary,
        "signals": [signal for signal in signals if signal],
    }


def _watch_areas_text(payload: dict[str, Any]) -> str:
    areas = [item["area"] for item in payload.get("watch_areas", [])[:2] if item.get("area")]
    return "、".join(areas)


def _build_review_outline(
    result: dict[str, Any],
    final_score: int,
    *,
    personality_payload: dict[str, Any],
    wealth_payload: dict[str, Any],
    career_payload: dict[str, Any],
    marriage_payload: dict[str, Any],
    fortune_payload: dict[str, Any],
    health_payload: dict[str, Any],
    relationship_payload: dict[str, Any],
    learning_payload: dict[str, Any],
    suitable_job_payload: dict[str, Any],
    stability_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    board = result["board"]
    features = result["features"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    labels = board["labels"]
    harms = features["harms"]
    patterns = features["patterns"]

    relation = RELATION_LABELS.get(features["palace_door_relation"], features["palace_door_relation"])
    stem_relation = RELATION_LABELS.get(features["stem_pair_relation"], features["stem_pair_relation"])
    risk_pairs_text = _join_or_none(patterns["risk_pairs"])
    tags_text = _join_or_none(scoring["tags"])
    cap_reasons_text = _join_or_none([CAP_REASON_LABELS.get(reason, reason) for reason in scoring["structural_cap_reasons"]])
    emptiness_text = _humanize_harm(harms["emptiness"], harms["emptiness_layers"], labels)
    door_pressure_text = _humanize_harm(harms["door_pressure"], [], labels)
    tomb_text = _humanize_harm(harms["tomb"], harms["tomb_layers"], labels)
    punishment_text = _humanize_harm(harms["punishment_hit"], harms["punishment_layers"], labels)

    personality_focus = _watch_areas_text(personality_payload)
    wealth_focus = _watch_areas_text(wealth_payload)
    career_focus = _watch_areas_text(career_payload)
    marriage_focus = _watch_areas_text(marriage_payload)
    fortune_focus = _watch_areas_text(fortune_payload)
    health_focus = _watch_areas_text(health_payload)
    relationship_focus = _watch_areas_text(relationship_payload)
    learning_focus = _watch_areas_text(learning_payload)
    suitable_job_focus = _watch_areas_text(suitable_job_payload)
    stability_focus = _watch_areas_text(stability_payload)

    return [
        _aspect(
            "personality",
            "性格",
            f"{personality_payload['level']}，主轴更接近{personality_payload['type']}。",
            [f"门位：{symbols['door']}", f"神位：{symbols['god']}", f"星位：{symbols['star']}", f"主要留意：{personality_focus}"],
        ),
        _aspect(
            "wealth",
            "财运",
            f"{wealth_payload['level']}，主轴更接近{wealth_payload['type']}。",
            [f"宫门关系：{relation}", f"风险标签：{tags_text}", f"主要留意：{wealth_focus}"],
        ),
        _aspect(
            "career",
            "事业",
            f"{career_payload['level']}，主轴更接近{career_payload['type']}。",
            [f"宫门关系：{relation}", f"后两干关系：{stem_relation}", f"主要留意：{career_focus}"],
        ),
        _aspect(
            "marriage",
            "婚姻",
            f"{marriage_payload['level']}，主轴更接近{marriage_payload['type']}。",
            [f"宫门关系：{relation}", f"风险组合：{risk_pairs_text}", f"主要留意：{marriage_focus}"],
        ),
        _aspect(
            "fortune",
            "运势",
            f"{fortune_payload['level']}，主轴更接近{fortune_payload['type']}。",
            [f"风险标签：{tags_text}", f"结构封顶：{cap_reasons_text}", f"主要留意：{fortune_focus}"],
        ),
        _aspect(
            "health",
            "健康",
            f"{health_payload['level']}，主轴更接近{health_payload['type']}。",
            [f"空亡：{emptiness_text}", f"入墓：{tomb_text}", f"击刑：{punishment_text}", f"主要留意：{health_focus}"],
        ),
        _aspect(
            "relationship",
            "人际感情",
            f"{relationship_payload['level']}，主轴更接近{relationship_payload['type']}。",
            [f"宫门关系：{relation}", f"风险标签：{tags_text}", f"主要留意：{relationship_focus}"],
        ),
        _aspect(
            "learning",
            "学习",
            f"{learning_payload['level']}，主轴更接近{learning_payload['type']}。",
            [f"星位：{symbols['star']}", f"神位：{symbols['god']}", f"主要留意：{learning_focus}"],
        ),
        _aspect(
            "suitable_job",
            "适合职业",
            f"{suitable_job_payload['level']}，主轴更接近{suitable_job_payload['type']}。",
            [
                f"门位：{symbols['door']}",
                f"神星门：{symbols['god']} / {symbols['star']} / {symbols['door']}",
                f"主要留意：{suitable_job_focus or suitable_job_payload['summary']}",
            ],
        ),
        _aspect(
            "stability",
            "稳定性",
            f"{stability_payload['level']}，主轴更接近{stability_payload['type']}。",
            [
                f"空亡：{emptiness_text}",
                f"门迫：{door_pressure_text}",
                f"入墓：{tomb_text}",
                f"击刑：{punishment_text}",
                f"主要留意：{stability_focus}",
            ],
        ),
    ]


def _build_components(base_scoring: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"key": key, "label": COMPONENT_LABELS[key], "value": base_scoring["components"][key]}
        for key in COMPONENT_ORDER
    ]


def build_score_template(result: dict[str, Any]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    labels = board["labels"]
    harms = features["harms"]
    patterns = features["patterns"]
    base_scoring = result["scoring"]
    final_score = base_scoring["score_after_structural_cap"]
    aspect_scores = build_aspect_scores(result)

    personality_payload = build_personality_payload(result, final_score, labels)
    wealth_payload = _build_wealth_payload(result, final_score, labels)
    career_payload = _build_career_payload(result, final_score, labels)
    marriage_payload = _build_marriage_payload(result, final_score, labels)
    fortune_payload = _build_fortune_payload(result, final_score, labels)
    health_payload = _build_health_payload(result, final_score, labels)
    relationship_payload = _build_relationship_payload(result, final_score, labels)
    learning_payload = _build_learning_payload(result, final_score, labels)
    suitable_job_payload = _build_suitable_job_payload(result, final_score, labels)
    stability_payload = _build_stability_payload(result, final_score, labels)

    wealth_payload["score"] = aspect_scores["wealth"]["score"]
    wealth_payload["grade"] = aspect_scores["wealth"]["grade"]
    career_payload["score"] = aspect_scores["career"]["score"]
    career_payload["grade"] = aspect_scores["career"]["grade"]
    marriage_payload["score"] = aspect_scores["love"]["score"]
    marriage_payload["grade"] = aspect_scores["love"]["grade"]
    health_payload["score"] = aspect_scores["health"]["score"]
    health_payload["grade"] = aspect_scores["health"]["grade"]
    relationship_payload["score"] = aspect_scores["social"]["score"]
    relationship_payload["grade"] = aspect_scores["social"]["grade"]
    learning_payload["score"] = aspect_scores["acad"]["score"]
    learning_payload["grade"] = aspect_scores["acad"]["grade"]
    stability_payload["score"] = base_scoring["score_after_structural_cap"]
    stability_payload["grade"] = None

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
        "four_harms_check": _build_four_harms_check(harms, labels),
        "pattern_check": _build_pattern_check(patterns, features["edge_flags"]),
        "board_description_payload": _build_board_description_payload(result, final_score, labels),
        "aspect_scores": aspect_scores,
        "personality_payload": personality_payload,
        "wealth_payload": wealth_payload,
        "career_payload": career_payload,
        "marriage_payload": marriage_payload,
        "fortune_payload": fortune_payload,
        "health_payload": health_payload,
        "relationship_payload": relationship_payload,
        "learning_payload": learning_payload,
        "suitable_job_payload": suitable_job_payload,
        "stability_payload": stability_payload,
        "review_outline": _build_review_outline(
            result,
            final_score,
            personality_payload=personality_payload,
            wealth_payload=wealth_payload,
            career_payload=career_payload,
            marriage_payload=marriage_payload,
            fortune_payload=fortune_payload,
            health_payload=health_payload,
            relationship_payload=relationship_payload,
            learning_payload=learning_payload,
            suitable_job_payload=suitable_job_payload,
            stability_payload=stability_payload,
        ),
    }


def _render_score_card(card: dict[str, Any]) -> str:
    score_summary = card["score_summary"]
    structure = card["structure"]
    patterns = card["pattern_check"]
    outline = card["review_outline"]

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
        "",
        "十方面模板",
    ]
    for index, aspect in enumerate(outline, start=1):
        lines.append(f"{index}. {aspect['title']}")
        lines.append(f"- 结论：{aspect['summary']}")
        lines.append(f"- 参考：{_join_or_none(aspect['signals'])}")
    return "\n".join(lines)


def render_score_template(result: dict[str, Any]) -> str:
    return _render_score_card(build_score_template(result))


def build_skill_package(result: dict[str, Any]) -> dict[str, Any]:
    from scoring.services.bundle_service import build_scoring_bundle

    return build_scoring_bundle(result, include_markdown=True)
