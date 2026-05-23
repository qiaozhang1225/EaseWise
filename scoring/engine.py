from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RULES_PATH = ROOT / "rules.json"
LAYER_ORDER = [
    "trigger",
    "palace",
    "god",
    "star",
    "door",
    "heaven_stem",
    "earth_stem",
]
LAYER_LABELS = {
    "trigger": "引干",
    "palace": "宫",
    "god": "神",
    "star": "星",
    "door": "门",
    "heaven_stem": "天干",
    "earth_stem": "地干",
}
LAYER_TO_SYSTEM = {
    "trigger": "stem",
    "palace": "palace",
    "god": "god",
    "star": "star",
    "door": "door",
    "heaven_stem": "stem",
    "earth_stem": "stem",
}
GENERATES = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}
CONTROLS = {
    "wood": "earth",
    "earth": "water",
    "water": "fire",
    "fire": "metal",
    "metal": "wood",
}
TOMB_PALACES = {
    "乙": "乾",
    "丙": "乾",
    "戊": "乾",
    "丁": "艮",
    "己": "艮",
    "庚": "艮",
    "辛": "巽",
    "壬": "巽",
    "癸": "坤",
}
PUNISHMENT_PALACES = {
    "戊": "震",
    "己": "坤",
    "庚": "艮",
    "辛": "离",
    "壬": "巽",
    "癸": "巽",
}


@dataclass
class Board:
    last7: str
    digits: dict[str, str]
    symbols: dict[str, str]
    gender: str


def load_rules(path: str | Path | None = None) -> dict[str, Any]:
    rules_path = Path(path) if path else RULES_PATH
    return json.loads(rules_path.read_text(encoding="utf-8"))


def normalize_gender(gender: str) -> str:
    lowered = gender.strip().lower()
    if lowered in {"male", "m", "man", "男", "男命"}:
        return "male"
    if lowered in {"female", "f", "woman", "女", "女命"}:
        return "female"
    raise ValueError(f"Unsupported gender value: {gender}")


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        raise ValueError("Phone input must contain at least 7 digits.")
    return digits


