from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from knowledge import (
    load_section_knowledge,
    load_section_model_pack,
    load_section_output_contract,
    load_section_style_examples,
    load_section_taxonomy,
    load_shared_foundation,
)
from product.backend.llm import DeepSeekAPIError, DeepSeekClient
from scoring.total_score.engine import load_rules, score_phone
from scoring.total_score.bundle import build_scoring_bundle

TonePack = Literal["customer", "professional"]
DEEPSEEK_PHONE_SUMMARY_ERROR = "DeepSeek 调用出现问题，手机号总评未生成。"
REQUIRED_ELEMENT_KEYS = ("宫", "门", "神", "星", "天干/地干", "特殊组合", "四害")


@dataclass
class PhoneSummaryRenderResult:
    title: str
    risk: str
    usage_guidance: str
    elements_check: dict[str, Any]
    tone_pack: TonePack
    model_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "risk": self.risk,
            "usage_guidance": self.usage_guidance,
            "elements_check": self.elements_check,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
        }


def build_phone_summary_prompts(payload: dict[str, Any], *, tone_pack: TonePack = "customer") -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    direct_checks = _direct_checks(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_section_model_pack("phone_summary", tone_pack)
    judgement_knowledge = load_section_knowledge("phone_summary")
    taxonomy = load_section_taxonomy("phone_summary")
    output_contract = load_section_output_contract("phone_summary")
    style_examples = load_section_style_examples("phone_summary")
    knowledge_block = (
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【手机号总评判断知识】\n"
        f"{judgement_knowledge}\n\n"
        "【手机号总评 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【手机号总评表达风格样例】\n"
        f"{style_examples}"
    )

    json_example = {
        "title": "这组号码能起势，但真正考验在落地时能不能稳住",
        "risk": "这个号不是没有亮点，而是亮点容易被后段的牵扯和风险层拖住。现实里常见的是看起来能推进、能接事，但一进入具体关系或执行环节，就容易出现反复、消耗或临门一脚差一点。",
        "usage_guidance": (
            "写作时请像直接看号一样，把最强的星、门、神、干支或特殊组合合起来判断，不要逐项复述字段。"
            "最终要让用户读完能感觉到：这个号在描述他过去使用时反复出现的状态。"
        ),
        "elements_check": {
            "宫": "一句话判断宫的底盘与大方向。",
            "门": "一句话判断门的现实动作和使用方式。",
            "神": "一句话判断神的气场和隐性状态。",
            "星": "一句话判断星的性格、气质或对象侧。",
            "天干/地干": "一句话判断后段格局、牵扯或应事。",
            "特殊组合": "一句话判断特殊组合带来的放大效应。",
            "四害": "一句话判断四害对现实的改写。",
        },
    }

    system_prompt = (
        "你是易如反掌的手机号总评渲染器，负责把代码锁定的盘面事实写成用户最终可见的总评。\n"
        "你的职责不是重算分数，也不是解释来源，更不是输出多余中间层。\n"
        "必须遵守这些硬规则：\n"
        "1. 最终只输出一个 JSON object，且只包含 title、risk、usage_guidance、elements_check。\n"
        "2. 不得修改或推翻 locked_fields。\n"
        "3. 不得把内部检查、内部备注、内部流程或任何来源痕迹写进最终输出。\n"
        "4. 不得出现任何资料来源、文档来源、内部来源或身份来源。\n"
        "5. risk 必须是一段话，控制在两到三句，讲清楚核心问题怎么落到现实里。\n"
        "6. usage_guidance 必须是一段话，要像一个有经验的人在直接判断号码，不要拆条，不要列表。\n"
        "7. usage_guidance 必须基于 elements_check 的七层判断综合成一段话；它不是 elements_check 的复制，但七层判断都要在最终段落里产生影响。\n"
        "8. title 只做一句判断式概括，不要写成摘要列表。\n"
        "9. 如果盘面是 mixed signals，只保留一个主轴和一个主矛盾，不要平均摊开。\n"
        "10. 可以从最强信号切入，但不得只围绕这一层展开。最终判断必须完成七层覆盖：宫定底盘和环境承接，门定现实动作和使用方式，神定气场和隐性助力，星定性格气质和对象侧，天干/地干定后段格局和内部牵扯，特殊组合定放大效应，四害定现实硬伤。\n"
        "11. 还要输出 elements_check，它必须分别包含对宫、门、神、星、天干/地干、特殊组合、四害的简短判断。\n"
        "12. 写作时要有主次：强信号深入写，弱信号自然带过；如果某层没有明显风险，也要体现它是助力、背景、放大层，还是无硬伤的稳定层。重点是合断，不是逐项查表。\n"
        "13. 风格要像一个懂盘的人在直接判断号码，而不是像表格说明书。\n\n"
        f"{knowledge_block}"
    )

    user_prompt = (
        "请基于系统提示词中的判断规则，以及下面的锁定事实和内部检查结果，输出一个 JSON object。\n\n"
        "【locked_fields：这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence：可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "【中间判断块：内部参考，用于帮助你抓强信号；最终不要出现字段名，不要逐项照抄】\n"
        f"{_dump_json(direct_checks)}\n\n"
        "输出要求：\n"
        "- title：一句话概括这个手机号，不要写成摘要。\n"
        "- risk：一段话，2-3 句，讲清楚号码暴露出的核心问题和现实落点。\n"
        "- usage_guidance：一段话，根据 knowledge 和盘面事实进行合断，必须让宫、门、神、星、天干/地干、特殊组合、四害七层判断都影响最终段落；不要求按固定顺序写，但不能只写其中一两层。\n"
        "- elements_check：结构化对象，必须包含宫、门、神、星、天干/地干、特殊组合、四害这七项，每项都用一句话做判断。\n"
        "- 最终只输出 JSON object。\n"
    )

    return system_prompt, user_prompt, json_example


def validate_model_output(payload: dict[str, Any], model_output: dict[str, Any]) -> tuple[bool, str]:
    required_fields = ("title", "risk", "usage_guidance")
    for field in required_fields:
        if not str(model_output.get(field) or "").strip():
            return False, f"missing_or_empty:{field}"

    elements_check = model_output.get("elements_check")
    if not isinstance(elements_check, dict):
        return False, "elements_check_must_be_object"
    for key in REQUIRED_ELEMENT_KEYS:
        if not str(elements_check.get(key) or "").strip():
            return False, f"missing_element:{key}"

    return True, "ok"


def render_phone_summary_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> PhoneSummaryRenderResult:
    score_template = package["score_template"]
    payload = score_template.get("phone_summary_facts") if isinstance(score_template.get("phone_summary_facts"), dict) else {}
    if not payload:
        raise DeepSeekAPIError(DEEPSEEK_PHONE_SUMMARY_ERROR)
    system_prompt, user_prompt, json_example = build_phone_summary_prompts(payload, tone_pack=tone_pack)

    model_name = model

    try:
        client = client or DeepSeekClient.from_env()
        response = client.chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.25,
            max_tokens=max_tokens,
        )
        model_output = response.json_object()
        model_name = response.model or model
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_PHONE_SUMMARY_ERROR) from exc

    valid, reason = validate_model_output(payload, model_output)
    if not valid:
        raise DeepSeekAPIError(DEEPSEEK_PHONE_SUMMARY_ERROR) from ValueError(f"phone_summary_invalid_output:{reason}")

    public_output = _public_output(model_output)

    return PhoneSummaryRenderResult(
        title=str(public_output["title"]).strip(),
        risk=str(public_output["risk"]).strip(),
        usage_guidance=str(public_output["usage_guidance"]).strip(),
        elements_check=dict(public_output["elements_check"]),
        tone_pack=tone_pack,
        model_name=model_name,
    )


