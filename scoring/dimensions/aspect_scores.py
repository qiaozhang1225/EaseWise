from __future__ import annotations

from typing import Any

ASPECT_SCORE_KEYS = (
    "career",
    "wealth",
    "love",
    "health",
    "acad",
    "social",
    "travel",
    "law",
    "risk",
)

RELATION_BONUSES = {
    "palace_generates_door": 10,
    "same_element": 7,
    "door_generates_palace": 4,
    "unrelated": 0,
    "palace_controls_door": -5,
    "door_controls_palace": -8,
}

STEM_RELATION_BONUSES = {
    "heaven_generates_earth": 5,
    "earth_generates_heaven": 4,
    "same_element": 3,
    "unrelated": 0,
    "heaven_controls_earth": -2,
    "earth_controls_heaven": -4,
}

DEFAULT_LAYER_PENALTIES = {
    "palace": 7,
    "door": 6,
    "star": 5,
    "god": 4,
    "trigger": 2,
    "heaven_stem": 4,
    "earth_stem": 4,
}

DEFAULT_TOMB_LAYER_PENALTIES = {
    "trigger": 2,
    "heaven_stem": 3,
    "earth_stem": 3,
}

DEFAULT_PATTERN_PENALTIES = {
    "triple_same": 2,
    "pair_69_96": 5,
    "pair_25_95": 12,
    "pair_27_99_92": 5,
    "peach_blossom_111_999": 4,
    "tail_repeat_bias": 2,
}

DEFAULT_CAP_PENALTIES = {
    "pair_25_95": 10,
    "pair_69_96": 6,
    "stacked_27_99_92": 8,
    "palace_empty_with_door_pressure": 8,
    "multiple_heavy_harms": 10,
}

