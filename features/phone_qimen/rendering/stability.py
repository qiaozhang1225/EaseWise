from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterator, Literal

from features.phone_qimen.knowledge import (
    load_section_knowledge,
    load_section_model_pack,
    load_section_output_contract,
    load_section_style_examples,
    load_section_taxonomy,
    load_shared_foundation,
)
from product.backend.llm import DeepSeekAPIError, DeepSeekClient, build_messages
from product.backend.llm.streaming_json import build_json_stream_instruction, extract_partial_json_string_field, loads_streamed_json_object
from features.phone_qimen.scoring.dimensions import score_phone_stability_dimensions
from features.phone_qimen.scoring.total_score.engine import LAYER_LABELS, load_rules
from features.phone_qimen.scoring.total_score.labels import (
    PATTERN_LABELS,
    RELATION_LABELS,
    _humanize_harm,
    _label,
)

TonePack = Literal["customer", "professional"]

DEEPSEEK_STABILITY_ERROR = "DeepSeek 调用出现问题，稳定性结果未生成。"
REQUIRED_ELEMENT_KEYS = (
    "整体承接",
    "宫门关系",
    "四害",
    "特殊组合",
    "神星门",
    "天干/地干",
    "风险敏感方向",
    "最终使用结论",
)


@dataclass
class StabilityRenderResult:
    verdict: str
    content: str
    elements_check: dict[str, Any]
    tone_pack: TonePack
    model_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "content": self.content,
            "elements_check": self.elements_check,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
        }


def build_stability_prompts(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    rules: dict[str, Any] | None = None,
) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    rules = rules or load_rules()
    score_result = score_phone_stability_dimensions(phone, gender, rules=rules)
    locked = _locked_fields(score_result)
    evidence = _evidence_fields(score_result)
    direct_checks = _direct_checks(score_result)
    shared_foundation = load_shared_foundation()
    model_pack = load_section_model_pack("stability", tone_pack)
    section_knowledge = load_section_knowledge("stability")
    taxonomy = load_section_taxonomy("stability")
    output_contract = load_section_output_contract("stability")
    style_examples = load_section_style_examples("stability")

    knowledge_block = (
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【稳定性判断知识】\n"
        f"{section_knowledge}\n\n"
        "【稳定性 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【稳定性表达风格样例】\n"
        f"{style_examples}"
    )

    json_example = {
        "verdict": locked["verdict"],
        "content": "请用一段自然中文把这个号码的长期使用意见写出来，直接说清楚适不适合主用、问题会在什么场景里出现、继续用要怎么避开。",
        "elements_check": {
            "整体承接": "一句话判断是否适合长期主用，并翻译成主用、辅助使用或谨慎使用的感受。",
            "宫门关系": "一句话判断环境和行动是否顺接，并翻译成长期推进会不会卡。",
            "四害": "一句话判断硬伤是否会反复放大，并翻译成落空、受压、收不住或临场出错。",
            "特殊组合": "一句话判断放大效应，并翻译成长期容易在哪些场景变明显。",
            "神星门": "一句话判断长期气质，并翻译成用户使用时的感受和节奏。",
            "天干/地干": "一句话判断后段收口与长期沉淀，并翻译成结果能否留住。",
            "风险敏感方向": "一句话判断弱项会在哪些方向放大长期风险；只有用户明确给出关注项时，才写成用户关注。",
            "最终使用结论": locked["verdict"],
        },
    }

    system_prompt = (
        "你是易如反掌的手机号稳定性渲染器，负责把代码锁定的稳定性事实写成用户最终可见的长期使用意见。\n"
        "你的职责不是改分、不是重新判断，也不是输出中间层解释。\n"
        "必须遵守这些硬规则：\n"
        "1. 最终只输出一个 JSON object，且只包含 verdict、content、elements_check。\n"
        "2. 不得修改或推翻 locked_fields。\n"
        "3. 不得出现课程、知识库、文档、老师、资料或来源痕迹。\n"
        "4. verdict 必须是代码锁定的四类之一，不能自行发明新档位。\n"
        "5. content 必须是一段话，不拆条，不列表，并且必须让用户知道适不适合主用、问题会在哪里长期反复、继续用要怎么调整。\n"
        "6. content 要把整体承接、宫门关系、四害、特殊组合、神星门、天干/地干和风险敏感方向综合成一个自然结论。\n"
        "7. content 必须优先写现实表现，例如长期联系、事业主号、合作收口、资金沉淀、关系维护、睡眠精力或出行安排；不要连续堆叠专业词。\n"
        "8. elements_check 是内部判断块，必须覆盖七层判断，但不要把它写成机械表格口吻；每项要写出专业层背后的现实含义。\n"
        "9. 不要只盯着单一切口，必须让七层都对最终结论产生影响。\n"
        "10. 不要输出 raw model output、fallback、置信度或任何内部流程字段。\n"
        "11. 分数只作为数字引用；content 和 elements_check 中都不要使用任何内部评分档位或分类标签。\n\n"
        "12. 专业词不是禁用词，但必须先点名、再翻译、再落到现实场景；例如写“空亡”时，要解释为事情容易落空、拖延或反复确认。\n"
        "13. content 不要出现“结构承接、可用空间、可用之处、现实承接感、底层结构、后段承接、结构封顶”等内部分析词。\n\n"
        f"{knowledge_block}"
    )

    user_prompt = (
        "请基于系统提示词中的判断规则，以及下面的锁定事实和内部检查结果，输出一个 JSON object。\n\n"
        "【locked_fields：这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence：可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "【direct_checks：内部参考，用于帮助你抓强信号；最终不要逐项照抄】\n"
        f"{_dump_json(direct_checks)}\n\n"
        "输出要求：\n"
        "- verdict：四类之一，必须和 locked_fields.verdict 一致。\n"
        "- content：一段话，直接说清楚长期使用意见和原因；必须写出用户能对照的长期使用场景。\n"
        "- elements_check：结构化对象，必须包含整体承接、宫门关系、四害、特殊组合、神星门、天干/地干、风险敏感方向、最终使用结论这八项，每项用一句话判断，并把专业层翻译成现实表现。\n"
        "- 用户主段落不要把专业词连续堆起来；如果写术语，必须紧跟生活化解释和现实场景。\n"
        "- 当前没有用户显式关注项，不要写“用户关注健康/稳定性”，只能写“盘面风险敏感方向”。\n"
        "- 最终只输出 JSON object。\n"
    )

    return system_prompt, user_prompt, json_example, locked


