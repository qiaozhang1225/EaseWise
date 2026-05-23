from __future__ import annotations

from typing import Any

from scoring.aspect_scores import build_aspect_scores, grade_from_score

PUBLIC_ASPECT_ORDER = [
    "career",
    "wealth",
    "love",
    "health",
    "acad",
    "social",
    "travel",
    "law",
    "risk",
]

DEFAULT_FREE_ASPECT_KEYS = [
    "career",
    "wealth",
    "love",
]
_OUTLINE_KEY_ALIAS = {
    "career": "career",
    "wealth": "wealth",
    "love": "marriage",
    "health": "health",
    "acad": "learning",
    "social": "relationship",
}
_PALACE_DISPLAY_ORDER = [
    ("xun", "巽", "巽宫", "东南"),
    ("li", "离", "离宫", "正南"),
    ("kun", "坤", "坤宫", "西南"),
    ("zhen", "震", "震宫", "正东"),
    ("center", "中", "中宫", "盘心"),
    ("dui", "兑", "兑宫", "正西"),
    ("gen", "艮", "艮宫", "东北"),
    ("kan", "坎", "坎宫", "正北"),
    ("qian", "乾", "乾宫", "西北"),
]
_PALACE_WUXING_LABELS = {
    "巽": "木",
    "离": "火",
    "坤": "土",
    "震": "木",
    "中": "土",
    "兑": "金",
    "艮": "土",
    "坎": "水",
    "乾": "金",
}


def build_phone_review_product_view(score_result: dict[str, Any], score_template: dict[str, Any]) -> dict[str, Any]:
    product_render = score_template.get("product_render") if isinstance(score_template.get("product_render"), dict) else {}
    board_payload = score_template.get("board_description_payload") if isinstance(score_template.get("board_description_payload"), dict) else {}
    score_summary = score_template.get("score_summary") if isinstance(score_template.get("score_summary"), dict) else {}
    final_score = int(score_summary.get("final_score", 0) or 0)
    aspect_scores = _resolve_aspect_scores(score_result, score_template)
    aspects = _build_public_aspects(score_result, score_template, product_render, aspect_scores)
    stability_payload = score_template.get("stability_payload") if isinstance(score_template.get("stability_payload"), dict) else {}

    return {
        "score": final_score,
        "summary": {
            "title": str(product_render.get("summary", {}).get("title") or _build_summary_title(board_payload, final_score)),
            "content": str(product_render.get("summary", {}).get("highlight") or _build_summary_content(board_payload, stability_payload)),
        },
        "board": _build_board_view(score_result, score_template),
        "board_analysis": {
            "title": "盘面分析 / 总评",
            "content": str(
                product_render.get("summary", {}).get("text")
                or product_render.get("board_description", {}).get("technical_narrative")
                or board_payload.get("practical_manifestation")
                or ""
            ).strip(),
        },
        "stability_judgement": {
            "label": "稳定性判断",
            "value": _build_stability_value(score_result, stability_payload, final_score),
        },
        "long_term_advice": _build_long_term_advice(score_result, score_template, product_render, aspects),
        "aspects": aspects,
        "aspect_scores": aspect_scores,
        "aspect_order": PUBLIC_ASPECT_ORDER.copy(),
    }


