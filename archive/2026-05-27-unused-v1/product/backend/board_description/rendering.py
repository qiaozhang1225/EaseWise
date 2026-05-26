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
from product.backend.llm import DeepSeekClient
from scoring.engine import load_rules, score_phone
from scoring.services.bundle_service import build_scoring_bundle

TonePack = Literal["customer", "professional"]

UNSUPPORTED_PATTERN_TERMS = ("轮回格", "蝴蝶双飞格")
HARM_TERMS = {
    "emptiness": "空亡",
    "door_pressure": "门迫",
    "tomb": "入墓",
    "punishment_hit": "击刑",
}


@dataclass
class BoardDescriptionRenderResult:
    board_basis: str
    core_relation_judgement: str
    technical_narrative: str
    practical_manifestation: str
    tone_pack: TonePack
    model_name: str
    used_fallback: bool
    raw_model_output: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "board_basis": self.board_basis,
            "core_relation_judgement": self.core_relation_judgement,
            "technical_narrative": self.technical_narrative,
            "practical_manifestation": self.practical_manifestation,
            "tone_pack": self.tone_pack,
            "model_name": self.model_name,
            "used_fallback": self.used_fallback,
            "raw_model_output": self.raw_model_output,
        }


def build_board_description_prompts(payload: dict[str, Any], *, tone_pack: TonePack = "professional") -> tuple[str, str, dict[str, Any]]:
    locked = _locked_fields(payload)
    evidence = _evidence_fields(payload)
    shared_foundation = load_shared_foundation()
    model_pack = load_section_model_pack("board_description", tone_pack)
    judgement_knowledge = load_section_knowledge("board_description")
    taxonomy = load_section_taxonomy("board_description")
    output_contract = load_section_output_contract("board_description")
    style_examples = load_section_style_examples("board_description")

    json_example = {
        "board_basis": f"后七位{locked['board_basis']['last7']}，对应引干{locked['board_basis']['trigger']}、宫{locked['board_basis']['palace']}、神{locked['board_basis']['god']}、星{locked['board_basis']['star']}、门{locked['board_basis']['door']}、天干{locked['board_basis']['heaven_stem']}、地干{locked['board_basis']['earth_stem']}。",
        "core_relation_judgement": f"宫门关系落在{locked['core_relations']['palace_door_relation']}，后两干关系落在{locked['core_relations']['stem_pair_relation']}，真正需要继续看的，是四害、特殊组合和封顶因素会不会压住主轴。",
        "technical_narrative": f"这张盘的主轴是{locked['main_axis']}，真正的主矛盾是{locked['main_contradiction']}。请在这里输出一段完整、自然、专业的中文盘面解释，围绕主轴、主矛盾、四害、特殊组合和现实压制层展开。",
        "practical_manifestation": locked["practical_manifestation"],
    }

    system_prompt = (
        "你是易如反掌的盘面解释渲染器，负责把代码锁定的结构化评分包写成可插入总评的奇门盘解读。\n"
        "你的职责不是重算分，也不是改写十方面，而是基于 locked_fields 和统一知识底座，输出一段真正像盘解的结构化结果。\n"
        "必须遵守这些硬规则：\n"
        "1. 不得修改或推翻 locked_fields。\n"
        "2. 不得重算分数、四害、关系、特殊组合或封顶原因。\n"
        "3. 不得发明 evidence 里没有出现的特殊格局，尤其不要主动写出轮回格或蝴蝶双飞格。\n"
        "4. 不得把盘面解释写成十方面总结。\n"
        "5. 必须按四段职责输出：盘面基础结构、核心关系判断、专业盘面描述、现实落点。\n"
        "6. 如果四害存在，必须显性点出对应的空亡、门迫、入墓、击刑。\n"
        "7. 如果盘面是混合信号，只能解释主矛盾，不要平均摊开。\n"
        "8. 最终只输出一个 JSON object，不输出 Markdown，不输出额外说明。"
    )

    user_prompt = (
        "请基于以下统一知识底座、盘面解释知识、风格样例、输出合同、locked_fields 和 evidence，输出一个 JSON object。\n\n"
        "【统一知识底座】\n"
        f"{shared_foundation}\n\n"
        "【当前语气包】\n"
        f"{model_pack}\n\n"
        "【盘面解释判断知识】\n"
        f"{judgement_knowledge}\n\n"
        "【盘面解释 taxonomy】\n"
        f"{taxonomy}\n\n"
        "【输出合同】\n"
        f"{output_contract}\n\n"
        "【盘面解释表达风格样例】\n"
        f"{style_examples}\n\n"
        "【locked_fields：这些值不能改】\n"
        f"{_dump_json(locked)}\n\n"
        "【evidence：可用于解释，但不能改写 locked_fields】\n"
        f"{_dump_json(evidence)}\n\n"
        "输出要求：\n"
        "- board_basis：1 句话，先把后七位和引干 / 宫 / 神 / 星 / 门 / 天干 / 地干定清楚。\n"
        "- core_relation_judgement：1-2 句话，必须交代宫门关系、后两干关系，并点出四害 / 特殊组合 / 封顶有没有压住盘面。\n"
        "- technical_narrative：一段完整中文盘解，必须明确 main_axis 和 main_contradiction，且要有厚度，不要写成十方面缩写。\n"
        "- practical_manifestation：1-2 句话，把盘面翻译成现实表现。\n"
        "- 最终只输出 JSON object。"
    )
    return system_prompt, user_prompt, json_example


