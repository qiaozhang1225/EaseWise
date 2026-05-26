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

DIMENSION_SCORE_V2_VERSION = "0.2.0"

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
    "stability",
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
    "stability": "稳定性",
}

RELATION_SCORES = {
    "palace_generates_door": 12,
    "same_element": 9,
    "door_generates_palace": 7,
    "unrelated": 5,
    "palace_controls_door": 1,
    "door_controls_palace": -2,
}

PAIR_RELATION_SCORES = {
    "heaven_generates_earth": 7,
    "earth_generates_heaven": 6,
    "same_element": 4,
    "unrelated": 2,
    "heaven_controls_earth": -1,
    "earth_controls_heaven": -3,
}

BASE_PROFILES: dict[str, dict[str, int]] = {
    "career": {"base": 66, "door": 8, "star": 7, "god": 6, "anchor": 8, "pair": 5},
    "wealth": {"base": 66, "door": 9, "star": 6, "god": 5, "anchor": 7, "pair": 5},
    "love": {"base": 67, "door": 8, "star": 5, "god": 8, "anchor": 6, "pair": 7},
    "health": {"base": 64, "door": 7, "star": 8, "god": 5, "anchor": 5, "pair": 4},
    "acad": {"base": 65, "door": 6, "star": 9, "god": 5, "anchor": 5, "pair": 6},
    "fortune": {"base": 67, "door": 7, "star": 6, "god": 7, "anchor": 7, "pair": 5},
    "investment": {"base": 63, "door": 8, "star": 5, "god": 6, "anchor": 6, "pair": 7},
    "travel": {"base": 65, "door": 8, "star": 6, "god": 7, "anchor": 6, "pair": 7},
    "social": {"base": 66, "door": 7, "star": 5, "god": 8, "anchor": 5, "pair": 6},
    "family": {"base": 67, "door": 8, "star": 6, "god": 7, "anchor": 6, "pair": 7},
    "personality": {"base": 68, "door": 7, "star": 7, "god": 6, "anchor": 6, "pair": 5},
    "fengshui": {"base": 64, "door": 8, "star": 6, "god": 7, "anchor": 7, "pair": 5},
    "stability": {"base": 62, "door": 8, "star": 6, "god": 6, "anchor": 6, "pair": 4},
}

DOOR_SCORES = {
    "career": {"开门": 12, "生门": 8, "景门": 4, "休门": 3, "杜门": 1, "惊门": -1, "伤门": -5, "死门": -8},
    "wealth": {"生门": 12, "开门": 10, "休门": 6, "景门": 5, "惊门": -1, "杜门": -2, "伤门": -4, "死门": -9},
    "love": {"休门": 10, "生门": 8, "开门": 4, "景门": 5, "杜门": 2, "惊门": -2, "伤门": -5, "死门": -8},
    "health": {"休门": 10, "生门": 7, "杜门": 4, "开门": 1, "景门": -1, "惊门": -4, "伤门": -7, "死门": -10},
    "acad": {"杜门": 10, "休门": 8, "生门": 6, "开门": 3, "景门": 2, "惊门": -3, "伤门": -5, "死门": -9},
    "fortune": {"开门": 8, "生门": 8, "休门": 7, "景门": 4, "惊门": -1, "杜门": -2, "伤门": -4, "死门": -8},
    "investment": {"生门": 10, "开门": 8, "休门": 4, "景门": 3, "惊门": -2, "杜门": -3, "伤门": -5, "死门": -9},
    "travel": {"开门": 10, "休门": 8, "生门": 7, "景门": 4, "惊门": -1, "杜门": -2, "伤门": -5, "死门": -8},
    "social": {"休门": 8, "开门": 7, "生门": 5, "景门": 4, "杜门": 1, "惊门": -2, "伤门": -5, "死门": -7},
    "family": {"休门": 11, "生门": 8, "开门": 4, "景门": 3, "杜门": 2, "惊门": -2, "伤门": -4, "死门": -9},
    "personality": {"休门": 7, "开门": 7, "生门": 5, "景门": 4, "杜门": 3, "惊门": -1, "伤门": -4, "死门": -6},
    "fengshui": {"生门": 8, "开门": 7, "休门": 6, "景门": 4, "杜门": 2, "惊门": -2, "伤门": -4, "死门": -8},
    "stability": {"休门": 8, "生门": 7, "开门": 4, "景门": 3, "杜门": 2, "惊门": -2, "伤门": -5, "死门": -9},
}