ASPECT_PROFILES: dict[str, dict[str, Any]] = {
    "career": {
        "base": 68,
        "door": {"开门": 9, "生门": 7, "休门": 3, "景门": 2, "惊门": -1, "杜门": -2, "伤门": -5, "死门": -8},
        "star": {"天心": 8, "天任": 7, "天辅": 5, "天冲": 4, "天英": 2, "天禽": 0, "天蓬": -2, "天柱": -3, "天芮": -8},
        "god": {"值符": 7, "值符+九天": 8, "九天": 6, "六合": 3, "太阴": 2, "九地": 1, "玄武": -2, "腾蛇": -4, "白虎": -5},
        "door_pressure_penalty": 7,
        "tomb_penalty": 5,
        "punishment_penalty": 5,
        "clean_bonus": 4,
    },
    "wealth": {
        "base": 68,
        "door": {"生门": 9, "开门": 8, "休门": 5, "景门": 4, "惊门": -1, "杜门": -2, "伤门": -4, "死门": -9},
        "star": {"天任": 8, "天心": 7, "天辅": 5, "天英": 3, "天禽": 1, "天冲": 1, "天蓬": -2, "天柱": -3, "天芮": -8},
        "god": {"值符": 6, "值符+九天": 7, "九天": 6, "六合": 4, "太阴": 3, "九地": 2, "玄武": -1, "腾蛇": -4, "白虎": -4},
        "door_pressure_penalty": 7,
        "tomb_penalty": 6,
        "punishment_penalty": 5,
        "clean_bonus": 4,
    },
    "love": {
        "base": 68,
        "door": {"休门": 8, "生门": 7, "景门": 4, "开门": 2, "杜门": 1, "惊门": -2, "伤门": -4, "死门": -8},
        "star": {"天辅": 6, "天任": 5, "天心": 4, "天英": 3, "天禽": 1, "天蓬": -2, "天冲": -2, "天柱": -4, "天芮": -6},
        "god": {"六合": 8, "太阴": 7, "九地": 3, "值符": 2, "九天": 1, "值符+九天": 0, "玄武": -3, "腾蛇": -5, "白虎": -6},
        "door_pressure_penalty": 4,
        "tomb_penalty": 4,
        "punishment_penalty": 5,
        "pattern_penalties": {"pair_27_99_92": 8, "peach_blossom_111_999": 7, "pair_69_96": 6},
        "clean_bonus": 3,
        "neutral_pair_bonus": 4,
    },
    "health": {
        "base": 66,
        "door": {"休门": 8, "生门": 6, "杜门": 4, "开门": 1, "景门": -1, "惊门": -4, "伤门": -6, "死门": -10},
        "star": {"天心": 6, "天任": 6, "天辅": 5, "天禽": 1, "天冲": -1, "天英": -3, "天蓬": -3, "天柱": -5, "天芮": -10},
        "god": {"太阴": 5, "九地": 5, "六合": 3, "值符": 2, "九天": 0, "值符+九天": -1, "玄武": -4, "腾蛇": -5, "白虎": -8},
        "layer_penalties": {"palace": 5, "door": 6, "star": 6, "god": 5, "trigger": 2, "heaven_stem": 4, "earth_stem": 4},
        "door_pressure_penalty": 6,
        "tomb_penalty": 7,
        "punishment_penalty": 6,
        "pattern_penalties": {"pair_25_95": 14, "pair_27_99_92": 4, "pair_69_96": 3, "peach_blossom_111_999": 3},
        "clean_bonus": 4,
    },
    "acad": {
        "base": 67,
        "door": {"休门": 8, "杜门": 7, "生门": 6, "开门": 2, "景门": 1, "惊门": -4, "伤门": -5, "死门": -10},
        "star": {"天辅": 8, "天心": 7, "天任": 6, "天英": 2, "天禽": 1, "天冲": 0, "天蓬": -2, "天柱": -6, "天芮": -8},
        "god": {"太阴": 6, "六合": 5, "九地": 4, "值符": 3, "九天": 2, "值符+九天": 1, "玄武": -3, "腾蛇": -4, "白虎": -5},
        "layer_penalties": {"palace": 4, "door": 5, "star": 5, "god": 4, "trigger": 2, "heaven_stem": 4, "earth_stem": 4},
        "door_pressure_penalty": 5,
        "tomb_penalty": 6,
        "punishment_penalty": 5,
        "pattern_penalties": {"pair_25_95": 12, "pair_27_99_92": 4, "pair_69_96": 4, "peach_blossom_111_999": 2},
        "clean_bonus": 4,
    },
    "social": {
        "base": 68,
        "door": {"休门": 6, "开门": 5, "生门": 4, "景门": 3, "杜门": 0, "惊门": -2, "伤门": -5, "死门": -7},
        "star": {"天辅": 5, "天英": 4, "天心": 3, "天任": 3, "天禽": 1, "天冲": 1, "天蓬": -2, "天柱": -4, "天芮": -6},
        "god": {"六合": 8, "太阴": 6, "九天": 3, "值符": 2, "九地": 2, "值符+九天": 1, "玄武": -3, "腾蛇": -5, "白虎": -6},
        "door_pressure_penalty": 5,
        "tomb_penalty": 4,
        "punishment_penalty": 6,
        "pattern_penalties": {"pair_27_99_92": 8, "peach_blossom_111_999": 6, "pair_69_96": 6},
        "clean_bonus": 3,
        "neutral_pair_bonus": 3,
    },
    "travel": {
        "base": 68,
        "door": {"开门": 8, "休门": 7, "生门": 6, "景门": 3, "惊门": -1, "杜门": -2, "伤门": -5, "死门": -8},
        "star": {"天冲": 6, "天任": 5, "天心": 4, "天英": 3, "天辅": 2, "天禽": 0, "天柱": -2, "天蓬": -5, "天芮": -6},
        "god": {"九天": 7, "值符+九天": 7, "值符": 6, "六合": 3, "太阴": 2, "九地": 2, "玄武": -2, "腾蛇": -4, "白虎": -4},
        "door_pressure_penalty": 6,
        "tomb_penalty": 5,
        "punishment_penalty": 4,
        "pattern_penalties": {"pair_25_95": 12, "pair_69_96": 5, "pair_27_99_92": 3, "peach_blossom_111_999": 2},
        "clean_bonus": 4,
    },
    "law": {
        "base": 69,
        "door": {"开门": 9, "生门": 7, "休门": 6, "景门": 4, "杜门": 1, "惊门": -4, "伤门": -5, "死门": -8},
        "star": {"天心": 8, "天辅": 6, "天任": 4, "天英": 2, "天禽": 1, "天冲": 0, "天柱": -2, "天蓬": -3, "天芮": -5},
        "god": {"值符": 7, "六合": 6, "太阴": 5, "九地": 2, "值符+九天": 2, "九天": 1, "玄武": -6, "腾蛇": -6, "白虎": -3},
        "door_pressure_penalty": 7,
        "tomb_penalty": 4,
        "punishment_penalty": 6,
        "pattern_penalties": {"pair_25_95": 12, "pair_69_96": 7, "pair_27_99_92": 2, "peach_blossom_111_999": 1},
        "clean_bonus": 4,
    },
    "risk": {
        "base": 72,
        "door": {"休门": 7, "生门": 6, "开门": 5, "杜门": 2, "景门": 1, "惊门": -3, "伤门": -5, "死门": -8},
        "star": {"天心": 6, "天任": 5, "天辅": 4, "天禽": 2, "天英": 0, "天冲": -1, "天柱": -3, "天蓬": -4, "天芮": -7},
        "god": {"九地": 6, "太阴": 5, "六合": 4, "值符": 3, "九天": 1, "值符+九天": 1, "玄武": -4, "腾蛇": -5, "白虎": -6},
        "layer_penalties": {"palace": 8, "door": 8, "star": 5, "god": 5, "trigger": 2, "heaven_stem": 4, "earth_stem": 4},
        "door_pressure_penalty": 8,
        "tomb_penalty": 6,
        "punishment_penalty": 7,
        "pattern_penalties": {"pair_25_95": 16, "pair_27_99_92": 7, "pair_69_96": 6, "peach_blossom_111_999": 6},
        "clean_bonus": 5,
    },
}


