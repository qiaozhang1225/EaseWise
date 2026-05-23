from __future__ import annotations

from typing import Any

from scoring.payloads.shared import (
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

def _pick_marriage_level(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_cap = bool(result["scoring"]["structural_cap_reasons"])
    relationship_disturbance = bool(detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}))
    control_strain = bool(detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}))

    if "pair_25_95" in detected or heavy_harm_count >= 2 or final_score < 45:
        return "当前不宜在婚姻上硬扛"
    if relationship_disturbance and (control_strain or heavy_harm_count >= 1 or final_score < 75):
        return "关系扰动偏明显"
    if heavy_harm_count >= 1 or has_cap or control_strain or relationship_disturbance or final_score < 82:
        return "能走下去，但更吃相处方式"
    if final_score >= 96 and heavy_harm_count == 0 and not has_cap and not detected:
        return "婚姻承接感很稳"
    return "婚姻整体可守"


def _pick_marriage_type(result: dict[str, Any]) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    tomb_layers = set(harms["tomb_layers"])

    if "pair_25_95" in detected or heavy_harm_count >= 2:
        return "高压消耗型"
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        return "桃花扰动型"
    if detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        return "权责失衡型"
    if harms["door_pressure"] or harms["punishment_hit"]:
        return "沟通拉扯型"
    if harms["tomb"] and tomb_layers.intersection({"trigger", "heaven_stem", "earth_stem"}):
        return "前合后松型"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        return "外界牵动型"
    if features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"} and features["stem_pair_relation"] in {"heaven_generates_earth", "earth_generates_heaven", "same_element"}:
        return "稳定陪伴型"
    return "慢热磨合型"


def _marriage_manifestation(marriage_type: str) -> str:
    return {
        "稳定陪伴型": "关系节奏相对平稳，长期陪伴感和过日子的承接力更容易养出来。",
        "慢热磨合型": "不是一上来就特别黏，但只要相处方式对，关系可以慢慢往稳里走。",
        "沟通拉扯型": "遇到分歧和情绪点时，更容易话赶话、各执一词，沟通成本偏高。",
        "桃花扰动型": "外界诱因、情绪摇摆或关系边界问题，更容易把婚姻层搅动起来。",
        "权责失衡型": "关系里容易出现谁更强势、谁来承担、谁说了算的拉扯。",
        "外界牵动型": "婚姻状态比较吃环境、人事和外部节奏，不是关起门来就能完全稳住。",
        "高压消耗型": "短期也许还能顶住，但长期相处更容易累、耗，反复翻旧账。",
        "前合后松型": "前面容易接上，后段真正进入长期磨合和家庭责任时更容易松、散或接不住。",
    }[marriage_type]


def _marriage_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if any(item["area"] == area for item in areas):
            return
        areas.append({"area": area, "reason": reason, "scenario": scenario})

    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_area("边界信任", "关系里的边界感、安全感和信任感更容易被外部扰动放大。", "异性往来、社交边界和伴侣安全感相关话题时更敏感。")
        add_area("外部诱因", "外界的人和事更容易把婚姻层的情绪与节奏带偏。", "社交活跃、桃花场景或关系敏感期时更明显。")
    if detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        add_area("权责分工", "关系里谁主导、谁承担、谁退让，更容易成为隐性拉扯点。", "结婚后分工、经济安排和家庭责任落位时更关键。")
    if harms["door_pressure"] or harms["punishment_hit"]:
        add_area("沟通情绪", "一到分歧点就更容易话赶话，沟通成本偏高。", "争执、冷战、敏感话题和情绪累积时更容易放大。")
    if harms["tomb"]:
        add_area("长期承诺", "前面能接上，但进入长期责任和沉淀阶段时更容易发沉。", "谈婚论嫁、婚后过日子、异地磨合或家庭责任加重时更值得看。")
    if heavy_harm_count >= 2 or "pair_25_95" in detected:
        add_area("压力消耗", "高压一来，关系里的耐受度和承接力更容易被持续消耗。", "经济压力、家庭压力和长期硬扛阶段更明显。")
    if harms["emptiness"] or features["palace_door_relation"] not in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_area("相处节奏", "关系并非完全接不住，但彼此接法和相处节奏不是满格。", "热恋转长期、同居或婚后日常时更能看出来。")
    if patterns["neutral_pairs"] and not areas:
        add_area("长期磨合", "这个号有一定黏合点，但能不能走稳，还是要看后续磨合质量。", "从有感觉走向长期陪伴和日常过日子时更值得观察。")
    if not areas and final_score >= 80:
        add_area("日常磨合", "整体不算差，但婚姻层真正拉开差距的，还是长期相处里的细节。", "长期陪伴、生活习惯和情绪接法上更能看出差异。")
    return areas[:3]