STAR_SCORES = {
    "career": {"天心": 11, "天任": 9, "天辅": 7, "天冲": 4, "天英": 2, "天禽": 1, "天蓬": 0, "天柱": -3, "天芮": -8},
    "wealth": {"天任": 10, "天心": 9, "天辅": 6, "天英": 4, "天禽": 2, "天冲": 1, "天蓬": 0, "天柱": -2, "天芮": -8},
    "love": {"天辅": 7, "天任": 6, "天心": 5, "天英": 4, "天禽": 2, "天蓬": -2, "天冲": -2, "天柱": -4, "天芮": -6},
    "health": {"天心": 7, "天任": 7, "天辅": 6, "天禽": 2, "天冲": -1, "天英": -3, "天蓬": -4, "天柱": -5, "天芮": -10},
    "acad": {"天辅": 10, "天心": 8, "天任": 7, "天英": 3, "天禽": 2, "天冲": 1, "天蓬": 0, "天柱": -4, "天芮": -7},
    "fortune": {"天心": 7, "天任": 6, "天辅": 5, "天英": 4, "天冲": 2, "天禽": 2, "天蓬": 0, "天柱": -2, "天芮": -7},
    "investment": {"天蓬": 4, "天心": 6, "天任": 5, "天辅": 4, "天英": 2, "天冲": 1, "天禽": 2, "天柱": -3, "天芮": -7},
    "travel": {"天冲": 8, "天任": 5, "天心": 4, "天英": 4, "天辅": 3, "天禽": 1, "天蓬": -4, "天柱": -2, "天芮": -5},
    "social": {"天辅": 7, "天心": 6, "天任": 5, "天英": 5, "天禽": 3, "天冲": 2, "天蓬": -2, "天柱": -4, "天芮": -5},
    "family": {"天心": 7, "天任": 6, "天辅": 6, "天禽": 3, "天英": 2, "天冲": 0, "天蓬": -2, "天柱": -4, "天芮": -6},
    "personality": {"天心": 8, "天任": 7, "天辅": 7, "天禽": 5, "天英": 4, "天蓬": -1, "天冲": -1, "天柱": -3, "天芮": -4},
    "fengshui": {"天心": 7, "天任": 6, "天辅": 5, "天英": 4, "天禽": 3, "天冲": 1, "天蓬": -3, "天柱": -2, "天芮": -5},
    "stability": {"天任": 7, "天心": 6, "天辅": 5, "天禽": 4, "天英": 2, "天冲": 1, "天蓬": -4, "天柱": -3, "天芮": -6},
}

GOD_SCORES = {
    "career": {"值符": 9, "值符+九天": 9, "九天": 8, "六合": 5, "太阴": 4, "九地": 3, "玄武": 0, "腾蛇": -3, "白虎": -4},
    "wealth": {"值符": 8, "值符+九天": 8, "九天": 7, "六合": 6, "太阴": 5, "九地": 4, "玄武": 1, "腾蛇": -3, "白虎": -4},
    "love": {"六合": 10, "太阴": 8, "九地": 4, "值符": 3, "九天": 2, "值符+九天": 1, "玄武": -3, "腾蛇": -5, "白虎": -6},
    "health": {"太阴": 6, "九地": 6, "六合": 4, "值符": 3, "九天": 1, "值符+九天": 0, "玄武": -4, "腾蛇": -5, "白虎": -8},
    "acad": {"太阴": 7, "六合": 6, "九地": 5, "值符": 4, "九天": 3, "值符+九天": 2, "玄武": -3, "腾蛇": -4, "白虎": -5},
    "fortune": {"值符": 8, "值符+九天": 8, "九天": 7, "六合": 5, "太阴": 4, "九地": 3, "玄武": -2, "腾蛇": -4, "白虎": -5},
    "investment": {"值符": 8, "值符+九天": 8, "九天": 7, "太阴": 5, "六合": 4, "九地": 3, "玄武": -4, "腾蛇": -5, "白虎": -6},
    "travel": {"九天": 10, "值符+九天": 9, "值符": 8, "六合": 4, "太阴": 3, "九地": 3, "玄武": -2, "腾蛇": -4, "白虎": -5},
    "social": {"六合": 10, "太阴": 7, "值符": 4, "九地": 4, "九天": 3, "值符+九天": 2, "玄武": -3, "腾蛇": -5, "白虎": -6},
    "family": {"六合": 9, "太阴": 8, "九地": 5, "值符": 4, "九天": 2, "值符+九天": 1, "玄武": -3, "腾蛇": -4, "白虎": -6},
    "personality": {"值符": 7, "六合": 7, "太阴": 6, "九地": 5, "九天": 4, "值符+九天": 4, "玄武": -3, "腾蛇": -4, "白虎": -5},
    "fengshui": {"值符": 8, "六合": 6, "太阴": 6, "九地": 5, "九天": 5, "值符+九天": 5, "玄武": -3, "腾蛇": -4, "白虎": -5},
    "stability": {"九地": 8, "太阴": 7, "六合": 6, "值符": 5, "九天": 3, "值符+九天": 3, "玄武": -4, "腾蛇": -5, "白虎": -6},
}