def grade_from_score(score: int | None) -> str | None:
    if score is None:
        return None
    if score >= 90:
        return "上吉"
    if score >= 80:
        return "中吉"
    if score >= 70:
        return "中平"
    return "落陷"


def build_aspect_scores(result: dict[str, Any]) -> dict[str, dict[str, int | str]]:
    return {aspect_key: _score_aspect(result, aspect_key) for aspect_key in ASPECT_SCORE_KEYS}


def _score_aspect(result: dict[str, Any], aspect_key: str) -> dict[str, int | str]:
    profile = ASPECT_PROFILES[aspect_key]
    board_symbols = result["board"]["symbols"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]

    score = int(profile["base"])
    score += RELATION_BONUSES.get(features["palace_door_relation"], 0)
    score += STEM_RELATION_BONUSES.get(features["stem_pair_relation"], 0)
    score += int(profile["door"].get(board_symbols["door"], 0))
    score += int(profile["star"].get(board_symbols["star"], 0))
    score += int(profile["god"].get(board_symbols["god"], 0))
    score -= _emptiness_penalty(harms, profile)
    if harms["door_pressure"]:
        score -= int(profile["door_pressure_penalty"])
    score -= _tomb_penalty(harms, profile)
    if harms["punishment_hit"]:
        score -= int(profile["punishment_penalty"])
    score -= _pattern_penalty(patterns, profile)
    score -= _cap_penalty(scoring.get("structural_cap_reasons", []), profile)
    score += _special_bonus(result, aspect_key, profile)
    score = min(score, _hard_cap(result, aspect_key))
    score = max(0, min(100, score))
    return {
        "score": score,
        "grade": grade_from_score(score) or "落陷",
    }


