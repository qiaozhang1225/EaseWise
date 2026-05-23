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

def _pick_health_level(result: dict[str, Any], final_score: int) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])

    if final_score >= 95 and heavy_harm_count == 0 and not has_emptiness and symbols["star"] != "天芮" and symbols["door"] != "死门" and symbols["god"] not in {"白虎", "腾蛇"} and not detected:
        return "健康承压感很稳"
    if heavy_harm_count >= 3 or final_score < 45 or "pair_25_95" in detected or (symbols["star"] == "天芮" and (harms["tomb"] or harms["punishment_hit"])):
        return "当前不宜长期硬扛"
    if heavy_harm_count >= 2 or symbols["star"] == "天芮" or symbols["door"] == "死门" or symbols["god"] == "白虎" or final_score < 65:
        return "健康负担偏明显"
    if has_emptiness or harms["tomb"] or harms["punishment_hit"] or risk_pairs.intersection({"27", "99", "92", "69", "96"}) or final_score < 80:
        return "有消耗，但还可控"
    return "健康整体可守"


def _pick_health_type(result: dict[str, Any]) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])

    if "pair_25_95" in detected or (harms["tomb"] and harms["punishment_hit"]) or result["scoring"]["structural_cap_reasons"]:
        return "反复折腾型"
    if harms["tomb"] and set(harms["tomb_layers"]).intersection({"trigger", "heaven_stem", "earth_stem"}):
        if symbols["star"] == "天芮" or symbols["door"] == "死门":
            return "慢性内耗型"
        return "恢复偏慢型"
    if symbols["door"] == "惊门" or symbols["star"] == "天柱" or symbols["god"] in {"玄武", "腾蛇"}:
        return "睡眠波动型"
    if risk_pairs.intersection({"27", "99", "92"}) or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        return "情绪牵动型"
    if symbols["door"] == "伤门" or symbols["god"] == "白虎" or symbols["star"] == "天英":
        return "火气偏旺型"
    if heavy_harm_count >= 2 or symbols["star"] == "天芮" or symbols["door"] == "死门":
        return "压力消耗型"
    if not harms["emptiness"] and not harms["tomb"] and not harms["punishment_hit"] and features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"}:
        return "节律稳定型"
    return "慢性内耗型"


def _health_manifestation(health_type: str) -> str:
    mapping = {
        "节律稳定型": "整体更像节律比较稳、消耗后能回得来，不太容易一边用一边持续往下掉。",
        "压力消耗型": "健康层更怕长期高压、连续透支和一直绷着不松，久了容易出现明显耗损感。",
        "恢复偏慢型": "前面不一定扛不住，但越往后越容易出现恢复慢、回得慢、缓不过来的感觉。",
        "睡眠波动型": "更容易在睡眠、紧绷、精神松不开和恢复不透这几层反复消耗。",
        "情绪牵动型": "情绪、人际和外部节奏更容易直接映到精力状态上，一乱就更难稳住。",
        "火气偏旺型": "更像火气、急躁、过热、容易顶着往前冲的体感，消耗往往来得更直接。",
        "慢性内耗型": "不是一下子爆开，而是更像长期操心、反复用神、慢慢把精力往下磨。",
        "反复折腾型": "容易出现反复折腾、刚缓一点又被重新拉回、修复速度跟不上消耗速度的状态。",
    }
    return mapping[health_type]


def _health_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if not any(item["area"] == area for item in areas):
            areas.append({"area": area, "reason": reason, "scenario": scenario})

    if symbols["door"] == "惊门" or symbols["star"] == "天柱" or symbols["god"] in {"玄武", "腾蛇"} or harms["emptiness"]:
        add_area("睡眠节律", "节律一乱，整个人的恢复和承压都会同步打折。", "作息颠倒、精神放不松和长期绷着扛时更明显。")
    if harms["tomb"] or symbols["star"] == "天芮" or symbols["door"] == "死门":
        add_area("恢复续航", "不是一下子扛不住，而是越往后越容易发沉、恢复慢。", "长期硬扛、连续消耗和高压收尾阶段更明显。")
    if harms["door_pressure"] or symbols["god"] == "白虎" or int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"]) >= 2:
        add_area("压力耗损", "真正拉开差距的往往不是有没有在扛，而是压力会不会越扛越透。", "高压推进、连续出力和责任堆积时更明显。")
    if harms["punishment_hit"] or set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_area("情绪内耗", "情绪波动、人际牵动和反复自耗更容易把状态慢慢拉低。", "关系扰动、外界带节奏和反复想太多时更明显。")
    if symbols["door"] == "伤门" or symbols["god"] == "白虎" or symbols["star"] == "天英":
        add_area("火气消耗", "这种盘更怕急顶、过热和硬冲，消耗往往来得快。", "情绪上头、急着推进和持续外放时更明显。")
    if "pair_25_95" in patterns["detected"] or result["scoring"]["structural_cap_reasons"]:
        add_area("反复折腾", "不是一次性的问题，而是刚缓一点又容易被重新拖回去。", "长期使用、反复修复和连续折腾阶段更明显。")
    if not areas and final_score >= 80:
        add_area("承压稳定", "整体主轴不差，更适合稳着用，而不是长期无节制透支。", "正常作息、按节奏推进和留恢复窗口时更占优势。")
    return areas[:3]


