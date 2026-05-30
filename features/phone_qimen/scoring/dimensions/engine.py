from __future__ import annotations

from typing import Any

from features.phone_qimen.scoring.total_score.engine import (
    build_board,
    detect_edge_flags,
    detect_harms,
    detect_patterns,
    element_relation,
    load_rules,
    pair_relation,
    score_phone,
)

DIMENSION_SCORE_VERSION = "0.1.1"

DIMENSION_ORDER = [
    "career",
    "wealth",
    "love",
    "health",
    "acad",
    "fortune",
    "investment",
    "travel",
    "social",
    "family",
    "personality",
    "fengshui",
]

DIMENSION_TITLES = {
    "career": "事业",
    "wealth": "财富",
    "love": "感情",
    "health": "健康",
    "acad": "学业",
    "fortune": "运势",
    "investment": "投资",
    "travel": "出行",
    "social": "人际",
    "family": "家庭",
    "personality": "性格",
    "fengshui": "风水",
}

RELATION_DELTAS = {
    "palace_generates_door": 5,
    "same_element": 4,
    "door_generates_palace": 2,
    "unrelated": 0,
    "palace_controls_door": -5,
    "door_controls_palace": -7,
}

STEM_DELTAS = {
    "heaven_generates_earth": 3,
    "earth_generates_heaven": 2,
    "same_element": 2,
    "unrelated": 0,
    "heaven_controls_earth": -3,
    "earth_controls_heaven": -4,
}

DOOR_DELTAS = {
    "career": {"开门": 8, "生门": 6, "景门": 3, "休门": 2, "杜门": 0, "惊门": -3, "伤门": -6, "死门": -8},
    "wealth": {"生门": 8, "开门": 6, "休门": 3, "景门": 2, "杜门": -2, "惊门": -4, "伤门": -6, "死门": -9},
    "love": {"休门": 6, "生门": 3, "六合": 0, "开门": 0, "景门": 1, "杜门": -2, "惊门": -5, "伤门": -7, "死门": -8},
    "health": {"休门": 7, "生门": 3, "杜门": 2, "开门": 0, "景门": -4, "惊门": -6, "伤门": -8, "死门": -10},
    "acad": {"杜门": 7, "休门": 6, "生门": 3, "开门": 1, "景门": 1, "惊门": -5, "伤门": -6, "死门": -8},
    "fortune": {"开门": 5, "生门": 5, "休门": 4, "景门": 2, "杜门": -2, "惊门": -4, "伤门": -6, "死门": -8},
    "investment": {"生门": 6, "开门": 5, "休门": 1, "景门": 1, "杜门": -4, "惊门": -6, "伤门": -7, "死门": -10},
    "travel": {"开门": 6, "休门": 5, "生门": 3, "景门": 2, "杜门": -5, "惊门": -6, "伤门": -8, "死门": -9},
    "social": {"休门": 5, "开门": 3, "生门": 2, "景门": 2, "杜门": -2, "惊门": -5, "伤门": -7, "死门": -8},
    "family": {"休门": 6, "生门": 3, "开门": 0, "景门": 0, "杜门": -1, "惊门": -5, "伤门": -7, "死门": -9},
    "personality": {"休门": 4, "开门": 4, "生门": 2, "景门": 2, "杜门": 1, "惊门": -3, "伤门": -5, "死门": -6},
    "fengshui": {"生门": 5, "开门": 4, "休门": 4, "景门": 2, "杜门": -1, "惊门": -5, "伤门": -6, "死门": -9},
}

