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


@dataclass
class CareerRenderResult:
    career_level: str
    career_type: str
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
            "career_level": self.career_level,
            "career_type": self.career_type,
            "core_judgement": self.core_judgement,
            "real_world_manifestation": self.real_world_manifestation,
            "advice": self.advice,
            "user_facing_paragraph": self.user_facing_paragraph,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
            "used_fallback": self.used_fallback,
            "raw_model_output": self.raw_model_output,
        }


def build_career_prompts(payload: dict[str, Any], *, tone_pack: TonePack = "customer") -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_aspect_model_pack("career", tone_pack)
    aspect_knowledge = load_aspect_knowledge("career")
    taxonomy = load_aspect_taxonomy("career")
    output_contract = load_aspect_output_contract("career")
    style_examples = load_aspect_style_examples("career")

    json_example = {
        "core_judgement": f"这个号码的事业状态属于{locked['level']}，整体更接近{locked['type']}，主因落在{locked['primary_driver']}。",
        "real_world_manifestation": locked["manifestation"],
        "user_facing_paragraph": "请在这里输出一段完整、自然、专业的中文事业说明。不要套固定起手，要根据这个号码最突出的事业矛盾来组织语言。",
    }

    system_prompt = (
        "你是易如反掌的事业解释渲染器，也是一个长期给人看手机号事业盘面的老师。\n"
        "你的职责不是改分，而是基于代码锁定事实和统一知识底座，写出自然、专业、但又让用户能听明白的事业说明。\n"
        "必须遵守这些硬规则：\n"
        "1. 不得修改或推翻 locked_fields。\n"
        "2. 不得新造事业档位、类型、分数或建议。\n"
        "3. 如遇 mixed signals，只解释主矛盾，不改 code-locked 结论。\n"
        "4. 不要把空亡、门迫、入墓、击刑逐条抄成 checklist。\n"
        "5. 最终只输出一个 JSON object，不输出 Markdown，不输出额外说明。\n"
        "6. 要点出真正的卡点，而不是像数据库字段拼接。\n"
        "7. 不要默认总用“不是不能……而是……”“问题不在……而在……”或“如果你当前正处在……”这类固定起手；只有真的适合时才使用。\n"
        "8. 你可以从盘面主轴、最疼的扣分、最敏感的事业场景、长期使用方式中的任何一个角度起笔。"
    )

    user_prompt = (
        "请基于以下统一知识底座、方面知识、风格样例、输出合同、locked_fields 和 evidence，输出一个 JSON object。\n\n"
        "【共享知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【事业判断知识】\n"
        f"{aspect_knowledge}\n\n"
        "【事业 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【事业表达风格样例】\n"
        f"{style_examples}\n\n"
        "【locked_fields｜这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence｜可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "输出要求：\n"
        "- core_judgement：1 句话，点明事业结论和主因。\n"
        "- real_world_manifestation：1 句话，贴近 locked_fields.manifestation，不跑题。\n"
        "- user_facing_paragraph：1 段完整中文说明，要有厚度，但不要写成同一套公式作文。\n"
        "- 可以自由选择切入角度：主轴切入、场景切入、扣分价值切入、长期使用切入都可以。\n"
        "- 不要所有号码都用同一种起手，不要所有场景都机械带上升职、创业、项目推进、长期结果沉淀这四个词。\n"
        "- 不要把四害写成 checklist。\n"
        "- 必须在语义上体现 level、type、advice 的意思，但不要机械复述标签。\n"
        "- 如果 score_gap >= 12，请说明为什么没到满分，以及哪些事业场景更值得留意。\n"
        "- 场景选择优先贴近 watch_areas 和 deduction_reasons，只挑最 relevant 的 1-2 个场景展开，不要贪多。\n"
        "- 如果是高分，也要讲清楚为什么还能长期用，以及哪些边角扣分仍需留意。\n"
        "- 如果是低分，不要只说不宜硬冲，要讲清楚为什么更耗、耗在哪、什么任务更容易被放大。"
    )
    return system_prompt, user_prompt, json_example


def validate_model_output(payload: dict[str, Any], model_output: dict[str, Any]) -> tuple[bool, str]:
    required_fields = ("core_judgement", "real_world_manifestation", "user_facing_paragraph")
    for field in required_fields:
        if not str(model_output.get(field) or "").strip():
            return False, f"missing_or_empty:{field}"

    paragraph = str(model_output["user_facing_paragraph"]).strip()
    if _looks_like_four_harms_checklist(paragraph):
        return False, "paragraph_repeats_four_harms"

    locked = _locked_fields(payload)
    combined_text = f"{model_output['core_judgement']}\n{paragraph}"
    if locked["level"] not in combined_text:
        return False, "missing_locked_level"
    if locked["type"] not in combined_text and locked["primary_driver"] not in combined_text:
        return False, "missing_type_or_primary_driver"
    if len(paragraph) < 120:
        return False, "paragraph_too_thin"
    return True, "ok"


