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

def _pick_wealth_level(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    has_cap = bool(result["scoring"]["structural_cap_reasons"])

    if "pair_25_95" in detected or heavy_harm_count >= 2 or final_score < 45:
        return "当前不宜把它当财运主用"
    if final_score >= 80 and heavy_harm_count == 1 and not has_emptiness and not has_cap and not risk_pairs:
        return "能进财，但更吃节奏和方法"
    if heavy_harm_count >= 1 or (has_emptiness and has_cap) or len(risk_pairs) >= 2 or final_score < 65:
        return "进财波动偏明显"
    if has_emptiness or risk_pairs or has_cap or final_score < 82:
        return "能进财，但更吃节奏和方法"
    if final_score >= 96 and heavy_harm_count == 0 and not has_emptiness and not detected:
        return "财运承接感很稳"
    return "财运整体可做"


def _pick_wealth_type(result: dict[str, Any]) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    edge_flags = set(features["edge_flags"])
    tomb_layers = set(harms["tomb_layers"])

    if int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"]) >= 2 or "pair_25_95" in detected:
        return "高压消耗型"
    if harms["door_pressure"] or harms["punishment_hit"]:
        return "现金流波动型"
    if harms["tomb"] and tomb_layers.intersection({"heaven_stem", "earth_stem", "trigger"}):
        return "前强后漏型"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        return "平台承载型"
    if risk_pairs.intersection({"69", "96"}):
        return "合作分利型"
    if risk_pairs.intersection({"27", "92", "99"}) or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        return "外财扰动型"
    if board["symbols"]["door"] in {"生门", "开门"} and features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"}:
        return "资源整合型"
    if "door_emptiness" in edge_flags or result["scoring"]["structural_cap_reasons"]:
        return "平台承载型"
    return "稳守积累型"


def _wealth_manifestation(wealth_type: str) -> str:
    return {
        "稳守积累型": "进财不一定一夜冲高，但更适合靠持续积累、稳扎稳打把钱留下来。",
        "资源整合型": "更适合靠平台、项目、资源统筹和结果导向去把财路做大。",
        "平台承载型": "机会和财路不一定少，但更吃平台、环境和资源位能不能托得住。",
        "现金流波动型": "不是完全没有财，而是回款、节奏和资金衔接更容易忽上忽下。",
        "合作分利型": "财路常和合作、分工、权责或分利结构绑在一起，分钱方式很关键。",
        "外财扰动型": "外界关系、人情往来或情绪扰动，更容易把财运节奏带偏。",
        "高压消耗型": "短期也许能冲，但长期更容易在压力、反复和消耗里把财折掉。",
        "前强后漏型": "前面容易看到进账或机会，后段守财、留财和持续收益更容易松。",
    }[wealth_type]


def _wealth_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    risk_pairs = set(patterns["risk_pairs"])
    detected = set(patterns["detected"])
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if any(item["area"] == area for item in areas):
            return
        areas.append({"area": area, "reason": reason, "scenario": scenario})

    if harms["door_pressure"] or heavy_harm_count >= 1:
        add_area("现金流节奏", "进财和回款的节奏更容易被卡住，前后衔接成本偏高。", "收款、回款、周转和项目节奏上更明显。")
    if risk_pairs.intersection({"69", "96"}):
        add_area("合作分利", "合作结构、分工边界和分利方式更容易直接影响财的留存。", "合伙、签约、分账和项目协同时更关键。")
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_area("外部扰财", "人情、关系和外部诱因更容易把财运节奏带偏。", "社交支出、关系花费和被外界牵动决策时更明显。")
    if harms["tomb"]:
        add_area("守财留财", "前面能进，但后段沉淀、保有和留存更容易掉分。", "利润留存、资金沉淀和长期收益闭环上更值得看。")
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        add_area("平台资源", "财路更依赖平台和资源位，自己硬冲未必最省力。", "选平台、接资源、借势放大时更值得看清。")
    if board["symbols"]["door"] in {"生门", "开门"} or "外扩驱动" in scoring["tags"]:
        add_area("扩张节奏", "有做大和扩财的心气，但扩张节奏如果快过承接，容易放大利润波动。", "加杠杆、扩项目、做放大动作时更关键。")
    if not areas and final_score >= 80:
        add_area("持续收益", "整体财路可做，但真正拉开差距的是能不能把一波钱变成长期稳定收益。", "长期经营、复利积累和资金安排上更能看出来。")
    return areas[:3]


def _wealth_deduction_reasons(result: dict[str, Any]) -> list[str]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        add_reason("平台层有空亡，说明财路承接和资源落点不是满格。")
    if features["palace_door_relation"] not in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_reason("宫门关系不算顺，说明环境、打法和财路匹配度还不是最省力的状态。")
    if harms["door_pressure"]:
        add_reason("门迫会把进财、回款和执行成本拉高，容易出现钱来得慢、用得快的情况。")
    if harms["tomb"] and set(harms["tomb_layers"]).intersection({"trigger", "heaven_stem", "earth_stem"}):
        add_reason("结果层有入墓，说明前面能进，后段守财、留财和持续收益更容易被压分。")
    if harms["punishment_hit"]:
        add_reason("击刑会把财路节律上的反复、额外成本和内耗感放大。")
    if set(patterns["risk_pairs"]).intersection({"69", "96"}):
        add_reason("69/96 这类组合会压到合作、分工、分利和持续收益的稳定度。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_reason("外部扰动组合容易带来漏财、扰节奏或被关系牵动的财务波动。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")
    return reasons[:3]


def _wealth_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _wealth_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "关键财务节点"

    if level == "财运承接感很稳":
        return "可以长期作为财运主用，适合持续经营、积累和放大资源。"
    if level == "财运整体可做":
        return "可以继续长期使用，财运层整体可做，但关键节点仍建议留意资金节奏和承接。"
    if level == "能进财，但更吃节奏和方法":
        if final_score >= 80:
            return f"可以长期作为财运主用，但它没到满格的部分主要落在{area_text}，这些地方更值得看紧。"
        return f"可以用在财运上，但更吃节奏、方法和资金安排，尤其在{area_text}上别硬推。"
    if level == "进财波动偏明显":
        return f"如果你当前特别看重现金流稳定、合作回款和持续收益，这个号不建议当财运主用，至少要先把{area_text}看清。"
    return f"如果你很在意财运连续性、资金安全和长期收益，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_wealth_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    risk_pairs = set(patterns["risk_pairs"])
    detected = set(patterns["detected"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    level = _pick_wealth_level(result, final_score)
    wealth_type = _pick_wealth_type(result)
    watch_areas = _wealth_watch_areas(result, final_score)
    deduction_reasons = _wealth_deduction_reasons(result)

    primary_driver = "进财层"
    if harms["emptiness"] and "palace" in harms["emptiness_layers"]:
        primary_driver = "平台层"
    elif harms["tomb"] and set(harms["tomb_layers"]).intersection({"heaven_stem", "earth_stem", "trigger"}):
        primary_driver = "留财层"
    elif risk_pairs.intersection({"69", "96"}):
        primary_driver = "合作层"
    elif risk_pairs.intersection({"27", "92", "99"}) or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        primary_driver = "外扰层"
    elif heavy_harm_count >= 2:
        primary_driver = "消耗层"

    secondary_driver = "留财层" if primary_driver != "留财层" else "进财层"

    return {
        "level": level,
        "type": wealth_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _wealth_manifestation(wealth_type),
        "advice": _wealth_advice(level, result, final_score),
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
            "allowed_levels": WEALTH_LEVELS,
            "allowed_types": WEALTH_TYPES,
            "rendering_goal": "Explain whether this number matches long-term wealth use, where the money deductions fall, and which money scenes are most worth watching.",
            "client_tone": "Professional but readable. Keep the judgement practical, explain earning, keeping, cashflow and collaboration clearly, and end with a clear keep-or-adjust verdict.",
        },
    }