STAR_DELTAS = {
    "career": {"天心": 7, "天任": 5, "天辅": 4, "天冲": 2, "天英": 1, "天禽": 0, "天蓬": -2, "天柱": -5, "天芮": -9},
    "wealth": {"天任": 6, "天心": 5, "天辅": 3, "天英": 3, "天禽": 0, "天冲": -1, "天蓬": -2, "天柱": -5, "天芮": -9},
    "love": {"天辅": 5, "天任": 3, "天心": 1, "天英": 1, "天禽": 1, "天冲": -5, "天蓬": -5, "天柱": -6, "天芮": -8},
    "health": {"天心": 4, "天任": 3, "天辅": 3, "天禽": 0, "天冲": -5, "天英": -6, "天蓬": -6, "天柱": -8, "天芮": -12},
    "acad": {"天辅": 7, "天心": 5, "天任": 4, "天英": 1, "天禽": 1, "天冲": -1, "天蓬": -2, "天柱": -6, "天芮": -8},
    "fortune": {"天心": 4, "天任": 4, "天辅": 3, "天英": 2, "天冲": 1, "天禽": 0, "天蓬": -3, "天柱": -5, "天芮": -8},
    "investment": {"天蓬": 3, "天心": 3, "天任": 3, "天辅": 2, "天英": 1, "天冲": 0, "天禽": 0, "天柱": -6, "天芮": -9},
    "travel": {"天冲": 5, "天任": 3, "天心": 2, "天英": 2, "天辅": 1, "天禽": 0, "天蓬": -6, "天柱": -5, "天芮": -7},
    "social": {"天辅": 5, "天心": 3, "天任": 3, "天英": 3, "天禽": 1, "天冲": -4, "天蓬": -5, "天柱": -6, "天芮": -7},
    "family": {"天心": 3, "天任": 3, "天辅": 4, "天禽": 1, "天英": 0, "天冲": -4, "天蓬": -5, "天柱": -6, "天芮": -8},
    "personality": {"天心": 5, "天任": 4, "天辅": 4, "天禽": 2, "天英": 2, "天冲": -3, "天蓬": -4, "天柱": -5, "天芮": -6},
    "fengshui": {"天心": 4, "天任": 4, "天辅": 3, "天英": 2, "天禽": 1, "天冲": -2, "天蓬": -5, "天柱": -5, "天芮": -8},
}

GOD_DELTAS = {
    "career": {"值符": 6, "值符+九天": 7, "九天": 6, "六合": 3, "太阴": 2, "九地": 1, "玄武": -4, "腾蛇": -6, "白虎": -7},
    "wealth": {"值符": 5, "值符+九天": 5, "九天": 4, "六合": 4, "太阴": 3, "九地": 3, "玄武": -6, "腾蛇": -6, "白虎": -7},
    "love": {"六合": 8, "太阴": 6, "九地": 3, "值符": 1, "九天": -2, "值符+九天": -2, "玄武": -7, "腾蛇": -8, "白虎": -9},
    "health": {"太阴": 5, "九地": 5, "六合": 2, "值符": 0, "九天": -2, "值符+九天": -3, "玄武": -6, "腾蛇": -8, "白虎": -10},
    "acad": {"太阴": 5, "六合": 4, "九地": 4, "值符": 2, "九天": 1, "值符+九天": 1, "玄武": -5, "腾蛇": -6, "白虎": -7},
    "fortune": {"值符": 5, "值符+九天": 5, "九天": 4, "六合": 3, "太阴": 2, "九地": 2, "玄武": -5, "腾蛇": -7, "白虎": -8},
    "investment": {"值符": 5, "值符+九天": 5, "九天": 4, "太阴": 3, "六合": 2, "九地": 1, "玄武": -8, "腾蛇": -9, "白虎": -9},
    "travel": {"九天": 7, "值符+九天": 6, "值符": 5, "六合": 2, "太阴": 1, "九地": 0, "玄武": -6, "腾蛇": -7, "白虎": -8},
    "social": {"六合": 7, "太阴": 5, "值符": 2, "九地": 2, "九天": 1, "值符+九天": 0, "玄武": -7, "腾蛇": -8, "白虎": -9},
    "family": {"六合": 7, "太阴": 6, "九地": 4, "值符": 2, "九天": -1, "值符+九天": -1, "玄武": -6, "腾蛇": -7, "白虎": -9},
    "personality": {"值符": 4, "六合": 4, "太阴": 3, "九地": 3, "九天": 2, "值符+九天": 2, "玄武": -5, "腾蛇": -7, "白虎": -7},
    "fengshui": {"值符": 5, "六合": 4, "太阴": 4, "九地": 4, "九天": 3, "值符+九天": 3, "玄武": -6, "腾蛇": -7, "白虎": -8},
}

RELATION_MULTIPLIERS = {
    "career": 1.15,
    "wealth": 1.10,
    "love": 0.85,
    "health": 0.75,
    "acad": 0.85,
    "fortune": 1.00,
    "investment": 1.05,
    "travel": 1.00,
    "social": 0.85,
    "family": 0.85,
    "personality": 0.65,
    "fengshui": 1.20,
}

