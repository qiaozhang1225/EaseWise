from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Literal

from features.four_pillars.engine import FOUR_PILLARS_ASPECT_ORDER, FOUR_PILLARS_ASPECTS, build_dayun_facts, build_liunian_facts
from features.four_pillars.knowledge import (
    load_aspect_section_knowledge,
    load_aspect_section_model_pack,
    load_aspect_section_output_contract,
    load_aspect_section_style_examples,
    load_aspect_section_taxonomy,
    load_luck_section_knowledge,
    load_luck_section_model_pack,
    load_luck_section_output_contract,
    load_luck_section_style_examples,
    load_luck_section_taxonomy,
    load_section_knowledge,
    load_section_model_pack,
    load_section_output_contract,
    load_section_style_examples,
    load_section_taxonomy,
    load_shared_foundation,
)
from product.backend.llm import DeepSeekAPIError, DeepSeekClient

TonePack = Literal["customer", "professional"]
SUMMARY_KEYS = ("日主", "五行", "十神", "合冲刑害", "喜忌")
DAYUN_KEYS = ("原局", "大运", "十神", "五行", "合冲刑害", "喜忌")
LIUNIAN_KEYS = ("原局", "大运", "流年", "十神", "五行", "合冲刑害", "喜忌")
DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR = "DeepSeek 调用出现问题，四柱总评未生成。"
DEEPSEEK_FOUR_PILLARS_LUCK_ERROR = "DeepSeek 调用出现问题，流年大运内容未生成。"
ASPECT_TITLE_MAP = {item["aspect_key"]: item["title"] for item in FOUR_PILLARS_ASPECTS}


def build_four_pillars_product_view(package: dict[str, Any]) -> dict[str, Any]:
    score_template = package["score_template"]
    chart = package["chart"]
    facts = package["deterministic_facts"]
    score_result = package["score_result"]
    product_render = score_template.get("product_render") if isinstance(score_template.get("product_render"), dict) else {}
    summary = product_render.get("summary") if isinstance(product_render.get("summary"), dict) else fallback_summary(package)
    aspects_render = score_template.get("product_aspects_render") if isinstance(score_template.get("product_aspects_render"), dict) else {}
    return {
        "score": int(score_result["final_score"]),
        "score_band": score_result["score_band"],
        "input_profile": score_template["input_profile"],
        "chart": chart,
        "summary": summary,
        "deterministic_facts": facts,
        "aspects": build_aspect_public_items(facts, aspects_render),
        "analysis_branches": {
            "chart_analysis": {"enabled": True},
            "luck_analysis": {"enabled": True},
        },
        "luck_analysis": {
            "enabled": True,
            "current_cycle_key": facts.get("luck_cycles", {}).get("current_cycle_key") if isinstance(facts.get("luck_cycles"), dict) else None,
            "cycles": facts.get("luck_cycles", {}).get("cycles", []) if isinstance(facts.get("luck_cycles"), dict) else [],
        },
    }


def build_product_review_core_render(package: dict[str, Any], *, tone_pack: TonePack = "customer") -> dict[str, Any]:
    return {"summary": render_summary_from_package(package, tone_pack=tone_pack)}


def build_product_review_aspects_render(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    on_result: Any | None = None,
) -> dict[str, dict[str, Any]]:
    rendered: dict[str, dict[str, Any]] = {}
    max_workers = min(_get_aspect_worker_count(), len(FOUR_PILLARS_ASPECT_ORDER))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(render_aspect_from_package, package, aspect_key=aspect_key, tone_pack=tone_pack): aspect_key
            for aspect_key in FOUR_PILLARS_ASPECT_ORDER
        }
        for future in as_completed(future_map):
            aspect_key = future_map[future]
            result = future.result()
            rendered[aspect_key] = result
            if callable(on_result):
                on_result(aspect_key, result)
    return {aspect_key: rendered[aspect_key] for aspect_key in FOUR_PILLARS_ASPECT_ORDER if aspect_key in rendered}


