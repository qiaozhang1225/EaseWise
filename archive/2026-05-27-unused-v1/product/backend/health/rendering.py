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
MEDICAL_DIAGNOSIS_TERMS = (
    "确诊",
    "癌症",
    "肿瘤",
    "糖尿病",
    "高血压",
    "抑郁症",
    "心脏病",
    "脑梗",
    "中风",
)
MEDICAL_DIAGNOSIS_BOUNDARY_PHRASES = (
    "不直接当病名或医学诊断",
    "不直接当医学诊断",
    "不直接当病名或诊断",
    "不直接当诊断",
    "不当病名或医学诊断",
    "不当医学诊断",
    "不是医学诊断",
    "不是诊断",
    "不做医学诊断",
    "不做诊断",
    "不作为医学诊断",
    "不作为诊断",
)


@dataclass
class HealthRenderResult:
    health_level: str
    health_type: str
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
            "health_level": self.health_level,
            "health_type": self.health_type,
            "core_judgement": self.core_judgement,
            "real_world_manifestation": self.real_world_manifestation,
            "advice": self.advice,
            "user_facing_paragraph": self.user_facing_paragraph,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
            "used_fallback": self.used_fallback,
            "raw_model_output": self.raw_model_output,
        }


def build_health_prompts(payload: dict[str, Any], *, tone_pack: TonePack = "customer") -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_aspect_model_pack("health", tone_pack)
    aspect_knowledge = load_aspect_knowledge("health")
    taxonomy = load_aspect_taxonomy("health")
    output_contract = load_aspect_output_contract("health")
    style_examples = load_aspect_style_examples("health")

    json_example = {
        "core_judgement": f"这个号码的健康状态属于{locked['level']}，整体更接近{locked['type']}，主因落在{locked['primary_driver']}。",
        "real_world_manifestation": locked["manifestation"],
        "user_facing_paragraph": "请在这里输出一段完整、自然、专业的中文健康说明。不要套固定起手，要围绕这个号码当前最突出的健康承压、节律或恢复矛盾去组织语言。",
    }

    system_prompt = (
        "你是易如反掌的健康解释渲染器，也是一个长期给人看手机号健康承载、精力消耗与恢复节律的老师。\n"
        "你的职责不是改分，而是基于代码锁定事实和统一知识底座，写出自然、专业、但用户能听明白的健康说明。\n"
        "必须遵守这些硬规则：\n"
        "1. 不得修改或推翻 locked_fields。\n"
        "2. 不得新造健康档位、类型、分数或建议。\n"
        "3. 如遇 mixed signals，只解释主矛盾，不改 code-locked 结论。\n"
        "4. 不要把空亡、门迫、入墓、击刑逐条抄成 checklist。\n"
        "5. 不要主动发明 evidence 里没有的特殊格局，也不要把合十格带进健康结论。\n"
        "6. 不得写具体病名、不得做医学诊断、不得把病象倾向写成医疗事实。\n"
        "7. 最终只输出一个 JSON object，不输出 Markdown，不输出额外说明。\n"
        "8. 段落里必须明确回答：如果用户看重睡眠、精力稳定、恢复力和少透支，这个号能不能继续长期使用。\n"
        "9. user_facing_paragraph 不必第一句就重复档位，可以从主矛盾、现实体感或敏感场景起笔。"
    )

    user_prompt = (
        "请基于以下统一知识底座、健康判断知识、风格样例、输出合同、locked_fields 和 evidence，输出一个 JSON object。\n\n"
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【健康判断知识】\n"
        f"{aspect_knowledge}\n\n"
        "【健康 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【健康表达风格样例】\n"
        f"{style_examples}\n\n"
        "【locked_fields｜这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence｜可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "输出要求：\n"
        "- core_judgement：1 句话，点明健康结论、类型和主因。\n"
        "- real_world_manifestation：1 句话，贴近 locked_fields.manifestation，不跑题。\n"
        "- user_facing_paragraph：1 段完整中文说明，要有厚度，但不要写成固定模板。\n"
        "- 可以自由选择切入角度：睡眠节律、精力承压、恢复续航、情绪内耗都可以。\n"
        "- 不要把所有号码都写成一样的开头。\n"
        "- 不要把四害写成 checklist。\n"
        "- 不要主动补出 evidence 里没有的特殊格局词。\n"
        "- 不要写具体病名、不要写医学诊断、不要把象意当成医疗结论。"
    )

    return system_prompt, user_prompt, json_example


def validate_model_output(payload: dict[str, Any], model_output: dict[str, Any]) -> tuple[bool, str]:
    locked = _locked_fields(payload)

    for key in ("core_judgement", "real_world_manifestation", "user_facing_paragraph"):
        if not str(model_output.get(key, "")).strip():
            return False, f"missing_{key}"

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
    if _mentions_medical_diagnosis_claim(combined):
        return False, "mentions_medical_diagnosis"
    if _looks_like_four_harms_checklist(paragraph):
        return False, "paragraph_repeats_four_harms"
    if len(paragraph) < 110:
        return False, "paragraph_too_thin"
    if not _paragraph_reflects_usage_advice(paragraph, locked["advice"]):
        return False, "paragraph_missing_usage_advice"
    return True, "ok"


