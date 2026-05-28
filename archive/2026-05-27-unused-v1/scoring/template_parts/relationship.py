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

def _pick_relationship_level(result: dict[str, Any], final_score: int) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    neutral_pairs = set(patterns["neutral_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_cap = bool(result["scoring"]["structural_cap_reasons"])
    relationship_disturbance = bool(detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}))
    control_strain = bool(detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}))

    if final_score >= 95 and heavy_harm_count == 0 and not has_cap and not relationship_disturbance and (symbols["god"] in {"六合", "太阴"} or neutral_pairs):
        return "人际感情承接感很稳"
    if "pair_25_95" in detected or heavy_harm_count >= 3 or final_score < 45:
        return "当前不宜在人际感情上硬扛"
    if relationship_disturbance and (control_strain or heavy_harm_count >= 1 or final_score < 75):
        return "人际感情扰动偏明显"
    if heavy_harm_count >= 1 or has_cap or control_strain or relationship_disturbance or final_score < 80:
        return "有来有往，但更吃分寸和边界"
    return "人际感情整体可守"


def _pick_relationship_type(result: dict[str, Any]) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    neutral_pairs = set(patterns["neutral_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])

    if "pair_25_95" in detected or heavy_harm_count >= 2:
        return "外热内耗型"
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        return "桃花牵动型"
    if detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or (symbols["door"] in {"开门", "伤门"} and symbols["god"] in {"值符", "白虎", "九天", "值符+九天"}):
        return "强势压场型"
    if harms["door_pressure"] or harms["punishment_hit"] or symbols["god"] in {"腾蛇", "玄武"} or symbols["star"] == "天柱":
        return "情绪反复型"
    if harms["emptiness"] and set(harms["emptiness_layers"]).intersection({"palace", "god", "star", "door"}):
        return "疏离回避型"
    if symbols["god"] == "太阴" or symbols["door"] == "休门" or symbols["star"] == "天辅":
        return "慢热走心型"
    if symbols["god"] == "六合" or neutral_pairs or features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"}:
        return "人缘承接型"
    return "边界敏感型"


def _relationship_manifestation(relationship_type: str) -> str:
    return {
        "人缘承接型": "更容易有人来有人往，合作、人缘和情感互动能接得住，不太会一上来就把关系用僵。",
        "慢热走心型": "不是一下子特别热，但更重感受和细节，熟了之后更容易建立稳定的人际和情感黏性。",
        "边界敏感型": "有互动、有来往，但更吃分寸、回应方式和边界感，拿捏不好就容易把本来不大的问题放大。",
        "桃花牵动型": "外界吸引、异性缘或关系牵动会比较明显，热闹不一定少，但更怕边界一乱、关系一多就反复。",
        "强势压场型": "表达、主导和结果感偏强，前面不一定没人缘，但容易让对方觉得压迫、讲道理或不好靠近。",
        "情绪反复型": "互动里更容易敏感、多想、误解或一下热一下冷，关系推进常常不是没机会，而是容易被情绪回拉。",
        "外热内耗型": "表面上未必没来往，但越深入越容易累、耗、反复，关系热闹感和真正省心感不是一回事。",
        "疏离回避型": "不是完全没有关系，而是更容易出现回应慢、在场感不足、心里有话不愿明说的状态。",
    }[relationship_type]


def _relationship_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    neutral_pairs = set(patterns["neutral_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if not any(item["area"] == area for item in areas):
            areas.append({"area": area, "reason": reason, "scenario": scenario})

    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}) or neutral_pairs:
        add_area("边界分寸", "来往和牵动不一定少，真正拉开差距的是边界和分寸感。", "异性往来、暧昧牵动和关系升温阶段更明显。")
    if detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or symbols["door"] in {"开门", "伤门"}:
        add_area("表达压感", "表达方式和主导感偏强时，容易让关系从沟通变成顶牛。", "谈分工、给意见和推进节奏时更明显。")
    if harms["door_pressure"] or harms["punishment_hit"] or symbols["god"] in {"腾蛇", "玄武"} or symbols["star"] == "天柱":
        add_area("情绪回应", "关系里真正怕的不是没话说，而是情绪一上来就把回应质量拉低。", "误解、敏感、临场反应和关系回拉时更明显。")
    if harms["emptiness"] or harms["tomb"]:
        add_area("在场感", "不是完全没有关系，而是回应、陪伴和后段承接更怕掉线。", "关系冷下来、长期相处和需要稳定回应时更明显。")
    if heavy_harm_count >= 1 or final_score < 80 or "pair_25_95" in detected:
        add_area("人际消耗", "热闹感不等于省心感，真正难的是越往后越容易累。", "高压阶段、反复修复和长期来往时更明显。")
    if not areas and final_score >= 80:
        add_area("关系承接", "整体有人缘和接得住的底子，关键是别把分寸用过头。", "日常来往、合作配合和稳定互动时更占优势。")
    return areas[:3]


def _relationship_deduction_reasons(result: dict[str, Any]) -> list[str]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    neutral_pairs = set(patterns["neutral_pairs"])
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if symbols["god"] == "六合":
        add_reason("六合会把合作、人缘和关系连接感往上抬，是人际层的加分项。")
    if neutral_pairs:
        add_reason("91/37/28/46/55 这类关系专用组合，说明关系吸附和来往机会不算少，但更要看边界怎么守。")
    if symbols["god"] == "太阴":
        add_reason("太阴会把细腻、感受和慢热感放大，人际上更重体验和默契，不是那种一上来就外放的人。")
    if harms["emptiness"]:
        add_reason("空亡会让回应、在场感或关系落点打折，看着有来往，不代表每一步都接得很实。")
    if harms["door_pressure"]:
        add_reason("门迫容易把表达压力和关系顶撞感放大。")
    if harms["tomb"]:
        add_reason("入墓更像话压在心里、后段发沉，关系越往后越吃长期承接。")
    if harms["punishment_hit"]:
        add_reason("击刑会把敏感、误解和关系里的阶段性反复放大。")
    if symbols["god"] in {"腾蛇", "玄武"} or symbols["star"] == "天柱":
        add_reason("腾蛇、玄武或天柱这类信号，容易把多想、防备和情绪回拉带进关系层。")
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_reason("27/99/92 或桃花扰动组合，会把外界牵动、关系反复和边界问题推得更前。")
    if detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        add_reason("69/96 这类组合，更怕主导感太强、权责失衡或谁都不愿让步。")
    if "pair_25_95" in detected:
        add_reason("25/95 这类重风险组合，会让关系层更怕长期折腾和反复消耗。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")

    if not reasons:
        add_reason("宫门关系和后两干承接不差，所以整体人际感情底子还能接得住。")
    return reasons[:3]


def _relationship_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _relationship_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "关系节奏"

    if level == "人际感情承接感很稳":
        return "如果你看重人缘、相处舒服度和长期情感承接，这个号可以长期坚持使用。"
    if level == "人际感情整体可守":
        return f"可以继续长期使用，人际感情层整体可守，但关键节点仍建议留意{area_text}。"
    if level == "有来有往，但更吃分寸和边界":
        if final_score >= 80:
            return f"可以继续长期使用，但它没到满格的部分主要落在{area_text}，如果你很看重关系质量，这些地方更值得经营。"
        return f"可以继续使用，但更吃分寸、回应方式和边界拿捏，尤其在{area_text}上别顺其自然。"
    if level == "人际感情扰动偏明显":
        return f"如果你当前特别看重人缘稳定、关系边界和情感舒适度，这个号不建议当人际感情主用，至少要先把{area_text}看清。"
    return f"如果你很在意人际感情、长期关系舒适度和少折腾，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_relationship_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    neutral_pairs = set(patterns["neutral_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])

    level = _pick_relationship_level(result, final_score)
    relationship_type = _pick_relationship_type(result)
    watch_areas = _relationship_watch_areas(result, final_score)
    deduction_reasons = _relationship_deduction_reasons(result)

    primary_driver = "相处层"
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}) or neutral_pairs:
        primary_driver = "边界层"
    elif detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        primary_driver = "主导层"
    elif harms["tomb"] or harms["emptiness"]:
        primary_driver = "承接层"
    elif harms["door_pressure"] or harms["punishment_hit"] or symbols["god"] in {"腾蛇", "玄武"}:
        primary_driver = "情绪层"
    elif heavy_harm_count >= 2 or "pair_25_95" in detected:
        primary_driver = "消耗层"

    secondary_driver = "回应层"
    if primary_driver != "情绪层" and (harms["door_pressure"] or harms["punishment_hit"] or symbols["god"] in {"腾蛇", "玄武"}):
        secondary_driver = "情绪层"
    elif primary_driver != "承接层" and (harms["tomb"] or harms["emptiness"]):
        secondary_driver = "承接层"
    elif primary_driver != "边界层" and (detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}) or neutral_pairs):
        secondary_driver = "边界层"

    return {
        "level": level,
        "type": relationship_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _relationship_manifestation(relationship_type),
        "advice": _relationship_advice(level, result, final_score),
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
            "door_personality": DOOR_PERSONALITY.get(symbols["door"], "有自己的节奏和边界感"),
            "god_tone": GOD_TONE.get(symbols["god"], "明显的内在驱动力"),
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
            "allowed_levels": RELATIONSHIP_LEVELS,
            "allowed_types": RELATIONSHIP_TYPES,
            "rendering_goal": "Explain whether this number matches long-term relationship and social use, where the people-and-emotion deductions fall, and which relationship scenes are most worth watching.",
            "client_tone": "Professional but readable. Keep a teacher-like tone, explain people dynamics, boundaries, response style and emotional drag clearly, and end with a clear keep-or-adjust verdict.",
        },
    }
