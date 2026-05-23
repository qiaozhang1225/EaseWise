from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from knowledge import (
    load_aspect_knowledge,
    load_aspect_model_pack,
    load_aspect_output_contract,
    load_aspect_style_examples,
    load_aspect_taxonomy,
    load_shared_foundation,
)
from product.backend.llm import DeepSeekClient
from scoring.engine import load_rules, score_phone
from scoring.services.bundle_service import build_scoring_bundle

TonePack = Literal["customer", "professional"]

FOUR_HARM_TERMS = ("空亡", "门迫", "入墓", "击刑")
UNSUPPORTED_PATTERN_TERMS = ("轮回格", "蝴蝶双飞格")
HARD_DESTINY_TERMS = ("命中注定", "只能做", "天生只能", "只适合这一行")


@dataclass
class SuitableJobRenderResult:
    suitable_job_level: str
    suitable_job_type: str
    core_judgement: str
    real_world_manifestation: str
    advice: str
    user_facing_paragraph: str
    tone_pack: TonePack
    model_name: str
    used_fallback: bool
    raw_model_output: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "suitable_job_level": self.suitable_job_level,
            "suitable_job_type": self.suitable_job_type,
            "core_judgement": self.core_judgement,
            "real_world_manifestation": self.real_world_manifestation,
            "advice": self.advice,
            "user_facing_paragraph": self.user_facing_paragraph,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
            "used_fallback": self.used_fallback,
            "raw_model_output": self.raw_model_output,
        }


def build_suitable_job_prompts(payload: dict[str, Any], *, tone_pack: TonePack = "customer") -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_aspect_model_pack("suitable_job", tone_pack)
    aspect_knowledge = load_aspect_knowledge("suitable_job")
    taxonomy = load_aspect_taxonomy("suitable_job")
    output_contract = load_aspect_output_contract("suitable_job")
    style_examples = load_aspect_style_examples("suitable_job")

    json_example = {
        "core_judgement": f"这个号码的职业适配状态属于{locked['level']}，整体更接近{locked['type']}，主因落在{locked['primary_driver']}。",
        "real_world_manifestation": locked["manifestation"],
        "user_facing_paragraph": "请在这里输出一段完整、自然、专业的中文职业适配说明。不要固定套话，要围绕这个号码在岗位匹配、工作方式、平台环境和现实角色上的主矛盾去组织语言。",
    }

    system_prompt = (
        "你是易如反掌的适合职业解释渲染器，也是一位长期给人看手机号职业匹配盘面的老师。\n"
        "你的职责不是改分，而是基于代码锁定事实和统一知识底座，写出自然、专业、但用户能听懂的职业适配说明。\n"
        "必须遵守这些硬规则：\n"
        "1. 不得修改或推翻 locked_fields。\n"
        "2. 不得新造职业档位、类型、分数或建议。\n"
        "3. mixed signals 只解释主矛盾，不改 code-locked 结论。\n"
        "4. 不要把空亡、门迫、入墓、击刑逐条抄成 checklist。\n"
        "5. 不要主动发明 evidence 里没有出现的特殊格局，尤其不要主动写出轮回格或蝴蝶双飞格。\n"
        "6. 只能写成‘更适合/更匹配’的职业倾向，不得写成宿命论，不得写成‘你只能做某职业’。\n"
        "7. 最终只输出一个 JSON object，不输出 Markdown，不输出额外说明。\n"
        "8. 段落里必须明确回答：如果用户看重职业匹配、长期定位和少走弯路，这个号能不能继续长期使用。\n"
        "9. 语气要像真实分析者在解释岗位匹配，不像数据库字段拼接。"
    )

    user_prompt = (
        "请基于以下统一知识底座、职业适配判断知识、风格样例、输出合同、locked_fields 和 evidence，输出一个 JSON object。\n\n"
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【职业适配判断知识】\n"
        f"{aspect_knowledge}\n\n"
        "【职业适配 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【职业适配表达风格样例】\n"
        f"{style_examples}\n\n"
        "【locked_fields：这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence：可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "输出要求：\n"
        "- core_judgement：1 句话，点明职业适配结论、类型和主因。\n"
        "- real_world_manifestation：1 句话，贴近 locked_fields.manifestation，不跑题。\n"
        "- user_facing_paragraph：一段完整中文职业适配说明，要有厚度，至少把主判断、适合角色、限制或代价、现实工作场景和长期建议讲清楚，不要写成固定模板。\n"
        "- 不能写成‘只能做’‘命中注定’之类的宿命判断。\n"
        "- 不要重复四害 checklist。\n"
        "- 最终只输出 JSON object。"
    )
    return system_prompt, user_prompt, json_example