def render_phone_summary_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> PhoneSummaryRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_phone_summary_from_package(
        package,
        tone_pack=tone_pack,
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
    )


def _locked_fields(payload: dict[str, Any]) -> dict[str, Any]:
    score_facts = payload["score_facts"]
    return {
        "score_band": payload["score_band"],
        "score_facts": score_facts,
        "board_basis": payload["board_basis"],
        "core_relations": payload["core_relations"],
    }


def _evidence_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "board_basis": payload["board_basis"],
        "score_facts": payload["score_facts"],
        "core_relations": payload["core_relations"],
        "technical_focus": payload["technical_focus"],
    }


def _direct_checks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    score_facts = payload["score_facts"]
    core = payload["core_relations"]
    checks: list[dict[str, Any]] = [
        {
            "name": "综合分",
            "fact": str(score_facts["final_score"]),
            "meaning": f"这张盘的总体底色已经定在 {payload['score_band']} 区间。",
            "weight": "medium",
        },
        {
            "name": "宫门关系",
            "fact": str(core["palace_door_relation"]),
            "meaning": "这一层决定大环境和现实动作是不是顺接。",
            "weight": "high",
        },
        {
            "name": "后两干关系",
            "fact": str(core["stem_pair_relation"]),
            "meaning": "这一层更像后段牵扯和内部受力情况。",
            "weight": "high",
        },
        {
            "name": "四害",
            "fact": "；".join([f"{key}:{value}" for key, value in core["four_harms"].items()]),
            "meaning": "四害是会直接改写现实表现的硬层，若为空则说明这层没有硬伤。",
            "weight": "high",
        },
        {
            "name": "特殊组合",
            "fact": "、".join([str(item) for item in core["pattern_flags"]]) or "无",
            "meaning": "特殊组合会放大主轴和风险，不是普通边角信息。",
            "weight": "high",
        },
        {
            "name": "封顶原因",
            "fact": "、".join([str(item) for item in core["structural_cap_reasons"]]) or "无",
            "meaning": "封顶原因限制上限，决定亮点能不能完整落地。",
            "weight": "high",
        },
    ]

    for item in payload.get("technical_focus", []):
        if not isinstance(item, dict):
            continue
        focus = str(item.get("focus") or "").strip()
        value = str(item.get("value") or "").strip()
        implication = str(item.get("implication") or "").strip()
        if not focus:
            continue
        checks.append(
            {
                "name": focus,
                "fact": value,
                "meaning": implication,
                "weight": "medium",
            }
        )

    return checks


def _public_output(model_output: dict[str, Any]) -> dict[str, Any]:
    elements_check = model_output.get("elements_check") if isinstance(model_output.get("elements_check"), dict) else {}
    return {
        "title": str(model_output.get("title") or "").strip(),
        "risk": str(model_output.get("risk") or "").strip(),
        "usage_guidance": str(model_output.get("usage_guidance") or "").strip(),
        "elements_check": {
            key: str(elements_check.get(key) or "").strip()
            for key in REQUIRED_ELEMENT_KEYS
        },
    }


def _dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