def _marriage_deduction_reasons(result: dict[str, Any]) -> list[str]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        add_reason("关系承接层有空亡，说明婚姻里的落点感和安定感不是满格。")
    if features["palace_door_relation"] not in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_reason("宫门关系不算顺，说明彼此接法和长期相处节奏还不是最省心的配置。")
    if harms["door_pressure"]:
        add_reason("门迫会把关系推进和沟通成本拉高，容易出现明明想靠近却越说越拧的情况。")
    if harms["tomb"] and set(harms["tomb_layers"]).intersection({"trigger", "heaven_stem", "earth_stem"}):
        add_reason("入墓会让情绪和问题更容易压着不说，进入长期责任阶段时更容易发沉。")
    if harms["punishment_hit"]:
        add_reason("击刑会把婚姻里的情绪反复、内耗和拉扯感放大。")
    if set(patterns["risk_pairs"]).intersection({"69", "96"}):
        add_reason("69/96 这类组合容易把关系里的强弱、控制感和分工失衡放大。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_reason("桃花扰动或关系反复的组合，会拉低婚姻层的边界感和稳定感。")
    if "pair_25_95" in patterns["detected"]:
        add_reason("25/95 这类重风险组合，会把婚姻层的长期承载压得更重。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")
    return reasons[:3]


def _marriage_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _marriage_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "相处节奏"

    if level == "婚姻承接感很稳":
        return "如果你看重婚姻关系和长期陪伴，这个号可以长期坚持使用。"
    if level == "婚姻整体可守":
        return f"可以继续长期使用，婚姻层整体可守，但关键节点仍建议留意{area_text}。"
    if level == "能走下去，但更吃相处方式":
        if final_score >= 80:
            return f"可以继续长期使用，但它没到满格的部分主要落在{area_text}，如果你很看重婚姻质量，这些地方更值得经营。"
        return f"可以用在婚姻关系上，但更吃相处方式和边界拿捏，尤其在{area_text}上别顺其自然。"
    if level == "关系扰动偏明显":
        return f"如果你当前特别看重婚姻稳定、伴侣关系和长期配合，这个号不建议当婚姻主用，至少要先把{area_text}看清。"
    return f"如果你很在意婚姻、家庭稳定和长期陪伴，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_marriage_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    level = _pick_marriage_level(result, final_score)
    marriage_type = _pick_marriage_type(result)
    watch_areas = _marriage_watch_areas(result, final_score)
    deduction_reasons = _marriage_deduction_reasons(result)

    primary_driver = "相处层"
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        primary_driver = "边界层"
    elif detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        primary_driver = "权责层"
    elif harms["tomb"]:
        primary_driver = "承诺层"
    elif heavy_harm_count >= 2 or "pair_25_95" in detected:
        primary_driver = "消耗层"
    elif harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        primary_driver = "承接层"

    secondary_driver = "相处层"
    if primary_driver != "承诺层" and harms["tomb"]:
        secondary_driver = "承诺层"
    elif primary_driver != "沟通层" and (harms["door_pressure"] or harms["punishment_hit"]):
        secondary_driver = "沟通层"
    elif primary_driver != "边界层" and (detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"})):
        secondary_driver = "边界层"

    return {
        "level": level,
        "type": marriage_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _marriage_manifestation(marriage_type),
        "advice": _marriage_advice(level, result, final_score),
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
            "neutral_pairs": patterns["neutral_pairs"],
            "structural_cap_reasons": _label_list(CAP_REASON_LABELS, scoring["structural_cap_reasons"]),
            "tags": scoring["tags"],
        },
        "model_pack": {
            "allowed_levels": MARRIAGE_LEVELS,
            "allowed_types": MARRIAGE_TYPES,
            "rendering_goal": "Explain whether this number matches long-term marriage use, where the relationship deductions fall, and what kind of long-term relationship friction is most worth watching.",
            "client_tone": "Professional but readable. Keep a teacher-like tone, explain relationship structure, and end with a clear keep-or-adjust verdict.",
        },
    }