STEM_MULTIPLIERS = {
    "career": 1.00,
    "wealth": 0.90,
    "love": 1.10,
    "health": 0.75,
    "acad": 0.90,
    "fortune": 0.90,
    "investment": 1.00,
    "travel": 0.90,
    "social": 0.90,
    "family": 1.00,
    "personality": 0.75,
    "fengshui": 0.90,
}

HARM_MULTIPLIERS = {
    "career": {"emptiness": 1.05, "door_pressure": 1.10, "tomb": 0.95, "punishment": 1.00},
    "wealth": {"emptiness": 1.00, "door_pressure": 1.05, "tomb": 1.15, "punishment": 1.00},
    "love": {"emptiness": 0.95, "door_pressure": 1.10, "tomb": 1.00, "punishment": 1.35},
    "health": {"emptiness": 1.15, "door_pressure": 1.20, "tomb": 1.25, "punishment": 1.40},
    "acad": {"emptiness": 1.10, "door_pressure": 0.90, "tomb": 0.95, "punishment": 1.00},
    "fortune": {"emptiness": 1.00, "door_pressure": 1.05, "tomb": 1.05, "punishment": 1.05},
    "investment": {"emptiness": 1.05, "door_pressure": 1.20, "tomb": 1.30, "punishment": 1.10},
    "travel": {"emptiness": 1.15, "door_pressure": 1.20, "tomb": 1.10, "punishment": 1.05},
    "social": {"emptiness": 0.95, "door_pressure": 1.05, "tomb": 0.95, "punishment": 1.30},
    "family": {"emptiness": 1.00, "door_pressure": 1.10, "tomb": 1.00, "punishment": 1.35},
    "personality": {"emptiness": 0.80, "door_pressure": 0.90, "tomb": 0.80, "punishment": 1.05},
    "fengshui": {"emptiness": 1.25, "door_pressure": 1.20, "tomb": 1.15, "punishment": 1.00},
}

PATTERN_MULTIPLIERS = {
    "career": {"triple_same": 0.80, "tail_repeat_bias": 0.80, "pair_69_96": 1.25, "pair_25_95": 1.05},
    "wealth": {"triple_same": 1.00, "tail_repeat_bias": 1.35, "pair_69_96": 1.25, "pair_25_95": 1.35},
    "love": {"triple_same": 1.15, "tail_repeat_bias": 1.15, "pair_27_99_92": 1.35, "peach_blossom_111_999": 1.50},
    "health": {"triple_same": 1.10, "tail_repeat_bias": 1.05, "pair_25_95": 1.20, "pair_27_99_92": 1.10},
    "acad": {"triple_same": 0.90, "tail_repeat_bias": 0.90, "pair_27_99_92": 1.00},
    "fortune": {"triple_same": 1.00, "tail_repeat_bias": 1.00, "pair_25_95": 1.20, "pair_69_96": 1.10},
    "investment": {"triple_same": 1.05, "tail_repeat_bias": 1.35, "pair_25_95": 1.55, "pair_69_96": 1.45},
    "travel": {"triple_same": 1.00, "tail_repeat_bias": 1.00, "pair_25_95": 1.15, "pair_27_99_92": 1.15},
    "social": {"triple_same": 1.10, "tail_repeat_bias": 1.10, "pair_27_99_92": 1.35, "peach_blossom_111_999": 1.40},
    "family": {"triple_same": 1.10, "tail_repeat_bias": 1.15, "pair_27_99_92": 1.30, "peach_blossom_111_999": 1.35},
    "personality": {"triple_same": 0.90, "tail_repeat_bias": 1.00, "pair_27_99_92": 1.05},
    "fengshui": {"triple_same": 1.00, "tail_repeat_bias": 1.10, "pair_25_95": 1.30, "pair_69_96": 1.15},
}

BASE_HARM_PENALTIES = {
    "palace": 6,
    "god": 3,
    "star": 4,
    "door": 7,
    "trigger": 2,
    "heaven_stem": 3,
    "earth_stem": 3,
}

BASE_TOMB_PENALTIES = {
    "trigger": 3,
    "heaven_stem": 4,
    "earth_stem": 4,
}

BASE_PATTERN_PENALTIES = {
    "triple_same": 4,
    "peach_blossom_111_999": 6,
    "pair_69_96": 8,
    "pair_25_95": 12,
    "pair_27_99_92": 7,
    "tail_repeat_bias": 4,
}

