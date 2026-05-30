from __future__ import annotations

from typing import Any

from .labels import CAP_REASON_LABELS, PATTERN_LABELS, RELATION_LABELS, _join_or_none, _label_list, _score_band


def _build_structure(features: dict[str, Any], base_scoring: dict[str, Any]) -> dict[str, Any]:
    return {
        "palace_door_relation": _label_list(RELATION_LABELS, [features["palace_door_relation"]])[0],
        "stem_pair_relation": _label_list(RELATION_LABELS, [features["stem_pair_relation"]])[0],
        "structural_cap_reasons": _label_list(CAP_REASON_LABELS, base_scoring["structural_cap_reasons"]),
    }


def _build_four_harms_check(harms: dict[str, Any], labels: dict[str, str]) -> dict[str, str]:
    return {
        "emptiness": "有" if harms["emptiness"] else "无",
        "door_pressure": "有" if harms["door_pressure"] else "无",
        "tomb": "有" if harms["tomb"] else "无",
        "punishment_hit": "有" if harms["punishment_hit"] else "无",
    }


def _build_pattern_check(patterns: dict[str, Any], edge_flags: list[str]) -> dict[str, Any]:
    return {
        "detected": _label_list(PATTERN_LABELS, patterns["detected"]),
        "risk_pairs": patterns["risk_pairs"],
        "neutral_pairs": patterns["neutral_pairs"],
        "neutral_pairs_scope": patterns.get("neutral_pair_scope"),
        "edge_flags": edge_flags,
    }


def build_phone_summary_facts(result: dict[str, Any], final_score: int) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    structure = _build_structure(features, scoring)
    return {
        "score_band": _score_band(final_score),
        "score_facts": {
            "raw_score": scoring["raw_score"],
            "final_score": final_score,
            "structural_cap": scoring["structural_cap"],
            "confidence": scoring["confidence"],
        },
        "board_basis": {
            "last7": board["last7"],
            "trigger": symbols["trigger"],
            "palace": symbols["palace"],
            "god": symbols["god"],
            "star": symbols["star"],
            "door": symbols["door"],
            "heaven_stem": symbols["heaven_stem"],
            "earth_stem": symbols["earth_stem"],
        },
        "core_relations": {
            "palace_door_relation": structure["palace_door_relation"],
            "stem_pair_relation": structure["stem_pair_relation"],
            "four_harms": {
                "emptiness": "有" if features["harms"]["emptiness"] else "无",
                "door_pressure": "有" if features["harms"]["door_pressure"] else "无",
                "tomb": "有" if features["harms"]["tomb"] else "无",
                "punishment_hit": "有" if features["harms"]["punishment_hit"] else "无",
            },
            "pattern_flags": _label_list(PATTERN_LABELS, features["patterns"]["detected"]),
            "structural_cap_reasons": structure["structural_cap_reasons"],
        },
        "technical_focus": [
            {"focus": "宫门关系", "value": structure["palace_door_relation"], "implication": "只保留关系事实。"},
            {"focus": "后两干关系", "value": structure["stem_pair_relation"], "implication": "只保留关系事实。"},
            {"focus": "四害", "value": _join_or_none([value for value in [
                "空亡" if features["harms"]["emptiness"] else "",
                "门迫" if features["harms"]["door_pressure"] else "",
                "入墓" if features["harms"]["tomb"] else "",
                "击刑" if features["harms"]["punishment_hit"] else "",
            ] if value]), "implication": "只保留事实，不再做型化解释。"},
        ],
    }
