from __future__ import annotations

from typing import Any

from scoring.template_parts.shared import (
    CAP_REASON_LABELS,
    CAREER_LEVELS,
    CAREER_TYPES,
    COMPONENT_LABELS,
    DOOR_PERSONALITY,
    EDGE_FLAG_LABELS,
    FORTUNE_LEVELS,
    FORTUNE_TYPES,
    GOD_TONE,
    HEALTH_LEVELS,
    HEALTH_TYPES,
    LEARNING_LEVELS,
    LEARNING_TYPES,
    MARRIAGE_LEVELS,
    MARRIAGE_TYPES,
    PATTERN_LABELS,
    RELATION_LABELS,
    RELATIONSHIP_LEVELS,
    RELATIONSHIP_TYPES,
    STABILITY_LEVELS,
    STABILITY_TYPES,
    SUITABLE_JOB_LEVELS,
    SUITABLE_JOB_TYPES,
    WEALTH_LEVELS,
    WEALTH_TYPES,
    _humanize_harm,
    _join_or_none,
    _label,
    _label_list,
    _pick_job_summary,
)

def _pick_stability_level(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    risk_pair_count = len(set(patterns["risk_pairs"]))
    has_cap = bool(result["scoring"]["structural_cap_reasons"])

    if heavy_harm_count >= 2 or "pair_25_95" in patterns["detected"] or final_score < 45:
        return "长期使用会比较折腾"
    if final_score >= 80 and heavy_harm_count == 1 and not has_emptiness and not has_cap and risk_pair_count == 0:
        return "有一定波动，但还能用"
    if heavy_harm_count >= 1 or (has_emptiness and has_cap) or risk_pair_count >= 2 or final_score < 65:
        return "波动感比较明显"
    if has_emptiness or risk_pair_count == 1 or has_cap or final_score < 80:
        return "有一定波动，但还能用"
    if final_score >= 95 and heavy_harm_count == 0 and not has_emptiness and not patterns["detected"]:
        return "整体比较稳"
    return "整体偏稳"


def _pick_stability_type(result: dict[str, Any]) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    edge_flags = set(features["edge_flags"])
    tomb_layers = set(harms["tomb_layers"])

    if int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"]) >= 2:
        return "慢性消耗型"
    if harms["door_pressure"] or "door_emptiness" in edge_flags:
        return "执行反复型"
    if harms["tomb"] and tomb_layers.intersection({"heaven_stem", "earth_stem", "trigger"}):
        return "结果发沉型"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        return "平台承载型"
    if set(patterns["risk_pairs"]).intersection({"27", "92", "99"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        return "关系牵动型"
    if set(patterns["risk_pairs"]).intersection({"69", "96"}) or result["scoring"]["structural_cap_reasons"]:
        return "前强后弱型"
    if features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"} and features["stem_pair_relation"] in {"heaven_generates_earth", "earth_generates_heaven", "same_element"}:
        return "整体顺接型"
    return "外强内虚型"


def _stability_manifestation(stability_type: str) -> str:
    return {
        "整体顺接型": "平台、执行和结果层衔接较顺，好的状态相对更容易留住。",
        "平台承载型": "机会和动作不一定少，但平台承接和长期稳定度不是满格。",
        "执行反复型": "推进过程中容易来回调整，做着做着会感觉变费劲。",
        "结果发沉型": "前面能起，后面收口、沉淀和保有度一般。",
        "外强内虚型": "表面能量不低，但长期使用会感觉不够扎实。",
        "关系牵动型": "容易被关系、人事、情绪或外部扰动带节奏。",
        "慢性消耗型": "短期不一定完全崩，但长期用着会累、会耗。",
        "前强后弱型": "起势不差，但越往后越容易掉，后段稳定度不如前段。",
    }[stability_type]


def _stability_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]

    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    risk_pairs = set(patterns["risk_pairs"])
    detected = set(patterns["detected"])
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str) -> None:
        if any(item["area"] == area for item in areas):
            return
        areas.append({"area": area, "reason": reason})

    if heavy_harm_count >= 1 or scoring["structural_cap_reasons"] or features["palace_door_relation"] not in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_area("事业", "推进、落地和后段承接更容易成为扣分点。")
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_area("婚姻关系", "关系扰动和情绪拉扯更容易放大波动。")
    if heavy_harm_count >= 2 or risk_pairs.intersection({"69", "96"}) or final_score < 60:
        add_area("财运", "资金节奏、合作稳定度和持续收益更容易受影响。")
    if heavy_harm_count >= 2 or symbols["star"] == "天芮" or symbols["door"] == "死门" or has_emptiness:
        add_area("健康精力", "长期消耗、恢复速度和稳定节律更值得留意。")
    if harms["door_pressure"] or harms["tomb"] or has_emptiness:
        add_area("学习沉淀", "持续专注、复盘沉淀和后段稳定输出容易被拉低。")

    if not areas and final_score >= 80:
        add_area("关键阶段", "整体能长期用，但关键阶段仍要看承接和节奏。")
    return areas[:3]


def _stability_deduction_reasons(result: dict[str, Any]) -> list[str]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        add_reason("平台层有空亡，说明承接感和长期稳定度会被压分。")
    if harms["door_pressure"]:
        add_reason("宫门相克，说明执行推进过程更容易有阻力和反复。")
    if harms["tomb"] and set(harms["tomb_layers"]).intersection({"trigger", "heaven_stem", "earth_stem"}):
        add_reason("结果层有入墓，说明前面能起，但后段收口、沉淀和保有度会被压分。")
    if harms["punishment_hit"]:
        add_reason("击刑会带来内耗、拉扯和稳定节律上的反复。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_reason("关系扰动组合会拉低婚姻和人际层面的稳定感。")
    if set(patterns["risk_pairs"]).intersection({"69", "96"}):
        add_reason("69/96 这类风险组合会压低权责、合作和持续收益的稳定性。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")
    return reasons[:3]


def _stability_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _stability_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "关键场景"

    if final_score == 100:
        return "这个号整体非常好，稳定性很完整，建议坚持长期使用。"
    if level == "整体比较稳":
        if final_score >= 95:
            return "可以长期使用，整体承接很完整；如果这是你的常用号，建议坚持使用。"
        return "可以长期使用，重点发挥长期积累和持续落地的优势。"
    if level == "整体偏稳":
        return f"可以继续长期使用，但在{area_text}上仍建议多看一眼节奏和承接。"
    if level == "有一定波动，但还能用":
        if final_score >= 80:
            return f"可以继续长期使用，但它没到满分的部分主要落在{area_text}；如果你特别看重这些方面，就别把它当成完全无代价的配置。"
        return f"可以继续使用，但不建议在{area_text}上长期硬扛；如果这些方面正是你最在意的，再评估是否继续长期主用。"
    if level == "波动感比较明显":
        return f"不建议继续长期主用，尤其如果你当前特别看重{area_text}，这些地方会更容易把问题放大。"
    return f"不建议继续长期使用，建议优先调整；尤其如果你当前特别看重{area_text}，这部分扣分会更直接地放大问题。"


def _build_stability_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    level = _pick_stability_level(result, final_score)
    stability_type = _pick_stability_type(result)
    watch_areas = _stability_watch_areas(result, final_score)
    deduction_reasons = _stability_deduction_reasons(result)
    primary_driver = "执行层"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        primary_driver = "平台层"
    elif harms["tomb"] and set(harms["tomb_layers"]).intersection({"heaven_stem", "earth_stem", "trigger"}):
        primary_driver = "结果层"
    elif set(patterns["risk_pairs"]).intersection({"27", "92", "99"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        primary_driver = "关系层"

    secondary_driver = "结果层" if primary_driver != "结果层" else "执行层"

    return {
        "level": level,
        "type": stability_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _stability_manifestation(stability_type),
        "advice": _stability_advice(level, result, final_score),
        "score_gap": max(0, 100 - final_score),
        "watch_areas": watch_areas,
        "deduction_reasons": deduction_reasons,
        "facts": {
            "score_after_structural_cap": final_score,
            "confidence": scoring["confidence"],
            "palace_door_relation": _label(RELATION_LABELS, features["palace_door_relation"]),
            "stem_pair_relation": _label(RELATION_LABELS, features["stem_pair_relation"]),
            "four_harms": {
                "emptiness": _humanize_harm(harms["emptiness"], harms["emptiness_layers"], labels),
                "door_pressure": _humanize_harm(harms["door_pressure"], [], labels),
                "tomb": _humanize_harm(harms["tomb"], harms["tomb_layers"], labels),
                "punishment_hit": _humanize_harm(harms["punishment_hit"], harms["punishment_layers"], labels),
            },
            "pattern_flags": _label_list(PATTERN_LABELS, patterns["detected"]),
            "risk_pairs": patterns["risk_pairs"],
            "structural_cap_reasons": _label_list(CAP_REASON_LABELS, scoring["structural_cap_reasons"]),
            "tags": scoring["tags"],
        },
        "model_pack": {
            "allowed_levels": STABILITY_LEVELS,
            "allowed_types": STABILITY_TYPES,
            "rendering_goal": "Do not repeat the four-harms checklist line by line in the main paragraph. Use the facts to explain what kind of stability this number has, how that tends to manifest, and what the practical suggestion is.",
            "client_tone": "Professional but readable. Use a light Qimen flavor, not heavy jargon stacking.",
        },
    }