def _build_public_aspects(
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    product_render: dict[str, Any],
    aspect_scores: dict[str, dict[str, int | str]],
) -> list[dict[str, Any]]:
    return [
        _build_standard_aspect(
            aspect_id="career",
            title="事业发展",
            payload_key="career_payload",
            score_template=score_template,
            product_render=product_render,
            aspect_scores=aspect_scores,
        ),
        _build_standard_aspect(
            aspect_id="wealth",
            title="财富状态",
            payload_key="wealth_payload",
            score_template=score_template,
            product_render=product_render,
            aspect_scores=aspect_scores,
        ),
        _build_standard_aspect(
            aspect_id="love",
            title="感情关系",
            payload_key="marriage_payload",
            score_template=score_template,
            product_render=product_render,
            aspect_scores=aspect_scores,
        ),
        _build_standard_aspect(
            aspect_id="health",
            title="健康状态",
            payload_key="health_payload",
            score_template=score_template,
            product_render=product_render,
            aspect_scores=aspect_scores,
        ),
        _build_standard_aspect(
            aspect_id="acad",
            title="学习成长",
            payload_key="learning_payload",
            score_template=score_template,
            product_render=product_render,
            aspect_scores=aspect_scores,
        ),
        _build_standard_aspect(
            aspect_id="social",
            title="人际支持",
            payload_key="relationship_payload",
            score_template=score_template,
            product_render=product_render,
            aspect_scores=aspect_scores,
        ),
        _build_travel_aspect(score_result, score_template, aspect_scores),
        _build_law_aspect(score_result, score_template, aspect_scores),
        _build_risk_aspect(score_result, score_template, aspect_scores),
    ]


