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

def _pick_career_level(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    risk_pair_count = len(set(patterns["risk_pairs"]))
    has_cap = bool(result["scoring"]["structural_cap_reasons"])
    favorable_relation = features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"}

    if heavy_harm_count >= 2 or "pair_25_95" in patterns["detected"] or final_score < 45:
        return "当前不宜硬冲"
    if final_score >= 80 and heavy_harm_count == 1 and not has_emptiness and not has_cap and risk_pair_count == 0:
        return "能做，但更吃环境和方式"
    if heavy_harm_count >= 1 or (has_emptiness and has_cap) or risk_pair_count >= 2 or final_score < 65:
        return "推进阻力偏明显"
    if has_emptiness or risk_pair_count == 1 or has_cap or not favorable_relation or final_score < 80:
        return "能做，但更吃环境和方式"
    if final_score >= 95 and heavy_harm_count == 0 and not has_emptiness and not patterns["detected"]:
        return "事业推进感很稳"
    return "事业整体可推"


def _pick_career_type(result: dict[str, Any]) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    edge_flags = set(features["edge_flags"])
    tomb_layers = set(harms["tomb_layers"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])

    if heavy_harm_count >= 2:
        return "高压消耗型"
    if set(patterns["risk_pairs"]).intersection({"69", "96"}) or result["scoring"]["structural_cap_reasons"]:
        return "权责压力型"
    if harms["door_pressure"] or "door_emptiness" in edge_flags:
        return "执行反复型"
    if harms["tomb"] and tomb_layers.intersection({"heaven_stem", "earth_stem", "trigger"}):
        return "后段掉速型"
    if set(patterns["risk_pairs"]).intersection({"27", "92", "99"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        return "人事牵动型"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        return "平台承载型"
    if features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"} and features["stem_pair_relation"] in {"heaven_generates_earth", "earth_generates_heaven", "same_element"}:
        return "稳推积累型"
    return "外强内虚型"


def _career_manifestation(career_type: str) -> str:
    return {
        "稳推积累型": "平台和动作的配合度可以，事业更适合持续累积、慢慢做出结果。",
        "平台承载型": "事情不是不能做，但平台匹配和承载力更决定事业上限。",
        "执行反复型": "明明在推进，但过程中容易反复调整，推进成本偏高。",
        "后段掉速型": "前段能起势，但后段收口、结果沉淀和保有度偏弱。",
        "权责压力型": "合作、分工和权责边界处理不好时，更容易丢分。",
        "人事牵动型": "团队关系、人事情绪和外部扰动更容易影响事业推进。",
        "高压消耗型": "短期也许能顶，但长期冲刺更容易越做越累、越做越耗。",
        "外强内虚型": "表面上有推进感，但长期稳定承接还不够扎实。",
    }[career_type]


def _career_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    favorable_relation = features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"}
    risk_pairs = set(patterns["risk_pairs"])
    detected = set(patterns["detected"])
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if any(item["area"] == area for item in areas):
            return
        areas.append({"area": area, "reason": reason, "scenario": scenario})

    if harms["emptiness"] and "palace" in harms["emptiness_layers"] or not favorable_relation:
        add_area("平台匹配", "平台承载和环境匹配更容易成为扣分点。", "换岗、跳槽、选平台时更值得看清。")
    if harms["door_pressure"] or heavy_harm_count >= 1:
        add_area("推进效率", "推进过程中更容易出现卡点、反复和额外成本。", "项目推进、执行落地和阶段目标上更明显。")
    if set(risk_pairs).intersection({"69", "96"}):
        add_area("合作权责", "分工、权责边界和合作结构更容易影响事业表现。", "合伙、签约、带团队或跨部门合作时更关键。")
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_area("人事协同", "团队关系、人事情绪和沟通氛围更容易放大波动。", "汇报沟通、团队配合和人际协同时更关键。")
    if harms["tomb"]:
        add_area("成果沉淀", "前面能起，但后段收口、结果沉淀和保有度更容易掉分。", "升职答卷、长期项目和结果闭环上更值得重视。")
    if heavy_harm_count >= 2 or symbols["star"] == "天芮" or symbols["door"] == "死门":
        add_area("压力消耗", "长期冲刺时更容易累、容易耗。", "高压岗位、密集冲刺和长期硬顶时更明显。")

    if not areas and final_score >= 80:
        add_area("关键节点", "整体能推，但关键阶段仍要看节奏和承接。", "晋升、转岗和项目收口时更值得看。")
    return areas[:3]


def _career_deduction_reasons(result: dict[str, Any]) -> list[str]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        add_reason("平台层有空亡，说明职业承载力和长期落点会被压分。")
    if features["palace_door_relation"] not in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_reason("宫门关系不算顺，说明环境与做事方式的匹配度还不是满格。")
    if harms["door_pressure"]:
        add_reason("门迫会把推进成本拉高，容易出现做事不轻松、推进不够顺的情况。")
    if harms["tomb"] and set(harms["tomb_layers"]).intersection({"trigger", "heaven_stem", "earth_stem"}):
        add_reason("结果层有入墓，说明前面能起，但后段收口、成果沉淀和保有度会被压分。")
    if harms["punishment_hit"]:
        add_reason("击刑会带来事业节律上的反复、内耗和不必要拉扯。")
    if set(patterns["risk_pairs"]).intersection({"69", "96"}):
        add_reason("69/96 这类组合会压到合作边界、权责分工和持续收益的稳定度。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_reason("人事扰动组合会拉低团队协同和事业推进的稳定感。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")
    return reasons[:3]


def _career_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _career_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "关键节点"

    if level == "事业推进感很稳":
        return "可以长期作为事业主用，适合持续积累和稳定发力。"
    if level == "事业整体可推":
        return "可以长期作为事业主用，但关键节点仍建议观察平台承接和推进节奏。"
    if level == "能做，但更吃环境和方式":
        if final_score >= 80:
            return f"可以长期作为事业主用，但它没到满格的部分主要落在{area_text}，这些部分更值得留意。"
        return f"可以用在事业上，但更吃平台、方法和配合，尤其在{area_text}上别用蛮力硬推。"
    if level == "推进阻力偏明显":
        return f"可以使用，但如果你当前特别看重{area_text}，建议先评估推进方式，再决定要不要硬推。"
    return f"建议优先调整事业使用策略，尤其如果你当前特别看重{area_text}，这些扣分会更直接放大问题。"


def _build_career_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    level = _pick_career_level(result, final_score)
    career_type = _pick_career_type(result)
    watch_areas = _career_watch_areas(result, final_score)
    deduction_reasons = _career_deduction_reasons(result)
    primary_driver = "推进层"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        primary_driver = "平台层"
    elif harms["tomb"] and set(harms["tomb_layers"]).intersection({"heaven_stem", "earth_stem", "trigger"}):
        primary_driver = "成果层"
    elif set(patterns["risk_pairs"]).intersection({"69", "96"}):
        primary_driver = "权责层"
    elif set(patterns["risk_pairs"]).intersection({"27", "92", "99"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        primary_driver = "人事层"

    secondary_driver = "成果层" if primary_driver != "成果层" else "推进层"

    return {
        "level": level,
        "type": career_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _career_manifestation(career_type),
        "advice": _career_advice(level, result, final_score),
        "score_gap": max(0, 100 - final_score),
        "watch_areas": watch_areas,
        "deduction_reasons": deduction_reasons,
        "facts": {
            "score_after_structural_cap": final_score,
            "confidence": scoring["confidence"],
            "palace_door_relation": _label(RELATION_LABELS, features["palace_door_relation"]),
            "stem_pair_relation": _label(RELATION_LABELS, features["stem_pair_relation"]),
            "door": symbols["door"],
            "star": symbols["star"],
            "god": symbols["god"],
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
            "allowed_levels": CAREER_LEVELS,
            "allowed_types": CAREER_TYPES,
            "rendering_goal": "Explain whether career can be pushed long-term, where the missing points are deducted, and which career scenes are most worth watching.",
            "client_tone": "Professional but readable. Keep the judgement practical and avoid mystical stacking.",
        },
    }