def validate_model_output(payload: dict[str, Any], model_output: dict[str, Any]) -> tuple[bool, str]:
    required_keys = {"core_judgement", "real_world_manifestation", "user_facing_paragraph"}
    if not required_keys.issubset(model_output):
        return False, "missing_required_keys"

    locked = _locked_fields(payload)
    core_judgement = str(model_output["core_judgement"]).strip()
    paragraph = str(model_output["user_facing_paragraph"]).strip()
    manifestation = str(model_output["real_world_manifestation"]).strip()
    combined = "\n".join((core_judgement, manifestation, paragraph))

    if locked["level"] not in core_judgement:
        return False, "core_judgement_missing_locked_level"
    if locked["type"] not in core_judgement:
        return False, "core_judgement_missing_locked_type"
    if any(term in combined for term in UNSUPPORTED_PATTERN_TERMS):
        return False, "mentions_unsupported_pattern"
    if any(term in combined for term in HARD_DESTINY_TERMS):
        return False, "uses_hard_destiny_claim"
    if _looks_like_four_harms_checklist(paragraph):
        return False, "paragraph_repeats_four_harms"
    if len(paragraph) < 140:
        return False, "paragraph_too_thin"
    if not _paragraph_reflects_usage_advice(paragraph, locked["advice"]):
        return False, "paragraph_missing_usage_advice"
    return True, "ok"


def render_suitable_job_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> SuitableJobRenderResult:
    payload = package["score_template"]["suitable_job_payload"]
    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_suitable_job_prompts(payload, tone_pack=tone_pack)

    raw_model_output: dict[str, Any] | None = None
    used_fallback = False
    model_name = model

    try:
        response = client.chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_example=json_example,
            model=model,
            thinking_enabled=thinking_enabled,
            temperature=0.3,
            max_tokens=max_tokens,
        )
        raw_model_output = response.json_object()
        model_name = response.model or model
        valid, _reason = validate_model_output(payload, raw_model_output)
        if not valid:
            raw_model_output = None
            used_fallback = True
    except Exception:
        raw_model_output = None
        used_fallback = True

    if raw_model_output is None:
        raw_model_output = {
            "core_judgement": _fallback_core_judgement(payload, tone_pack=tone_pack),
            "real_world_manifestation": payload["manifestation"],
            "user_facing_paragraph": _fallback_paragraph(payload, tone_pack=tone_pack),
        }

    return SuitableJobRenderResult(
        suitable_job_level=payload["level"],
        suitable_job_type=payload["type"],
        core_judgement=str(raw_model_output["core_judgement"]).strip(),
        real_world_manifestation=str(raw_model_output["real_world_manifestation"]).strip(),
        advice=payload["advice"],
        user_facing_paragraph=str(raw_model_output["user_facing_paragraph"]).strip(),
        tone_pack=tone_pack,
        model_name=model_name,
        used_fallback=used_fallback,
        raw_model_output=raw_model_output,
    )


def render_suitable_job_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> SuitableJobRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_suitable_job_from_package(
        package,
        tone_pack=tone_pack,
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
    )


def _locked_fields(payload: dict[str, Any]) -> dict[str, Any]:
    facts = payload["facts"]
    return {
        "level": payload["level"],
        "type": payload["type"],
        "primary_driver": payload["primary_driver"],
        "secondary_driver": payload["secondary_driver"],
        "manifestation": payload["manifestation"],
        "advice": payload["advice"],
        "score_gap": payload["score_gap"],
        "watch_areas": payload.get("watch_areas", []),
        "deduction_reasons": payload.get("deduction_reasons", []),
        "score_after_structural_cap": facts["score_after_structural_cap"],
        "confidence": facts["confidence"],
    }


def _evidence_fields(payload: dict[str, Any]) -> dict[str, Any]:
    facts = payload["facts"]
    return {
        "palace_door_relation": facts["palace_door_relation"],
        "stem_pair_relation": facts["stem_pair_relation"],
        "door": facts["door"],
        "star": facts["star"],
        "god": facts["god"],
        "door_personality": facts.get("door_personality"),
        "god_tone": facts.get("god_tone"),
        "four_harms": facts["four_harms"],
        "pattern_flags": facts["pattern_flags"],
        "risk_pairs": facts["risk_pairs"],
        "structural_cap_reasons": facts["structural_cap_reasons"],
        "tags": facts["tags"],
    }