EDGE_PENALTIES = {
    "palace_emptiness": 5,
    "god_emptiness": 2,
    "star_emptiness": 3,
    "door_emptiness": 5,
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

TOPIC_HIGH_RISK_PAIRS = {
    "career": {"69", "96", "25", "95"},
    "wealth": {"25", "95", "69", "96"},
    "love": {"27", "99", "92", "111", "999"},
    "health": {"25", "95", "27", "99", "92"},
    "acad": {"25", "95", "27", "99", "92"},
    "fortune": {"25", "95", "27", "99", "92", "69", "96"},
    "investment": {"25", "95", "69", "96", "27", "99", "92"},
    "travel": {"25", "95", "27", "99", "92"},
    "social": {"27", "99", "92", "111", "999"},
    "family": {"27", "99", "92", "111", "999"},
    "personality": {"25", "95", "27", "99", "92"},
    "fengshui": {"25", "95", "69", "96", "27", "99", "92"},
}

STRUCTURAL_CAPS = {
    "career": {"pair_25_95": 68, "pair_69_96": 75, "stacked_27_99_92": 72, "multiple_heavy_harms": 66, "palace_empty_with_door_pressure": 68},
    "wealth": {"pair_25_95": 62, "pair_69_96": 72, "stacked_27_99_92": 68, "multiple_heavy_harms": 62, "palace_empty_with_door_pressure": 66},
    "love": {"pair_25_95": 62, "pair_69_96": 72, "stacked_27_99_92": 62, "multiple_heavy_harms": 58},
    "health": {"pair_25_95": 56, "pair_69_96": 68, "stacked_27_99_92": 62, "multiple_heavy_harms": 54},
    "acad": {"pair_25_95": 62, "pair_69_96": 72, "stacked_27_99_92": 66, "multiple_heavy_harms": 60},
    "fortune": {"pair_25_95": 60, "pair_69_96": 72, "stacked_27_99_92": 66, "multiple_heavy_harms": 60},
    "investment": {"pair_25_95": 52, "pair_69_96": 64, "stacked_27_99_92": 60, "multiple_heavy_harms": 52},
    "travel": {"pair_25_95": 58, "pair_69_96": 70, "stacked_27_99_92": 64, "multiple_heavy_harms": 58},
    "social": {"pair_25_95": 62, "pair_69_96": 70, "stacked_27_99_92": 60, "multiple_heavy_harms": 58},
    "family": {"pair_25_95": 60, "pair_69_96": 68, "stacked_27_99_92": 60, "multiple_heavy_harms": 56},
    "personality": {"pair_25_95": 64, "pair_69_96": 72, "stacked_27_99_92": 66, "multiple_heavy_harms": 62},
    "fengshui": {"pair_25_95": 56, "pair_69_96": 68, "stacked_27_99_92": 62, "multiple_heavy_harms": 54, "palace_empty_with_door_pressure": 64},
}


def _clamp(score: int) -> int:
    return max(0, min(100, score))


def _weighted_delta(value: int, multiplier: float) -> int:
    return round(value * multiplier)


def _add_delta(value: int, reason: str, positive: list[dict[str, Any]], risk: list[dict[str, Any]]) -> tuple[int, int]:
    if value > 0:
        positive.append({"reason": reason, "delta": value})
        return value, 0
    if value < 0:
        risk.append({"reason": reason, "delta": abs(value)})
        return 0, abs(value)
    return 0, 0


def _max_upward_delta(base_score: int, risk_delta: int, structural_reasons: list[str]) -> int:
    if structural_reasons:
        return 8
    if risk_delta >= 24:
        return 6
    if risk_delta >= 18:
        return 9
    if risk_delta >= 12:
        return 13
    if base_score < 55:
        return 18
    if base_score < 70:
        return 20
    if base_score < 82:
        return 17
    return 14


def _max_downward_delta(base_score: int) -> int:
    if base_score >= 80:
        return 34
    if base_score >= 65:
        return 30
    if base_score >= 55:
        return 24
    return 20


def _baseline_absorbed_risk(base_score: int, risk_delta: int, structural_reasons: list[str]) -> int:
    """The total score has already absorbed common risks; dimensions only price topic sensitivity."""
    if risk_delta <= 0:
        return 0
    if structural_reasons:
        return min(risk_delta, 6)
    if base_score < 55:
        return min(risk_delta, 5)
    if base_score < 75:
        return min(risk_delta, 6)
    if base_score < 85:
        return min(risk_delta, 5)
    return min(risk_delta, 4)


def _base_alignment_bias(base_score: int) -> int:
    if base_score < 55:
        return 3
    if base_score < 60:
        return 2
    if base_score < 65:
        return 1
    return 0


def _general_harm_penalty(topic_key: str, harm_key: str, base_value: int) -> int:
    return _weighted_delta(base_value, HARM_MULTIPLIERS[topic_key].get(harm_key, 1.0))


def _pattern_penalty(topic_key: str, pattern_key: str) -> int:
    base = BASE_PATTERN_PENALTIES.get(pattern_key, 0)
    multiplier = PATTERN_MULTIPLIERS[topic_key].get(pattern_key, 0.35)
    return _weighted_delta(base, multiplier)


def _structural_cap_reasons(harms: dict[str, Any], patterns: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    if "pair_25_95" in patterns["detected"]:
        reasons.append("pair_25_95")
    if "pair_69_96" in patterns["detected"]:
        reasons.append("pair_69_96")
    if len({pair for pair in patterns["risk_pairs"] if pair in {"27", "99", "92"}}) >= 2:
        reasons.append("stacked_27_99_92")
    if harms["door_pressure"] and "palace" in harms["emptiness_layers"]:
        reasons.append("palace_empty_with_door_pressure")
    if heavy_harm_count >= 2:
        reasons.append("multiple_heavy_harms")
    if "door" in harms["emptiness_layers"] and any(layer in harms["tomb_layers"] for layer in {"heaven_stem", "earth_stem"}):
        reasons.append("door_empty_with_result_tomb")
    return reasons


def _topic_bonus(topic_key: str, symbols: dict[str, str], harms: dict[str, Any], patterns: dict[str, Any], relation: str) -> tuple[int, list[dict[str, Any]]]:
    if harms["emptiness"] or harms["door_pressure"] or harms["tomb"] or harms["punishment_hit"] or patterns["detected"]:
        risk_clean = False
    else:
        risk_clean = True

    bonuses: list[dict[str, Any]] = []
    value = 0
    if risk_clean:
        value += 3
        bonuses.append({"reason": "无四害与特殊组合干扰", "delta": 3})
    if topic_key == "career" and symbols["door"] in {"开门", "生门"} and symbols["star"] == "天心":
        value += 2
        bonuses.append({"reason": "门星适合事业推进", "delta": 2})
    if topic_key == "wealth" and symbols["door"] == "生门" and symbols["star"] in {"天任", "天心", "天辅"}:
        value += 2
        bonuses.append({"reason": "生门配可用星，财务承接有亮点", "delta": 2})
    if topic_key in {"love", "social", "family"} and patterns["neutral_pairs"]:
        value += 2
        bonuses.append({"reason": "合十结构对关系类专题可作参考", "delta": 2})
    if topic_key == "investment" and symbols["star"] == "天蓬" and symbols["door"] == "生门":
        value += 2
        bonuses.append({"reason": "投资胆识与进财门同见", "delta": 2})
    if topic_key == "travel" and symbols["god"] in {"九天", "值符+九天", "值符"} and symbols["door"] in {"开门", "休门", "生门"}:
        value += 2
        bonuses.append({"reason": "出行外拓条件较顺", "delta": 2})
    if topic_key == "health" and symbols["god"] in {"太阴", "九地"} and symbols["door"] == "休门":
        value += 2
        bonuses.append({"reason": "健康恢复与调养信号同见", "delta": 2})
    if topic_key == "fengshui" and relation in {"palace_generates_door", "same_element", "door_generates_palace"} and not harms["emptiness"]:
        value += 2
        bonuses.append({"reason": "空间承接关系较顺", "delta": 2})
    return value, bonuses


def _score_topic(result: dict[str, Any], topic_key: str) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    symbols = board["symbols"]
    harms = features["harms"]
    patterns = features["patterns"]
    edge_flags = features["edge_flags"]
    base_score = int(result["baseline"]["final_score"])

    positive_reasons: list[dict[str, Any]] = []
    risk_reasons: list[dict[str, Any]] = []
    positive_delta = 0
    risk_delta = 0

    relation = features["palace_door_relation"]
    stem_relation = features["stem_pair_relation"]
    relation_delta = _weighted_delta(RELATION_DELTAS.get(relation, 0), RELATION_MULTIPLIERS[topic_key])
    stem_delta = _weighted_delta(STEM_DELTAS.get(stem_relation, 0), STEM_MULTIPLIERS[topic_key])
    add_pos, add_risk = _add_delta(relation_delta, f"宫门关系:{relation}", positive_reasons, risk_reasons)
    positive_delta += add_pos
    risk_delta += add_risk
    add_pos, add_risk = _add_delta(stem_delta, f"天干/地干:{stem_relation}", positive_reasons, risk_reasons)
    positive_delta += add_pos
    risk_delta += add_risk

    for layer_name, table in (
        ("门", DOOR_DELTAS),
        ("星", STAR_DELTAS),
        ("神", GOD_DELTAS),
    ):
        symbol_key = {"门": "door", "星": "star", "神": "god"}[layer_name]
        value = int(table[topic_key].get(symbols[symbol_key], 0))
        add_pos, add_risk = _add_delta(value, f"{layer_name}:{symbols[symbol_key]}", positive_reasons, risk_reasons)
        positive_delta += add_pos
        risk_delta += add_risk

    emptiness_penalty = 0
    for layer in harms["emptiness_layers"]:
        penalty = _general_harm_penalty(topic_key, "emptiness", BASE_HARM_PENALTIES.get(layer, 2))
        emptiness_penalty += penalty
        if penalty:
            risk_reasons.append({"reason": f"空亡:{layer}", "delta": penalty})
    risk_delta += emptiness_penalty

    door_pressure_penalty = 0
    if harms["door_pressure"]:
        door_pressure_penalty = _general_harm_penalty(topic_key, "door_pressure", 8)
        risk_delta += door_pressure_penalty
        risk_reasons.append({"reason": "门迫", "delta": door_pressure_penalty})

    tomb_penalty = 0
    if harms["tomb"]:
        for layer in harms["tomb_layers"]:
            penalty = _general_harm_penalty(topic_key, "tomb", BASE_TOMB_PENALTIES.get(layer, 3))
            tomb_penalty += penalty
            risk_reasons.append({"reason": f"入墓:{layer}", "delta": penalty})
    risk_delta += tomb_penalty

    punishment_penalty = 0
    if harms["punishment_hit"]:
        punishment_penalty = _general_harm_penalty(topic_key, "punishment", 7)
        risk_delta += punishment_penalty
        risk_reasons.append({"reason": "刑击", "delta": punishment_penalty})

    pattern_penalty = 0
    for detected in patterns["detected"]:
        penalty = _pattern_penalty(topic_key, detected)
        pattern_penalty += penalty
        if penalty:
            risk_reasons.append({"reason": f"特殊组合:{detected}", "delta": penalty})
    risk_delta += pattern_penalty

    edge_penalty = 0
    for flag in edge_flags:
        penalty = int(EDGE_PENALTIES.get(flag, 0))
        edge_penalty += penalty
        if penalty:
            risk_reasons.append({"reason": f"边界特征:{flag}", "delta": penalty})
    risk_delta += edge_penalty

    bonus, bonus_reasons = _topic_bonus(topic_key, symbols, harms, patterns, relation)
    positive_delta += bonus
    positive_reasons.extend(bonus_reasons)

    structural_cap_reasons = [
        reason
        for reason in _structural_cap_reasons(harms, patterns)
        if reason in STRUCTURAL_CAPS[topic_key]
    ]
    gross_risk_delta = risk_delta
    baseline_absorbed_risk = _baseline_absorbed_risk(base_score, gross_risk_delta, structural_cap_reasons)
    risk_delta = max(0, gross_risk_delta - baseline_absorbed_risk)

    max_upward_delta = _max_upward_delta(base_score, risk_delta, structural_cap_reasons)
    max_downward_delta = _max_downward_delta(base_score)
    raw_delta = positive_delta - risk_delta
    bounded_delta = max(-max_downward_delta, min(max_upward_delta, raw_delta))
    raw_score = _clamp(base_score + bounded_delta)
    alignment_bias = _base_alignment_bias(base_score)

    structural_cap = 100
    for reason in structural_cap_reasons:
        structural_cap = min(structural_cap, int(STRUCTURAL_CAPS[topic_key].get(reason, 100)))
    score = min(_clamp(raw_score + alignment_bias), structural_cap)

    risk_pairs = sorted(set(patterns["risk_pairs"]).intersection(TOPIC_HIGH_RISK_PAIRS[topic_key]))
    return {
        "topic_key": topic_key,
        "topic_title": DIMENSION_TITLES[topic_key],
        "score": score,
        "components": {
            "base_score": base_score,
            "positive_delta": positive_delta,
            "risk_delta": risk_delta,
            "gross_risk_delta": gross_risk_delta,
            "baseline_absorbed_risk": baseline_absorbed_risk,
            "raw_delta": raw_delta,
            "bounded_delta": bounded_delta,
            "raw_score": raw_score,
            "alignment_bias": alignment_bias,
            "final_score": score,
            "max_upward_delta": max_upward_delta,
            "max_downward_delta": max_downward_delta,
            "relation_delta": relation_delta,
            "stem_delta": stem_delta,
            "door_delta": DOOR_DELTAS[topic_key].get(symbols["door"], 0),
            "star_delta": STAR_DELTAS[topic_key].get(symbols["star"], 0),
            "god_delta": GOD_DELTAS[topic_key].get(symbols["god"], 0),
            "emptiness_penalty": emptiness_penalty,
            "door_pressure_penalty": door_pressure_penalty,
            "tomb_penalty": tomb_penalty,
            "punishment_penalty": punishment_penalty,
            "pattern_penalty": pattern_penalty,
            "edge_penalty": edge_penalty,
            "bonus": bonus,
            "positive_reasons": positive_reasons,
            "risk_reasons": risk_reasons,
        },
        "features": {
            "anchor_relation": relation,
            "palace_door_relation": relation,
            "stem_relation": stem_relation,
            "stem_pair_relation": stem_relation,
            "palace": symbols["palace"],
            "door": symbols["door"],
            "star": symbols["star"],
            "god": symbols["god"],
            "harms": harms,
            "patterns": patterns,
            "edge_flags": edge_flags,
        },
        "risks": {
            "high_risk_pairs": risk_pairs,
            "structural_cap_reasons": structural_cap_reasons,
            "risk_reasons": risk_reasons,
        },
        "caps": {
            "structural_cap": structural_cap,
            "applied": structural_cap_reasons,
        },
    }


def score_phone_dimensions(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = rules or load_rules()
    baseline_result = score_phone(phone, gender, rules)
    board = build_board(phone, gender, rules)
    features = {
        "palace_door_relation": element_relation(
            rules["palace_elements"][board.symbols["palace"]],
            rules["door_elements"][board.symbols["door"]],
        ),
        "stem_pair_relation": pair_relation(
            rules["stem_elements"][board.symbols["heaven_stem"]],
            rules["stem_elements"][board.symbols["earth_stem"]],
        ),
        "harms": detect_harms(board, rules),
        "patterns": detect_patterns(board),
        "edge_flags": detect_edge_flags(board),
    }
    result: dict[str, Any] = {
        "rules_version": rules["version"],
        "algorithm_version": DIMENSION_SCORE_VERSION,
        "input": {
            "phone": phone,
            "gender": board.gender,
        },
        "baseline": {
            "final_score": int(baseline_result["scoring"]["score_after_structural_cap"]),
            "raw_score": int(baseline_result["scoring"]["raw_score"]),
            "structural_cap": int(baseline_result["scoring"]["structural_cap"]),
            "structural_cap_reasons": baseline_result["scoring"]["structural_cap_reasons"],
            "tags": baseline_result["scoring"]["tags"],
        },
        "board": {
            "last7": board.last7,
            "digits": board.digits,
            "symbols": board.symbols,
        },
        "features": features,
        "dimensions": {},
    }

    dimensions = {
        topic_key: _score_topic(result, topic_key)
        for topic_key in DIMENSION_ORDER
    }
    result["dimensions"] = dimensions
    result["summary"] = {
        "topic_order": DIMENSION_ORDER,
        "base_score": result["baseline"]["final_score"],
        "average_score": round(sum(item["score"] for item in dimensions.values()) / len(dimensions), 2),
        "best_topics": sorted(
            ((key, data["score"]) for key, data in dimensions.items()),
            key=lambda item: item[1],
            reverse=True,
        )[:3],
        "weak_topics": sorted(
            ((key, data["score"]) for key, data in dimensions.items()),
            key=lambda item: item[1],
        )[:3],
    }
    return result


def build_dimension_scores(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return score_phone_dimensions(phone, gender, rules=rules)
