from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Literal

from knowledge import (
    load_aspect_section_knowledge,
    load_aspect_section_model_pack,
    load_aspect_section_output_contract,
    load_aspect_section_style_examples,
    load_aspect_section_taxonomy,
    load_section_knowledge,
    load_shared_foundation,
)
from product.backend.llm import DeepSeekAPIError, DeepSeekClient
from scoring.dimension_score_v3 import score_phone_dimensions_v3
from scoring.engine import load_rules
from scoring.payloads.shared import CAP_REASON_LABELS, EDGE_FLAG_LABELS, PATTERN_LABELS, RELATION_LABELS

TonePack = Literal["customer", "professional"]

DEEPSEEK_ASPECT_V2_ERROR = "DeepSeek 调用出现问题，专项结果未生成。"

ASPECT_V2_SPECS: list[dict[str, str]] = [
    {"aspect_key": "career", "title": "事业"},
    {"aspect_key": "wealth", "title": "财富"},
    {"aspect_key": "love", "title": "感情"},
    {"aspect_key": "health", "title": "健康"},
    {"aspect_key": "acad", "title": "学业"},
    {"aspect_key": "fortune", "title": "运势"},
    {"aspect_key": "investment", "title": "投资"},
    {"aspect_key": "travel", "title": "出行"},
    {"aspect_key": "social", "title": "人际"},
    {"aspect_key": "family", "title": "家庭"},
    {"aspect_key": "personality", "title": "性格"},
    {"aspect_key": "fengshui", "title": "风水"},
]

REQUIRED_ELEMENT_KEYS = ("宫", "门", "神", "星", "天干/地干", "特殊组合", "四害")


@dataclass
class AspectV2RenderResult:
    aspect_key: str
    title: str
    score: int
    content: str
    risk: str
    elements_check: dict[str, Any]
    tone_pack: TonePack
    model_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "aspect_key": self.aspect_key,
            "title": self.title,
            "score": self.score,
            "content": self.content,
            "risk": self.risk,
            "elements_check": self.elements_check,
        }


def render_aspects_v2_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> dict[str, AspectV2RenderResult]:
    rules = load_rules()
    package = {
        "score_result": score_phone_dimensions_v3(phone, gender, rules=rules),
        "score_template": {},
    }
    return render_aspects_v2_from_package(
        package,
        tone_pack=tone_pack,
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
    )


def render_aspects_v2_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
    on_result: Any | None = None,
) -> dict[str, AspectV2RenderResult]:
    client = client or DeepSeekClient.from_env()
    rendered: dict[str, AspectV2RenderResult] = {}
    max_workers = min(_get_aspect_worker_count(), len(ASPECT_V2_SPECS))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(
                render_aspect_v2_from_package,
                package,
                aspect_key=spec["aspect_key"],
                tone_pack=tone_pack,
                client=client,
                model=model,
                thinking_enabled=thinking_enabled,
                max_tokens=max_tokens,
            ): spec["aspect_key"]
            for spec in ASPECT_V2_SPECS
        }
        for future in as_completed(future_map):
            aspect_key = future_map[future]
            result = future.result()
            rendered[aspect_key] = result
            if callable(on_result):
                on_result(aspect_key, result)
    return {
        spec["aspect_key"]: rendered[spec["aspect_key"]]
        for spec in ASPECT_V2_SPECS
        if spec["aspect_key"] in rendered
    }


