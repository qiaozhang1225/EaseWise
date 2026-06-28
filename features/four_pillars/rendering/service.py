from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Iterator, Literal

from features.four_pillars.engine import FOUR_PILLARS_ASPECT_ORDER, FOUR_PILLARS_ASPECTS, build_chart_display, build_dayun_facts, build_liunian_facts
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
from product.backend.llm import DeepSeekAPIError, DeepSeekClient, build_messages
from product.backend.llm.streaming_json import build_json_stream_instruction, extract_partial_json_string_field, loads_streamed_json_object

LOGGER = logging.getLogger(__name__)

TonePack = Literal["customer", "professional"]
SUMMARY_KEYS = ("日主", "五行", "十神", "合冲刑害", "喜忌")
DAYUN_KEYS = ("原局", "大运", "十神", "五行", "合冲刑害", "喜忌")
LIUNIAN_KEYS = ("原局", "大运", "流年", "十神", "五行", "合冲刑害", "喜忌")
DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR = "DeepSeek 调用出现问题，四柱总评未生成。"
DEEPSEEK_FOUR_PILLARS_LUCK_ERROR = "DeepSeek 调用出现问题，流年大运内容未生成。"
DEEPSEEK_FOUR_PILLARS_ASPECT_ERROR = "DeepSeek 调用出现问题，专项结果未生成。"
ASPECT_TITLE_MAP = {item["aspect_key"]: item["title"] for item in FOUR_PILLARS_ASPECTS}
ASPECT_RENDER_FALLBACKS = {
    "marriage": ("love",),
    "fortune": ("annual_trend",),
    "family": ("family_environment",),
    "fengshui": ("family_environment",),
}
ASPECT_SUMMARY_CARD_KEYS = {
    "personality": ("pattern", "favorable_strategy"),
    "wealth": ("wealth", "favorable_strategy"),
    "marriage": ("marriage",),
    "career": ("pattern", "wealth", "favorable_strategy"),
    "health": ("health", "risk_window"),
    "fortune": ("risk_window", "favorable_strategy"),
    "investment": ("wealth", "risk_window", "favorable_strategy"),
    "social": ("family_environment", "pattern"),
    "industry": ("pattern", "favorable_strategy", "wealth"),
    "fengshui": ("ancestral_environment", "family_environment", "favorable_strategy"),
    "family": ("family_environment", "ancestral_environment"),
    "pattern": ("pattern", "favorable_strategy"),
}
ASPECT_SUMMARY_RELATED_KEYS = {
    "personality": ("personality", "pattern", "career"),
    "wealth": ("wealth", "investment", "career"),
    "marriage": ("marriage", "family"),
    "career": ("career", "industry", "wealth", "pattern"),
    "health": ("health", "fortune"),
    "fortune": ("fortune", "health", "wealth", "marriage"),
    "investment": ("investment", "wealth", "career"),
    "social": ("social", "family", "career"),
    "industry": ("industry", "career", "wealth", "pattern"),
    "fengshui": ("fengshui", "family"),
    "family": ("family", "marriage", "fengshui"),
    "pattern": ("pattern", "personality", "career"),
}
FALLBACK_ASPECT_TITLE_SUFFIX = "：先看自身状态，再看五行流通"
FALLBACK_ASPECT_CONTENT_MARKER = "这说明该领域不是单点判断，要结合五行流通、十神主题和现实节奏来看。"


def build_four_pillars_product_view(package: dict[str, Any]) -> dict[str, Any]:
    score_template = package["score_template"]
    chart = package["chart"]
    facts = package["deterministic_facts"]
    product_render = score_template.get("product_render") if isinstance(score_template.get("product_render"), dict) else {}
    summary = product_render.get("summary") if isinstance(product_render.get("summary"), dict) else fallback_summary(package)
    aspects_render = score_template.get("product_aspects_render") if isinstance(score_template.get("product_aspects_render"), dict) else {}
    return {
        "input_profile": score_template["input_profile"],
        "chart": chart,
        "chart_display": build_chart_display(score_template["input_profile"], chart, facts),
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


def render_summary_from_package(package: dict[str, Any], *, tone_pack: TonePack = "customer") -> dict[str, Any]:
    system_prompt, user_prompt, json_example = build_summary_prompts(package, tone_pack=tone_pack)
    try:
        response = DeepSeekClient.from_env().chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=None,
            model="deepseek-v4-pro",
            thinking_enabled=False,
            temperature=0.25,
            max_tokens=3600,
            llm_scene="four_pillars.summary",
            priority_class="foreground_core",
        )
        payload = response.json_object()
        if validate_summary_output(payload):
            return public_summary_output(payload)
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR)


def stream_summary_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 3600,
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    system_prompt, user_prompt, json_example = build_summary_prompts(package, tone_pack=tone_pack)
    messages = build_messages(
        system_prompt=f"{system_prompt.rstrip()}\n\n{build_json_stream_instruction(json_example)}",
        user_prompt=user_prompt,
    )
    raw_content = ""
    emitted_fields = {"title": "", "comprehensive_text": "", "overview": "", "risk": "", "usage_guidance": ""}
    model_name = model
    try:
        client = client or DeepSeekClient.from_env()
        yield {"event": "status", "data": {"message": "正在生成四柱综合评述"}}
        for chunk in client.stream_chat(
            messages,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.25,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            llm_scene="four_pillars.summary",
            priority_class="foreground_core",
            user_id=user_id,
            request_id=request_id,
        ):
            if chunk.raw.get("model"):
                model_name = str(chunk.raw.get("model") or model_name)
            if not chunk.content_delta:
                continue
            raw_content += chunk.content_delta
            for field in ("title", "comprehensive_text", "overview", "risk", "usage_guidance"):
                current_text = extract_partial_json_string_field(raw_content, field)
                if current_text is None:
                    continue
                previous_text = emitted_fields[field]
                if current_text == previous_text:
                    continue
                delta = current_text[len(previous_text):] if current_text.startswith(previous_text) else current_text
                emitted_fields[field] = current_text
                if delta:
                    yield {"event": "delta", "data": {"field": field, "delta": delta, "text": current_text}}

        payload = loads_streamed_json_object(raw_content)
        if validate_summary_output(payload):
            yield {"event": "result", "data": {"summary": public_summary_output(payload), "model_name": model_name}}
            return
    except Exception as exc:
        if isinstance(exc, DeepSeekAPIError):
            raise
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_SUMMARY_ERROR)