def render_career_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 900,
) -> CareerRenderResult:
    payload = package["score_template"]["career_payload"]
    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_career_prompts(payload, tone_pack=tone_pack)

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
            temperature=0.35,
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

    return CareerRenderResult(
        career_level=payload["level"],
        career_type=payload["type"],
        core_judgement=str(raw_model_output["core_judgement"]).strip(),
        real_world_manifestation=str(raw_model_output["real_world_manifestation"]).strip(),
        advice=payload["advice"],
        user_facing_paragraph=str(raw_model_output["user_facing_paragraph"]).strip(),
        tone_pack=tone_pack,
        model_name=model_name,
        used_fallback=used_fallback,
        raw_model_output=raw_model_output,
    )


def render_career_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 900,
) -> CareerRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_career_from_package(
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
        "score_gap": payload.get("score_gap", 0),
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
        "four_harms": facts["four_harms"],
        "pattern_flags": facts["pattern_flags"],
        "risk_pairs": facts["risk_pairs"],
        "structural_cap_reasons": facts["structural_cap_reasons"],
        "tags": facts["tags"],
    }


def _fallback_core_judgement(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    if tone_pack == "professional":
        return f"从事业盘面看，这个号码归在{payload['level']}，主轴更接近{payload['type']}，主要矛盾落在{payload['primary_driver']}。"
    return f"这个号码的事业状态属于{payload['level']}，整体更接近{payload['type']}，主因落在{payload['primary_driver']}。"


def _fallback_paragraph(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    extra = _fallback_gap_note(payload)
    advice_clause = _advice_clause(payload["advice"])
    if tone_pack == "professional":
        base = (
            f"从事业盘面看，这个号码归在{payload['level']}，主轴更接近{payload['type']}。"
            f"它的问题不一定在开局有没有机会，而在{payload['primary_driver']}与{payload['secondary_driver']}之间能不能长期承接。"
            f"现实里更容易表现成{payload['manifestation']}"
            f"因此这类号码在事业上{advice_clause}"
        )
        return f"{base}{extra}"

    base = (
        f"这个号码在事业上属于{payload['level']}。从奇门盘面看，它更接近{payload['type']}，问题不一定在表面有没有机会，"
        f"而在{payload['primary_driver']}能不能把事业推进长期接住。现实里更容易表现成{payload['manifestation']}"
        f"如果你当前正处在升职、创业、项目推进或长期结果沉淀阶段，这部分波动会更容易被放大，因此{advice_clause}"
    )
    return f"{base}{extra}"


def _fallback_gap_note(payload: dict[str, Any]) -> str:
    score_gap = int(payload.get("score_gap") or 0)
    if score_gap < 12:
        return ""

    reasons = [str(item).rstrip("。") for item in payload.get("deduction_reasons", []) if item]
    areas = [str(item.get("area")) for item in payload.get("watch_areas", []) if item.get("area")]
    scenarios = [str(item.get("scenario")) for item in payload.get("watch_areas", []) if item.get("scenario")]
    if not reasons and not areas:
        return ""

    reason_text = "；".join(reasons[:2]) if reasons else "还有一些结构性扣分点"
    area_text = "、".join(areas[:2]) if areas else "关键节点"
    if scenarios:
        scenario_text = "；".join(s.rstrip("。") for s in scenarios[:2])
        return f" 它没有到满分，主要是因为{reason_text}。如果你当前特别看重{area_text}，这些场景里会更明显：{scenario_text}。"
    return f" 它没有到满分，主要是因为{reason_text}。如果你当前特别看重{area_text}，这部分扣分就更值得留意。"


def _advice_clause(advice: str) -> str:
    cleaned = str(advice).strip()
    if cleaned.startswith("建议"):
        return cleaned
    return f"建议{cleaned}"


def _looks_like_four_harms_checklist(text: str) -> bool:
    hit_terms = [term for term in FOUR_HARM_TERMS if term in text]
    if len(hit_terms) < 3:
        return False
    checklist_markers = ("有", "无", "：", ":", "、")
    return any(marker in text for marker in checklist_markers)


def _dump_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