def resolve_mapping_value(value: Any, gender: str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if gender in value:
            return value[gender]
        if "default" in value:
            return value["default"]
    raise ValueError(f"Unsupported mapping value: {value}")


def build_board(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> Board:
    rules = rules or load_rules()
    normalized_gender = normalize_gender(gender)
    digits = normalize_phone(phone)
    last7 = digits[-7:]
    board_digits = dict(zip(LAYER_ORDER, list(last7)))
    symbols: dict[str, str] = {}
    for layer, digit in board_digits.items():
        system = LAYER_TO_SYSTEM[layer]
        raw_value = rules["digit_mapping"][digit][system]
        symbols[layer] = resolve_mapping_value(raw_value, normalized_gender)
    return Board(
        last7=last7,
        digits=board_digits,
        symbols=symbols,
        gender=normalized_gender,
    )


def element_relation(source: str, target: str) -> str:
    if source == target:
        return "same_element"
    if GENERATES[source] == target:
        return "palace_generates_door"
    if GENERATES[target] == source:
        return "door_generates_palace"
    if CONTROLS[source] == target:
        return "palace_controls_door"
    if CONTROLS[target] == source:
        return "door_controls_palace"
    return "unrelated"


def pair_relation(source: str, target: str) -> str:
    if source == target:
        return "same_element"
    if GENERATES[source] == target:
        return "heaven_generates_earth"
    if GENERATES[target] == source:
        return "earth_generates_heaven"
    if CONTROLS[source] == target:
        return "heaven_controls_earth"
    if CONTROLS[target] == source:
        return "earth_controls_heaven"
    return "unrelated"


def detect_edge_flags(board: Board) -> list[str]:
    flags: list[str] = []
    for layer in ("palace", "god", "star", "door"):
        if board.digits[layer] == "0":
            flags.append(f"{layer}_emptiness")
    for layer in ("trigger", "heaven_stem", "earth_stem"):
        if board.digits[layer] == "0":
            flags.append(f"{layer}_generic_emptiness")
    if board.digits["god"] == "9":
        flags.append("god_9_dual_read")
    if board.digits["palace"] == "5":
        flags.append("palace_5_special")
    if board.digits["star"] == "5":
        flags.append("star_5_special")
    if board.digits["door"] == "5":
        flags.append("door_5_special")
    if board.digits["star"] == "2":
        flags.append("star_2_special")
    if board.digits["door"] == "2":
        flags.append("door_2_special")
    return flags


def detect_harms(board: Board, rules: dict[str, Any]) -> dict[str, Any]:
    palace_symbol = board.symbols["palace"]
    door_symbol = board.symbols["door"]
    palace_element = rules["palace_elements"][palace_symbol]
    door_element = rules["door_elements"][door_symbol]

    emptiness_layers = [
        layer
        for layer in LAYER_ORDER
        if board.digits[layer] == "0"
    ]
    stem_layers = {
        "trigger": board.symbols["trigger"],
        "heaven_stem": board.symbols["heaven_stem"],
        "earth_stem": board.symbols["earth_stem"],
    }
    tomb_hits = [
        layer
        for layer, stem in stem_layers.items()
        if TOMB_PALACES.get(stem) == palace_symbol
    ]
    punishment_hits = [
        layer
        for layer, stem in stem_layers.items()
        if PUNISHMENT_PALACES.get(stem) == palace_symbol
    ]
    return {
        "emptiness": bool(emptiness_layers),
        "emptiness_layers": emptiness_layers,
        "door_pressure": element_relation(door_element, palace_element) == "palace_controls_door",
        "tomb": bool(tomb_hits),
        "tomb_layers": tomb_hits,
        "punishment_hit": bool(punishment_hits),
        "punishment_layers": punishment_hits,
    }


def detect_patterns(board: Board) -> dict[str, Any]:
    last7 = board.last7
    pairs = [last7[index : index + 2] for index in range(len(last7) - 1)]
    triples = [last7[index : index + 3] for index in range(len(last7) - 2)]
    risk_pairs = {pair for pair in pairs if pair in {"69", "96", "25", "95", "27", "99", "92"}}
    neutral_pairs = {pair for pair in pairs if pair in {"91", "37", "28", "46", "55"}}
    counts = {digit: last7.count(digit) for digit in set(last7)}

    detected: list[str] = []
    if any(triple[0] == triple[1] == triple[2] for triple in triples):
        detected.append("triple_same")
    if "111" in triples or "999" in triples:
        detected.append("peach_blossom_111_999")
    if any(pair in {"69", "96"} for pair in risk_pairs):
        detected.append("pair_69_96")
    if any(pair in {"25", "95"} for pair in risk_pairs) or "905" in last7:
        detected.append("pair_25_95")
    if any(pair in {"27", "99", "92"} for pair in risk_pairs):
        detected.append("pair_27_99_92")
    if board.digits["earth_stem"] == board.digits["heaven_stem"]:
        detected.append("tail_repeat_bias")

    return {
        "pairs": pairs,
        "triples": triples,
        "risk_pairs": sorted(risk_pairs),
        "neutral_pairs": sorted(neutral_pairs),
        "neutral_pair_scope": "relationship_only",
        "detected": detected,
        "digit_counts": counts,
    }


def score_palace_door(board: Board, harms: dict[str, Any], rules: dict[str, Any]) -> tuple[int, str]:
    palace_symbol = board.symbols["palace"]
    door_symbol = board.symbols["door"]
    palace_element = rules["palace_elements"][palace_symbol]
    door_element = rules["door_elements"][door_symbol]
    relation = element_relation(palace_element, door_element)
    score = rules["weights"]["palace_door"].get(relation, 10)
    palace_context = rules["weights"].get("palace_context", {})
    if "palace" in harms["emptiness_layers"]:
        borrowed_palace_cap = palace_context.get("borrowed_palace_cap")
        if borrowed_palace_cap is not None:
            score = min(score, borrowed_palace_cap)
    return score, relation


def score_god(board: Board, harms: dict[str, Any], rules: dict[str, Any]) -> int:
    score = rules["weights"]["god"][board.symbols["god"]]
    god_context = rules["weights"].get("god_context", {})
    if "god" in harms["emptiness_layers"]:
        borrowed_god_cap = god_context.get("borrowed_god_cap")
        if borrowed_god_cap is not None:
            score = min(score, borrowed_god_cap)
    return max(0, score)


def score_star(board: Board, harms: dict[str, Any], rules: dict[str, Any]) -> int:
    score = rules["weights"]["star"][board.symbols["star"]]
    star_context = rules["weights"].get("star_context", {})
    if "star" in harms["emptiness_layers"]:
        borrowed_star_cap = star_context.get("borrowed_star_cap")
        if borrowed_star_cap is not None:
            score = min(score, borrowed_star_cap)
    return max(0, score)


def score_door(board: Board, harms: dict[str, Any], rules: dict[str, Any]) -> int:
    score = rules["weights"]["door"][board.symbols["door"]]
    door_context = rules["weights"].get("door_context", {})
    if "door" in harms["emptiness_layers"]:
        borrowed_door_cap = door_context.get("borrowed_door_cap")
        if borrowed_door_cap is not None:
            score = min(score, borrowed_door_cap)
    return max(0, score)


def score_stems(board: Board, harms: dict[str, Any], rules: dict[str, Any]) -> tuple[int, str]:
    heaven = board.symbols["heaven_stem"]
    earth = board.symbols["earth_stem"]
    trigger = board.symbols["trigger"]
    heaven_element = rules["stem_elements"][heaven]
    earth_element = rules["stem_elements"][earth]
    trigger_element = rules["stem_elements"][trigger]
    relation = pair_relation(heaven_element, earth_element)
    if heaven == earth:
        score = rules["weights"]["stem_pair"]["same_stem"]
    else:
        score = rules["weights"]["stem_pair"][relation]
    if (
        trigger_element == heaven_element
        or trigger_element == earth_element
        or GENERATES[trigger_element] == heaven_element
        or GENERATES[trigger_element] == earth_element
    ):
        score += rules["weights"]["trigger_alignment_bonus"]
    score = min(15, score)

    stem_context = rules["weights"].get("stem_context", {})
    tomb_layers = set(harms["tomb_layers"])
    if "trigger" in tomb_layers:
        score -= stem_context.get("trigger_tomb_penalty", 0)
    if "heaven_stem" in tomb_layers:
        score -= stem_context.get("heaven_tomb_penalty", 0)
    if "earth_stem" in tomb_layers:
        score -= stem_context.get("earth_tomb_penalty", 0)
    if {"heaven_stem", "earth_stem"}.issubset(tomb_layers):
        score -= stem_context.get("double_result_tomb_penalty", 0)

    return max(0, score), relation


def score_harms(harms: dict[str, Any], rules: dict[str, Any]) -> tuple[int, int]:
    weights = rules["weights"]["harms"]
    penalty = 0
    for layer in harms["emptiness_layers"]:
        if layer == "palace":
            penalty += weights["palace_emptiness"]
        elif layer == "god":
            penalty += weights["god_emptiness"]
        elif layer == "star":
            penalty += weights["star_emptiness"]
        elif layer == "door":
            penalty += weights["door_emptiness"]
        else:
            penalty += weights["other_emptiness"]
    if harms["door_pressure"]:
        penalty += weights["door_pressure"]
    for layer in harms["tomb_layers"]:
        if layer == "trigger":
            penalty += weights.get("trigger_tomb", weights.get("tomb", 0))
        elif layer == "heaven_stem":
            penalty += weights.get("heaven_tomb", weights.get("tomb", 0))
        elif layer == "earth_stem":
            penalty += weights.get("earth_tomb", weights.get("tomb", 0))
        else:
            penalty += weights.get("tomb", 0)
    result_tomb_layers = {layer for layer in harms["tomb_layers"] if layer in {"heaven_stem", "earth_stem"}}
    if "door" in harms["emptiness_layers"] and result_tomb_layers:
        penalty += weights.get("door_empty_with_result_tomb", 0)
    if "door" in harms["emptiness_layers"] and len(result_tomb_layers) >= 2:
        penalty += weights.get("door_empty_with_double_result_tomb", 0)
    if harms["punishment_hit"]:
        penalty += weights["punishment_hit"]
    return max(0, weights["base"] - penalty), penalty


def score_patterns(patterns: dict[str, Any], rules: dict[str, Any]) -> int:
    weights = rules["weights"]["patterns"]
    penalty = 0
    for detected in patterns["detected"]:
        penalty += weights[detected]
    return penalty


def apply_structural_caps(
    board: Board,
    harms: dict[str, Any],
    patterns: dict[str, Any],
    raw_score: int,
    rules: dict[str, Any],
) -> tuple[int, int, list[str]]:
    caps = rules["caps"]
    applied: list[tuple[int, str]] = []

    if "pair_25_95" in patterns["detected"]:
        applied.append((caps["pair_25_95"], "pair_25_95"))
    if "pair_69_96" in patterns["detected"]:
        applied.append((caps["general_69_96"], "pair_69_96"))
    stacked_relationship_pairs = {
        pair for pair in patterns["risk_pairs"] if pair in {"27", "99", "92"}
    }
    if len(stacked_relationship_pairs) >= 2:
        applied.append((caps["stacked_27_99_92"], "stacked_27_99_92"))
    if harms["door_pressure"] and "palace" in harms["emptiness_layers"]:
        applied.append((caps["palace_empty_with_door_pressure"], "palace_empty_with_door_pressure"))
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    if heavy_harm_count >= 2:
        applied.append((caps["multiple_heavy_harms"], "multiple_heavy_harms"))

    if not applied:
        return min(100, raw_score), 100, []
    structural_cap = min(cap for cap, _ in applied)
    return min(structural_cap, raw_score), structural_cap, [reason for _, reason in applied]


def build_tags(
    board: Board,
    relation: str,
    harms: dict[str, Any],
    patterns: dict[str, Any],
) -> list[str]:
    tags: list[str] = []
    if relation == "palace_generates_door":
        tags.append("平台托举")
    if relation == "door_controls_palace":
        tags.append("门迫风险")
    if board.symbols["god"] in {"值符", "值符+九天", "九天"}:
        tags.append("外扩驱动")
    if "pair_69_96" in patterns["detected"]:
        tags.append("权责风险")
    if "pair_25_95" in patterns["detected"]:
        tags.append("重风险组合")
    if "pair_27_99_92" in patterns["detected"] or "peach_blossom_111_999" in patterns["detected"]:
        tags.append("桃花扰动")
    if harms["punishment_hit"] or harms["door_pressure"] or board.symbols["star"] == "天芮":
        tags.append("高压消耗")
    if "palace" in harms["emptiness_layers"]:
        tags.append("落不实")
    return sorted(set(tags))


def compute_confidence(board: Board, edge_flags: list[str]) -> str:
    if not edge_flags:
        return "A"
    severe = {
        "palace_emptiness",
        "palace_5_special",
        "star_5_special",
        "door_5_special",
    }
    if severe.intersection(edge_flags) or len(edge_flags) >= 3:
        return "C"
    if board.digits["god"] == "9":
        return "B"
    return "B"


def score_phone(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = rules or load_rules()
    board = build_board(phone, gender, rules)
    edge_flags = detect_edge_flags(board)
    harms = detect_harms(board, rules)
    patterns = detect_patterns(board)
    palace_door_score, relation = score_palace_door(board, harms, rules)
    god_score = score_god(board, harms, rules)
    star_score = score_star(board, harms, rules)
    door_score = score_door(board, harms, rules)
    stem_score, stem_relation = score_stems(board, harms, rules)
    harm_score, harm_penalty = score_harms(harms, rules)
    pattern_penalty = score_patterns(patterns, rules)

    raw_score = palace_door_score + god_score + star_score + door_score + stem_score + harm_score
    raw_score -= pattern_penalty
    raw_score = max(0, min(100, raw_score))

    capped_score, structural_cap, structural_cap_reasons = apply_structural_caps(
        board=board,
        harms=harms,
        patterns=patterns,
        raw_score=raw_score,
        rules=rules,
    )
    confidence = compute_confidence(board, edge_flags)
    tags = build_tags(board, relation, harms, patterns)

    return {
        "rules_version": rules["version"],
        "input": {
            "phone": phone,
            "gender": board.gender,
        },
        "board": {
            "last7": board.last7,
            "digits": board.digits,
            "symbols": board.symbols,
            "labels": LAYER_LABELS,
        },
        "features": {
            "palace_door_relation": relation,
            "stem_pair_relation": stem_relation,
            "harms": harms,
            "patterns": patterns,
            "edge_flags": edge_flags,
        },
        "scoring": {
            "components": {
                "palace_door": palace_door_score,
                "god": god_score,
                "star": star_score,
                "door": door_score,
                "stems": stem_score,
                "harms": harm_score,
                "pattern_penalty": pattern_penalty,
            },
            "raw_score": raw_score,
            "score_after_structural_cap": capped_score,
            "structural_cap": structural_cap,
            "structural_cap_reasons": structural_cap_reasons,
            "confidence": confidence,
            "tags": tags,
        },
    }


def main() -> None:
    raise SystemExit("Use `python -m scoring.cli`.")


if __name__ == "__main__":
    main()