def stream_product_review_core_render(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    for render_event in stream_summary_from_package(package, tone_pack=tone_pack, user_id=user_id, request_id=request_id):
        event_name = str(render_event.get("event") or "")
        event_data = render_event.get("data") if isinstance(render_event.get("data"), dict) else {}
        if event_name == "status":
            yield {"event": "core_status", "data": {"section": "four_pillars_summary", **event_data}}
            continue
        if event_name == "delta":
            yield {"event": "core_delta", "data": {"section": "four_pillars_summary", **event_data}}
            continue
        if event_name == "result":
            summary = event_data.get("summary")
            if not isinstance(summary, dict):
                raise DeepSeekAPIError("four_pillars_summary_stream_missing_result")
            yield {
                "event": "section_complete",
                "data": {"section": "four_pillars_summary", "payload": summary, "model_name": event_data.get("model_name")},
            }
            yield {"event": "result", "data": {"product_render": {"summary": summary}}}
            return
    raise DeepSeekAPIError("four_pillars_summary_stream_missing_result")


def render_aspect_from_package(package: dict[str, Any], *, aspect_key: str, tone_pack: TonePack = "customer") -> dict[str, Any]:
    if aspect_key not in FOUR_PILLARS_ASPECT_ORDER:
        raise ValueError("invalid_aspect_key")
    system_prompt, user_prompt, json_example = build_aspect_prompts(package, aspect_key=aspect_key, tone_pack=tone_pack)
    _log_prompt_budget(f"four_pillars.aspect.{aspect_key}", system_prompt, user_prompt, json_example)
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
    except Exception as exc:
        if isinstance(exc, DeepSeekAPIError):
            raise
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_ASPECT_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_ASPECT_ERROR)


def stream_aspect_from_package(
    package: dict[str, Any],
    *,
    aspect_key: str,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    if aspect_key not in FOUR_PILLARS_ASPECT_ORDER:
        raise ValueError("invalid_aspect_key")

    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_aspect_prompts(package, aspect_key=aspect_key, tone_pack=tone_pack)
    _log_prompt_budget(f"four_pillars.aspect_unlock.{aspect_key}", system_prompt, user_prompt, json_example)
    json_instruction = (
        "Return valid json only. The final answer must be a single json object.\n"
        f"JSON shape example:\n{json.dumps(json_example, ensure_ascii=False, indent=2)}"
    )
    messages = build_messages(system_prompt=f"{system_prompt.rstrip()}\n\n{json_instruction}", user_prompt=user_prompt)

    raw_content = ""
    emitted_fields = {"title": "", "risk": "", "content": ""}
    model_name = model
    try:
        yield {"event": "status", "data": {"message": "正在生成专项判断"}}
        for chunk in client.stream_chat(
            messages,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.25,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            llm_scene=f"four_pillars.aspect_unlock.{aspect_key}",
            priority_class="foreground_interactive",
            user_id=user_id,
            request_id=request_id,
        ):
            if chunk.raw.get("model"):
                model_name = str(chunk.raw.get("model") or model_name)
            if not chunk.content_delta:
                continue
            raw_content += chunk.content_delta
            for field in ("title", "risk", "content"):
                current_text = _extract_partial_json_string_field(raw_content, field)
                if current_text is None:
                    continue
                previous_text = emitted_fields[field]
                if current_text == previous_text:
                    continue
                delta = current_text[len(previous_text):] if current_text.startswith(previous_text) else current_text
                emitted_fields[field] = current_text
                if delta:
                    yield {"event": "delta", "data": {"field": field, "delta": delta, "text": current_text}}

        payload = _loads_streamed_json_object(raw_content)
        if validate_aspect_output(payload, aspect_key=aspect_key):
            output = public_aspect_output(payload, aspect_key=aspect_key)
            yield {"event": "result", "data": {"aspect": output, "model_name": model_name}}
            return
    except Exception as exc:
        if isinstance(exc, DeepSeekAPIError):
            raise
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_ASPECT_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_ASPECT_ERROR)