def _fallback_core_judgement(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    if tone_pack == "professional":
        return f"从职业适配看，这个号码归在{payload['level']}，主轴更接近{payload['type']}，主要矛盾落在{payload['primary_driver']}。"
    return f"这个号码的职业适配状态属于{payload['level']}，整体更接近{payload['type']}，主因落在{payload['primary_driver']}。"


def _fallback_paragraph(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    watch_text = "、".join(item["area"] for item in payload.get("watch_areas", [])[:2]) or payload["primary_driver"]
    reasons = payload.get("deduction_reasons", [])[:2]
    extra = _fallback_gap_note(payload)
    verdict = _usage_verdict_sentence(payload["advice"])

    if tone_pack == "professional":
        paragraph = (
            f"从职业适配看，这个号码归在{payload['level']}，主轴更接近{payload['type']}。"
            f"真正需要看的，是{payload['primary_driver']}与{payload['secondary_driver']}之间，能不能把岗位发挥、平台承接和长期定位一起接住。"
            f"{payload['manifestation']}{extra}当前更值得盯住的是{watch_text}，因为这些地方往往决定它是越做越顺，还是角色一换、环境一变，优势就开始打折。"
        )
    else:
        paragraph = (
            f"这个号码看适合职业，当前落在{payload['level']}这一档，主轴更接近{payload['type']}，重点不只是有没有能力，而是这种能力放到什么岗位、什么分工里更容易稳定发挥。"
            f"{payload['manifestation']}{extra}它更值得留意的是{watch_text}，这些地方往往就是现实里最容易把职业优势放大，或者把岗位代价拉出来的位置。"
        )

    if reasons:
        paragraph = f"{paragraph}{' '.join(reason if reason.endswith('。') else f'{reason}。' for reason in reasons)}{verdict}"
    else:
        paragraph = f"{paragraph}{verdict}"
    return paragraph


def _fallback_gap_note(payload: dict[str, Any]) -> str:
    score_gap = int(payload.get("score_gap") or 0)
    if score_gap <= 0:
        return "这类盘面的岗位匹配、发挥方式和长期定位相对完整。"
    if score_gap <= 10:
        return "它不是职业方向有硬伤，而是边角位置还留着一点分工或环境上的回拉。"
    if score_gap <= 22:
        return "它的问题不在完全做不了，而在角色一深入、岗位一拉长以后，更吃平台、边界和长期落点。"

    reasons = [str(item).rstrip("。") for item in payload.get("deduction_reasons", []) if item]
    areas = [str(item.get("area")) for item in payload.get("watch_areas", []) if item.get("area")]
    if not reasons and not areas:
        return "它的主矛盾不在表面有没有能力，而在角色和环境一不对路时，职业成本会慢慢浮出来。"

    reason_text = "；".join(reasons[:2]) if reasons else "还有一些职业结构上的扣分"
    area_text = "、".join(areas[:2]) if areas else "关键岗位场景"
    return f"它没有到满分，主要是因为{reason_text}。如果你当前特别看重{area_text}，这部分扣分就更值得正视。"


def _usage_verdict_sentence(advice: str) -> str:
    return str(advice).strip().rstrip("。") + "。"


def _paragraph_reflects_usage_advice(paragraph: str, advice: str) -> bool:
    advice_text = str(advice)
    positive_markers = ("长期使用", "继续长期使用", "继续使用", "坚持使用", "职业适配主用")
    negative_markers = ("不建议继续长期使用", "不建议当职业适配主用", "建议优先调整", "不建议继续用")

    if "坚持使用" in advice_text:
        return any(marker in paragraph for marker in ("坚持使用", "长期使用", "继续长期使用"))
    if any(marker in advice_text for marker in ("不建议继续长期使用", "不建议当职业适配主用", "优先调整")):
        return any(marker in paragraph for marker in negative_markers)
    if any(marker in advice_text for marker in ("长期使用", "继续长期使用", "继续使用")):
        return any(marker in paragraph for marker in positive_markers)
    return True


def _looks_like_four_harms_checklist(text: str) -> bool:
    hit_terms = [term for term in FOUR_HARM_TERMS if term in text]
    if len(hit_terms) < 3:
        return False
    checklist_markers = ("有", "无", "：", ":", "、")
    return any(marker in text for marker in checklist_markers)


def _dump_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