def validate_model_output(payload: dict[str, Any], model_output: dict[str, Any]) -> tuple[bool, str]:
    required_keys = {"board_basis", "core_relation_judgement", "technical_narrative", "practical_manifestation"}
    if not required_keys.issubset(model_output):
        return False, "missing_required_keys"

    locked = _locked_fields(payload)
    board_basis = str(model_output["board_basis"]).strip()
    core = str(model_output["core_relation_judgement"]).strip()
    technical = str(model_output["technical_narrative"]).strip()
    practical = str(model_output["practical_manifestation"]).strip()
    combined = "\n".join((board_basis, core, technical, practical))

    for marker in _board_basis_markers(locked["board_basis"]):
        if marker not in board_basis:
            return False, "board_basis_missing_locked_symbol"
    if locked["core_relations"]["palace_door_relation"] not in core:
        return False, "core_relation_missing_palace_door_relation"
    if locked["core_relations"]["stem_pair_relation"] not in core:
        return False, "core_relation_missing_stem_pair_relation"
    if locked["main_axis"] not in technical:
        return False, "technical_narrative_missing_main_axis"
    if locked["main_contradiction"] not in technical:
        return False, "technical_narrative_missing_main_contradiction"
    if any(term in combined for term in UNSUPPORTED_PATTERN_TERMS):
        return False, "mentions_unsupported_pattern"
    if not _mentions_active_harms(combined, locked["core_relations"]["four_harms"]):
        return False, "missing_active_harm_reference"
    if locked["core_relations"]["pattern_flags"] and not _mentions_pattern_reference(combined, locked["core_relations"]["pattern_flags"], locked["core_relations"]["risk_pairs"]):
        return False, "missing_pattern_reference"
    if locked["core_relations"]["structural_cap_reasons"] and not _mentions_structural_cap_reference(combined, locked["core_relations"]["structural_cap_reasons"]):
        return False, "missing_structural_cap_reference"
    if len(technical) < 160:
        return False, "technical_narrative_too_thin"
    if not _practical_manifestation_matches(practical, payload["manifestation_keywords"]):
        return False, "practical_manifestation_off_topic"
    return True, "ok"


def render_board_description_from_package(
    package: dict[str, Any],
    *,
    tone_pack: TonePack = "professional",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1100,
) -> BoardDescriptionRenderResult:
    payload = package["score_template"]["board_description_payload"]
    client = client or DeepSeekClient.from_env()
    system_prompt, user_prompt, json_example = build_board_description_prompts(payload, tone_pack=tone_pack)

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
            "board_basis": _fallback_board_basis(payload),
            "core_relation_judgement": _fallback_core_relation_judgement(payload),
            "technical_narrative": _fallback_technical_narrative(payload, tone_pack=tone_pack),
            "practical_manifestation": _fallback_practical_manifestation(payload),
        }

    return BoardDescriptionRenderResult(
        board_basis=str(raw_model_output["board_basis"]).strip(),
        core_relation_judgement=str(raw_model_output["core_relation_judgement"]).strip(),
        technical_narrative=str(raw_model_output["technical_narrative"]).strip(),
        practical_manifestation=str(raw_model_output["practical_manifestation"]).strip(),
        tone_pack=tone_pack,
        model_name=model_name,
        used_fallback=used_fallback,
        raw_model_output=raw_model_output,
    )


def render_board_description_from_phone(
    phone: str,
    gender: str,
    *,
    tone_pack: TonePack = "professional",
    client: DeepSeekClient | None = None,
    model: str = "deepseek-v4-pro",
    thinking_enabled: bool = False,
    max_tokens: int = 1100,
) -> BoardDescriptionRenderResult:
    rules = load_rules()
    package = build_scoring_bundle(score_phone(phone, gender, rules))
    return render_board_description_from_package(
        package,
        tone_pack=tone_pack,
        client=client,
        model=model,
        thinking_enabled=thinking_enabled,
        max_tokens=max_tokens,
    )