def build_summary_prompts(package: dict[str, Any], *, tone_pack: TonePack) -> tuple[str, str, dict[str, Any]]:
    locked_facts = _summary_prompt_locked_facts(package)
    knowledge = "\n\n".join(
        [
            "【当前语气包】\n" + load_section_model_pack("chart_summary", tone_pack),
            "【四柱 explicit knowledge 摘录与综评合断规则】\n" + load_section_knowledge("chart_summary"),
            "【综评证据维度】\n" + load_section_taxonomy("chart_summary"),
            "【输出合同】\n" + load_section_output_contract("chart_summary"),
            "【表达样例】\n" + load_section_style_examples("chart_summary"),
        ]
    )
    json_example = {
        "title": "",
        "comprehensive_text": "",
        "overview": "",
        "risk": "",
        "usage_guidance": "",
        "key_judgements": [
            {
                "key": "",
                "label": "",
                "title": "",
                "content": "",
                "basis": "",
                "level": "",
            },
        ],
        "life_risk_windows": [
            {
                "age_range": "",
                "year_range": "",
                "risk_type": "",
                "trigger": "",
                "guidance": "",
                "level": "",
            }
        ],
        "time_highlights": [
            {
                "year": "",
                "age": "",
                "title": "",
                "content": "",
                "trigger": "",
            }
        ],
        "favorable_strategy": {
            "favorable_elements": [],
            "unfavorable_elements": [],
            "supportive_environments": [],
            "avoid_patterns": [],
            "action_guidance": "",
        },
        "elements_check": {
            "日主": "",
            "五行": "",
            "十神": "",
            "合冲刑害": "",
            "喜忌": "",
        },
    }
    return (
        "你是易如反掌的四柱八字综合评述渲染器。只输出 JSON object，不输出 markdown。\n"
        "任务：基于 locked facts 和下方 explicit knowledge 摘录，把命盘最关键的判断写成一段可读、可对照现实的综合评述。\n"
        "硬规则：不得改盘、改写确定性事实或编造 facts；专业词第一次出现要马上解释；使用倾向/风险窗口表达，不写确定灾祸、疾病诊断、寿命、必然离婚或投资承诺；不出现内部字段名和“结构承接/可用空间”等内部话术。\n"
        "控量规则：知识包用于判断，不要逐条复述；comprehensive_text 必须单段 320-520 个中文字符，其他结构化字段写短句，避免 JSON 过长。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出 title、comprehensive_text、overview、risk、usage_guidance、key_judgements、life_risk_windows、time_highlights、favorable_strategy、elements_check。\n"
        "comprehensive_text 是用户主文案：一整段话，320-520 个中文字符，不换行，优先串联命格主轴、婚恋、财富、健康、家庭/环境、风险窗口和喜忌策略。\n"
        "key_judgements 输出 6-8 个结构化依据，每项 content 不超过 80 字；life_risk_windows 优先从 summary_highlights.life_risk_windows 选 3 个，最多 5 个；time_highlights 只提取最多 3 个年份/年龄重点。\n\n"
        f"【locked facts】\n{_dump_json(locked_facts)}",
        json_example,
    )


def _summary_prompt_locked_facts(package: dict[str, Any]) -> dict[str, Any]:
    facts = package.get("deterministic_facts") if isinstance(package.get("deterministic_facts"), dict) else {}
    score_template = package.get("score_template") if isinstance(package.get("score_template"), dict) else {}
    input_profile = package.get("input_profile") if isinstance(package.get("input_profile"), dict) else score_template.get("input_profile")
    summary_fact_keys = (
        "input_summary",
        "day_master",
        "element_counts",
        "ten_god_counts",
        "interactions",
        "empty_branches",
        "tombs",
        "shen_sha",
        "aspect_signals",
        "summary_highlights",
    )
    return {
        "input_profile": input_profile if isinstance(input_profile, dict) else {},
        "chart": package.get("chart") if isinstance(package.get("chart"), dict) else {},
        "deterministic_facts": {
            key: facts.get(key)
            for key in summary_fact_keys
            if key in facts
        },
    }