def _emptiness_penalty(harms: dict[str, Any], profile: dict[str, Any]) -> int:
    layer_penalties = dict(DEFAULT_LAYER_PENALTIES)
    layer_penalties.update(profile.get("layer_penalties", {}))
    return sum(int(layer_penalties.get(layer, 2)) for layer in harms["emptiness_layers"])


def _tomb_penalty(harms: dict[str, Any], profile: dict[str, Any]) -> int:
    if not harms["tomb"]:
        return 0
    penalty = int(profile["tomb_penalty"])
    tomb_layer_penalties = dict(DEFAULT_TOMB_LAYER_PENALTIES)
    tomb_layer_penalties.update(profile.get("tomb_layer_penalties", {}))
    for layer in harms["tomb_layers"]:
        penalty += int(tomb_layer_penalties.get(layer, 0))
    return penalty


def _pattern_penalty(patterns: dict[str, Any], profile: dict[str, Any]) -> int:
    penalties = dict(DEFAULT_PATTERN_PENALTIES)
    penalties.update(profile.get("pattern_penalties", {}))
    return sum(int(penalties.get(flag, 0)) for flag in patterns["detected"])


def _cap_penalty(structural_cap_reasons: list[str], profile: dict[str, Any]) -> int:
    penalties = dict(DEFAULT_CAP_PENALTIES)
    penalties.update(profile.get("cap_penalties", {}))
    return sum(int(penalties.get(reason, 0)) for reason in structural_cap_reasons)


def _special_bonus(result: dict[str, Any], aspect_key: str, profile: dict[str, Any]) -> int:
    board_symbols = result["board"]["symbols"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    bonus = 0

    if not harms["door_pressure"] and not harms["tomb"] and not harms["punishment_hit"] and not patterns["detected"] and not scoring["structural_cap_reasons"]:
        bonus += int(profile.get("clean_bonus", 0))

    if aspect_key in {"love", "social"} and patterns["neutral_pairs"]:
        bonus += int(profile.get("neutral_pair_bonus", 0))

    if aspect_key == "acad" and board_symbols["star"] in {"天辅", "天心", "天任"} and board_symbols["door"] in {"休门", "杜门", "生门"}:
        bonus += 2

    if aspect_key == "travel" and board_symbols["god"] in {"九天", "值符", "值符+九天"} and board_symbols["door"] in {"开门", "休门", "生门"}:
        bonus += 2

    if aspect_key == "law" and board_symbols["star"] == "天心" and board_symbols["door"] in {"开门", "生门", "休门"}:
        bonus += 2

    if aspect_key == "risk":
        heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
        if heavy_harm_count == 0 and not patterns["detected"] and not scoring["structural_cap_reasons"]:
            bonus += 4

    return bonus


def _hard_cap(result: dict[str, Any], aspect_key: str) -> int:
    patterns = result["features"]["patterns"]
    structural_cap_reasons = set(result["scoring"]["structural_cap_reasons"])
    heavy_harm_count = int(result["features"]["harms"]["door_pressure"]) + int(result["features"]["harms"]["tomb"]) + int(result["features"]["harms"]["punishment_hit"])
    cap = 100

    if "pair_25_95" in patterns["detected"]:
        cap = min(cap, 59 if aspect_key in {"health", "risk"} else 68)

    if "multiple_heavy_harms" in structural_cap_reasons or heavy_harm_count >= 3:
        cap = min(cap, 54 if aspect_key in {"health", "risk"} else 64)

    if "palace_empty_with_door_pressure" in structural_cap_reasons and aspect_key in {"career", "wealth", "travel", "law"}:
        cap = min(cap, 68)

    if "stacked_27_99_92" in structural_cap_reasons and aspect_key in {"love", "social", "risk"}:
        cap = min(cap, 68)

    if "pair_69_96" in patterns["detected"] and aspect_key in {"career", "wealth", "law"}:
        cap = min(cap, 79)

    return cap
