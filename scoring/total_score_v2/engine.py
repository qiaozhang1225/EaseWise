from __future__ import annotations

from typing import Any

from scoring.engine import (
    build_board,
    detect_edge_flags,
    detect_harms,
    detect_patterns,
    element_relation,
    load_rules,
    pair_relation,
)

TOTAL_SCORE_V2_VERSION = "0.1.0"

ANCHOR_RELATION_SCORES = {
    "palace_generates_door": 88,
    "same_element": 82,
    "door_generates_palace": 78,
    "unrelated": 74,
    "palace_controls_door": 64,
    "door_controls_palace": 54,
}

SUPPORT_DOOR_SCORES = {
    "生门": 12,
    "休门": 10,
    "开门": 9,
    "景门": 6,
    "杜门": 4,
    "惊门": 2,
    "伤门": 0,
    "死门": -7,
}

SUPPORT_STAR_SCORES = {
    "天心": 10,
    "天任": 9,
    "天辅": 8,
    "天英": 6,
    "天冲": 4,
    "天禽": 3,
    "天蓬": 1,
    "天柱": -1,
    "天芮": -8,
}

SUPPORT_GOD_SCORES = {
    "值符": 9,
    "值符+九天": 9,
    "六合": 8,
    "太阴": 7,
    "九天": 6,
    "九地": 5,
    "玄武": 2,
    "腾蛇": 0,
    "白虎": -2,
}

SUPPORT_STEM_RELATION_SCORES = {
    "heaven_generates_earth": 8,
    "earth_generates_heaven": 7,
    "same_element": 5,
    "unrelated": 2,
    "heaven_controls_earth": -1,
    "earth_controls_heaven": -3,
}

STABILITY_LAYER_PENALTIES = {
    "palace": 8,
    "god": 5,
    "star": 5,
    "door": 8,
    "trigger": 2,
    "heaven_stem": 3,
    "earth_stem": 3,
}

STABILITY_TOMB_LAYER_PENALTIES = {
    "trigger": 2,
    "heaven_stem": 3,
    "earth_stem": 3,
}

STABILITY_PATTERN_PENALTIES = {
    "triple_same": 2,
    "peach_blossom_111_999": 4,
    "pair_69_96": 5,
    "pair_25_95": 12,
    "pair_27_99_92": 6,
    "tail_repeat_bias": 2,
}

STABILITY_EDGE_PENALTIES = {
    "palace_emptiness": 6,
    "god_emptiness": 3,
    "star_emptiness": 4,
    "door_emptiness": 6,
    "trigger_generic_emptiness": 1,
    "heaven_stem_generic_emptiness": 1,
    "earth_stem_generic_emptiness": 1,
    "god_9_dual_read": 1,
    "palace_5_special": 1,
    "star_5_special": 1,
    "door_5_special": 1,
    "star_2_special": 1,
    "door_2_special": 1,
}

CAPS = {
    "pair_25_95": 64,
    "pair_69_96": 78,
    "stacked_27_99_92": 72,
    "palace_empty_with_door_pressure": 68,
    "multiple_heavy_harms": 66,
    "door_empty_with_result_tomb": 64,
}


def _clamp(score: int) -> int:
    return max(0, min(100, score))


def _score_anchor(board: Any, harms: dict[str, Any], rules: dict[str, Any]) -> tuple[int, str]:
    palace_symbol = board.symbols["palace"]
    door_symbol = board.symbols["door"]
    palace_element = rules["palace_elements"][palace_symbol]
    door_element = rules["door_elements"][door_symbol]
    relation = element_relation(palace_element, door_element)

    score = ANCHOR_RELATION_SCORES.get(relation, 74)
    if "palace" in harms["emptiness_layers"]:
        score -= 8
    if "door" in harms["emptiness_layers"]:
        score -= 6
    if harms["door_pressure"]:
        score -= 5
    if board.digits["palace"] == "5":
        score -= 2
    if board.digits["door"] == "5":
        score -= 1
    return _clamp(score), relation