def _build_standard_aspect(
    *,
    aspect_id: str,
    title: str,
    payload_key: str,
    score_template: dict[str, Any],
    product_render: dict[str, Any],
    aspect_scores: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    payload = score_template.get(payload_key) if isinstance(score_template.get(payload_key), dict) else {}
    sections = product_render.get("sections") if isinstance(product_render.get("sections"), dict) else {}
    outline_items = product_render.get("outline") if isinstance(product_render.get("outline"), list) else score_template.get("review_outline", [])
    outline_map = {
        str(item.get("key") or "").strip().lower(): item
        for item in outline_items
        if isinstance(item, dict)
    }
    source_key = _OUTLINE_KEY_ALIAS[aspect_id]
    rendered_section = sections.get(source_key) if isinstance(sections.get(source_key), dict) else {}
    outline_item = outline_map.get(source_key, {})

    core_judge = _first_non_empty(
        rendered_section.get("core_judgement"),
        outline_item.get("summary"),
        _build_payload_summary(payload),
    )
    explain = _first_non_empty(
        rendered_section.get("user_facing_paragraph"),
        rendered_section.get("real_world_manifestation"),
        payload.get("manifestation"),
    )
    signal = _first_non_empty(
        _first_item(outline_item.get("signals")),
        _watch_area_signal(payload),
        _facts_signal(payload),
    )
    suggestion = _first_non_empty(
        rendered_section.get("advice"),
        payload.get("advice"),
    )
    aspect_score = _resolve_aspect_score_value(aspect_scores, aspect_id, payload)

    return {
        "aspect_id": aspect_id,
        "title": title,
        "short_title": title[:2],
        "score": aspect_score,
        "level": _level_badge(payload, score=aspect_score),
        "level_text": str(payload.get("level") or "").strip() or None,
        "core_judge": core_judge or None,
        "explain": explain or None,
        "signal": signal or None,
        "suggestion": suggestion or None,
    }


def _build_travel_aspect(
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    aspect_scores: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    symbols = score_result["board"]["symbols"]
    harms = score_result["features"]["harms"]
    patterns = score_result["features"]["patterns"]
    final_score = int(score_template["score_summary"]["final_score"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    risk_pairs = set(patterns["risk_pairs"])

    rank = 2
    if symbols["door"] in {"开门", "休门", "生门"} and final_score >= 82 and heavy_harm_count == 0:
        rank = 0
    elif symbols["door"] in {"开门", "休门", "生门", "景门"} and final_score >= 72 and heavy_harm_count <= 1:
        rank = 1
    elif symbols["star"] == "天蓬" or symbols["door"] in {"死门", "伤门"} or heavy_harm_count >= 2 or risk_pairs.intersection({"69", "96"}):
        rank = 3

    return {
        "aspect_id": "travel",
        "title": "出行变动",
        "short_title": "出行",
        "score": _resolve_aspect_score_value(aspect_scores, "travel"),
        "level": _resolve_aspect_grade(aspect_scores, "travel"),
        "level_text": [
            "出行变动承接顺",
            "出行变动整体可控",
            "出行变动需看时机",
            "出行变动波动偏明显",
        ][rank],
        "core_judge": (
            f"当前盘面落在{symbols['palace']}宫，门位为{symbols['door']}、星位为{symbols['star']}，"
            f"出行、搬迁和较大的外部变动更适合按节奏推进，不适合只凭一时冲动决定。"
        ),
        "explain": (
            f"出行变动这类事项更看门位推进感、盘面承接和途中波动。现在的结构里，{symbols['door']}决定你在路上的推进方式，"
            f"{symbols['star']}会影响临场判断，{symbols['god']}则更像外部配合度。若近期要安排远行、搬迁、换城市或高频奔波，"
            "建议把时间窗口、预算与备选方案都准备充分。"
        ),
        "signal": _first_non_empty(
            _risk_pairs_signal(risk_pairs),
            _harm_signal(harms),
            f"重点先看门位 {symbols['door']} 和星位 {symbols['star']} 的组合节奏。",
        ),
        "suggestion": (
            "涉及出差、远行、搬迁或换环境时，优先做足行程确认、时间缓冲和备用方案；如果近期体感阻力明显，先缩短决策链路再行动。"
        ),
    }


def _build_law_aspect(
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    aspect_scores: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    symbols = score_result["board"]["symbols"]
    harms = score_result["features"]["harms"]
    patterns = score_result["features"]["patterns"]
    final_score = int(score_template["score_summary"]["final_score"])
    risk_pairs = set(patterns["risk_pairs"])

    rank = 2
    if symbols["door"] in {"开门", "生门"} and symbols["god"] in {"值符", "六合", "太阴"} and not harms["door_pressure"] and final_score >= 80:
        rank = 0
    elif symbols["door"] in {"休门", "景门"} and not harms["punishment_hit"] and not risk_pairs.intersection({"69", "96"}):
        rank = 1
    elif symbols["door"] in {"惊门", "伤门"} or symbols["god"] in {"玄武", "腾蛇"} or harms["punishment_hit"] or risk_pairs.intersection({"69", "96"}):
        rank = 3

    return {
        "aspect_id": "law",
        "title": "合同风险",
        "short_title": "合同",
        "score": _resolve_aspect_score_value(aspect_scores, "law"),
        "level": _resolve_aspect_grade(aspect_scores, "law"),
        "level_text": [
            "合同把控相对稳",
            "合同风险整体可控",
            "合同细节需反复确认",
            "合同风险需要明显加防",
        ][rank],
        "core_judge": (
            f"合同、文书和口头承诺这类事项，当前更受{symbols['door']}与{symbols['god']}的影响。"
            "能不能把事情谈成不是唯一重点，能不能把责任边界、交付口径和证据链写清楚更关键。"
        ),
        "explain": (
            f"{symbols['door']}会直接影响谈判和文书推进方式，{symbols['god']}更多体现对方表态和隐性变量。"
            "如果近期有签约、合作、借贷、转介绍、代办或需要留痕的事务，建议把关键约定落到文字，不要只靠熟人关系或口头默契。"
        ),
        "signal": _first_non_empty(
            _risk_pairs_signal(risk_pairs),
            _harm_signal(harms),
            f"若出现 {symbols['door']} 带来的反复确认感，优先补足条款、截图、转账备注与交付节点。",
        ),
        "suggestion": "签约前把付款节点、违约责任、交付边界和证据留存做完整；重要事项尽量书面确认，别把默认理解当成正式约定。",
    }


def _build_risk_aspect(
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    aspect_scores: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    symbols = score_result["board"]["symbols"]
    harms = score_result["features"]["harms"]
    patterns = score_result["features"]["patterns"]
    stability_payload = score_template.get("stability_payload") if isinstance(score_template.get("stability_payload"), dict) else {}
    final_score = int(score_template["score_summary"]["final_score"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])

    rank = 2
    if final_score >= 84 and heavy_harm_count == 0 and not detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}):
        rank = 0
    elif final_score >= 72 and heavy_harm_count <= 1 and not risk_pairs.intersection({"27", "92", "99"}):
        rank = 1
    elif heavy_harm_count >= 2 or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "92", "99"}):
        rank = 3

    return {
        "aspect_id": "risk",
        "title": "重大风险",
        "short_title": "风险",
        "score": _resolve_aspect_score_value(aspect_scores, "risk"),
        "level": _resolve_aspect_grade(aspect_scores, "risk"),
        "level_text": [
            "重大风险整体可控",
            "重大风险总体可防",
            "重大风险需要提前预案",
            "重大风险不宜硬扛",
        ][rank],
        "core_judge": (
            f"重大风险层面更看四害、特殊组合和整体稳定性。当前结构里，{stability_payload.get('level', '稳定性结果')}是底色，"
            "真正需要警惕的是那些会在放大场景里突然拖慢、压住或反复消耗的因素。"
        ),
        "explain": (
            f"从{symbols['palace']}宫承接、{symbols['door']}门推进到{symbols['star']}星放大，这组号码不是单纯看表面顺不顺，"
            "而是看当事情进入高压力、高投入或长期拉扯状态后，是否容易出现节奏失控、错误判断或成本放大。"
        ),
        "signal": _first_non_empty(
            _risk_pairs_signal(risk_pairs),
            _harm_signal(harms),
            "遇到高杠杆、高承诺或需要一次性重投入的事项时，先把风险预案准备好。",
        ),
        "suggestion": "涉及大额投入、长期绑定、情绪化决策或高风险尝试时，优先做减法；把风险拆小、把周期缩短，比硬扛更适合当前盘面。",
    }


def _build_board_view(score_result: dict[str, Any], score_template: dict[str, Any]) -> dict[str, Any]:
    board = score_result["board"]
    symbols = board["symbols"]
    board_payload = score_template.get("board_description_payload") if isinstance(score_template.get("board_description_payload"), dict) else {}
    basis = board_payload.get("board_basis") if isinstance(board_payload.get("board_basis"), dict) else {}
    structure = score_template.get("structure") if isinstance(score_template.get("structure"), dict) else {}
    harms = score_template.get("four_harms_check") if isinstance(score_template.get("four_harms_check"), dict) else {}
    patterns = score_template.get("pattern_check") if isinstance(score_template.get("pattern_check"), dict) else {}
    palace_direction_map = {
        palace_key: direction
        for _, palace_key, _, direction in _PALACE_DISPLAY_ORDER
    }
    cells: list[dict[str, Any]] = []

    for slot_id, palace_key, title, direction in _PALACE_DISPLAY_ORDER:
        cells.append(
            {
                "slot_id": slot_id,
                "palace_key": palace_key,
                "palace_name": title,
                "direction": direction,
                "wuxing": _PALACE_WUXING_LABELS.get(palace_key),
                "is_active": slot_id != "center" and symbols["palace"] == palace_key,
            }
        )

    return {
        "center_basis": {
            "trigger": str(basis.get("trigger") or symbols["trigger"]),
        },
        "active_basis": {
            "palace": str(basis.get("palace") or symbols["palace"]),
            "direction": palace_direction_map.get(str(basis.get("palace") or symbols["palace"])),
            "god": str(basis.get("god") or symbols["god"]),
            "star": str(basis.get("star") or symbols["star"]),
            "door": str(basis.get("door") or symbols["door"]),
            "heaven_stem": str(basis.get("heaven_stem") or symbols["heaven_stem"]),
            "earth_stem": str(basis.get("earth_stem") or symbols["earth_stem"]),
        },
        "grid_cells": cells,
        "relations": {
            "palace_door_relation": str(structure.get("palace_door_relation") or "") or None,
            "stem_pair_relation": str(structure.get("stem_pair_relation") or "") or None,
        },
        "risks": {
            "four_harms": {
                "emptiness": str(harms.get("emptiness") or "无"),
                "door_pressure": str(harms.get("door_pressure") or "无"),
                "tomb": str(harms.get("tomb") or "无"),
                "punishment_hit": str(harms.get("punishment_hit") or "无"),
            },
            "pattern_flags": [str(item) for item in patterns.get("detected", []) if str(item).strip()],
            "risk_pairs": [str(item) for item in patterns.get("risk_pairs", []) if str(item).strip()],
            "structural_cap_reasons": [str(item) for item in structure.get("structural_cap_reasons", []) if str(item).strip()],
        },
        "summary": {
            "main_axis": str(board_payload.get("main_axis") or "") or None,
            "main_contradiction": str(board_payload.get("main_contradiction") or "") or None,
        },
    }


def _build_long_term_advice(
    score_result: dict[str, Any],
    score_template: dict[str, Any],
    product_render: dict[str, Any],
    aspects: list[dict[str, Any]],
) -> list[str]:
    summary = product_render.get("summary") if isinstance(product_render.get("summary"), dict) else {}
    sections = product_render.get("sections") if isinstance(product_render.get("sections"), dict) else {}
    stability_section = sections.get("stability") if isinstance(sections.get("stability"), dict) else {}
    stability_payload = score_template.get("stability_payload") if isinstance(score_template.get("stability_payload"), dict) else {}
    advice_items = [
        _first_non_empty(stability_section.get("advice"), stability_payload.get("advice")),
        str(summary.get("recommendation") or "").strip(),
        _priority_hint(score_result, aspects),
    ]
    deduped: list[str] = []
    for item in advice_items:
        text = str(item or "").strip()
        if text and text not in deduped:
            deduped.append(text)
    return deduped[:3]


def _build_summary_title(board_payload: dict[str, Any], final_score: int) -> str:
    score_band = str(board_payload.get("score_band") or "").strip()
    main_axis = str(board_payload.get("main_axis") or "").strip()
    if score_band and main_axis:
        return f"{score_band} · {main_axis}"
    if score_band:
        return score_band
    if main_axis:
        return main_axis
    return f"综合评分 {final_score}"


def _build_summary_content(board_payload: dict[str, Any], stability_payload: dict[str, Any]) -> str:
    return _first_non_empty(
        board_payload.get("practical_manifestation"),
        stability_payload.get("manifestation"),
        stability_payload.get("advice"),
    )


def _build_stability_value(score_result: dict[str, Any], stability_payload: dict[str, Any], final_score: int) -> str:
    harms = score_result["features"]["harms"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    level_text = str(stability_payload.get("level") or "").strip()
    if final_score >= 82 and heavy_harm_count == 0 and "长期使用会比较折腾" not in level_text:
        return "适合长期使用"
    if final_score >= 68 and heavy_harm_count <= 1:
        return "可以继续使用，但要观察波动"
    return "不建议长期主用"


def _level_badge(payload: dict[str, Any], *, score: int | None = None) -> str | None:
    if score is not None:
        return grade_from_score(score)
    level_text = str(payload.get("level") or "").strip()
    if not level_text:
        return None
    allowed_levels = payload.get("model_pack", {}).get("allowed_levels")
    if isinstance(allowed_levels, list) and level_text in allowed_levels:
        index = allowed_levels.index(level_text)
        legacy_score = [92, 84, 74, 62, 52][min(index, 4)]
        return grade_from_score(legacy_score)
    if any(keyword in level_text for keyword in ("很稳", "起势很顺")):
        return grade_from_score(92)
    if any(keyword in level_text for keyword in ("整体可", "可守", "可走")):
        return grade_from_score(84)
    if any(keyword in level_text for keyword in ("能", "可控", "有起伏", "有消耗")):
        return grade_from_score(74)
    return grade_from_score(62)


def _resolve_aspect_scores(score_result: dict[str, Any], score_template: dict[str, Any]) -> dict[str, dict[str, int | str]]:
    raw_aspect_scores = score_template.get("aspect_scores")
    if isinstance(raw_aspect_scores, dict):
        normalized: dict[str, dict[str, int | str]] = {}
        for aspect_id, payload in raw_aspect_scores.items():
            if not isinstance(payload, dict):
                continue
            score = payload.get("score")
            grade = payload.get("grade")
            if score is None:
                continue
            normalized[str(aspect_id)] = {
                "score": int(score),
                "grade": str(grade or grade_from_score(int(score)) or "落陷"),
            }
        if normalized:
            return normalized
    return build_aspect_scores(score_result)


def _resolve_aspect_score_value(
    aspect_scores: dict[str, dict[str, int | str]],
    aspect_id: str,
    payload: dict[str, Any] | None = None,
) -> int | None:
    raw = aspect_scores.get(aspect_id, {}).get("score")
    if raw is not None:
        return int(raw)
    if isinstance(payload, dict) and payload.get("score") is not None:
        return int(payload["score"])
    return None


def _resolve_aspect_grade(aspect_scores: dict[str, dict[str, int | str]], aspect_id: str) -> str | None:
    payload = aspect_scores.get(aspect_id, {})
    grade = payload.get("grade")
    if grade is not None:
        return str(grade)
    score = payload.get("score")
    if score is None:
        return None
    return grade_from_score(int(score))


def _build_payload_summary(payload: dict[str, Any]) -> str:
    level_text = str(payload.get("level") or "").strip()
    type_text = str(payload.get("type") or "").strip()
    manifestation = str(payload.get("manifestation") or "").strip()
    parts = [item for item in [level_text, type_text, manifestation] if item]
    return "，".join(parts[:2]) + (f"。{manifestation}" if manifestation and len(parts) >= 2 else manifestation)


def _watch_area_signal(payload: dict[str, Any]) -> str:
    watch_areas = payload.get("watch_areas")
    if not isinstance(watch_areas, list):
        return ""
    areas = [str(item.get("area") if isinstance(item, dict) else item).strip() for item in watch_areas[:2]]
    areas = [item for item in areas if item]
    if not areas:
        return ""
    return f"重点留意：{'、'.join(areas)}。"


def _facts_signal(payload: dict[str, Any]) -> str:
    facts = payload.get("facts")
    if not isinstance(facts, dict):
        return ""
    for key in ("palace_door_relation", "stem_pair_relation", "door", "star", "god"):
        value = str(facts.get(key) or "").strip()
        if value:
            return f"当前关键观察点：{value}。"
    return ""


def _risk_pairs_signal(risk_pairs: set[str]) -> str:
    if not risk_pairs:
        return ""
    return f"当前号码里有需要留意的组合：{'、'.join(sorted(risk_pairs))}。"


def _harm_signal(harms: dict[str, Any]) -> str:
    active = []
    if harms["emptiness"]:
        active.append("空亡")
    if harms["door_pressure"]:
        active.append("门迫")
    if harms["tomb"]:
        active.append("入墓")
    if harms["punishment_hit"]:
        active.append("击刑")
    if not active:
        return ""
    return f"盘面里已有 {'、'.join(active)} 信号，做重大决定时更要留缓冲。"


def _priority_hint(score_result: dict[str, Any], aspects: list[dict[str, Any]]) -> str:
    symbols = score_result["board"]["symbols"]
    best_aspects = [item["title"] for item in aspects if item.get("level") in {"上吉", "中吉"}][:2]
    if best_aspects:
        return f"如果你当前更关注 {best_aspects[0]}{' 与 ' + best_aspects[1] if len(best_aspects) > 1 else ''}，这组号码更适合先围绕这些场景持续观察。"
    return f"先看 {symbols['door']} 对日常使用节奏的影响，再决定是否继续深度投入这组号码。"


def _first_item(value: Any) -> str:
    if isinstance(value, list):
        for item in value:
            text = str(item or "").strip()
            if text:
                return text
    return ""


def _first_non_empty(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""
