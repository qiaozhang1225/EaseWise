from __future__ import annotations

from typing import Any

COMPONENT_LABELS = {
    "palace_door": "宫门关系",
    "god": "神位权重",
    "star": "星位权重",
    "door": "门位权重",
    "stems": "后两干",
    "harms": "四害保留分",
    "pattern_penalty": "特殊组合扣分",
}
COMPONENT_ORDER = ("palace_door", "god", "star", "door", "stems", "harms", "pattern_penalty")

RELATION_LABELS = {
    "palace_generates_door": "宫生门",
    "same_element": "同气",
    "door_generates_palace": "门生宫",
    "palace_controls_door": "宫克门",
    "door_controls_palace": "门克宫",
    "heaven_generates_earth": "天干生地干",
    "earth_generates_heaven": "地干生天干",
    "heaven_controls_earth": "天干克地干",
    "earth_controls_heaven": "地干克天干",
    "unrelated": "关系平",
}

PATTERN_LABELS = {
    "triple_same": "三连号放大",
    "peach_blossom_111_999": "111/999 放大",
    "pair_69_96": "69/96 风险组合",
    "pair_25_95": "25/95 重风险组合",
    "pair_27_99_92": "27/99/92 扰动组合",
    "tail_repeat_bias": "尾位重复偏压",
}

EDGE_FLAG_LABELS = {
    "palace_emptiness": "宫空亡",
    "god_emptiness": "神空亡",
    "star_emptiness": "星空亡",
    "door_emptiness": "门空亡",
    "trigger_generic_emptiness": "引干空亡",
    "heaven_stem_generic_emptiness": "天干空亡",
    "earth_stem_generic_emptiness": "地干空亡",
    "god_9_dual_read": "神位 9 双重读取",
    "palace_5_special": "宫位 5 特例",
    "star_5_special": "星位 5 特例",
    "door_5_special": "门位 5 特例",
    "star_2_special": "星位 2 特例",
    "door_2_special": "门位 2 特例",
}

CAP_REASON_LABELS = {
    "pair_25_95": "25/95 触发封顶",
    "pair_69_96": "69/96 触发封顶",
    "stacked_27_99_92": "27/99/92 叠加触发封顶",
    "palace_empty_with_door_pressure": "宫空亡叠加门迫触发封顶",
    "multiple_heavy_harms": "多重重害叠加触发封顶",
}


def _label(mapping: dict[str, str], value: str) -> str:
    return mapping.get(value, value)


def _label_list(mapping: dict[str, str], values: list[str]) -> list[str]:
    return [_label(mapping, value) for value in values]


def _humanize_harm(present: bool, layers: list[str], labels: dict[str, str]) -> str:
    if not present:
        return "无"
    if layers:
        return f"有（{'、'.join(labels.get(layer, layer) for layer in layers)}）"
    return "有"


def _join_or_none(values: list[str]) -> str:
    cleaned = [value for value in values if value]
    return "、".join(cleaned) if cleaned else "无"


def _score_band(score: int) -> str:
    if score >= 85:
        return "偏强"
    if score >= 70:
        return "中上"
    if score >= 55:
        return "中等"
    if score >= 40:
        return "偏弱"
    return "承压"