def _health_deduction_reasons(result: dict[str, Any]) -> list[str]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if symbols["star"] == "天芮":
        add_reason("天芮落健康层时，更像长期消耗、操心和恢复发虚的病象倾向。")
    if symbols["door"] == "死门":
        add_reason("死门会把发沉、压着扛和恢复偏慢这类问题放大。")
    if harms["emptiness"]:
        add_reason("空亡会让节律和落地承接打折，睡眠、状态和恢复更容易忽上忽下。")
    if harms["door_pressure"]:
        add_reason("门迫会把当前承压成本和身体绷紧感放大。")
    if harms["tomb"]:
        add_reason("入墓更像后段发沉，说明真正难的不是短期扛，而是长期恢复跟不上。")
    if harms["punishment_hit"]:
        add_reason("击刑会把阶段反复、紧绷和内耗感放大。")
    if symbols["god"] == "白虎":
        add_reason("白虎会把高压、急顶和硬碰硬式的消耗推得更前。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_reason("外部扰动组合会让健康层更容易被情绪、人际和外界节奏带偏。")
    if "pair_25_95" in patterns["detected"]:
        add_reason("25/95 这类重风险组合，会把反复折腾和长期耗损压得更重。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")

    if not reasons:
        add_reason("宫门关系顺接、四害较轻，所以整体承压、节律和恢复力更完整。")
    return reasons[:3]


def _health_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _health_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "关键阶段"

    if level == "健康承压感很稳":
        return "如果你看重健康承载、精力稳定和恢复力，这个号可以长期坚持使用。"
    if level == "健康整体可守":
        return f"可以继续长期使用，健康层整体可守，但关键节点仍建议留意{area_text}。"
    if level == "有消耗，但还可控":
        if final_score >= 80:
            return f"可以继续长期使用，但更吃节律和恢复管理，尤其在{area_text}上别长期硬扛。"
        return f"可以继续使用，但不适合长期透支着用，尤其在{area_text}上更要讲节奏。"
    if level == "健康负担偏明显":
        return f"如果你当前特别看重睡眠、精力稳定和少透支，这个号不建议当健康主用，至少要先把{area_text}看清。"
    return f"如果你很在意健康承载、长期精力和恢复力，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_health_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])

    level = _pick_health_level(result, final_score)
    health_type = _pick_health_type(result)
    watch_areas = _health_watch_areas(result, final_score)
    deduction_reasons = _health_deduction_reasons(result)

    primary_driver = "承压层"
    if symbols["star"] == "天芮" or symbols["door"] == "死门" or harms["tomb"]:
        primary_driver = "恢复层"
    elif harms["punishment_hit"] or risk_pairs.intersection({"27", "99", "92"}) or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or symbols["door"] == "惊门":
        primary_driver = "情绪层"
    elif harms["door_pressure"] or symbols["god"] == "白虎":
        primary_driver = "压力层"
    elif harms["emptiness"]:
        primary_driver = "节律层"
    elif symbols["door"] == "伤门" or symbols["star"] == "天英":
        primary_driver = "火耗层"
    elif "pair_25_95" in detected or scoring["structural_cap_reasons"]:
        primary_driver = "消耗层"

    secondary_driver = "节律层"
    if primary_driver != "恢复层" and (symbols["star"] == "天芮" or symbols["door"] == "死门" or harms["tomb"]):
        secondary_driver = "恢复层"
    elif primary_driver != "压力层" and (harms["door_pressure"] or symbols["god"] == "白虎"):
        secondary_driver = "压力层"
    elif primary_driver != "情绪层" and (harms["punishment_hit"] or risk_pairs.intersection({"27", "99", "92"}) or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or symbols["door"] == "惊门"):
        secondary_driver = "情绪层"
    elif primary_driver != "节律层" and harms["emptiness"]:
        secondary_driver = "节律层"

    return {
        "level": level,
        "type": health_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _health_manifestation(health_type),
        "advice": _health_advice(level, result, final_score),
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
            "structural_cap_reasons": _label_list(CAP_REASON_LABELS, scoring["structural_cap_reasons"]),
            "tags": scoring["tags"],
        },
        "model_pack": {
            "allowed_levels": HEALTH_LEVELS,
            "allowed_types": HEALTH_TYPES,
            "rendering_goal": "Explain the number's health-bearing capacity, where its sleep, pressure, recovery or stress trend gets dragged down, and whether it still suits long-term use when the user cares about health and energy stability.",
            "client_tone": "Professional but readable. Explain current pressure, rhythm, recovery, practical blockers, and end with a clear keep-or-adjust verdict.",
        },
    }