def validate_model_output(model_output: dict[str, Any]) -> tuple[bool, str]:
    verdict = str(model_output.get("verdict") or "").strip()
    content = str(model_output.get("content") or "").strip()
    elements_check = model_output.get("elements_check")

    if not verdict:
        return False, "missing_or_empty:verdict"
    if not content:
        return False, "missing_or_empty:content"
    if not isinstance(elements_check, dict):
        return False, "elements_check_must_be_object"
    for key in REQUIRED_ELEMENT_KEYS:
        if not str(elements_check.get(key) or "").strip():
            return False, f"missing_element:{key}"
    return True, "ok"


def render_stability_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> StabilityRenderResult:
    rules = load_rules()
    system_prompt, user_prompt, json_example, locked = build_stability_prompts(phone, gender, tone_pack=tone_pack, rules=rules)
    client = client or DeepSeekClient.from_env()

    try:
        response = client.chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.2,
            max_tokens=max_tokens,
            llm_scene="phone_qimen.stability",
            priority_class="foreground_core",
        )
        model_output = response.json_object()
        model_name = response.model or model
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR) from exc

    valid, reason = validate_model_output(model_output)
    if not valid:
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR) from ValueError(f"stability_invalid_output:{reason}")

    verdict = str(model_output["verdict"]).strip()
    if verdict != locked["verdict"]:
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR) from ValueError("stability_verdict_mismatch")

    public_output = _public_output(model_output)
    return StabilityRenderResult(
        verdict=str(public_output["verdict"]).strip(),
        content=str(public_output["content"]).strip(),
        elements_check=dict(public_output["elements_check"]),
        tone_pack=tone_pack,
        model_name=model_name,
    )