def _score_support(board: Any, harms: dict[str, Any], rules: dict[str, Any]) -> tuple[int, str]:
    symbols = board.symbols
    heaven = symbols["heaven_stem"]
    earth = symbols["earth_stem"]
    trigger = symbols["trigger"]
    heaven_element = rules["stem_elements"][heaven]
    earth_element = rules["stem_elements"][earth]
    trigger_element = rules["stem_elements"][trigger]
    stem_relation = pair_relation(heaven_element, earth_element)

    score = 58
    score += SUPPORT_DOOR_SCORES[symbols["door"]]
    score += SUPPORT_STAR_SCORES[symbols["star"]]
    score += SUPPORT_GOD_SCORES[symbols["god"]]
    score += SUPPORT_STEM_RELATION_SCORES[stem_relation]

    if (
        trigger_element == heaven_element
        or trigger_element == earth_element
        or trigger_element == "earth"
    ):
        score += 2
    if symbols["door"] in {"生门", "休门", "开门"} and symbols["star"] in {"天心", "天任", "天辅"}:
        score += 3
    if symbols["god"] in {"值符", "值符+九天", "六合", "太阴"} and symbols["star"] in {"天心", "天任", "天辅"}:
        score += 2
    if "star" in harms["emptiness_layers"]:
        score -= 2
    if "god" in harms["emptiness_layers"]:
        score -= 1
    return _clamp(score), stem_relation


def _score_stability(board: Any, harms: dict[str, Any], patterns: dict[str, Any], edge_flags: list[str]) -> int:
    score = 100

    for layer in harms["emptiness_layers"]:
        score -= STABILITY_LAYER_PENALTIES.get(layer, 2)
    if harms["door_pressure"]:
        score -= 8
    for layer in harms["tomb_layers"]:
        score -= STABILITY_TOMB_LAYER_PENALTIES.get(layer, 0)
    if harms["punishment_hit"]:
        score -= 8

    for detected in patterns["detected"]:
        score -= STABILITY_PATTERN_PENALTIES.get(detected, 0)
    for flag in edge_flags:
        score -= STABILITY_EDGE_PENALTIES.get(flag, 0)

    result_tomb_layers = {layer for layer in harms["tomb_layers"] if layer in {"heaven_stem", "earth_stem"}}
    if "door" in harms["emptiness_layers"] and result_tomb_layers:
        score -= 4
    if "door" in harms["emptiness_layers"] and len(result_tomb_layers) >= 2:
        score -= 3

    if not harms["emptiness"] and not harms["door_pressure"] and not harms["tomb"] and not harms["punishment_hit"] and not patterns["detected"]:
        score += 4

    if board.digits["palace"] == board.digits["door"] == "5":
        score -= 2

    return _clamp(score)


def _compute_confidence(board: Any, harms: dict[str, Any], patterns: dict[str, Any], edge_flags: list[str]) -> str:
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    severe = {
        "palace_emptiness",
        "door_emptiness",
        "star_emptiness",
        "palace_5_special",
        "door_5_special",
    }
    if severe.intersection(edge_flags) or heavy_harm_count >= 3 or len(patterns["detected"]) >= 3:
        return "C"
    if edge_flags or heavy_harm_count >= 1 or patterns["detected"] or board.digits["god"] == "9":
        return "B"
    return "A"


