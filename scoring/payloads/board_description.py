from __future__ import annotations

from typing import Any

from scoring.payloads.shared import (
    BOARD_DESCRIPTION_SECTION_ORDER,
    CAP_REASON_LABELS,
    EDGE_FLAG_LABELS,
    NEUTRAL_PAIR_NOTE,
    NEUTRAL_PAIR_SCOPE,
    PATTERN_LABELS,
    RELATION_LABELS,
    _humanize_harm,
    _label,
    _label_list,
    _score_band,
)


def _build_structure(features: dict[str, Any], base_scoring: dict[str, Any]) -> dict[str, Any]:
    return {
        "palace_door_relation": _label(RELATION_LABELS, features["palace_door_relation"]),
        "stem_pair_relation": _label(RELATION_LABELS, features["stem_pair_relation"]),
        "structural_cap_reasons": _label_list(CAP_REASON_LABELS, base_scoring["structural_cap_reasons"]),
    }


def _build_four_harms_check(harms: dict[str, Any], labels: dict[str, str]) -> dict[str, str]:
    return {
        "emptiness": _humanize_harm(harms["emptiness"], harms["emptiness_layers"], labels),
        "door_pressure": _humanize_harm(harms["door_pressure"], [], labels),
        "tomb": _humanize_harm(harms["tomb"], harms["tomb_layers"], labels),
        "punishment_hit": _humanize_harm(harms["punishment_hit"], harms["punishment_layers"], labels),
    }


def _build_pattern_check(patterns: dict[str, Any], edge_flags: list[str]) -> dict[str, Any]:
    return {
        "detected": _label_list(PATTERN_LABELS, patterns["detected"]),
        "risk_pairs": patterns["risk_pairs"],
        "neutral_pairs": patterns["neutral_pairs"],
        "neutral_pairs_scope": patterns.get("neutral_pair_scope", NEUTRAL_PAIR_SCOPE),
        "neutral_pairs_note": NEUTRAL_PAIR_NOTE,
        "edge_flags": _label_list(EDGE_FLAG_LABELS, edge_flags),
    }


def _board_main_axis(result: dict[str, Any], final_score: int) -> str:
    symbols = result["board"]["symbols"]
    harms = result["features"]["harms"]
    door = symbols["door"]
    star = symbols["star"]
    god = symbols["god"]

    if door == "惊门" or star == "天柱" or god in {"螣蛇", "玄武"}:
        return "风险感知与应急反应"
    if door == "伤门" or god == "白虎":
        return "强执行与压力穿透"
    if door in {"生门", "开门"} and star in {"天心", "天任"}:
        return "务实承接与结构推进"
    if door in {"景门", "开门"} or star == "天英" or god in {"九天", "值符+九天"}:
        return "外放拓展与结果放大"
    if door in {"休门", "杜门"} or star == "天辅" or god == "太阴":
        return "内盘整合与节奏沉淀"
    if door == "死门" or star == "天芮" or harms["tomb"]:
        return "承压收束与后段消耗"
    if final_score >= 85:
        return "平台承接与长期稳定"
    return "结构混合与现实回拉"