def render_health_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> HealthRenderResult:
    payload = package["score_template"]["health_payload"]
    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_health_prompts(payload, tone_pack=tone_pack)

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

    return HealthRenderResult(
        health_level=payload["level"],
        health_type=payload["type"],
        core_judgement=str(raw_model_output["core_judgement"]).strip(),
        real_world_manifestation=str(raw_model_output["real_world_manifestation"]).strip(),
        advice=payload["advice"],
        user_facing_paragraph=str(raw_model_output["user_facing_paragraph"]).strip(),
        tone_pack=tone_pack,
        model_name=model_name,
        used_fallback=used_fallback,
        raw_model_output=raw_model_output,
    )


def render_health_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 950,
) -> HealthRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_health_from_package(
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
        return f"从健康承载和精力节律看，这个号码的健康状态落在{payload['level']}，主轴更接近{payload['type']}，主因落在{payload['primary_driver']}。"
    return f"这个号码当前的健康状态属于{payload['level']}，整体更接近{payload['type']}，主因落在{payload['primary_driver']}。"


def _fallback_paragraph(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    watch_text = "、".join(item["area"] for item in payload.get("watch_areas", [])[:2]) or payload["primary_driver"]
    reasons = payload.get("deduction_reasons", [])[:2]
    extra = _fallback_gap_note(payload)
    verdict = _usage_verdict_sentence(payload["advice"])

    if tone_pack == "professional":
        paragraph = (
            f"这个号码放在健康层面，当前落在{payload['level']}，主轴更接近{payload['type']}。{payload['manifestation']}"
            f"{extra}当前更值得盯住的是{watch_text}，因为这几层会直接决定精力承压、节律稳定和后续恢复是不是跟得上。"
        )
    else:
        paragraph = (
            f"这个号码看健康，当前属于{payload['level']}，主轴更接近{payload['type']}，重点不只是有没有一点累，而是这种累会不会越拖越久、越用越透。{payload['manifestation']}"
            f"{extra}它更值得留意的是{watch_text}，这些地方往往就是现实里最容易把睡眠、精力和恢复力拉下来的位置。"
        )

    boundary = "这里更适合把它理解成健康承载、精力消耗和恢复节律的倾向，不直接当病名或医学诊断。"
    if reasons:
        paragraph = f"{paragraph}{' '.join(reason if reason.endswith('。') else f'{reason}。' for reason in reasons)}{boundary}{verdict}"
    else:
        paragraph = f"{paragraph}{boundary}{verdict}"
    return paragraph


def _fallback_gap_note(payload: dict[str, Any]) -> str:
    score_gap = int(payload.get("score_gap", 0))
    if score_gap <= 0:
        return "这类盘面的承压感、节律感和恢复力相对完整。"
    if score_gap <= 12:
        return "它不是完全有问题，而是边角位置还留着一点节律或恢复上的回拉。"
    if score_gap <= 25:
        return "它的问题不在一下子爆出来，而在长期使用时更吃节律、恢复和消耗管理。"
    return "它的主矛盾不在表面一时扛不扛得住，而在久了以后更容易透支、反复和发沉。"


def _usage_verdict_sentence(advice: str) -> str:
    advice = advice.strip()
    return advice if advice.endswith("。") else f"{advice}。"


def _paragraph_reflects_usage_advice(paragraph: str, advice: str) -> bool:
    if "不建议" in advice:
        return "不建议" in paragraph or "不宜" in paragraph
    if "可以长期坚持使用" in advice:
        return "可以长期坚持使用" in paragraph or ("可以长期" in paragraph and "使用" in paragraph)
    if "可以继续长期使用" in advice:
        return "可以继续长期使用" in paragraph or ("可以继续" in paragraph and "长期" in paragraph)
    if "可以继续使用" in advice:
        return "可以继续使用" in paragraph or ("可以继续" in paragraph and "使用" in paragraph)
    return any(token in paragraph for token in ("长期使用", "继续使用", "不建议"))


def _mentions_medical_diagnosis_claim(text: str) -> bool:
    normalized = text
    for phrase in MEDICAL_DIAGNOSIS_BOUNDARY_PHRASES:
        normalized = normalized.replace(phrase, "")
    if any(term in normalized for term in MEDICAL_DIAGNOSIS_TERMS):
        return True
    return "诊断" in normalized


def _looks_like_four_harms_checklist(text: str) -> bool:
    if sum(term in text for term in FOUR_HARM_TERMS) >= 3:
        return True
    checklist_tokens = ("空亡无", "门迫无", "入墓无", "击刑无", "空亡有", "门迫有", "入墓有", "击刑有")
    return any(token in text for token in checklist_tokens)


def _dump_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