def build_aspect_locked_facts(package: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    if aspect_key not in FOUR_PILLARS_ASPECT_ORDER:
        raise ValueError("invalid_aspect_key")
    facts = package.get("deterministic_facts") if isinstance(package.get("deterministic_facts"), dict) else {}
    score_template = package.get("score_template") if isinstance(package.get("score_template"), dict) else {}
    input_profile = package.get("input_profile") if isinstance(package.get("input_profile"), dict) else score_template.get("input_profile")
    summary_highlights = facts.get("summary_highlights") if isinstance(facts.get("summary_highlights"), dict) else {}
    payload: dict[str, Any] = {
        "aspect_key": aspect_key,
        "aspect_title": ASPECT_TITLE_MAP.get(aspect_key, aspect_key),
        "input_profile": input_profile if isinstance(input_profile, dict) else {},
        "chart": package.get("chart") if isinstance(package.get("chart"), dict) else {},
        "deterministic_facts": {
            "input_summary": facts.get("input_summary"),
            "day_master": facts.get("day_master"),
            "element_counts": facts.get("element_counts"),
            "ten_god_counts": facts.get("ten_god_counts"),
            "interactions": facts.get("interactions"),
            "empty_branches": facts.get("empty_branches"),
            "tombs": facts.get("tombs"),
            "shen_sha": _compact_shen_sha(facts.get("shen_sha")),
            "aspect_signals": facts.get("aspect_signals"),
            "summary_highlights": _aspect_summary_highlights(summary_highlights, aspect_key),
        },
    }
    if aspect_key == "fortune":
        payload["deterministic_facts"]["luck_context"] = _aspect_fortune_luck_context(facts, summary_highlights)
    return payload


def _compact_shen_sha(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    result: dict[str, Any] = {}
    if isinstance(payload.get("summary"), dict):
        result["summary"] = payload["summary"]
    by_pillar = payload.get("by_pillar")
    if isinstance(by_pillar, dict):
        result["by_pillar_names"] = {
            str(pillar): [
                str(item.get("name") if isinstance(item, dict) else item)
                for item in items
                if str(item.get("name") if isinstance(item, dict) else item).strip()
            ][:10]
            for pillar, items in by_pillar.items()
            if isinstance(items, list)
        }
    return result


def _aspect_summary_highlights(summary_highlights: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    if not isinstance(summary_highlights, dict):
        return {}
    selected_card_keys = set(ASPECT_SUMMARY_CARD_KEYS.get(aspect_key, (aspect_key,)))
    selected_related_keys = set(ASPECT_SUMMARY_RELATED_KEYS.get(aspect_key, (aspect_key,)))
    cards = []
    for item in summary_highlights.get("key_judgement_facts", []):
        if not isinstance(item, dict):
            continue
        item_key = str(item.get("key") or "").strip()
        related = {str(value) for value in item.get("related_aspects", []) if str(value).strip()} if isinstance(item.get("related_aspects"), list) else set()
        if item_key in selected_card_keys or related.intersection(selected_related_keys):
            cards.append(item)
    result: dict[str, Any] = {
        "version": summary_highlights.get("version"),
        "judgement_policy": summary_highlights.get("judgement_policy"),
        "key_judgement_facts": cards[:4],
    }
    if aspect_key in {"fortune", "health", "marriage", "wealth", "investment", "family"}:
        windows = summary_highlights.get("life_risk_windows")
        if isinstance(windows, list):
            result["life_risk_windows"] = windows[:5]
    if aspect_key in {"personality", "pattern", "career", "social", "industry"}:
        special_patterns = summary_highlights.get("special_patterns")
        if isinstance(special_patterns, list):
            result["special_patterns"] = special_patterns[:5]
    if aspect_key in {"fengshui", "family"} and isinstance(summary_highlights.get("environment_symbols"), dict):
        result["environment_symbols"] = summary_highlights["environment_symbols"]
    if aspect_key in {"fortune", "wealth", "investment", "career", "industry", "fengshui", "pattern", "personality"} and isinstance(summary_highlights.get("favorable_strategy"), dict):
        result["favorable_strategy"] = summary_highlights["favorable_strategy"]
    return result


def _aspect_fortune_luck_context(facts: dict[str, Any], summary_highlights: dict[str, Any]) -> dict[str, Any]:
    luck_cycles = facts.get("luck_cycles") if isinstance(facts.get("luck_cycles"), dict) else {}
    current_cycle_key = str(luck_cycles.get("current_cycle_key") or "")
    cycles = luck_cycles.get("cycles") if isinstance(luck_cycles.get("cycles"), list) else []
    current_cycle = None
    if current_cycle_key:
        for item in cycles:
            if isinstance(item, dict) and str(item.get("cycle_key") or "") == current_cycle_key:
                current_cycle = _compact_luck_cycle(item)
                break
    if current_cycle is None:
        for item in cycles:
            if isinstance(item, dict) and item.get("is_current"):
                current_cycle = _compact_luck_cycle(item)
                break
    windows = summary_highlights.get("life_risk_windows") if isinstance(summary_highlights, dict) else []
    return {
        "current_year": luck_cycles.get("current_year"),
        "current_cycle_key": current_cycle_key or None,
        "current_cycle": current_cycle,
        "key_year_windows": windows[:5] if isinstance(windows, list) else [],
    }


def _compact_luck_cycle(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "cycle_key": cycle.get("cycle_key"),
        "start_year": cycle.get("start_year"),
        "end_year": cycle.get("end_year"),
        "start_age": cycle.get("start_age"),
        "end_age": cycle.get("end_age"),
        "ganzhi": cycle.get("ganzhi"),
        "stem": cycle.get("stem"),
        "branch": cycle.get("branch"),
        "stem_ten_god": cycle.get("stem_ten_god"),
        "stem_element": cycle.get("stem_element"),
        "branch_element": cycle.get("branch_element"),
        "di_shi": cycle.get("di_shi"),
        "xun_kong": cycle.get("xun_kong"),
        "shen_sha": cycle.get("shen_sha"),
    }


def build_aspect_prompts(package: dict[str, Any], *, aspect_key: str, tone_pack: TonePack) -> tuple[str, str, dict[str, Any]]:
    title = ASPECT_TITLE_MAP[aspect_key]
    locked_facts = build_aspect_locked_facts(package, aspect_key)
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
    json_example = {
        "aspect_key": aspect_key,
        "title": "",
        "content": "",
        "risk": "",
        "elements_check": {
            "日主": "",
            "五行": "",
            "十神": "",
            "合冲刑害": "",
            "喜忌": "",
        },
    }
    return (
        f"你是易如反掌的四柱八字「{title}」专项渲染器。只输出 JSON object。\n"
        "不得出现课程、来源、内部字段名。\n\n"
        "表达要求：先给现实判断，再补命理依据；用户应该能把内容对照到自己的生活、工作、关系或财务场景。\n"
        "所有专业词必须跟着解释现实含义，例如正印解释为学习/资质/长辈资源，伤官解释为表达锋芒/突破规则，七杀解释为压力/竞争/执行力。\n"
        "专业词不是禁用词，但必须先点名、再翻译、再落到现实场景；不能只写“伤官明显”“空亡较重”“格局不错”。\n"
        "格局专项必须说明格局如何影响资源获取、表达方式、压力处理和成长路径；不能只列正印、伤官、七杀等术语。\n"
        "运势专项只写阶段趋势和近期变化，不替代大运、流年付费生成。\n"
        "title、content、risk 不要出现“结构承接、可用空间、可用之处、现实承接感、底层结构、后段承接”等内部分析词。\n"
        "不要写绝对发财、疾病、离婚、灾祸或确定事件。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出 aspect_key、title、content、risk、elements_check。\n\n"
        "如果使用伤官、正印、七杀、财星、官杀、比劫、夫妻宫、墓库、禄神、空亡、格局等专业词，必须紧跟白话解释和现实场景。\n\n"
        f"【locked facts】\n{_dump_json(locked_facts)}",
        json_example,
    )


def validate_summary_output(payload: dict[str, Any]) -> bool:
    return all(str(payload.get(key) or "").strip() for key in ("title", "comprehensive_text")) and _has_element_keys(payload)


def validate_aspect_output(payload: dict[str, Any], *, aspect_key: str) -> bool:
    if str(payload.get("aspect_key") or "").strip() != aspect_key:
        return False
    if not all(str(payload.get(key) or "").strip() for key in ("title", "content", "risk")):
        return False
    return _has_element_keys(payload)


def public_summary_output(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": str(payload.get("title") or "").strip(),
        "comprehensive_text": str(payload.get("comprehensive_text") or "").strip(),
        "overview": str(payload.get("overview") or "").strip(),
        "risk": str(payload.get("risk") or "").strip(),
        "usage_guidance": str(payload.get("usage_guidance") or "").strip(),
        "key_judgements": _summary_key_judgements(payload.get("key_judgements")),
        "life_risk_windows": _summary_life_risk_windows(payload.get("life_risk_windows")),
        "time_highlights": _summary_time_highlights(payload.get("time_highlights"), payload.get("life_risk_windows")),
        "favorable_strategy": _summary_favorable_strategy(payload.get("favorable_strategy")),
        "elements_check": _string_dict(payload.get("elements_check")),
    }


def public_aspect_output(payload: dict[str, Any], *, aspect_key: str) -> dict[str, Any]:
    return {
        "aspect_key": aspect_key,
        "title": str(payload.get("title") or ASPECT_TITLE_MAP[aspect_key]).strip(),
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
    _log_prompt_budget("four_pillars.luck.dayun", system_prompt, user_prompt, json_example)
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
        LOGGER.warning(
            "four_pillars_dayun_invalid_output cycle_key=%s payload_keys=%s content=%s",
            facts.get("selected_cycle", {}).get("cycle_key") if isinstance(facts.get("selected_cycle"), dict) else None,
            sorted(payload.keys()),
            response.content[:800],
        )
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
    _log_prompt_budget("four_pillars.luck.liunian", system_prompt, user_prompt, json_example)
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
        LOGGER.warning(
            "four_pillars_liunian_invalid_output cycle_key=%s year=%s payload_keys=%s content=%s",
            facts.get("selected_cycle", {}).get("cycle_key") if isinstance(facts.get("selected_cycle"), dict) else None,
            facts.get("selected_year", {}).get("year") if isinstance(facts.get("selected_year"), dict) else None,
            sorted(payload.keys()),
            response.content[:800],
        )
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_LUCK_ERROR) from exc
    raise DeepSeekAPIError(DEEPSEEK_FOUR_PILLARS_LUCK_ERROR)


def stream_dayun_from_package(
    package: dict[str, Any],
    *,
    cycle_key: str,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 2200,
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    facts = build_dayun_facts(package, cycle_key)
    system_prompt, user_prompt, json_example = build_dayun_prompts(facts, tone_pack=tone_pack)
    _log_prompt_budget("four_pillars.luck.dayun.stream", system_prompt, user_prompt, json_example)
    yield from _stream_luck_render_from_prompts(
        facts=facts,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_example=json_example,
        fields=("title", "trend_tendency", "core_theme", "opportunities", "risks", "action_guidance"),
        validate_output=validate_dayun_output,
        public_output=public_dayun_output,
        llm_scene="four_pillars.luck.dayun",
        status_message="正在生成大运综评",
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
        user_id=user_id,
        request_id=request_id,
    )


def stream_liunian_from_package(
    package: dict[str, Any],
    *,
    cycle_key: str,
    year: int,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 2400,
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    facts = build_liunian_facts(package, cycle_key, year)
    system_prompt, user_prompt, json_example = build_liunian_prompts(facts, tone_pack=tone_pack)
    _log_prompt_budget("four_pillars.luck.liunian.stream", system_prompt, user_prompt, json_example)
    yield from _stream_luck_render_from_prompts(
        facts=facts,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_example=json_example,
        fields=("title", "year_focus", "opportunities", "risks", "action_guidance"),
        validate_output=validate_liunian_output,
        public_output=public_liunian_output,
        llm_scene="four_pillars.luck.liunian",
        status_message="正在生成流年评测",
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
        user_id=user_id,
        request_id=request_id,
    )


def _stream_luck_render_from_prompts(
    *,
    facts: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    json_example: dict[str, Any],
    fields: tuple[str, ...],
    validate_output: Any,
    public_output: Any,
    llm_scene: str,
    status_message: str,
    client: DeepSeekClient | None,
    model: str,
    thinking_enabled: bool,
    max_tokens: int,
    user_id: str | None,
    request_id: str | None,
) -> Iterator[dict[str, Any]]:
    messages = build_messages(
        system_prompt=f"{system_prompt.rstrip()}\n\n{build_json_stream_instruction(json_example)}",
        user_prompt=user_prompt,
    )
    raw_content = ""
    emitted_fields = {field: "" for field in fields}
    model_name = model
    try:
        client = client or DeepSeekClient.from_env()
        yield {"event": "status", "data": {"message": status_message}}
        for chunk in client.stream_chat(
            messages,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.25,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            llm_scene=llm_scene,
            priority_class="foreground_interactive",
            user_id=user_id,
            request_id=request_id,
        ):
            if chunk.raw.get("model"):
                model_name = str(chunk.raw.get("model") or model_name)
            if not chunk.content_delta:
                continue
            raw_content += chunk.content_delta
            for field in fields:
                current_text = extract_partial_json_string_field(raw_content, field)
                if current_text is None:
                    continue
                previous_text = emitted_fields[field]
                if current_text == previous_text:
                    continue
                delta = current_text[len(previous_text):] if current_text.startswith(previous_text) else current_text
                emitted_fields[field] = current_text
                if delta:
                    yield {"event": "delta", "data": {"field": field, "delta": delta, "text": current_text}}

        payload = loads_streamed_json_object(raw_content)
        if validate_output(payload, facts):
            yield {"event": "result", "data": {"render": public_output(payload), "model_name": model_name}}
            return
        LOGGER.warning(
            "four_pillars_luck_stream_invalid_output scene=%s payload_keys=%s content=%s",
            llm_scene,
            sorted(payload.keys()),
            raw_content[:800],
        )
    except Exception as exc:
        if isinstance(exc, DeepSeekAPIError):
            raise
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
        "title": "",
        "trend_tendency": "",
        "core_theme": "",
        "opportunities": "",
        "risks": "",
        "action_guidance": "",
        "elements_check": {key: "" for key in DAYUN_KEYS},
    }
    return (
        "你是易如反掌的四柱八字大运综评渲染器。只输出 JSON object。\n"
        "cycle_key 和 cycle_ganzhi 必须与 locked facts 完全一致，不得重新排盘，不得修改事实。\n"
        "输出要直白、有现实落点，但不能写绝对灾祸、疾病、离婚或发财承诺。\n\n"
        "可以使用大运、十神、合冲刑害、空亡、墓库、禄神等专业词，但第一次出现必须马上解释成现实含义。\n"
        "用户主文案不要出现“结构承接、可用空间、可用之处、现实承接感、底层结构、后段承接”等内部分析词。\n\n"
        "主文案字段必须各司其职：opportunities 只写机会与助力，risks 只写风险与消耗，action_guidance 只写行动建议。\n"
        "主文案字段写成自然段，不要使用 1、2、3、①②③、项目符号或小标题列表；elements_check 可以保留结构化判断。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出大运综评。\n\n"
        "输出要遵守“专业词 + 白话解释 + 现实对照”的顺序。\n\n"
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
        "title": "",
        "year_focus": "",
        "opportunities": "",
        "risks": "",
        "relationship_career_wealth_health_notes": {
            "relationship": "",
            "career": "",
            "wealth": "",
            "health": "",
        },
        "action_guidance": "",
        "elements_check": {key: "" for key in LIUNIAN_KEYS},
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
        "可以使用流年、十神、合冲刑害、空亡、墓库、禄神等专业词，但第一次出现必须马上解释成现实含义。\n"
        "用户主文案不要出现“结构承接、可用空间、可用之处、现实承接感、底层结构、后段承接”等内部分析词。\n\n"
        "主文案字段必须各司其职：opportunities 只写机会与助力，risks 只写风险与消耗，action_guidance 只写行动建议。\n"
        "主文案字段写成自然段，不要使用 1、2、3、①②③、项目符号或小标题列表；elements_check 可以保留结构化判断。\n\n"
        f"{knowledge}",
        "请基于 locked facts 输出单年流年评测。\n\n"
        "输出要遵守“专业词 + 白话解释 + 现实对照”的顺序。\n\n"
        f"【locked facts】\n{_dump_json(facts)}",
        json_example,
    )


def validate_dayun_output(payload: dict[str, Any], facts: dict[str, Any]) -> bool:
    selected = facts["selected_cycle"]
    if str(payload.get("cycle_key") or "") != str(selected.get("cycle_key") or ""):
        return False
    if str(payload.get("cycle_ganzhi") or "") != str(selected.get("ganzhi") or ""):
        return False
    if not all(str(payload.get(key) or "").strip() for key in ("title", "core_theme", "opportunities", "risks", "action_guidance")):
        return False
    if not str(payload.get("trend_tendency") or payload.get("score_tendency") or "").strip():
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
        "trend_tendency": str(payload.get("trend_tendency") or payload.get("score_tendency") or "").strip(),
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
        payload = _rendered_aspect_payload(rendered, aspect_key)
        if not isinstance(payload, dict):
            payload = fallback_aspect_from_facts(facts, aspect_key)
        items.append(
            {
                "aspect_key": aspect_key,
                "title": str(payload.get("title") or ASPECT_TITLE_MAP[aspect_key]),
                "short_title": ASPECT_TITLE_MAP[aspect_key],
                "is_unlocked": False,
                "unlock_points": 0,
                "content": str(payload.get("content") or ""),
                "risk": str(payload.get("risk") or ""),
                "elements_check": _string_dict(payload.get("elements_check")),
            }
        )
    return items


def _rendered_aspect_payload(rendered: dict[str, Any], aspect_key: str) -> dict[str, Any] | None:
    if not isinstance(rendered, dict):
        return None
    payload = rendered.get(aspect_key)
    if isinstance(payload, dict):
        return payload
    for legacy_key in ASPECT_RENDER_FALLBACKS.get(aspect_key, ()):
        payload = rendered.get(legacy_key)
        if isinstance(payload, dict):
            return {**payload, "aspect_key": aspect_key}
    return None


def fallback_summary(package: dict[str, Any]) -> dict[str, Any]:
    facts = package["deterministic_facts"]
    chart = package["chart"]
    strength = facts["day_master"]["strength"]
    favorable = "、".join(facts["day_master"]["favorable_elements"])
    interactions = facts["interactions"]
    highlights = facts.get("summary_highlights") if isinstance(facts.get("summary_highlights"), dict) else {}
    risk_items = interactions["clashes"] + interactions["harms"] + interactions["breaks"]
    risk_text = "、".join(risk_items) if risk_items else "没有明显硬冲硬害"
    cards = highlights.get("key_judgement_facts") if isinstance(highlights.get("key_judgement_facts"), list) else []
    risk_windows = highlights.get("life_risk_windows") if isinstance(highlights.get("life_risk_windows"), list) else []
    strategy = highlights.get("favorable_strategy") if isinstance(highlights.get("favorable_strategy"), dict) else {}
    return {
        "title": f"{chart['day_master']}日主，{strength['label']}",
        "comprehensive_text": f"这张命盘的主轴是{strength['label']}，需要把日主承载、五行流通、十神主题和风险窗口一起看。总评先抓最明显的婚恋、财富、健康、家庭环境和喜忌策略：关系上看夫妻宫和配偶星的稳定度，财富上看财星、财库和比劫分财，健康上看五行偏枯带来的长期消耗，家庭与祖上环境只按年柱、月柱和地支象意提示。喜用候选为{favorable}，现实里更适合先稳作息、现金流和合作边界，再进入专项看完整推演。",
        "overview": f"这张命盘的主轴是{strength['label']}，需要把日主承载、五行流通、十神主题和风险窗口一起看。",
        "risk": f"这张命盘的主要风险在于{risk_text}。如果现实环境持续高压或关系牵扯较多，原本能用出来的优势也容易变成消耗。",
        "usage_guidance": f"使用这张命盘的优势，要先围绕{favorable}建立节奏，再看事业、财富和关系里哪些事情最适合推进，不宜只凭单一机会硬推。",
        "key_judgements": [
            {
                "key": str(item.get("key") or ""),
                "label": str(item.get("label") or ""),
                "title": str(item.get("title") or ""),
                "content": str(item.get("reading") or ""),
                "basis": "；".join(str(value) for value in item.get("basis", []) if str(value).strip()) if isinstance(item.get("basis"), list) else str(item.get("basis") or ""),
                "level": str(item.get("level") or "medium"),
            }
            for item in cards
            if isinstance(item, dict)
        ],
        "life_risk_windows": [
            {
                "age_range": str(item.get("age_range") or ""),
                "year_range": _summary_year_range(item),
                "risk_type": str(item.get("risk_type") or ""),
                "trigger": "、".join(str(value) for value in item.get("trigger_tags", []) if str(value).strip()) if isinstance(item.get("trigger_tags"), list) else "",
                "guidance": str(item.get("reality_focus") or ""),
                "level": str(item.get("level") or "medium"),
            }
            for item in risk_windows
            if isinstance(item, dict)
        ],
        "time_highlights": _summary_time_highlights(None, risk_windows),
        "favorable_strategy": {
            "favorable_elements": list(strategy.get("favorable_elements", [])) if isinstance(strategy.get("favorable_elements"), list) else facts["day_master"]["favorable_elements"],
            "unfavorable_elements": list(strategy.get("unfavorable_elements", [])) if isinstance(strategy.get("unfavorable_elements"), list) else facts["day_master"]["unfavorable_elements"],
            "supportive_environments": list(strategy.get("supportive_environments", [])) if isinstance(strategy.get("supportive_environments"), list) else [],
            "avoid_patterns": list(strategy.get("avoid_patterns", [])) if isinstance(strategy.get("avoid_patterns"), list) else [],
            "action_guidance": "先稳作息、现金流和合作边界，再选择能放大喜用方向的环境。",
        },
        "elements_check": {
            "日主": f"{chart['day_master']}日主，{strength['label']}。",
            "五行": f"五行计数为{facts['element_counts']}。",
            "十神": f"十神分布为{facts['ten_god_counts']}。",
            "合冲刑害": f"合冲刑害为{interactions}，用于判断变化、拉扯和关系牵动。",
            "喜忌": f"喜用候选为{favorable}。",
        },
    }


def fallback_aspect(package: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    return fallback_aspect_from_facts(package["deterministic_facts"], aspect_key)


def fallback_aspect_from_facts(facts: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    title = ASPECT_TITLE_MAP[aspect_key]
    strength_label = facts["day_master"]["strength"]["label"]
    risks = facts["interactions"]["clashes"] + facts["interactions"]["harms"] + facts["interactions"]["breaks"]
    risk_text = "、".join(risks) if risks else "没有明显硬性冲突"
    return {
        "aspect_key": aspect_key,
        "title": f"{title}：先看自身状态，再看五行流通",
        "content": f"{title}专项里，命盘的基础状态是{strength_label}。这说明该领域不是单点判断，要结合五行流通、十神主题和现实节奏来看。",
        "risk": f"{title}上需要留意的是{risk_text}，遇到压力时要减少硬碰硬和长期消耗。",
        "elements_check": {
            "日主": strength_label,
            "五行": f"五行计数为{facts['element_counts']}",
            "十神": f"十神分布为{facts['ten_god_counts']}",
            "合冲刑害": f"合冲刑害为{facts['interactions']}",
            "喜忌": f"喜用候选为{facts['day_master']['favorable_elements']}",
        },
    }


def is_fallback_aspect_payload(payload: Any, aspect_key: str | None = None) -> bool:
    if not isinstance(payload, dict):
        return False
    title = str(payload.get("title") or "").strip()
    content = str(payload.get("content") or "").strip()
    if aspect_key and aspect_key in ASPECT_TITLE_MAP and title == f"{ASPECT_TITLE_MAP[aspect_key]}{FALLBACK_ASPECT_TITLE_SUFFIX}":
        return FALLBACK_ASPECT_CONTENT_MARKER in content
    if title.endswith(FALLBACK_ASPECT_TITLE_SUFFIX) and FALLBACK_ASPECT_CONTENT_MARKER in content:
        return True
    return content.startswith(("命盘的基础状态是",)) and FALLBACK_ASPECT_CONTENT_MARKER in content


def _summary_key_judgements(payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, list):
        return []
    items: list[dict[str, str]] = []
    for raw_item in payload:
        if not isinstance(raw_item, dict):
            continue
        item = {
            "key": str(raw_item.get("key") or "").strip(),
            "label": str(raw_item.get("label") or "").strip(),
            "title": str(raw_item.get("title") or "").strip(),
            "content": str(raw_item.get("content") or "").strip(),
            "basis": _summary_basis_text(raw_item.get("basis")),
            "level": str(raw_item.get("level") or "medium").strip(),
        }
        if item["label"] and (item["title"] or item["content"]):
            items.append(item)
    return items[:8]


def _summary_life_risk_windows(payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, list):
        return []
    items: list[dict[str, str]] = []
    for raw_item in payload:
        if not isinstance(raw_item, dict):
            continue
        item = {
            "age_range": str(raw_item.get("age_range") or "").strip(),
            "year_range": str(raw_item.get("year_range") or "").strip() or _summary_year_range(raw_item),
            "risk_type": str(raw_item.get("risk_type") or "").strip(),
            "trigger": str(raw_item.get("trigger") or "").strip() or _summary_basis_text(raw_item.get("trigger_tags")),
            "guidance": str(raw_item.get("guidance") or raw_item.get("reality_focus") or "").strip(),
            "level": str(raw_item.get("level") or "medium").strip(),
        }
        if (item["age_range"] or item["year_range"]) and (item["risk_type"] or item["guidance"]):
            items.append(item)
    return items[:5]


def _summary_time_highlights(payload: Any, fallback_windows: Any = None) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if isinstance(payload, list):
        for raw_item in payload:
            if not isinstance(raw_item, dict):
                continue
            item = {
                "year": str(raw_item.get("year") or "").strip(),
                "age": str(raw_item.get("age") or "").strip(),
                "title": str(raw_item.get("title") or "").strip(),
                "content": str(raw_item.get("content") or "").strip(),
                "trigger": str(raw_item.get("trigger") or "").strip(),
            }
            if (item["year"] or item["age"]) and (item["title"] or item["content"]):
                items.append(item)
    if items:
        return items[:3]

    windows = fallback_windows if isinstance(fallback_windows, list) else []
    for raw_item in windows:
        if not isinstance(raw_item, dict):
            continue
        year_range = str(raw_item.get("year_range") or "").strip() or _summary_year_range(raw_item)
        age_range = str(raw_item.get("age_range") or "").strip()
        risk_type = str(raw_item.get("risk_type") or "").strip()
        guidance = str(raw_item.get("guidance") or raw_item.get("reality_focus") or "").strip()
        trigger = str(raw_item.get("trigger") or "").strip() or _summary_basis_text(raw_item.get("trigger_tags"))
        if not (year_range or age_range):
            continue
        items.append(
            {
                "year": year_range,
                "age": age_range,
                "title": risk_type or "阶段提醒",
                "content": guidance,
                "trigger": trigger,
            }
        )
    return items[:3]


def _summary_favorable_strategy(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "favorable_elements": [],
            "unfavorable_elements": [],
            "supportive_environments": [],
            "avoid_patterns": [],
            "action_guidance": "",
        }
    return {
        "favorable_elements": _string_list(payload.get("favorable_elements")),
        "unfavorable_elements": _string_list(payload.get("unfavorable_elements")),
        "supportive_environments": _string_list(payload.get("supportive_environments")),
        "avoid_patterns": _string_list(payload.get("avoid_patterns")),
        "action_guidance": str(payload.get("action_guidance") or "").strip(),
    }


def _summary_basis_text(payload: Any) -> str:
    if isinstance(payload, list):
        return "；".join(str(item).strip() for item in payload if str(item).strip())
    return str(payload or "").strip()


def _summary_year_range(item: dict[str, Any]) -> str:
    start_year = int(item.get("start_year") or 0)
    end_year = int(item.get("end_year") or 0)
    if start_year and end_year and start_year != end_year:
        return f"{start_year}-{end_year}年"
    if start_year:
        return f"{start_year}年"
    return ""


def _string_list(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        return []
    return [str(item).strip() for item in payload if str(item).strip()]


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


def _log_prompt_budget(scene: str, system_prompt: str, user_prompt: str, json_example: dict[str, Any]) -> None:
    facts_chars = 0
    if "【locked facts】" in user_prompt:
        facts_chars = len(user_prompt.split("【locked facts】", 1)[1])
    LOGGER.info(
        "four_pillars_prompt_budget scene=%s system_chars=%s user_chars=%s facts_chars=%s example_chars=%s approx_knowledge_chars=%s",
        scene,
        len(system_prompt),
        len(user_prompt),
        facts_chars,
        len(json.dumps(json_example, ensure_ascii=False, default=str)),
        _approx_knowledge_chars(system_prompt),
    )


def _approx_knowledge_chars(system_prompt: str) -> int:
    markers = ("【四柱 explicit knowledge", "【统一知识底座】", "【当前语气包】")
    starts = [system_prompt.find(marker) for marker in markers if system_prompt.find(marker) >= 0]
    if not starts:
        return 0
    return len(system_prompt[min(starts):])


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _get_aspect_worker_count() -> int:
    try:
        return max(1, min(8, int(os.environ.get("EASEWISE_FOUR_PILLARS_ASPECT_WORKERS", "4"))))
    except ValueError:
        return 4


def _loads_streamed_json_object(raw_content: str) -> dict[str, Any]:
    text = raw_content.strip()
    if not text:
        raise DeepSeekAPIError("DeepSeek returned empty content; cannot parse JSON.")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DeepSeekAPIError(f"DeepSeek content is not valid JSON: {text}") from exc
    if not isinstance(parsed, dict):
        raise DeepSeekAPIError(f"DeepSeek JSON response is not an object: {parsed}")
    return parsed


def _extract_partial_json_string_field(raw_content: str, field: str) -> str | None:
    key = json.dumps(field, ensure_ascii=False)
    key_index = raw_content.find(key)
    if key_index < 0:
        return None
    colon_index = raw_content.find(":", key_index + len(key))
    if colon_index < 0:
        return None
    value_index = colon_index + 1
    while value_index < len(raw_content) and raw_content[value_index].isspace():
        value_index += 1
    if value_index >= len(raw_content) or raw_content[value_index] != '"':
        return None

    chars: list[str] = []
    index = value_index + 1
    while index < len(raw_content):
        char = raw_content[index]
        if char == '"':
            return "".join(chars)
        if char != "\\":
            chars.append(char)
            index += 1
            continue

        if index + 1 >= len(raw_content):
            break
        escaped = raw_content[index + 1]
        if escaped == "u":
            hex_text = raw_content[index + 2:index + 6]
            if len(hex_text) < 4:
                break
            try:
                chars.append(chr(int(hex_text, 16)))
            except ValueError:
                chars.append("\\u" + hex_text)
            index += 6
            continue
        chars.append(
            {
                '"': '"',
                "\\": "\\",
                "/": "/",
                "b": "\b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
            }.get(escaped, escaped)
        )
        index += 2
    return "".join(chars)