def render_aspect_v2_from_package(
    package: dict[str, Any],
    *,
    aspect_key: str,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> AspectV2RenderResult:
    score_template = package.get("score_template")
    if not isinstance(score_template, dict):
        raise DeepSeekAPIError(DEEPSEEK_ASPECT_V2_ERROR)

    client = client or DeepSeekClient.from_env()
    dimension_result = _resolve_dimension_result(package)
    payload = _build_aspect_payload(dimension_result, score_template, aspect_key)
    system_prompt, user_prompt, json_example = build_aspect_v2_prompts(aspect_key, payload, tone_pack=tone_pack)

    try:
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
        raise DeepSeekAPIError(DEEPSEEK_ASPECT_V2_ERROR) from exc

    valid, reason = validate_model_output(aspect_key, payload, model_output)
    if not valid:
        raise DeepSeekAPIError(DEEPSEEK_ASPECT_V2_ERROR) from ValueError(f"aspect_v2_invalid_output:{reason}")

    public_output = _public_output(model_output, aspect_key=aspect_key)
    return AspectV2RenderResult(
        aspect_key=str(public_output["aspect_key"]),
        title=str(public_output["title"]).strip(),
        score=int(public_output["score"]),
        content=str(public_output["content"]).strip(),
        risk=str(public_output["risk"]).strip(),
        elements_check=dict(public_output["elements_check"]),
        tone_pack=tone_pack,
        model_name=model_name,
    )


def build_aspect_v2_prompts(
    aspect_key: str,
    payload: dict[str, Any],
    *,
    tone_pack: TonePack = "customer",
) -> tuple[str, str, dict[str, Any]]:
    if aspect_key not in {item["aspect_key"] for item in ASPECT_V2_SPECS}:
        raise ValueError("invalid_aspect_key")

    shared_foundation = load_shared_foundation()
    general_judgement_knowledge = load_section_knowledge("phone_summary")
    model_pack = load_aspect_section_model_pack(aspect_key, tone_pack)
    judgement_knowledge = load_aspect_section_knowledge(aspect_key)
    taxonomy = load_aspect_section_taxonomy(aspect_key)
    output_contract = load_aspect_section_output_contract(aspect_key)
    style_examples = load_aspect_section_style_examples(aspect_key)

    json_example = {
        "aspect_key": aspect_key,
        "title": f"{payload['title']}上有可用之处，但要看承接和风险层是否压住",
        "score": payload["score"],
        "content": "请用一段自然中文输出专项综合评价，重点描述可核实的信息和轻度建议。",
        "risk": "请用一段话输出专项风险提示，语气比 content 更重。",
        "elements_check": {
            "宫": "一句话判断宫。",
            "门": "一句话判断门。",
            "神": "一句话判断神。",
            "星": "一句话判断星。",
            "天干/地干": "一句话判断天干/地干。",
            "特殊组合": "一句话判断特殊组合。",
            "四害": "一句话判断四害。",
        },
    }

    system_prompt = (
        f"你是易如反掌的「{payload['title']}」专项渲染器。\n"
        "你的任务不是改分，不是重算，也不是扩写成别的专题。\n"
        "必须严格遵守：\n"
        "1. 最终只输出一个 JSON object，且只包含 aspect_key、title、score、content、risk、elements_check。\n"
        "2. element_checks 是中间层判断，必须先完成再写 content 和 risk；最终 content 和 risk 都要体现 element_checks 的结果。\n"
        "3. content 重点写综合评价、可核实的信息和轻度建议，不要变成 checklist。\n"
        "4. risk 重点写 element_checks 里的风险项，语气要更重，但不能写成恐吓。\n"
        "5. 不要出现课程、知识库、老师、资料、文档来源痕迹。\n"
        "6. 只能使用 locked_fields 中的结构事实与系统提示词里的知识底座，不能引入未提供的维度标签或历史结论。\n"
        "7. 不要发明 locked facts 里没有的判断。\n"
        "8. 不要把 content 和 risk 写成一样。\n"
        "9. 不要只盯一个切口，必须让宫、门、神、星、天干/地干、特殊组合、四害都影响最终结论。\n\n"
        f"{shared_foundation}\n\n"
        f"【通用盘面判断知识】\n{general_judgement_knowledge}\n\n"
        f"【当前语气包】\n{model_pack}\n\n"
        f"【专项判断知识】\n{judgement_knowledge}\n\n"
        f"【taxonomy】\n{taxonomy}\n\n"
        f"【输出合同】\n{output_contract}\n\n"
        f"【表达样例】\n{style_examples}"
    )

    user_prompt = (
        "请基于下面的 locked facts 和内部检查结果输出一个 JSON object。\n\n"
        f"【locked_fields】\n{_dump_json(payload)}\n\n"
        "输出要求：\n"
        f"- aspect_key 固定为 {aspect_key}\n"
        f"- title 写一句“{payload['title']}”专项的判断式标题，不要只写专项名称，也不要写成其他专项。\n"
        "- score 必须和 locked_fields.score 一致，不得改动。\n"
        "- content 写专项综合评价，重点是描述信息和轻度建议。\n"
        "- risk 写专项风险提示，重点是 element_checks 里最需要重视的风险项。\n"
        "- elements_check 必须包含 宫、门、神、星、天干/地干、特殊组合、四害 七项，每项都要一句话。\n"
        "- 最终只输出 JSON object。\n"
    )

    return system_prompt, user_prompt, json_example


def validate_model_output(
    aspect_key: str,
    payload: dict[str, Any],
    model_output: dict[str, Any],
) -> tuple[bool, str]:
    for field in ("aspect_key", "title", "score", "content", "risk", "elements_check"):
        if field not in model_output:
            return False, f"missing_field:{field}"

    if str(model_output.get("aspect_key") or "").strip() != aspect_key:
        return False, "aspect_key_mismatch"
    if not str(model_output.get("title") or "").strip():
        return False, "missing_title"
    try:
        score = int(model_output.get("score"))
    except Exception:
        return False, "score_not_int"
    if score != int(payload.get("score", -1) or -1):
        return False, "score_mismatch"

    content = str(model_output.get("content") or "").strip()
    risk = str(model_output.get("risk") or "").strip()
    elements_check = model_output.get("elements_check")
    if not content:
        return False, "missing_content"
    if not risk:
        return False, "missing_risk"
    if not isinstance(elements_check, dict):
        return False, "elements_check_must_be_object"
    for key in REQUIRED_ELEMENT_KEYS:
        if not str(elements_check.get(key) or "").strip():
            return False, f"missing_element:{key}"
    return True, "ok"


def _build_aspect_payload(score_result: dict[str, Any], score_template: dict[str, Any], aspect_key: str) -> dict[str, Any]:
    if aspect_key not in score_result.get("dimensions", {}):
        raise DeepSeekAPIError(DEEPSEEK_ASPECT_V2_ERROR)
    dimension = score_result["dimensions"][aspect_key]
    board = score_result["board"]
    features = score_result["features"]
    return {
        "aspect_key": aspect_key,
        "title": _aspect_title(aspect_key),
        "score": int(dimension["score"]),
        "dimension_score": _clean_dimension(dimension),
        "board": board,
        "features": _clean_features(features),
        "locked_score": int(dimension["score"]),
    }


def _resolve_dimension_result(package: dict[str, Any]) -> dict[str, Any]:
    score_template = package.get("score_template") if isinstance(package.get("score_template"), dict) else {}
    existing = score_template.get("dimension_score_v3") if isinstance(score_template, dict) else None
    if isinstance(existing, dict) and isinstance(existing.get("dimensions"), dict):
        return existing

    existing = score_template.get("dimension_score_v2") if isinstance(score_template, dict) else None
    if isinstance(existing, dict) and isinstance(existing.get("dimensions"), dict):
        return existing

    score_result = package.get("score_result")
    if isinstance(score_result, dict) and isinstance(score_result.get("dimensions"), dict):
        return score_result
    if not isinstance(score_result, dict):
        raise DeepSeekAPIError(DEEPSEEK_ASPECT_V2_ERROR)

    input_payload = score_result.get("input") if isinstance(score_result.get("input"), dict) else {}
    phone = str(input_payload.get("phone") or "").strip()
    gender = str(input_payload.get("gender") or "").strip()
    if not phone or not gender:
        meta = score_template.get("meta") if isinstance(score_template.get("meta"), dict) else {}
        phone = str(meta.get("phone") or "").strip()
        gender = str(meta.get("gender") or "").strip()
    if not phone or not gender:
        raise DeepSeekAPIError(DEEPSEEK_ASPECT_V2_ERROR)
    return score_phone_dimensions_v3(phone, gender, rules=load_rules())


def _clean_dimension(dimension: dict[str, Any]) -> dict[str, Any]:
    components = dimension.get("components") if isinstance(dimension.get("components"), dict) else {}
    features = dimension.get("features") if isinstance(dimension.get("features"), dict) else {}
    risks = dimension.get("risks") if isinstance(dimension.get("risks"), dict) else {}
    caps = dimension.get("caps") if isinstance(dimension.get("caps"), dict) else {}
    return {
        "topic_key": dimension.get("topic_key"),
        "topic_title": dimension.get("topic_title"),
        "score": dimension.get("score"),
        "components": components,
        "features": _clean_features(features),
        "risks": {
            "high_risk_pairs": risks.get("high_risk_pairs", []),
            "structural_cap_reasons": risks.get("structural_cap_reasons", []),
            "structural_cap_reason_labels": _label_list(CAP_REASON_LABELS, risks.get("structural_cap_reasons", [])),
        },
        "caps": {
            "structural_cap": caps.get("structural_cap"),
            "applied": caps.get("applied", []),
            "applied_labels": _label_list(CAP_REASON_LABELS, caps.get("applied", [])),
        },
    }


def _clean_features(features: dict[str, Any]) -> dict[str, Any]:
    patterns = features.get("patterns") if isinstance(features.get("patterns"), dict) else {}
    edge_flags = features.get("edge_flags") if isinstance(features.get("edge_flags"), list) else []
    return {
        "anchor_relation": features.get("anchor_relation"),
        "anchor_relation_label": RELATION_LABELS.get(str(features.get("anchor_relation") or ""), features.get("anchor_relation")),
        "palace_door_relation": features.get("palace_door_relation"),
        "palace_door_relation_label": RELATION_LABELS.get(str(features.get("palace_door_relation") or ""), features.get("palace_door_relation")),
        "stem_relation": features.get("stem_relation"),
        "stem_relation_label": RELATION_LABELS.get(str(features.get("stem_relation") or ""), features.get("stem_relation")),
        "stem_pair_relation": features.get("stem_pair_relation"),
        "stem_pair_relation_label": RELATION_LABELS.get(str(features.get("stem_pair_relation") or ""), features.get("stem_pair_relation")),
        "palace": features.get("palace"),
        "door": features.get("door"),
        "star": features.get("star"),
        "god": features.get("god"),
        "harms": features.get("harms", {}),
        "patterns": {
            **patterns,
            "detected_labels": _label_list(PATTERN_LABELS, patterns.get("detected", [])),
        },
        "edge_flags": edge_flags,
        "edge_flag_labels": _label_list(EDGE_FLAG_LABELS, edge_flags),
    }


def _label_list(mapping: dict[str, str], values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [mapping.get(str(value), str(value)) for value in values]


def _aspect_title(aspect_key: str) -> str:
    for item in ASPECT_V2_SPECS:
        if item["aspect_key"] == aspect_key:
            return item["title"]
    return aspect_key


def _public_output(model_output: dict[str, Any], *, aspect_key: str) -> dict[str, Any]:
    return {
        "aspect_key": str(model_output["aspect_key"]).strip() or aspect_key,
        "title": str(model_output["title"]).strip(),
        "score": int(model_output["score"]),
        "content": str(model_output["content"]).strip(),
        "risk": str(model_output["risk"]).strip(),
        "elements_check": dict(model_output["elements_check"]),
    }


def render_aspect_v2_from_phone(
    phone: str,
    gender: str,
    *,
    aspect_key: str,
    tone_pack: TonePack = "customer",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1800,
) -> AspectV2RenderResult:
    rules = load_rules()
    package = {
        "score_result": score_phone_dimensions_v3(phone, gender, rules=rules),
        "score_template": {},
    }
    score_template = {
        "score_summary": {},
        "board_description_payload": {},
        "aspect_scores": {},
    }
    package["score_template"] = score_template
    return render_aspect_v2_from_package(
        package,
        aspect_key=aspect_key,
        tone_pack=tone_pack,
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
    )


def _dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _get_aspect_worker_count() -> int:
    raw_value = os.getenv("EASEWISE_ASPECT_V2_WORKERS", "8").strip()
    try:
        return max(1, min(8, int(raw_value)))
    except ValueError:
        return 8