def render_stability_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> StabilityRenderResult:
    score_result = package.get("score_result")
    if not isinstance(score_result, dict):
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR)
    input_payload = score_result.get("input")
    if not isinstance(input_payload, dict):
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR)
    phone = str(input_payload.get("phone") or "").strip()
    gender = str(input_payload.get("gender") or "").strip()
    if not phone or not gender:
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR)
    return render_stability_from_phone(
        phone,
        gender,
        tone_pack=tone_pack,
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
    )


def stream_stability_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    score_result = package.get("score_result")
    if not isinstance(score_result, dict):
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR)
    input_payload = score_result.get("input")
    if not isinstance(input_payload, dict):
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR)
    phone = str(input_payload.get("phone") or "").strip()
    gender = str(input_payload.get("gender") or "").strip()
    if not phone or not gender:
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR)

    rules = load_rules()
    system_prompt, user_prompt, json_example, locked = build_stability_prompts(phone, gender, tone_pack=tone_pack, rules=rules)
    messages = build_messages(
        system_prompt=f"{system_prompt.rstrip()}\n\n{build_json_stream_instruction(json_example)}",
        user_prompt=user_prompt,
    )

    raw_content = ""
    emitted_fields = {"verdict": "", "content": ""}
    model_name = model
    try:
        client = client or DeepSeekClient.from_env()
        yield {"event": "status", "data": {"message": "正在生成长期使用建议"}}
        for chunk in client.stream_chat(
            messages,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.2,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            llm_scene="phone_qimen.stability",
            priority_class="foreground_core",
            user_id=user_id,
            request_id=request_id,
        ):
            if chunk.raw.get("model"):
                model_name = str(chunk.raw.get("model") or model_name)
            if not chunk.content_delta:
                continue
            raw_content += chunk.content_delta
            for field in ("verdict", "content"):
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

        model_output = loads_streamed_json_object(raw_content)
        valid, reason = validate_model_output(model_output)
        if not valid:
            raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR) from ValueError(f"stability_invalid_output:{reason}")
        if str(model_output["verdict"]).strip() != locked["verdict"]:
            raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR) from ValueError("stability_verdict_mismatch")

        public_output = _public_output(model_output)
        result = StabilityRenderResult(
            verdict=str(public_output["verdict"]).strip(),
            content=str(public_output["content"]).strip(),
            elements_check=dict(public_output["elements_check"]),
            tone_pack=tone_pack,
            model_name=model_name,
        )
        yield {"event": "result", "data": {"stability": result.to_dict(), "model_name": result.model_name}}
    except Exception as exc:
        if isinstance(exc, DeepSeekAPIError):
            raise
        raise DeepSeekAPIError(DEEPSEEK_STABILITY_ERROR) from exc


def _locked_fields(score_result: dict[str, Any]) -> dict[str, Any]:
    stability = score_result["dimensions"]["stability"]
    harms = score_result["features"]["harms"]
    patterns = score_result["features"]["patterns"]
    board = score_result["board"]
    scoring = stability["components"]
    risks = stability["risks"]
    caps = stability["caps"]
    return {
        "verdict": _pick_verdict(stability, score_result),
        "score": stability["score"],
        "structural_cap": caps["structural_cap"],
        "structural_cap_reasons": caps["applied"],
        "high_risk_pairs": risks["high_risk_pairs"],
        "components": scoring,
        "board": {
            "last7": board["last7"],
            "digits": board["digits"],
            "symbols": board["symbols"],
        },
        "features": {
            "palace_door_relation": score_result["features"]["palace_door_relation"],
            "stem_pair_relation": score_result["features"]["stem_pair_relation"],
            "harms": harms,
            "patterns": patterns,
            "edge_flags": score_result["features"]["edge_flags"],
        },
        "sensitive_topics": _sensitive_topics(score_result),
    }


def _evidence_fields(score_result: dict[str, Any]) -> dict[str, Any]:
    stability = score_result["dimensions"]["stability"]
    return {
        "score": stability["score"],
        "components": stability["components"],
        "risks": stability["risks"],
        "caps": stability["caps"],
        "features": score_result["features"],
        "board": score_result["board"],
        "summary": score_result["summary"],
    }


