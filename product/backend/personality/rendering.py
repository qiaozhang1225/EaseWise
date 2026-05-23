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
UNSUPPORTED_PATTERN_TERMS = ("合十格", "轮回格", "蝴蝶双飞格")


@dataclass
class PersonalityRenderResult:
    personality_level: str
    personality_type: str
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
            "personality_level": self.personality_level,
            "personality_type": self.personality_type,
            "core_judgement": self.core_judgement,
            "real_world_manifestation": self.real_world_manifestation,
            "advice": self.advice,
            "user_facing_paragraph": self.user_facing_paragraph,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
            "used_fallback": self.used_fallback,
            "raw_model_output": self.raw_model_output,
        }


def build_personality_prompts(
    payload: dict[str, Any], *, tone_pack: TonePack = "customer"
) -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_aspect_model_pack("personality", tone_pack)
    aspect_knowledge = load_aspect_knowledge("personality")
    taxonomy = load_aspect_taxonomy("personality")
    output_contract = load_aspect_output_contract("personality")
    style_examples = load_aspect_style_examples("personality")

    json_example = {
        "core_judgement": f"这个号码的性格状态属于{locked['level']}，整体更接近{locked['type']}，主因落在{locked['primary_driver']}。",
        "real_world_manifestation": locked["manifestation"],
        "user_facing_paragraph": "请在这里输出一段完整、自然、专业的中文性格说明。不要写成心理测试标签清单，要围绕这个号码最突出的气质主轴、表达方式和长期使用感去组织语言。",
    }

    system_prompt = (
        "你是易如反掌的性格解释渲染器，也是一位长期给人看手机号气质状态的分析者。\n"
        "你的职责不是改分，而是基于代码锁定事实和统一知识底座，写出自然、专业、但用户能听懂的性格说明。\n"
        "必须遵守这些硬规则：\n"
        "1. 不得修改或推翻 locked_fields。\n"
        "2. 不得新造性格档位、类型、分数或建议。\n"
        "3. mixed signals 只解释主矛盾，不改 code-locked 结论。\n"
        "4. 不要把空亡、门迫、入墓、击刑逐条抄成 checklist。\n"
        "5. 不要把性格写成心理测试标签堆叠，也不要主动发明 evidence 里没有的特殊格局。\n"
        "6. 最终只输出一个 JSON object，不输出 Markdown，不输出额外说明。\n"
        "7. 段落里必须明确回答：如果用户看重对外气质、表达状态和长期舒服度，这个号适不适合继续长期使用。\n"
        "8. 语气要像真实分析者在解释一个号码会把人带成什么状态，不像数据库字段拼接。"
    )

    user_prompt = (
        "请基于以下统一知识底座、性格判断知识、风格样例、输出合同、locked_fields 和 evidence，输出一个 JSON object。\n\n"
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【性格判断知识】\n"
        f"{aspect_knowledge}\n\n"
        "【性格 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【性格表达风格样例】\n"
        f"{style_examples}\n\n"
        "【locked_fields：这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence：可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "输出要求：\n"
        "- core_judgement：1 句话，点明性格结论、类型和主因。\n"
        "- real_world_manifestation：1 句话，贴近 locked_fields.manifestation。\n"
        "- user_facing_paragraph：1 段完整中文说明，要有厚度，但不要写成 checklist 或人格测试。\n"
        "- 必须明确体现 level、type、advice 的意思。\n"
        "- 如果 score_gap >= 12，请说明没到满分主要扣在哪里。\n"
        "- 如果 watch_areas 很集中，优先围绕最 relevant 的 1-2 个现实场景展开。"
    )

    return system_prompt, user_prompt, json_example


def validate_model_output(payload: dict[str, Any], model_output: dict[str, Any]) -> tuple[bool, str]:
    required_fields = ("core_judgement", "real_world_manifestation", "user_facing_paragraph")
    for field in required_fields:
        if not str(model_output.get(field) or "").strip():
            return False, f"missing_or_empty:{field}"

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
    if len(paragraph) < 110:
        return False, "paragraph_too_thin"
    if not _paragraph_reflects_usage_advice(paragraph, locked["advice"]):
        return False, "paragraph_missing_usage_advice"
    return True, "ok"