STEM_RELATION_SCORES = {
    "career": {"heaven_generates_earth": 8, "earth_generates_heaven": 6, "same_element": 5, "unrelated": 3, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "wealth": {"heaven_generates_earth": 7, "earth_generates_heaven": 6, "same_element": 4, "unrelated": 3, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "love": {"heaven_generates_earth": 8, "earth_generates_heaven": 8, "same_element": 5, "unrelated": 3, "heaven_controls_earth": -3, "earth_controls_heaven": -4},
    "health": {"heaven_generates_earth": 5, "earth_generates_heaven": 4, "same_element": 3, "unrelated": 2, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "acad": {"heaven_generates_earth": 6, "earth_generates_heaven": 5, "same_element": 4, "unrelated": 2, "heaven_controls_earth": -1, "earth_controls_heaven": -3},
    "fortune": {"heaven_generates_earth": 7, "earth_generates_heaven": 6, "same_element": 4, "unrelated": 3, "heaven_controls_earth": -1, "earth_controls_heaven": -3},
    "investment": {"heaven_generates_earth": 8, "earth_generates_heaven": 6, "same_element": 4, "unrelated": 2, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "travel": {"heaven_generates_earth": 7, "earth_generates_heaven": 6, "same_element": 4, "unrelated": 3, "heaven_controls_earth": -1, "earth_controls_heaven": -3},
    "social": {"heaven_generates_earth": 6, "earth_generates_heaven": 5, "same_element": 4, "unrelated": 3, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "family": {"heaven_generates_earth": 7, "earth_generates_heaven": 6, "same_element": 5, "unrelated": 3, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "personality": {"heaven_generates_earth": 6, "earth_generates_heaven": 5, "same_element": 5, "unrelated": 3, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "fengshui": {"heaven_generates_earth": 6, "earth_generates_heaven": 5, "same_element": 4, "unrelated": 3, "heaven_controls_earth": -2, "earth_controls_heaven": -4},
    "stability": {"heaven_generates_earth": 5, "earth_generates_heaven": 5, "same_element": 4, "unrelated": 2, "heaven_controls_earth": -3, "earth_controls_heaven": -4},
}

EMPTY_PENALTIES = {
    "palace": 8,
    "god": 4,
    "star": 5,
    "door": 7,
    "trigger": 2,
    "heaven_stem": 3,
    "earth_stem": 3,
}

TOMB_PENALTIES = {
    "trigger": 2,
    "heaven_stem": 3,
    "earth_stem": 3,
}

PATTERN_PENALTIES = {
    "triple_same": 2,
    "peach_blossom_111_999": 4,
    "pair_69_96": 6,
    "pair_25_95": 10,
    "pair_27_99_92": 5,
    "tail_repeat_bias": 2,
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

TOPIC_CAPS = {
    "career": {"pair_25_95": 68, "pair_69_96": 78, "stacked_27_99_92": 72, "multiple_heavy_harms": 66, "palace_empty_with_door_pressure": 70},
    "wealth": {"pair_25_95": 64, "pair_69_96": 76, "stacked_27_99_92": 70, "multiple_heavy_harms": 62, "palace_empty_with_door_pressure": 68},
    "love": {"pair_25_95": 62, "pair_69_96": 74, "stacked_27_99_92": 66, "multiple_heavy_harms": 60},
    "health": {"pair_25_95": 58, "pair_69_96": 70, "stacked_27_99_92": 64, "multiple_heavy_harms": 54},
    "acad": {"pair_25_95": 64, "pair_69_96": 74, "stacked_27_99_92": 68, "multiple_heavy_harms": 60},
    "fortune": {"pair_25_95": 62, "pair_69_96": 74, "stacked_27_99_92": 68, "multiple_heavy_harms": 60},
    "investment": {"pair_25_95": 55, "pair_69_96": 68, "stacked_27_99_92": 62, "multiple_heavy_harms": 52},
    "travel": {"pair_25_95": 60, "pair_69_96": 72, "stacked_27_99_92": 66, "multiple_heavy_harms": 58},
    "social": {"pair_25_95": 62, "pair_69_96": 70, "stacked_27_99_92": 64, "multiple_heavy_harms": 58},
    "family": {"pair_25_95": 60, "pair_69_96": 70, "stacked_27_99_92": 62, "multiple_heavy_harms": 56},
    "personality": {"pair_25_95": 66, "pair_69_96": 74, "stacked_27_99_92": 68, "multiple_heavy_harms": 62},
    "fengshui": {"pair_25_95": 58, "pair_69_96": 70, "stacked_27_99_92": 64, "multiple_heavy_harms": 54, "palace_empty_with_door_pressure": 66},
    "stability": {"pair_25_95": 50, "pair_69_96": 68, "stacked_27_99_92": 60, "multiple_heavy_harms": 48, "palace_empty_with_door_pressure": 56, "door_empty_with_result_tomb": 54},
}

TOPIC_WEIGHTS = {
    "career": {
        "core_doors": {"开门", "生门", "景门"},
        "core_stars": {"天心", "天任", "天辅"},
        "core_gods": {"值符", "值符+九天", "九天", "六合", "太阴"},
        "risk_doors": {"死门", "伤门"},
        "risk_stars": {"天芮", "天柱"},
        "risk_gods": {"腾蛇", "白虎", "玄武"},
    },
    "wealth": {
        "core_doors": {"生门", "开门", "休门"},
        "core_stars": {"天任", "天心", "天辅", "天英"},
        "core_gods": {"值符", "值符+九天", "九天", "六合", "太阴", "九地"},
        "risk_doors": {"死门", "伤门"},
        "risk_stars": {"天芮", "天柱"},
        "risk_gods": {"腾蛇", "白虎", "玄武"},
    },
    "love": {
        "core_doors": {"休门", "生门", "开门"},
        "core_stars": {"天辅", "天任", "天心", "天英", "天禽"},
        "core_gods": {"六合", "太阴", "九地", "值符"},
        "risk_doors": {"死门", "伤门", "惊门"},
        "risk_stars": {"天芮", "天冲", "天柱"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "health": {
        "core_doors": {"休门", "生门", "杜门"},
        "core_stars": {"天心", "天任", "天辅", "天禽"},
        "core_gods": {"太阴", "九地", "六合"},
        "risk_doors": {"死门", "伤门", "惊门", "景门"},
        "risk_stars": {"天芮", "天柱", "天英", "天蓬"},
        "risk_gods": {"白虎", "腾蛇", "玄武"},
    },
    "acad": {
        "core_doors": {"休门", "杜门", "生门"},
        "core_stars": {"天辅", "天心", "天任", "天蓬", "白虎"},
        "core_gods": {"太阴", "六合", "九地", "九天"},
        "risk_doors": {"死门", "伤门", "惊门"},
        "risk_stars": {"天芮", "天柱"},
        "risk_gods": {"玄武", "腾蛇"},
    },
    "fortune": {
        "core_doors": {"开门", "生门", "休门"},
        "core_stars": {"天心", "天任", "天辅", "天英"},
        "core_gods": {"值符", "值符+九天", "九天", "六合", "太阴", "九地"},
        "risk_doors": {"死门", "伤门"},
        "risk_stars": {"天芮", "天柱"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "investment": {
        "core_doors": {"生门", "开门"},
        "core_stars": {"天蓬", "天心", "天任", "天辅"},
        "core_gods": {"值符", "值符+九天", "九天", "太阴", "六合"},
        "risk_doors": {"死门", "伤门", "惊门"},
        "risk_stars": {"天芮", "天柱"},
        "risk_gods": {"腾蛇", "白虎", "玄武"},
    },
    "travel": {
        "core_doors": {"开门", "休门", "生门"},
        "core_stars": {"天冲", "天任", "天心", "天英"},
        "core_gods": {"九天", "值符+九天", "值符", "六合", "太阴"},
        "risk_doors": {"死门", "伤门", "惊门", "杜门"},
        "risk_stars": {"天芮", "天柱", "天蓬"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "social": {
        "core_doors": {"休门", "开门", "生门", "景门"},
        "core_stars": {"天辅", "天心", "天任", "天英", "天禽"},
        "core_gods": {"六合", "太阴", "九天", "九地", "值符"},
        "risk_doors": {"死门", "伤门", "惊门"},
        "risk_stars": {"天芮", "天柱", "天冲"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "family": {
        "core_doors": {"休门", "生门", "开门"},
        "core_stars": {"天心", "天任", "天辅", "天禽"},
        "core_gods": {"六合", "太阴", "九地", "值符"},
        "risk_doors": {"死门", "伤门", "惊门"},
        "risk_stars": {"天芮", "天柱", "天冲"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "personality": {
        "core_doors": {"休门", "开门", "生门", "景门"},
        "core_stars": {"天心", "天任", "天辅", "天禽", "天英"},
        "core_gods": {"值符", "六合", "太阴", "九地", "九天"},
        "risk_doors": {"死门", "伤门", "惊门"},
        "risk_stars": {"天芮", "天柱", "天冲", "天蓬"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "fengshui": {
        "core_doors": {"生门", "开门", "休门"},
        "core_stars": {"天心", "天任", "天辅", "天英"},
        "core_gods": {"值符", "六合", "太阴", "九地", "九天"},
        "risk_doors": {"死门", "伤门", "惊门", "杜门"},
        "risk_stars": {"天芮", "天柱", "天蓬"},
        "risk_gods": {"玄武", "腾蛇", "白虎"},
    },
    "stability": {
        "core_doors": {"休门", "生门"},
        "core_stars": {"天任", "天心", "天辅", "天禽"},
        "core_gods": {"九地", "太阴", "六合", "值符"},
        "risk_doors": {"死门", "伤门", "惊门", "景门"},
        "risk_stars": {"天芮", "天柱", "天冲", "天蓬"},
        "risk_gods": {"玄武", "腾蛇", "白虎", "九天"},
    },
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
    "stability": {"25", "95", "69", "96", "27", "99", "92", "111", "999"},
}

TOPIC_EDGE_WEIGHTS = {
    "career": {"palace_emptiness": 5, "door_emptiness": 6, "palace_5_special": 1, "door_5_special": 1},
    "wealth": {"palace_emptiness": 4, "door_emptiness": 6, "palace_5_special": 1, "door_5_special": 1},
    "love": {"palace_emptiness": 5, "door_emptiness": 4, "god_9_dual_read": 1},
    "health": {"palace_emptiness": 4, "door_emptiness": 6, "star_2_special": 2, "door_2_special": 2},
    "acad": {"palace_emptiness": 4, "door_emptiness": 5, "star_2_special": 1, "door_2_special": 1},
    "fortune": {"palace_emptiness": 4, "door_emptiness": 5},
    "investment": {"palace_emptiness": 5, "door_emptiness": 6},
    "travel": {"palace_emptiness": 4, "door_emptiness": 5},
    "social": {"palace_emptiness": 4, "door_emptiness": 4},
    "family": {"palace_emptiness": 5, "door_emptiness": 5},
    "personality": {"palace_emptiness": 3, "door_emptiness": 3},
    "fengshui": {"palace_emptiness": 6, "door_emptiness": 6},
    "stability": {"palace_emptiness": 6, "door_emptiness": 6, "god_emptiness": 3, "star_emptiness": 4},
}

TOPIC_NAMES = {
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
    "stability": "稳定性",
}


def _clamp(score: int) -> int:
    return max(0, min(100, score))


def _score_topic(
    result: dict[str, Any],
    topic_key: str,
) -> dict[str, Any]:
    profile = BASE_PROFILES[topic_key]
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    edge_flags = features["edge_flags"]
    symbols = board["symbols"]
    score = int(profile["base"])

    anchor_relation = features["palace_door_relation"]
    stem_relation = features["stem_pair_relation"]
    score += RELATION_SCORES.get(anchor_relation, 0)
    score += PAIR_RELATION_SCORES.get(stem_relation, 0)

    door_score = int(DOOR_SCORES[topic_key].get(symbols["door"], 0))
    star_score = int(STAR_SCORES[topic_key].get(symbols["star"], 0))
    god_score = int(GOD_SCORES[topic_key].get(symbols["god"], 0))
    stem_score = int(STEM_RELATION_SCORES[topic_key].get(stem_relation, 0))

    score += door_score + star_score + god_score + stem_score

    emptiness_penalty = 0
    for layer in harms["emptiness_layers"]:
        emptiness_penalty += int(EMPTY_PENALTIES.get(layer, 2))
        emptiness_penalty += int(TOPIC_EDGE_WEIGHTS[topic_key].get(f"{layer}_bonus", 0))
    if "palace" in harms["emptiness_layers"]:
        emptiness_penalty += int(TOPIC_EDGE_WEIGHTS[topic_key].get("palace_emptiness", 0))
    if "door" in harms["emptiness_layers"]:
        emptiness_penalty += int(TOPIC_EDGE_WEIGHTS[topic_key].get("door_emptiness", 0))
    score -= emptiness_penalty

    if harms["door_pressure"]:
        score -= 6 if topic_key in {"career", "wealth", "travel", "fengshui", "stability"} else 4
    tomb_penalty = 0
    if harms["tomb"]:
        for layer in harms["tomb_layers"]:
            tomb_penalty += int(TOMB_PENALTIES.get(layer, 0))
        tomb_penalty += 4 if topic_key in {"career", "wealth", "investment", "fengshui", "stability"} else 3
    score -= tomb_penalty
    if harms["punishment_hit"]:
        score -= 7 if topic_key in {"love", "health", "stability", "family"} else 5

    pattern_penalty = 0
    for detected in patterns["detected"]:
        pattern_penalty += int(PATTERN_PENALTIES.get(detected, 0))
    score -= pattern_penalty

    edge_penalty = 0
    for flag in edge_flags:
        edge_penalty += int(EDGE_PENALTIES.get(flag, 0))
        edge_penalty += int(TOPIC_EDGE_WEIGHTS[topic_key].get(flag, 0))
    score -= edge_penalty

    bonus = _topic_bonus(result, topic_key, score)
    score += bonus

    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    confidence = "A"
    if heavy_harm_count >= 3 or len(patterns["detected"]) >= 3 or any(flag in {"palace_emptiness", "door_emptiness"} for flag in edge_flags):
        confidence = "C"
    elif heavy_harm_count >= 1 or patterns["detected"] or result["board"]["digits"]["god"] == "9":
        confidence = "B"

    confidence_shrink = {"A": 1.0, "B": 0.97, "C": 0.93}[confidence]
    score = round(score * confidence_shrink + 58 * (1 - confidence_shrink))
    score = _clamp(score)

    structural_cap_reasons: list[str] = []
    topic_caps = TOPIC_CAPS[topic_key]
    if "pair_25_95" in patterns["detected"]:
        structural_cap_reasons.append("pair_25_95")
    if "pair_69_96" in patterns["detected"]:
        structural_cap_reasons.append("pair_69_96")
    if len({pair for pair in patterns["risk_pairs"] if pair in {"27", "99", "92"}}) >= 2:
        structural_cap_reasons.append("stacked_27_99_92")
    if harms["door_pressure"] and "palace" in harms["emptiness_layers"]:
        structural_cap_reasons.append("palace_empty_with_door_pressure")
    if heavy_harm_count >= 2:
        structural_cap_reasons.append("multiple_heavy_harms")
    if "door" in harms["emptiness_layers"] and any(layer in harms["tomb_layers"] for layer in {"heaven_stem", "earth_stem"}):
        structural_cap_reasons.append("door_empty_with_result_tomb")

    structural_cap = 100
    for reason in structural_cap_reasons:
        structural_cap = min(structural_cap, int(topic_caps.get(reason, 100)))
    if structural_cap_reasons:
        score = min(score, structural_cap)

    risk_pairs = sorted(set(patterns["risk_pairs"]).intersection(TOPIC_HIGH_RISK_PAIRS[topic_key]))
    topic_score = {
        "topic_key": topic_key,
        "topic_title": DIMENSION_TITLES[topic_key],
        "score": score,
        "components": {
            "base": int(profile["base"]),
            "anchor_relation": anchor_relation,
            "anchor_relation_score": RELATION_SCORES.get(anchor_relation, 0),
            "stem_relation": stem_relation,
            "stem_relation_score": PAIR_RELATION_SCORES.get(stem_relation, 0),
            "door": symbols["door"],
            "door_score": door_score,
            "star": symbols["star"],
            "star_score": star_score,
            "god": symbols["god"],
            "god_score": god_score,
            "stem_score": stem_score,
            "emptiness_penalty": emptiness_penalty,
            "door_pressure_penalty": 6 if harms["door_pressure"] else 0,
            "tomb_penalty": tomb_penalty,
            "punishment_penalty": 7 if harms["punishment_hit"] and topic_key in {"love", "health", "stability", "family"} else 5 if harms["punishment_hit"] else 0,
            "pattern_penalty": pattern_penalty,
            "edge_penalty": edge_penalty,
            "bonus": bonus,
            "confidence_shrink": confidence_shrink,
        },
        "features": {
            "anchor_relation": anchor_relation,
            "stem_relation": stem_relation,
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
        },
        "caps": {
            "structural_cap": structural_cap,
            "applied": structural_cap_reasons,
        },
    }
    return topic_score


def _topic_bonus(result: dict[str, Any], topic_key: str, current_score: int) -> int:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    bonus = 0

    if not harms["emptiness"] and not harms["door_pressure"] and not harms["tomb"] and not harms["punishment_hit"] and not patterns["detected"]:
        bonus += 3
    if topic_key in {"love", "social", "family"} and patterns["neutral_pairs"]:
        bonus += 2
    if topic_key == "acad" and symbols["star"] in {"天辅", "天心", "天任"} and symbols["door"] in {"休门", "杜门", "生门"}:
        bonus += 3
    if topic_key == "career" and symbols["door"] in {"开门", "生门"} and symbols["god"] in {"值符", "值符+九天", "九天"}:
        bonus += 2
    if topic_key == "career" and symbols["star"] == "天心" and symbols["door"] == "开门":
        bonus += 2
    if topic_key == "wealth" and symbols["door"] == "生门" and (symbols["star"] in {"天任", "天心", "天辅"} or symbols["god"] in {"值符", "值符+九天"}):
        bonus += 2
    if topic_key == "investment" and symbols["star"] == "天蓬":
        bonus += 2
    if topic_key == "investment" and symbols["star"] == "天蓬" and symbols["door"] == "生门":
        bonus += 2
    if topic_key == "travel" and symbols["god"] in {"九天", "值符", "值符+九天"}:
        bonus += 2
    if topic_key == "travel" and symbols["god"] in {"九天", "值符", "值符+九天"} and symbols["door"] in {"开门", "休门", "生门"}:
        bonus += 2
    if topic_key == "health" and symbols["god"] in {"太阴", "九地"}:
        bonus += 2
    if topic_key == "health" and symbols["god"] in {"太阴", "九地"} and symbols["door"] == "休门":
        bonus += 2
    if topic_key == "fengshui" and features["palace_door_relation"] in {"palace_generates_door", "same_element", "door_generates_palace"}:
        bonus += 2
    if topic_key == "fengshui" and not harms["emptiness"] and not harms["door_pressure"]:
        bonus += 2
    if topic_key == "stability" and symbols["god"] == "九地":
        bonus += 3
    if topic_key == "stability" and not harms["emptiness"] and not harms["door_pressure"] and not harms["tomb"] and not harms["punishment_hit"]:
        bonus += 3
    if current_score >= 85 and not patterns["detected"] and not harms["emptiness"]:
        bonus += 1
    return bonus


def score_phone_dimensions_v2(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = rules or load_rules()
    board = build_board(phone, gender, rules)
    result = {
        "rules_version": rules["version"],
        "algorithm_version": DIMENSION_SCORE_V2_VERSION,
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
        },
        "dimensions": {},
    }

    dimensions: dict[str, Any] = {}
    for topic_key in DIMENSION_ORDER:
        topic_score = _score_topic(result, topic_key)
        dimensions[topic_key] = topic_score

    result["dimensions"] = dimensions
    result["summary"] = {
        "topic_order": DIMENSION_ORDER,
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


def build_dimension_scores_v2(
    phone: str,
    gender: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return score_phone_dimensions_v2(phone, gender, rules=rules)