def _direct_checks(score_result: dict[str, Any]) -> list[dict[str, Any]]:
    stability = score_result["dimensions"]["stability"]
    features = score_result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    board = score_result["board"]
    sensitive_topics = _sensitive_topics(score_result)
    checks: list[dict[str, Any]] = [
        {
            "name": "整体承接",
            "fact": f"{stability['score']}分",
            "meaning": "先看这个号能不能长期接得住。",
            "weight": "high",
        },
        {
            "name": "宫门关系",
            "fact": _label(RELATION_LABELS, features["palace_door_relation"]),
            "meaning": "宫门关系决定底盘和现实动作是不是顺接。",
            "weight": "high",
        },
        {
            "name": "四害",
            "fact": "；".join(
                [
                    f"空亡:{_humanize_harm(harms['emptiness'], harms['emptiness_layers'], LAYER_LABELS)}",
                    f"门迫:{_humanize_harm(harms['door_pressure'], [], LAYER_LABELS)}",
                    f"入墓:{_humanize_harm(harms['tomb'], harms['tomb_layers'], LAYER_LABELS)}",
                    f"击刑:{_humanize_harm(harms['punishment_hit'], harms['punishment_layers'], LAYER_LABELS)}",
                ]
            ),
            "meaning": "四害决定长期使用会不会持续消耗。",
            "weight": "high",
        },
        {
            "name": "特殊组合",
            "fact": "、".join(_label(PATTERN_LABELS, item) for item in patterns["detected"]) or "无",
            "meaning": "特殊组合会放大或改写长期体验。",
            "weight": "high",
        },
        {
            "name": "神星门",
            "fact": f"{board['symbols']['god']} / {board['symbols']['star']} / {board['symbols']['door']}",
            "meaning": "神星门决定气质、执行和长期使用感。",
            "weight": "high",
        },
        {
            "name": "天干/地干",
            "fact": features["stem_pair_relation"],
            "meaning": "后段收口和长期沉淀是否顺。",
            "weight": "high",
        },
        {
            "name": "风险敏感方向",
            "fact": "、".join(sensitive_topics) or "无明显风险敏感方向",
            "meaning": "这些是由稳定性维度分识别出的弱项方向，不代表用户显式关注。",
            "weight": "medium",
        },
        {
            "name": "最终使用结论",
            "fact": _pick_verdict(stability, score_result),
            "meaning": "最终建议必须与 verdict 一致。",
            "weight": "high",
        },
    ]
    return checks


def _pick_verdict(stability: dict[str, Any], score_result: dict[str, Any]) -> str:
    score = int(stability["score"])
    harms = score_result["features"]["harms"]
    patterns = score_result["features"]["patterns"]
    cap_reasons = set(stability["caps"]["applied"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    severe_patterns = {"pair_25_95", "pair_69_96", "stacked_27_99_92"}
    severe_pairs = severe_patterns.intersection(set(stability["risks"]["structural_cap_reasons"]))
    if score >= 85 and heavy_harm_count == 0 and not cap_reasons and not severe_pairs:
        return "适合长期使用"
    if score >= 72 and heavy_harm_count <= 1 and len(cap_reasons) <= 1:
        return "可以继续使用，但要注意使用方式"
    if score >= 60 or heavy_harm_count <= 2:
        return "不建议继续长期主用"
    return "不建议长期使用，请尽快调整"


def _sensitive_topics(score_result: dict[str, Any]) -> list[str]:
    summary = score_result.get("summary")
    if not isinstance(summary, dict):
        return []
    weak_topics = summary.get("weak_topics")
    if not isinstance(weak_topics, list):
        return []
    sensitive_topics: list[str] = []
    for item in weak_topics[:3]:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        topic_key = str(item[0]).strip()
        if not topic_key:
            continue
        topic_title = score_result["dimensions"].get(topic_key, {}).get("topic_title")
        if topic_title:
            sensitive_topics.append(str(topic_title))
    return sensitive_topics


def _public_output(model_output: dict[str, Any]) -> dict[str, Any]:
    elements_check = model_output.get("elements_check") if isinstance(model_output.get("elements_check"), dict) else {}
    return {
        "verdict": str(model_output.get("verdict") or "").strip(),
        "content": str(model_output.get("content") or "").strip(),
        "elements_check": {
            key: str(elements_check.get(key) or "").strip()
            for key in REQUIRED_ELEMENT_KEYS
        },
    }


def _dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