def render_personality_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> PersonalityRenderResult:
    payload = package["score_template"]["personality_payload"]
    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_personality_prompts(payload, tone_pack=tone_pack)

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

    return PersonalityRenderResult(
        personality_level=payload["level"],
        personality_type=payload["type"],
        core_judgement=str(raw_model_output["core_judgement"]).strip(),
        real_world_manifestation=str(raw_model_output["real_world_manifestation"]).strip(),
        advice=payload["advice"],
        user_facing_paragraph=str(raw_model_output["user_facing_paragraph"]).strip(),
        tone_pack=tone_pack,
        model_name=model_name,
        used_fallback=used_fallback,
        raw_model_output=raw_model_output,
    )


def render_personality_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> PersonalityRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_personality_from_package(
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
        "door_personality": facts["door_personality"],
        "god_tone": facts["god_tone"],
        "four_harms": facts["four_harms"],
        "pattern_flags": facts["pattern_flags"],
        "risk_pairs": facts["risk_pairs"],
        "structural_cap_reasons": facts["structural_cap_reasons"],
        "tags": facts["tags"],
    }


def _fallback_core_judgement(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    if tone_pack == "professional":
        return f"从性格呈现看，这个号码归在{payload['level']}，主轴更接近{payload['type']}，主要矛盾落在{payload['primary_driver']}。"
    return f"这个号码的性格状态属于{payload['level']}，整体更接近{payload['type']}，主因落在{payload['primary_driver']}。"


def _fallback_paragraph(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    extra = _fallback_gap_note(payload)
    verdict = _usage_verdict_sentence(payload["advice"])

    if tone_pack == "professional":
        base = (
            f"从性格呈现看，这个号码归在{payload['level']}，主轴更接近{payload['type']}。"
            f"真正需要看的，不只是个性强不强，而是{payload['primary_driver']}和{payload['secondary_driver']}之间，"
            f"能不能把这种气质用一种省力、顺手的方式带出来。"
            f"现实里更容易表现成{payload['manifestation']}"
            f"结论上，{verdict}"
        )
        return f"{base}{extra}"

    base = (
        f"这个号码放在性格上，主轴落在{payload['level']}这一档，更接近{payload['type']}。"
        f"它更怕的不是没个性，而是{payload['primary_driver']}这一层如果用得不顺，"
        f"就容易把人带进紧绷、别扭或内耗里。"
        f"现实里通常会表现成{payload['manifestation']}"
        f"如果回到长期使用这个问题上，{verdict}"
    )
    return f"{base}{extra}"


def _fallback_gap_note(payload: dict[str, Any]) -> str:
    score_gap = int(payload.get("score_gap") or 0)
    if score_gap < 12:
        return ""

    reasons = [str(item).rstrip("。") for item in payload.get("deduction_reasons", []) if item]
    areas = [str(item.get("area")) for item in payload.get("watch_areas", []) if item.get("area")]
    if not reasons and not areas:
        return ""

    reason_text = "；".join(reasons[:2]) if reasons else "还有一些性格结构上的扣分"
    area_text = "、".join(areas[:2]) if areas else "关键相处场景"
    return f" 它没有到满分，主要是因为{reason_text}。如果你当前特别看重{area_text}，这部分扣分就会更值得重视。"


def _usage_verdict_sentence(advice: str) -> str:
    return str(advice).strip().rstrip("。") + "。"


def _paragraph_reflects_usage_advice(paragraph: str, advice: str) -> bool:
    advice_text = str(advice)
    positive_markers = ("长期使用", "继续长期使用", "继续使用", "坚持使用")
    negative_markers = ("不建议继续长期使用", "不建议长期硬扛", "建议优先调整", "不建议继续用")

    if "坚持使用" in advice_text:
        return any(marker in paragraph for marker in ("坚持使用", "长期使用", "继续长期使用"))
    if any(marker in advice_text for marker in ("不建议继续长期使用", "不建议长期硬扛", "优先调整")):
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