def _locked_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "section_order": payload["section_order"],
        "score_band": payload["score_band"],
        "main_axis": payload["main_axis"],
        "main_contradiction": payload["main_contradiction"],
        "practical_manifestation": payload["practical_manifestation"],
        "board_basis": payload["board_basis"],
        "core_relations": payload["core_relations"],
    }


def _evidence_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "score_facts": payload["score_facts"],
        "technical_focus": payload["technical_focus"],
    }


def _fallback_board_basis(payload: dict[str, Any]) -> str:
    basis = payload["board_basis"]
    return (
        f"后七位{basis['last7']}，对应引干{basis['trigger']}、宫{basis['palace']}、神{basis['god']}、"
        f"星{basis['star']}、门{basis['door']}、天干{basis['heaven_stem']}、地干{basis['earth_stem']}。"
    )


def _fallback_core_relation_judgement(payload: dict[str, Any]) -> str:
    relations = payload["core_relations"]
    four_harms = relations["four_harms"]
    active_harms = [term for key, term in HARM_TERMS.items() if four_harms[key] != "无"]
    harm_text = "四害层目前无硬伤。"
    if active_harms:
        harm_text = f"四害层重点落在{'、'.join(active_harms)}，说明真正压盘的不是表面亮点，而是这些层位的回拉。"

    pattern_parts: list[str] = []
    if relations["pattern_flags"]:
        pattern_parts.append(f"特殊组合带着{'、'.join(relations['pattern_flags'])}。")
    if relations["structural_cap_reasons"]:
        pattern_parts.append(f"结构封顶原因落在{'、'.join(relations['structural_cap_reasons'])}。")
    pattern_text = " ".join(pattern_parts)

    return (
        f"宫门关系落在{relations['palace_door_relation']}，后两干关系落在{relations['stem_pair_relation']}。"
        f"{harm_text}{pattern_text}"
    ).strip()


def _fallback_technical_narrative(payload: dict[str, Any], *, tone_pack: TonePack) -> str:
    focus = payload.get("technical_focus", [])
    focus_text = " ".join(
        f"{item['focus']}看{item['value']}，{item['implication']}" for item in focus[:4]
    )
    score_facts = payload["score_facts"]
    score_gap = int(score_facts.get("score_gap") or 0)
    gap_note = ""
    if score_gap > 0:
        gap_note = f"代码原始分和最终分之间还有{score_gap}分回拉，说明盘面亮点并没有原样落进现实。"

    if tone_pack == "customer":
        return (
            f"这张盘真正的主轴是{payload['main_axis']}，真正的主矛盾是{payload['main_contradiction']}。"
            f"不要只看表面有没有势头，更要看哪些层把这股势头接住了，哪些层又在现实里把它拽回来。"
            f"{focus_text}{gap_note}"
            f"所以这类盘解读时，重点不是把所有术语都说一遍，而是看亮点为什么能起、又是被哪一层压住，最后才知道这张盘为什么会显成现在这个样子。"
        )

    return (
        f"这张盘的主轴是{payload['main_axis']}，真正主导落地感的，是“{payload['main_contradiction']}”这一层。"
        f"盘面不能只按表面吉象平均理解，因为真正改写现实表现的，往往是关系顺逆、四害压制、特殊组合放大和封顶原因叠加之后留下来的结构。"
        f"{focus_text}{gap_note}"
        f"所以这类盘解释时，先要定主轴，再要指出压制层，最后才能说明为什么它在现实里会显成这样的力度、节奏和代价。"
    )


def _fallback_practical_manifestation(payload: dict[str, Any]) -> str:
    return str(payload["practical_manifestation"]).strip()


def _board_basis_markers(basis: dict[str, str]) -> list[str]:
    return [
        f"后七位{basis['last7']}",
        f"引干{basis['trigger']}",
        f"宫{basis['palace']}",
        f"神{basis['god']}",
        f"星{basis['star']}",
        f"门{basis['door']}",
        f"天干{basis['heaven_stem']}",
        f"地干{basis['earth_stem']}",
    ]


def _mentions_active_harms(text: str, four_harms: dict[str, str]) -> bool:
    for key, term in HARM_TERMS.items():
        if four_harms[key] != "无" and term not in text:
            return False
    return True


def _mentions_pattern_reference(text: str, pattern_flags: list[str], risk_pairs: list[str]) -> bool:
    if any(flag in text for flag in pattern_flags):
        return True
    return any(pair in text for pair in risk_pairs)


def _mentions_structural_cap_reference(text: str, cap_reasons: list[str]) -> bool:
    if "封顶" in text:
        return True
    return any(reason in text for reason in cap_reasons)


def _practical_manifestation_matches(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _dump_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