def render_summary_from_package(package: dict[str, Any], *, tone_pack: TonePack = "customer") -> dict[str, Any]:
    system_prompt, user_prompt, json_example = build_summary_prompts(package, tone_pack=tone_pack)
    try:
        response = DeepSeekClient.from_env().chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model="deepseek-v4-pro",
            thinking_enabled=False,
            temperature=0.25,
            max_tokens=1600,
            llm_scene="four_pillars.summary",
            priority_class="foreground_core",
        )
        payload = response.json_object()
        if validate_summary_output(payload):
            return public_summary_output(payload)
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR)


def render_aspect_from_package(package: dict[str, Any], *, aspect_key: str, tone_pack: TonePack = "customer") -> dict[str, Any]:
    if aspect_key not in FOUR_PILLARS_ASPECT_ORDER:
        raise ValueError("invalid_aspect_key")
    system_prompt, user_prompt, json_example = build_aspect_prompts(package, aspect_key=aspect_key, tone_pack=tone_pack)
    try:
        response = DeepSeekClient.from_env().chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model="deepseek-v4-pro",
            thinking_enabled=False,
            temperature=0.25,
            max_tokens=1600,
            llm_scene=f"four_pillars.aspect.{aspect_key}",
            priority_class="background_prefetch",
        )
        payload = response.json_object()
        if validate_aspect_output(payload, aspect_key=aspect_key):
            return public_aspect_output(payload, aspect_key=aspect_key)
    except Exception:
        pass
    return fallback_aspect(package, aspect_key)


def build_summary_prompts(package: dict[str, Any], *, tone_pack: TonePack) -> tuple[str, str, dict[str, Any]]:
    knowledge = "\n\n".join(
        [
            "【统一知识底座】\n" + load_shared_foundation(),
            "【当前语气包】\n" + load_section_model_pack("chart_summary", tone_pack),
            "【总评判断知识】\n" + load_section_knowledge("chart_summary"),
            "【总评 taxonomy】\n" + load_section_taxonomy("chart_summary"),
            "【输出合同】\n" + load_section_output_contract("chart_summary"),
            "【表达样例】\n" + load_section_style_examples("chart_summary"),
        ]
    )
    json_example = {
        "title": "这张命盘的主轴是先稳住承载，再把输出和资源流动起来",
        "risk": "命局里有明显的拉扯信号，容易在压力和关系牵动中消耗。真正需要留意的不是有没有机会，而是机会来了以后能不能稳定承接。",
        "usage_guidance": "适合先建立稳定节奏，再用表达、学习或专业能力去带动资源，不宜长期处在高冲突和高消耗环境里。",
        "elements_check": {
            "日主": "日主承载方式的判断。",
            "五行": "五行偏向和流通判断。",
            "十神": "十神主题判断。",
            "合冲刑害": "结构互动判断。",
            "喜忌": "喜用与节制方向判断。",
        },
    }
    return (
        "你是易如反掌的四柱八字总评渲染器。只输出 JSON object，不要输出 markdown。\n"
        "不得修改 locked facts，不得出现课程、来源、内部字段名。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出 title、risk、usage_guidance、elements_check。\n\n"
        f"【locked facts】\n{_dump_json(package)}",
        json_example,
    )