def _board_main_contradiction(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    cap_reasons = result["scoring"]["structural_cap_reasons"]

    if cap_reasons or "pair_25_95" in patterns["detected"] or "pair_27_99_92" in patterns["detected"]:
        return "亮点还在，但四害或特殊组合会在落地层明显压住结构"
    if harms["tomb"] and harms["punishment_hit"]:
        return "前段不一定弱，真正掉分常在后段发沉和高压反噬"
    if harms["emptiness"] or harms["door_pressure"]:
        return "表面结构不差，但关键层位发空或受压，容易出现有力使不出的回拉"
    if features["palace_door_relation"] in {"palace_controls_door", "door_controls_palace"} or features["stem_pair_relation"] in {"heaven_controls_earth", "earth_controls_heaven"}:
        return "盘面不是没有亮点，而是内外层关系带克，现实承接更吃环境和角色匹配"
    if patterns["risk_pairs"]:
        return "局部组合会放大波动，不能只看表面吉象"
    if final_score >= 85:
        return "亮点基本接得住，主要是边角位置还有一点回拉"
    if final_score >= 70:
        return "有可用结构，但边角层仍会不时回拉节奏"
    return "亮点有限，真正的压力在结构后段和现实承接"


def _board_manifestation_keywords(axis: str) -> list[str]:
    mapping = {
        "务实承接与结构推进": ["推进", "承接", "结构", "资源"],
        "外放拓展与结果放大": ["对外", "拓展", "结果", "放大"],
        "内盘整合与节奏沉淀": ["整合", "沉淀", "节奏", "框架"],
        "风险感知与应急反应": ["风险", "应急", "排障", "收口"],
        "强执行与压力穿透": ["执行", "硬推", "压力", "结果"],
        "承压收束与后段消耗": ["承压", "收束", "后段", "消耗"],
        "平台承接与长期稳定": ["平台", "承接", "稳定", "长期"],
        "结构混合与现实回拉": ["回拉", "现实", "混合", "节奏"],
    }
    return mapping.get(axis, ["结构", "落地", "节奏", "承接"])


def _board_practical_manifestation(axis: str, contradiction: str, final_score: int) -> str:
    base_mapping = {
        "务实承接与结构推进": "这张盘更容易在需要判断、推进、整合资源和把事情往前带的场景里发挥优势。",
        "外放拓展与结果放大": "这张盘更适合放到对外拓展、结果展示、资源放大和影响力扩散的场景里看。",
        "内盘整合与节奏沉淀": "这张盘真正的价值更容易体现在内部整合、稳住节奏、做细做深和长期沉淀上。",
        "风险感知与应急反应": "这张盘在识别风险、快速反应、临场排障和兜底收口上通常更敏感。",
        "强执行与压力穿透": "这张盘在压任务、赶进度、直面结果和顶住压力硬推进时更容易显出主轴。",
        "承压收束与后段消耗": "这张盘前面未必差，但越到后段越要看承压、收束和消耗控制。",
        "平台承接与长期稳定": "这张盘更适合放到平台承接、长期运营和稳定积累的框架里理解。",
        "结构混合与现实回拉": "这张盘不是单线条优势，而是结构里有可用点，也有现实层面的回拉。",
    }
    base = base_mapping.get(axis, "这张盘的重点不在单点好坏，而在结构主轴和现实落点是否能接上。")

    if "四害或特殊组合" in contradiction:
        return f"{base}但真正决定上限的，不是前端有没有亮点，而是四害、风险组合和封顶因素会不会把结构压住。"
    if "后段发沉" in contradiction or "后段和现实承接" in contradiction:
        return f"{base}实际使用时要重点观察后段是否发沉、承压后会不会掉速，以及消耗是不是逐步累积。"
    if "带克" in contradiction or "发空或受压" in contradiction:
        return f"{base}一旦环境承接不住、角色边界不清，盘面的优点就容易先被回拉，再被现实消耗。"
    if final_score >= 85:
        return f"{base}整体上它的亮点是能接得住的，只要不放到明显相克或高消耗的位置，落地表现通常不会太差。"
    return f"{base}整体并不是不能用，而是要把主轴放到对的位置上，盘面的优势才会真正兑现。"


def _board_relation_implication(relation: str, *, relation_type: str) -> str:
    if relation in {"宫生门", "门生宫", "天干生地干", "地干生天干"}:
        return "这一层关系偏顺接，外在动作和现实承接更容易互相接住。"
    if relation == "同气":
        return "这一层关系同频，优点和缺点都容易被一起放大。"
    if relation in {"宫克门", "门克宫", "天干克地干", "地干克天干"}:
        if relation_type == "palace_door":
            return "这一层关系带克，常见表现是盘面动作和平台承接之间容易打架。"
        return "这一层关系带克，常见表现是前后层节奏和现实落地之间容易互相牵制。"
    return "这一层关系没有明显互推，也不是最重的相互伤耗。"


def _board_harm_implication(four_harms: dict[str, str]) -> str:
    active = [
        name
        for name, value in (
            ("空亡", four_harms["emptiness"]),
            ("门迫", four_harms["door_pressure"]),
            ("入墓", four_harms["tomb"]),
            ("击刑", four_harms["punishment_hit"]),
        )
        if value != "无"
    ]
    if not active:
        return "四害层目前没有硬伤，说明主轴亮点不太容易被这一层直接打断。"
    joined = "、".join(active)
    return f"四害层要重点看{joined}，因为这些往往决定盘面是停在表面好看，还是会在现实里被压住。"


def _board_symbol_implication(result: dict[str, Any], main_axis: str) -> str:
    symbols = result["board"]["symbols"]
    return f"{symbols['god']}、{symbols['star']}和{symbols['door']}这组三层符号，整体更容易把盘面拉向“{main_axis}”这一侧，而不是平均分散。"


def _board_technical_focus(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> list[dict[str, str]]:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    base_scoring = result["scoring"]
    structure = _build_structure(features, base_scoring)
    four_harms = _build_four_harms_check(harms, labels)
    pattern_check = _build_pattern_check(patterns, features["edge_flags"])
    main_axis = _board_main_axis(result, final_score)

    focus = [
        {
            "focus": "盘面主轴",
            "value": main_axis,
            "implication": "先定这张盘真正往哪边偏，再决定后面的盘解口径。",
        },
        {
            "focus": "宫门关系",
            "value": structure["palace_door_relation"],
            "implication": _board_relation_implication(structure["palace_door_relation"], relation_type="palace_door"),
        },
        {
            "focus": "后两干关系",
            "value": structure["stem_pair_relation"],
            "implication": _board_relation_implication(structure["stem_pair_relation"], relation_type="stems"),
        },
        {
            "focus": "神星门组合",
            "value": f"{result['board']['symbols']['god']} / {result['board']['symbols']['star']} / {result['board']['symbols']['door']}",
            "implication": _board_symbol_implication(result, main_axis),
        },
    ]

    if any(value != "无" for value in four_harms.values()):
        active_harms = "、".join(
            name
            for name, value in (
                ("空亡", four_harms["emptiness"]),
                ("门迫", four_harms["door_pressure"]),
                ("入墓", four_harms["tomb"]),
                ("击刑", four_harms["punishment_hit"]),
            )
            if value != "无"
        )
        focus.append(
            {
                "focus": "四害落点",
                "value": active_harms,
                "implication": _board_harm_implication(four_harms),
            }
        )

    if pattern_check["detected"]:
        focus.append(
            {
                "focus": "特殊组合",
                "value": "、".join(pattern_check["detected"]),
                "implication": "特殊组合不是单独决定吉凶，而是会放大主轴、风险和落地偏差。",
            }
        )

    if structure["structural_cap_reasons"]:
        focus.append(
            {
                "focus": "封顶因素",
                "value": "、".join(structure["structural_cap_reasons"]),
                "implication": "这些结构封顶因素会限制上限，让前端亮点很难完整兑现到现实层。",
            }
        )

    return focus


def _build_board_description_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    structure = _build_structure(features, scoring)
    four_harms = _build_four_harms_check(features["harms"], labels)
    pattern_check = _build_pattern_check(features["patterns"], features["edge_flags"])
    main_axis = _board_main_axis(result, final_score)
    main_contradiction = _board_main_contradiction(result, final_score)

    return {
        "section_order": BOARD_DESCRIPTION_SECTION_ORDER,
        "score_band": _score_band(final_score),
        "main_axis": main_axis,
        "main_contradiction": main_contradiction,
        "practical_manifestation": _board_practical_manifestation(main_axis, main_contradiction, final_score),
        "manifestation_keywords": _board_manifestation_keywords(main_axis),
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
        "score_facts": {
            "code_base_score": scoring["raw_score"],
            "score_after_structural_cap": scoring["score_after_structural_cap"],
            "structural_cap": scoring["structural_cap"],
            "final_score": final_score,
            "score_gap": max(0, int(scoring["raw_score"]) - int(final_score)),
            "confidence": scoring["confidence"],
            "tags": scoring["tags"],
        },
        "core_relations": {
            "palace_door_relation": structure["palace_door_relation"],
            "stem_pair_relation": structure["stem_pair_relation"],
            "four_harms": four_harms,
            "pattern_flags": pattern_check["detected"],
            "risk_pairs": pattern_check["risk_pairs"],
            "edge_flags": pattern_check["edge_flags"],
            "structural_cap_reasons": structure["structural_cap_reasons"],
        },
        "technical_focus": _board_technical_focus(result, final_score, labels),
    }