def _apply_caps(
    harms: dict[str, Any],
    patterns: dict[str, Any],
    raw_score: int,
) -> tuple[int, int, list[str]]:
    applied: list[tuple[int, str]] = []
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    result_tomb_layers = {layer for layer in harms["tomb_layers"] if layer in {"heaven_stem", "earth_stem"}}

    if "pair_25_95" in patterns["detected"]:
        applied.append((CAPS["pair_25_95"], "pair_25_95"))
    if "pair_69_96" in patterns["detected"]:
        applied.append((CAPS["pair_69_96"], "pair_69_96"))
    if len({pair for pair in patterns["risk_pairs"] if pair in {"27", "99", "92"}}) >= 2:
        applied.append((CAPS["stacked_27_99_92"], "stacked_27_99_92"))
    if harms["door_pressure"] and "palace" in harms["emptiness_layers"]:
        applied.append((CAPS["palace_empty_with_door_pressure"], "palace_empty_with_door_pressure"))
    if heavy_harm_count >= 2:
        applied.append((CAPS["multiple_heavy_harms"], "multiple_heavy_harms"))
    if "door" in harms["emptiness_layers"] and result_tomb_layers:
        applied.append((CAPS["door_empty_with_result_tomb"], "door_empty_with_result_tomb"))

    if not applied:
        return _clamp(raw_score), 100, []

    structural_cap = min(cap for cap, _ in applied)
    return _clamp(min(raw_score, structural_cap)), structural_cap, [reason for _, reason in applied]


def _build_tags(
    board: Any,
    harms: dict[str, Any],
    patterns: dict[str, Any],
    anchor_relation: str,
) -> list[str]:
    tags: list[str] = []
    if anchor_relation in {"palace_generates_door", "same_element", "door_generates_palace"}:
        tags.append("平台承接")
    if anchor_relation == "door_controls_palace":
        tags.append("门迫风险")
    if "pair_25_95" in patterns["detected"]:
        tags.append("重风险组合")
    if "pair_69_96" in patterns["detected"]:
        tags.append("权责风险")
    if "pair_27_99_92" in patterns["detected"] or "peach_blossom_111_999" in patterns["detected"]:
        tags.append("桃花扰动")
    if harms["punishment_hit"] or harms["door_pressure"] or board.symbols["star"] == "天芮":
        tags.append("高压消耗")
    if "palace" in harms["emptiness_layers"]:
        tags.append("落不实")
    if not harms["emptiness"] and not harms["door_pressure"] and not harms["tomb"] and not harms["punishment_hit"] and not patterns["detected"]:
        tags.append("结构稳定")
    return sorted(set(tags))


def score_phone_total_v2(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = rules or load_rules()
    board = build_board(phone, gender, rules)
    edge_flags = detect_edge_flags(board)
    harms = detect_harms(board, rules)
    patterns = detect_patterns(board)

    anchor_score, anchor_relation = _score_anchor(board, harms, rules)
    support_score, stem_relation = _score_support(board, harms, rules)
    stability_score = _score_stability(board, harms, patterns, edge_flags)

    weighted_raw = round(anchor_score * 0.34 + support_score * 0.31 + stability_score * 0.35)
    confidence = _compute_confidence(board, harms, patterns, edge_flags)
    confidence_shrink = {"A": 1.0, "B": 0.97, "C": 0.93}[confidence]
    score_after_confidence = round(weighted_raw * confidence_shrink + 60 * (1 - confidence_shrink))

    raw_score = _clamp(score_after_confidence)
    capped_score, structural_cap, structural_cap_reasons = _apply_caps(harms, patterns, raw_score)
    tags = _build_tags(board, harms, patterns, anchor_relation)

    return {
        "rules_version": rules["version"],
        "algorithm_version": TOTAL_SCORE_V2_VERSION,
        "input": {
            "phone": phone,
            "gender": board.gender,
        },
        "board": {
            "last7": board.last7,
            "digits": board.digits,
            "symbols": board.symbols,
        },
        "features": {
            "anchor_relation": anchor_relation,
            "stem_pair_relation": stem_relation,
            "harms": harms,
            "patterns": patterns,
            "edge_flags": edge_flags,
        },
        "scoring": {
            "components": {
                "anchor_score": anchor_score,
                "support_score": support_score,
                "stability_score": stability_score,
                "weighted_raw": weighted_raw,
                "confidence_shrink": confidence_shrink,
            },
            "raw_score": raw_score,
            "score_after_structural_cap": capped_score,
            "structural_cap": structural_cap,
            "structural_cap_reasons": structural_cap_reasons,
            "confidence": confidence,
            "tags": tags,
        },
    }


def build_total_score_v2(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return score_phone_total_v2(phone, gender, rules=rules)