def build_aspect_prompts(package: dict[str, Any], *, aspect_key: str, tone_pack: TonePack) -> tuple[str, str, dict[str, Any]]:
    title = ASPECT_TITLE_MAP[aspect_key]
    knowledge = "\n\n".join(
        [
            "【统一知识底座】\n" + load_shared_foundation(),
            "【当前语气包】\n" + load_aspect_section_model_pack(aspect_key, tone_pack),
            "【专项判断知识】\n" + load_aspect_section_knowledge(aspect_key),
            "【专项 taxonomy】\n" + load_aspect_section_taxonomy(aspect_key),
            "【输出合同】\n" + load_aspect_section_output_contract(aspect_key),
            "【表达样例】\n" + load_aspect_section_style_examples(aspect_key),
        ]
    )
    score = int(package["deterministic_facts"]["aspect_scores"][aspect_key]["score"])
    json_example = {
        "aspect_key": aspect_key,
        "title": f"{title}上有可用空间，但要看结构承接",
        "score": score,
        "content": "一段专项综合评价。",
        "risk": "一段专项风险提醒。",
        "elements_check": {
            "日主": "一句日主相关判断。",
            "五行": "一句五行相关判断。",
            "十神": "一句十神相关判断。",
            "合冲刑害": "一句互动结构判断。",
            "喜忌": "一句喜忌方向判断。",
        },
    }
    return (
        f"你是易如反掌的四柱八字「{title}」专项渲染器。只输出 JSON object。\n"
        "score 必须等于 locked facts 中的 score，不得重算或改动。\n"
        "不得出现课程、来源、内部字段名。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出 aspect_key、title、score、content、risk、elements_check。\n\n"
        f"【locked facts】\n{_dump_json(package)}",
        json_example,
    )


def validate_summary_output(payload: dict[str, Any]) -> bool:
    return all(str(payload.get(key) or "").strip() for key in ("title", "risk", "usage_guidance")) and _has_element_keys(payload)


def validate_aspect_output(payload: dict[str, Any], *, aspect_key: str) -> bool:
    if str(payload.get("aspect_key") or "").strip() != aspect_key:
        return False
    try:
        score = int(payload.get("score"))
    except Exception:
        return False
    if score < 0:
        return False
    if not all(str(payload.get(key) or "").strip() for key in ("title", "content", "risk")):
        return False
    return _has_element_keys(payload)


def public_summary_output(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": str(payload.get("title") or "").strip(),
        "risk": str(payload.get("risk") or "").strip(),
        "usage_guidance": str(payload.get("usage_guidance") or "").strip(),
        "elements_check": _string_dict(payload.get("elements_check")),
    }


def public_aspect_output(payload: dict[str, Any], *, aspect_key: str) -> dict[str, Any]:
    return {
        "aspect_key": aspect_key,
        "title": str(payload.get("title") or ASPECT_TITLE_MAP[aspect_key]).strip(),
        "score": int(payload.get("score") or 0),
        "content": str(payload.get("content") or "").strip(),
        "risk": str(payload.get("risk") or "").strip(),
        "elements_check": _string_dict(payload.get("elements_check")),
    }


def render_dayun_from_package(
    package: dict[str, Any],
    *,
    cycle_key: str,
    tone_pack: TonePack = "customer",
) -> dict[str, Any]:
    facts = build_dayun_facts(package, cycle_key)
    system_prompt, user_prompt, json_example = build_dayun_prompts(facts, tone_pack=tone_pack)
    try:
        response = DeepSeekClient.from_env().chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model="deepseek-v4-pro",
            thinking_enabled=False,
            temperature=0.25,
            max_tokens=2200,
            llm_scene="four_pillars.luck.dayun",
            priority_class="foreground_core",
        )
        payload = response.json_object()
        if validate_dayun_output(payload, facts):
            output = public_dayun_output(payload)
            output["_llm_meta"] = response.llm_meta
            return output
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_LUCK_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_LUCK_ERROR)


def render_liunian_from_package(
    package: dict[str, Any],
    *,
    cycle_key: str,
    year: int,
    tone_pack: TonePack = "customer",
) -> dict[str, Any]:
    facts = build_liunian_facts(package, cycle_key, year)
    system_prompt, user_prompt, json_example = build_liunian_prompts(facts, tone_pack=tone_pack)
    try:
        response = DeepSeekClient.from_env().chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model="deepseek-v4-pro",
            thinking_enabled=False,
            temperature=0.25,
            max_tokens=2400,
            llm_scene="four_pillars.luck.liunian",
            priority_class="foreground_core",
        )
        payload = response.json_object()
        if validate_liunian_output(payload, facts):
            output = public_liunian_output(payload)
            output["_llm_meta"] = response.llm_meta
            return output
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_LUCK_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_LUCK_ERROR)


