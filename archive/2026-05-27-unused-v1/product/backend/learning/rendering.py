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


@dataclass
class LearningRenderResult:
    learning_level: str
    learning_type: str
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
            "learning_level": self.learning_level,
            "learning_type": self.learning_type,
            "core_judgement": self.core_judgement,
            "real_world_manifestation": self.real_world_manifestation,
            "advice": self.advice,
            "user_facing_paragraph": self.user_facing_paragraph,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
            "used_fallback": self.used_fallback,
            "raw_model_output": self.raw_model_output,
        }


def build_learning_prompts(payload: dict[str, Any], *, tone_pack: TonePack = "customer") -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_aspect_model_pack("learning", tone_pack)
    aspect_knowledge = load_aspect_knowledge("learning")
    taxonomy = load_aspect_taxonomy("learning")
    output_contract = load_aspect_output_contract("learning")
    style_examples = load_aspect_style_examples("learning")

    json_example = {
        "core_judgement": f"这个号码的学习状态属于{locked['level']}，整体更接近{locked['type']}，主因落在{locked['primary_driver']}。",
        "real_world_manifestation": locked["manifestation"],
        "user_facing_paragraph": "请在这里输出一段完整、自然、专业的中文学习说明。不要固定套话，要围绕这个号码在学习吸收、专注节奏、复盘沉淀和输出转化上的主矛盾去组织语言。",
    }

    system_prompt = (
        "你是易如反掌的学习解释渲染器，也是一位长期给人看手机号学习盘面的老师。\n"
        "你的职责不是改分，而是基于代码锁定事实和统一知识底座，写出自然、专业、但用户能听懂的学习说明。\n"
        "必须遵守这些硬规则：\n"
        "1. 不得修改或推翻 locked_fields。\n"
        "2. 不得新造学习档位、类型、分数或建议。\n"
        "3. mixed signals 只解释主矛盾，不改 code-locked 结论。\n"
        "4. 不要把空亡、门迫、入墓、击刑逐条抄成 checklist。\n"
        "5. 不要主动发明 evidence 里没有出现的特殊格局，尤其不要主动写出轮回格或蝴蝶双飞格。\n"
        "6. 不得把学习输出写成智商诊断、学历保证或宿命判断。\n"
        "7. 最终只输出一个 JSON object，不输出 Markdown，不输出额外说明。\n"
        "8. 段落里必须明确回答：如果用户看重学习效率、吸收能力和长期沉淀，这个号能不能继续长期使用。\n"
        "9. 语气要像真实分析者在解释这类学习结构，不像数据库字段拼接。"
    )

    user_prompt = (
        "请基于以下统一知识底座、学习判断知识、风格样例、输出合同、locked_fields 和 evidence，输出一个 JSON object。\n\n"
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【学习判断知识】\n"
        f"{aspect_knowledge}\n\n"
        "【学习 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【学习表达风格样例】\n"
        f"{style_examples}\n\n"
        "【locked_fields：这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence：可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "输出要求：\n"
        "- core_judgement：1 句话，点明学习结论、类型和主因。\n"
        "- real_world_manifestation：1 句话，贴近 locked_fields.manifestation，不跑题。\n"
        "- user_facing_paragraph：一段完整中文学习说明，要有厚度，至少把主判断、主矛盾、现实表现和长期建议讲清楚，不要写成固定模板。\n"
        "- 不要重复四害 checklist。\n"
        "- 不要写轮回格、蝴蝶双飞格。\n"
        "- 不要写成智商、学历或命运保证。\n"
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
    if _looks_like_four_harms_checklist(paragraph):
        return False, "paragraph_repeats_four_harms"
    if len(paragraph) < 140:
        return False, "paragraph_too_thin"
    if not _paragraph_reflects_usage_advice(paragraph, locked["advice"]):
        return False, "paragraph_missing_usage_advice"
    return True, "ok"


def render_learning_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> LearningRenderResult:
    payload = package["score_template"]["learning_payload"]
    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_learning_prompts(payload, tone_pack=tone_pack)

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

    return LearningRenderResult(
        learning_level=payload["level"],
        learning_type=payload["type"],
        core_judgement=str(raw_model_output["core_judgement"]).strip(),
        real_world_manifestation=str(raw_model_output["real_world_manifestation"]).strip(),
        advice=payload["advice"],
        user_facing_paragraph=str(raw_model_output["user_facing_paragraph"]).strip(),
        tone_pack=tone_pack,
        model_name=model_name,
        used_fallback=used_fallback,
        raw_model_output=raw_model_output,
    )


def render_learning_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> LearningRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_learning_from_package(
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
        return f"从学习承接力看，这个号码归在{payload['level']}，主轴更接近{payload['type']}，主要矛盾落在{payload['primary_driver']}。"
    return f"这个号码的学习状态属于{payload['level']}，整体更接近{payload['type']}，主因落在{payload['primary_driver']}。"


def _fallback_paragraph(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    watch_text = "、".join(item["area"] for item in payload.get("watch_areas", [])[:2]) or payload["primary_driver"]
    reasons = payload.get("deduction_reasons", [])[:2]
    extra = _fallback_gap_note(payload)
    verdict = _usage_verdict_sentence(payload["advice"])

    if tone_pack == "professional":
        paragraph = (
            f"从学习承接力看，这个号码归在{payload['level']}，主轴更接近{payload['type']}。"
            f"真正需要看的，是{payload['primary_driver']}与{payload['secondary_driver']}之间，能不能把吸收、节奏和长期沉淀一起接住。"
            f"{payload['manifestation']}{extra}当前更值得盯住的是{watch_text}，因为这些地方往往决定这类号码是越学越顺，还是前面学得进、后面留不住。"
        )
    else:
        paragraph = (
            f"这个号码看学习，当前落在{payload['level']}这一档，主轴更接近{payload['type']}，重点不只是聪不聪明，而是学进去的东西能不能稳稳吸收、复盘并长期留下来。"
            f"{payload['manifestation']}{extra}它更值得留意的是{watch_text}，这些地方往往就是现实里最容易把学习从有感觉，慢慢拖成有输入、没沉淀的位置。"
        )

    if reasons:
        paragraph = f"{paragraph}{' '.join(reason if reason.endswith('。') else f'{reason}。' for reason in reasons)}{verdict}"
    else:
        paragraph = f"{paragraph}{verdict}"
    return paragraph


def _fallback_gap_note(payload: dict[str, Any]) -> str:
    score_gap = int(payload.get("score_gap") or 0)
    if score_gap <= 0:
        return "这类盘面的吸收、专注和长期沉淀相对完整。"
    if score_gap <= 10:
        return "它不是学习有硬伤，而是边角位置还留着一点节奏或复盘上的回拉。"
    if score_gap <= 22:
        return "它的问题不在完全学不进，而在学习一拉长、一进到复盘和输出环节以后，更吃方法、节奏和留存质量。"

    reasons = [str(item).rstrip("。") for item in payload.get("deduction_reasons", []) if item]
    areas = [str(item.get("area")) for item in payload.get("watch_areas", []) if item.get("area")]
    if not reasons and not areas:
        return "它的主矛盾不在表面有没有学习力，而在学习越往后越容易发散、发沉或出现反复。"

    reason_text = "；".join(reasons[:2]) if reasons else "还有一些学习结构上的扣分"
    area_text = "、".join(areas[:2]) if areas else "关键学习场景"
    return f"它没有到满分，主要是因为{reason_text}。如果你当前特别看重{area_text}，这部分扣分就更值得正视。"


def _usage_verdict_sentence(advice: str) -> str:
    return str(advice).strip().rstrip("。") + "。"


def _paragraph_reflects_usage_advice(paragraph: str, advice: str) -> bool:
    advice_text = str(advice)
    positive_markers = ("长期使用", "继续长期使用", "继续使用", "坚持使用", "学习主用")
    negative_markers = ("不建议继续长期使用", "不建议当学习主用", "建议优先调整", "不建议继续用")

    if "坚持使用" in advice_text:
        return any(marker in paragraph for marker in ("坚持使用", "长期使用", "继续长期使用"))
    if any(marker in advice_text for marker in ("不建议继续长期使用", "不建议当学习主用", "优先调整")):
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
