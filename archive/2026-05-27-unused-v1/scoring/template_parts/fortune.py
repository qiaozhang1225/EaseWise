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

def _pick_fortune_level(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    has_cap = bool(result["scoring"]["structural_cap_reasons"])
    detected = set(patterns["detected"])
    high_quality_relations = {"palace_generates_door", "same_element", "door_generates_palace"}

    if final_score >= 95 and heavy_harm_count == 0 and not has_emptiness and not detected and features["palace_door_relation"] in high_quality_relations:
        return "运势起势很顺"
    if heavy_harm_count >= 3 or final_score < 45 or "pair_25_95" in detected:
        return "当前不宜硬扛运势"
    if heavy_harm_count >= 2 or has_cap or final_score < 65:
        return "运势波动偏明显"
    if final_score >= 80 and heavy_harm_count <= 1 and not has_cap:
        return "运势整体可走"
    return "有起伏，但还能借势"


def _pick_fortune_type(result: dict[str, Any]) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    risk_pairs = set(patterns["risk_pairs"])
    detected = set(patterns["detected"])
    symbols = board["symbols"]
    relation = features["palace_door_relation"]

    if detected.intersection({"pair_25_95", "pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or result["scoring"]["structural_cap_reasons"]:
        return "风险回拉型"
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        return "关系牵动型"
    if harms["tomb"] and set(harms["tomb_layers"]).intersection({"trigger", "heaven_stem", "earth_stem"}):
        return "前通后滞型"
    if harms["punishment_hit"] or symbols["door"] == "死门" or symbols["star"] == "天芮":
        return "消耗承压型"
    if harms["door_pressure"] or relation in {"palace_controls_door", "door_controls_palace"} or harms["emptiness"]:
        return "低开反复型"
    if symbols["door"] in {"开门", "景门"} or symbols["god"] in {"九天", "值符+九天"} or symbols["star"] == "天英":
        return "外放起伏型"
    if relation in {"palace_generates_door", "same_element"} and symbols["door"] in {"开门", "生门"}:
        return "平台放大型"
    return "顺流承接型"


def _fortune_manifestation(fortune_type: str) -> str:
    mapping = {
        "顺流承接型": "整体不是硬冲出来的势，而是机会、节奏和承接相对接得上，用起来更容易有顺手感。",
        "平台放大型": "更像借平台、资源、环境或外部通道把势能放大，前提是节奏别乱、动作别冒进。",
        "前通后滞型": "前面不是完全起不来，而是走到后段更容易发沉、掉速，关键在后续续航和收口。",
        "关系牵动型": "运势不完全由自己单线决定，关系、人情、外界反馈和环境牵动会更直接地改写阶段体验。",
        "风险回拉型": "前面不是完全没势，但势头一起来，关键节点就容易被风险、拖延或现实问题往回拽。",
        "消耗承压型": "整体更怕高压硬扛，容易出现表面还在推、里面却已经开始耗的状态。",
        "外放起伏型": "起势、曝光和推进感不弱，但节奏一放大，波动也更容易被同步放大。",
        "低开反复型": "不是完全没有机会，而是起势偏慢、临门易卡，常常需要额外力气去接住局面。",
    }
    return mapping[fortune_type]


def _fortune_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = result["board"]["symbols"]
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if not any(item["area"] == area for item in areas):
            areas.append({"area": area, "reason": reason, "scenario": scenario})

    if patterns["risk_pairs"] and set(patterns["risk_pairs"]).intersection({"69", "96"}) or "pair_25_95" in patterns["detected"] or result["scoring"]["structural_cap_reasons"]:
        add_area("风险回拉", "已经起来的势头更怕被结构风险拉回去。", "谈结果、冲节点、准备放大动作时更明显。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_area("外部牵动", "关系、人情和外部节奏更容易改写当前阶段的运势体感。", "社交牵动、合作推进和情绪波动期更明显。")
    if harms["tomb"] or symbols["door"] == "死门" or symbols["star"] == "天芮":
        add_area("后段续航", "前面未必差，但越往后越怕发沉、掉速和消耗累积。", "长期硬扛、连续推进和收尾阶段更值得看。")
    if harms["door_pressure"] or features["palace_door_relation"] in {"palace_controls_door", "door_controls_palace"}:
        add_area("推进节奏", "真正拉开差距的往往不是有没有机会，而是临门能不能顺着推进。", "卡节点、谈合作和执行转折时更明显。")
    if harms["emptiness"]:
        add_area("落地承接", "看着有势，不代表每一步都能稳稳落到手里。", "机会来了要不要接、接了能不能稳住时更关键。")
    if (symbols["door"] in {"开门", "景门"} or symbols["god"] in {"九天", "值符+九天"}) and final_score >= 65:
        add_area("起势放大", "这个号有把外部势能放大的能力，但也更吃节奏和边界。", "主动出击、扩张曝光和拉资源时更明显。")
    if not areas and final_score >= 80:
        add_area("顺势放大", "整体主轴不差，更适合顺势推进而不是频繁折返。", "主动谈机会、落项目和持续推进时更占优势。")
    return areas[:3]


def _fortune_deduction_reasons(result: dict[str, Any]) -> list[str]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    reasons: list[str] = []

    def add_reason(text: str) -> None:
        if text not in reasons:
            reasons.append(text)

    if features["palace_door_relation"] not in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_reason("宫门关系不算顺，说明起势和承接之间不是完全同步。")
    if harms["emptiness"]:
        add_reason("空亡会让运势层的落点感打折，有机会但不一定每次都能接满。")
    if harms["door_pressure"]:
        add_reason("门迫会把推进成本和临门卡顿感放大。")
    if harms["tomb"]:
        add_reason("入墓更像后段发沉，说明前面起势未必差，但持续走久了更容易钝住。")
    if harms["punishment_hit"]:
        add_reason("击刑会把阶段反复、硬碰硬和内耗感放大。")
    if set(patterns["risk_pairs"]).intersection({"69", "96"}):
        add_reason("69/96 这类风险组合，容易把已经起来的势头重新拉回震荡。")
    if "pair_25_95" in patterns["detected"]:
        add_reason("25/95 这类重风险组合，会直接压低整体运势的可持续性。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}) or set(patterns["detected"]).intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        add_reason("外部扰动组合会让运势更容易被关系、人情或外界节奏带偏。")
    for reason in scoring["structural_cap_reasons"]:
        add_reason(f"结构封顶提示：{CAP_REASON_LABELS.get(reason, reason)}。")

    if not reasons:
        add_reason("宫门关系顺接、四害较轻，所以整体运势的起势感和承接感更完整。")
    return reasons[:3]


def _fortune_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _fortune_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "关键节点"

    if level == "运势起势很顺":
        return "如果你看重当前阶段的顺势感、机会承接和整体起色，这个号可以长期坚持使用。"
    if level == "运势整体可走":
        return f"可以继续长期使用，整体运势可走，但关键节点仍建议留意{area_text}。"
    if level == "有起伏，但还能借势":
        if final_score >= 80:
            return f"可以继续长期使用，但更吃节奏和借势方式，尤其在{area_text}上别硬冲。"
        return f"可以继续使用，但不适合把每一步都当成顺风局，尤其在{area_text}上更要讲方法。"
    if level == "运势波动偏明显":
        return f"如果你当前特别看重整体顺遂感、推进效率和少折腾，这个号不建议当运势主用，至少要先把{area_text}看清。"
    return f"如果你很在意当前阶段的运势、顺势推进和少折腾，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_fortune_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    risk_pairs = set(patterns["risk_pairs"])
    detected = set(patterns["detected"])

    level = _pick_fortune_level(result, final_score)
    fortune_type = _pick_fortune_type(result)
    watch_areas = _fortune_watch_areas(result, final_score)
    deduction_reasons = _fortune_deduction_reasons(result)

    primary_driver = "顺接层"
    if detected.intersection({"pair_25_95", "pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or scoring["structural_cap_reasons"]:
        primary_driver = "风险层"
    elif detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        primary_driver = "外扰层"
    elif harms["tomb"] or symbols["door"] == "死门" or symbols["star"] == "天芮":
        primary_driver = "续航层"
    elif harms["door_pressure"] or features["palace_door_relation"] in {"palace_controls_door", "door_controls_palace"}:
        primary_driver = "节奏层"
    elif harms["emptiness"]:
        primary_driver = "落地层"
    elif symbols["door"] in {"开门", "景门"} or symbols["god"] in {"九天", "值符+九天"}:
        primary_driver = "放大层"

    secondary_driver = "节奏层"
    if primary_driver != "风险层" and (detected.intersection({"pair_25_95", "pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or scoring["structural_cap_reasons"]):
        secondary_driver = "风险层"
    elif primary_driver != "外扰层" and (detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"})):
        secondary_driver = "外扰层"
    elif primary_driver != "续航层" and (harms["tomb"] or symbols["door"] == "死门" or symbols["star"] == "天芮"):
        secondary_driver = "续航层"
    elif primary_driver != "落地层" and harms["emptiness"]:
        secondary_driver = "落地层"

    return {
        "level": level,
        "type": fortune_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _fortune_manifestation(fortune_type),
        "advice": _fortune_advice(level, result, final_score),
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
            "allowed_levels": FORTUNE_LEVELS,
            "allowed_types": FORTUNE_TYPES,
            "rendering_goal": "Explain the number's current-stage momentum, where its overall trend gets amplified or pulled back, and whether it still suits long-term use when the user cares about current fortune.",
            "client_tone": "Professional but readable. Explain current momentum, stage rhythm, practical blockers, and end with a clear keep-or-adjust verdict.",
        },
    }