def build_dayun_prompts(facts: dict[str, Any], *, tone_pack: TonePack) -> tuple[str, str, dict[str, Any]]:
    selected = facts["selected_cycle"]
    knowledge = "\n\n".join(
        [
            "【统一知识底座】\n" + load_shared_foundation(),
            "【当前语气包】\n" + load_luck_section_model_pack("dayun", tone_pack),
            "【大运判断知识】\n" + load_luck_section_knowledge("dayun"),
            "【大运 taxonomy】\n" + load_luck_section_taxonomy("dayun"),
            "【输出合同】\n" + load_luck_section_output_contract("dayun"),
            "【表达样例】\n" + load_luck_section_style_examples("dayun"),
        ]
    )
    json_example = {
        "cycle_key": selected["cycle_key"],
        "cycle_ganzhi": selected["ganzhi"],
        "title": "这步大运会把机会和压力同时推到台前",
        "score_tendency": "机会上升，但承接压力也会上升",
        "core_theme": "一段十年主轴判断。",
        "opportunities": "一段机会判断。",
        "risks": "一段风险判断。",
        "action_guidance": "一段行动建议。",
        "elements_check": {key: f"{key}判断。" for key in DAYUN_KEYS},
    }
    return (
        "你是易如反掌的四柱八字大运综评渲染器。只输出 JSON object。\n"
        "cycle_key 和 cycle_ganzhi 必须与 locked facts 完全一致，不得重新排盘，不得修改事实。\n"
        "输出要直白、有现实落点，但不能写绝对灾祸、疾病、离婚或发财承诺。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出大运综评。\n\n"
        f"【locked facts】\n{_dump_json(facts)}",
        json_example,
    )


def build_liunian_prompts(facts: dict[str, Any], *, tone_pack: TonePack) -> tuple[str, str, dict[str, Any]]:
    selected_cycle = facts["selected_cycle"]
    selected_year = facts["selected_year"]
    json_example = {
        "cycle_key": selected_cycle["cycle_key"],
        "year": selected_year["year"],
        "year_ganzhi": selected_year["ganzhi"],
        "title": "这一年适合推进关键事项，但别把压力带进关系和财务",
        "year_focus": "一段年度主轴判断。",
        "opportunities": "一段年度机会判断。",
        "risks": "一段年度风险判断。",
        "relationship_career_wealth_health_notes": {
            "relationship": "关系备注。",
            "career": "事业备注。",
            "wealth": "财富备注。",
            "health": "健康备注。",
        },
        "action_guidance": "一段行动建议。",
        "elements_check": {key: f"{key}判断。" for key in LIUNIAN_KEYS},
    }
    knowledge = "\n\n".join(
        [
            "【统一知识底座】\n" + load_shared_foundation(),
            "【当前语气包】\n" + load_luck_section_model_pack("liunian", tone_pack),
            "【流年判断知识】\n" + load_luck_section_knowledge("liunian"),
            "【流年 taxonomy】\n" + load_luck_section_taxonomy("liunian"),
            "【输出合同】\n" + load_luck_section_output_contract("liunian"),
            "【表达样例】\n" + load_luck_section_style_examples("liunian"),
        ]
    )
    return (
        "你是易如反掌的四柱八字流年渲染器。只输出 JSON object。\n"
        "cycle_key、year、year_ganzhi 必须与 locked facts 完全一致，不得重新排盘，不得修改事实。\n"
        "输出要直接说清当年的机会、风险和行动边界，但不能写确定日期或绝对事件。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出单年流年评测。\n\n"
        f"【locked facts】\n{_dump_json(facts)}",
        json_example,
    )


def validate_dayun_output(payload: dict[str, Any], facts: dict[str, Any]) -> bool:
    selected = facts["selected_cycle"]
    if str(payload.get("cycle_key") or "") != str(selected.get("cycle_key") or ""):
        return False
    if str(payload.get("cycle_ganzhi") or "") != str(selected.get("ganzhi") or ""):
        return False
    if not all(str(payload.get(key) or "").strip() for key in ("title", "score_tendency", "core_theme", "opportunities", "risks", "action_guidance")):
        return False
    return _has_required_element_keys(payload, DAYUN_KEYS)


def validate_liunian_output(payload: dict[str, Any], facts: dict[str, Any]) -> bool:
    selected_cycle = facts["selected_cycle"]
    selected_year = facts["selected_year"]
    if str(payload.get("cycle_key") or "") != str(selected_cycle.get("cycle_key") or ""):
        return False
    try:
        if int(payload.get("year")) != int(selected_year.get("year")):
            return False
    except Exception:
        return False
    if str(payload.get("year_ganzhi") or "") != str(selected_year.get("ganzhi") or ""):
        return False
    if not all(str(payload.get(key) or "").strip() for key in ("title", "year_focus", "opportunities", "risks", "action_guidance")):
        return False
    notes = payload.get("relationship_career_wealth_health_notes")
    if not isinstance(notes, dict):
        return False
    for key in ("relationship", "career", "wealth", "health"):
        if not str(notes.get(key) or "").strip():
            return False
    return _has_required_element_keys(payload, LIUNIAN_KEYS)


def public_dayun_output(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "cycle_key": str(payload.get("cycle_key") or "").strip(),
        "cycle_ganzhi": str(payload.get("cycle_ganzhi") or "").strip(),
        "title": str(payload.get("title") or "").strip(),
        "score_tendency": str(payload.get("score_tendency") or "").strip(),
        "core_theme": str(payload.get("core_theme") or "").strip(),
        "opportunities": str(payload.get("opportunities") or "").strip(),
        "risks": str(payload.get("risks") or "").strip(),
        "action_guidance": str(payload.get("action_guidance") or "").strip(),
        "elements_check": _string_dict(payload.get("elements_check")),
        "generated_at": _utc_now(),
    }


def public_liunian_output(payload: dict[str, Any]) -> dict[str, Any]:
    notes = payload.get("relationship_career_wealth_health_notes") if isinstance(payload.get("relationship_career_wealth_health_notes"), dict) else {}
    return {
        "cycle_key": str(payload.get("cycle_key") or "").strip(),
        "year": int(payload.get("year") or 0),
        "year_ganzhi": str(payload.get("year_ganzhi") or "").strip(),
        "title": str(payload.get("title") or "").strip(),
        "year_focus": str(payload.get("year_focus") or "").strip(),
        "opportunities": str(payload.get("opportunities") or "").strip(),
        "risks": str(payload.get("risks") or "").strip(),
        "relationship_career_wealth_health_notes": {key: str(notes.get(key) or "").strip() for key in ("relationship", "career", "wealth", "health")},
        "action_guidance": str(payload.get("action_guidance") or "").strip(),
        "elements_check": _string_dict(payload.get("elements_check")),
        "generated_at": _utc_now(),
    }


def build_aspect_public_items(facts: dict[str, Any], rendered: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for aspect_key in FOUR_PILLARS_ASPECT_ORDER:
        aspect_score = facts["aspect_scores"][aspect_key]
        payload = rendered.get(aspect_key) if isinstance(rendered, dict) else None
        if not isinstance(payload, dict):
            payload = fallback_aspect_from_facts(facts, aspect_key)
        items.append(
            {
                "aspect_key": aspect_key,
                "title": str(payload.get("title") or ASPECT_TITLE_MAP[aspect_key]),
                "short_title": ASPECT_TITLE_MAP[aspect_key],
                "score": int(payload.get("score") or aspect_score["score"]),
                "is_unlocked": False,
                "unlock_points": 0,
                "content": str(payload.get("content") or ""),
                "risk": str(payload.get("risk") or ""),
                "elements_check": _string_dict(payload.get("elements_check")),
            }
        )
    return items


def fallback_summary(package: dict[str, Any]) -> dict[str, Any]:
    facts = package["deterministic_facts"]
    chart = package["chart"]
    strength = facts["day_master"]["strength"]
    favorable = "、".join(facts["day_master"]["favorable_elements"])
    interactions = facts["interactions"]
    risk_items = interactions["clashes"] + interactions["harms"] + interactions["breaks"]
    risk_text = "、".join(risk_items) if risk_items else "没有明显硬冲硬害"
    return {
        "title": f"{chart['day_master']}日主，{strength['label']}",
        "risk": f"这张命盘的主要风险在于{risk_text}。如果现实环境持续高压或关系牵扯较多，容易把原本可用的结构变成消耗。",
        "usage_guidance": f"使用这张命盘的优势，要先围绕{favorable}建立节奏，再看事业、财富和关系的具体承接，不宜只凭单一机会硬推。",
        "elements_check": {
            "日主": f"{chart['day_master']}日主，{strength['label']}。",
            "五行": f"五行计数为{facts['element_counts']}。",
            "十神": f"十神分布为{facts['ten_god_counts']}。",
            "合冲刑害": f"结构互动为{interactions}。",
            "喜忌": f"喜用候选为{favorable}。",
        },
    }


def fallback_aspect(package: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    return fallback_aspect_from_facts(package["deterministic_facts"], aspect_key)


def fallback_aspect_from_facts(facts: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    title = ASPECT_TITLE_MAP[aspect_key]
    score = int(facts["aspect_scores"][aspect_key]["score"])
    strength_label = facts["day_master"]["strength"]["label"]
    risks = facts["interactions"]["clashes"] + facts["interactions"]["harms"] + facts["interactions"]["breaks"]
    risk_text = "、".join(risks) if risks else "没有明显硬性冲突"
    return {
        "aspect_key": aspect_key,
        "title": f"{title}：先看承载，再看流通",
        "score": score,
        "content": f"{title}专项里，命盘的基础状态是{strength_label}。这说明该领域不是单点判断，要结合五行流通、十神主题和现实节奏来看。",
        "risk": f"{title}上需要留意的是{risk_text}，遇到压力时要减少硬碰硬和长期消耗。",
        "elements_check": {
            "日主": strength_label,
            "五行": f"五行计数为{facts['element_counts']}",
            "十神": f"十神分布为{facts['ten_god_counts']}",
            "合冲刑害": f"互动结构为{facts['interactions']}",
            "喜忌": f"喜用候选为{facts['day_master']['favorable_elements']}",
        },
    }


def _has_element_keys(payload: dict[str, Any]) -> bool:
    elements_check = payload.get("elements_check")
    if not isinstance(elements_check, dict):
        return False
    return all(str(elements_check.get(key) or "").strip() for key in SUMMARY_KEYS)


def _has_required_element_keys(payload: dict[str, Any], required_keys: tuple[str, ...]) -> bool:
    elements_check = payload.get("elements_check")
    if not isinstance(elements_check, dict):
        return False
    return all(str(elements_check.get(key) or "").strip() for key in required_keys)


def _string_dict(payload: Any) -> dict[str, str]:
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value).strip() for key, value in payload.items() if str(key).strip() and str(value).strip()}


def _dump_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _get_aspect_worker_count() -> int:
    try:
        return max(1, min(8, int(os.environ.get("EASEWISE_FOUR_PILLARS_ASPECT_WORKERS", "4"))))
    except ValueError:
        return 4
