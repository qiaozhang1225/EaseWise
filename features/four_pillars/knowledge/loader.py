from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable, Literal

AspectSectionName = Literal[
    "personality",
    "wealth",
    "marriage",
    "career",
    "health",
    "fortune",
    "investment",
    "social",
    "industry",
    "fengshui",
    "family",
    "pattern",
    "love",
    "family_environment",
    "annual_trend",
]
SectionName = Literal["chart_summary"]
LuckSectionName = Literal["dayun", "liunian"]
TonePack = Literal["customer", "professional"]

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = ROOT / "knowledge"
SHARED_FOUNDATION_FILES = (
    "shared/model-baseline.md",
    "shared/interpretation-boundaries.md",
    "shared/user-readable-expression.md",
    "shared/professional-terms.md",
)
EXPLICIT_KNOWLEDGE_FILE = "explicit-knowledge.md"
ASPECT_SECTION_ALIASES = {
    "love": "marriage",
    "annual_trend": "fortune",
}
LEGACY_ASPECT_SECTION_FALLBACKS = {
    "marriage": "love",
    "fortune": "annual_trend",
    "fengshui": "family_environment",
}
ASPECT_LABELS = {
    "personality": "性格",
    "wealth": "财运",
    "marriage": "婚姻",
    "career": "事业",
    "health": "健康",
    "fortune": "运势",
    "investment": "投资",
    "social": "人际",
    "industry": "行业",
    "fengshui": "风水",
    "family": "家庭",
    "pattern": "格局",
    "love": "婚姻",
    "family_environment": "风水与家庭环境",
    "annual_trend": "运势",
}


def resolve_knowledge_path(relative_path: str) -> Path:
    return KNOWLEDGE_ROOT / relative_path


@lru_cache(maxsize=None)
def _read(relative_path: str) -> str:
    return resolve_knowledge_path(relative_path).read_text(encoding="utf-8").strip()


def _join(relative_paths: Iterable[str]) -> str:
    return "\n\n".join(_read(path) for path in relative_paths)


def _read_optional(relative_path: str) -> str | None:
    path = resolve_knowledge_path(relative_path)
    if not path.exists():
        return None
    return _read(relative_path)


def _aspect_dir(aspect: str) -> str:
    return ASPECT_SECTION_ALIASES.get(aspect, aspect)


def _load_aspect_file(aspect: AspectSectionName, filename: str, fallback: str) -> str:
    aspect_name = str(aspect)
    primary = _aspect_dir(aspect_name)
    content = _read_optional(f"sections/aspects/{primary}/{filename}")
    if content is not None:
        return content
    legacy = LEGACY_ASPECT_SECTION_FALLBACKS.get(primary)
    if legacy:
        content = _read_optional(f"sections/aspects/{legacy}/{filename}")
        if content is not None:
            return content
    return fallback


def _aspect_label(aspect: str) -> str:
    return ASPECT_LABELS.get(aspect, aspect)


def _generic_aspect_model_pack(aspect: str, tone_pack: TonePack) -> str:
    label = _aspect_label(aspect)
    tone = "面向普通用户" if tone_pack == "customer" else "面向专业复核"
    return (
        f"# {label} Model Pack\n\n"
        f"- 语气：{tone}，先给现实判断，再补命理依据。\n"
        "- 避免连续堆叠术语；必须把十神、五行、冲合刑害翻译成用户可对照的生活、工作、关系或财务场景。\n"
        "- 可以指出倾向、模式和风险边界，不能写确定发财、离婚、疾病、灾祸或绝对吉凶。\n"
        "- 每段都要围绕“现实表现 -> 命理依据 -> 可执行提醒”的顺序组织。"
    )


def _generic_aspect_taxonomy(aspect: str) -> str:
    label = _aspect_label(aspect)
    return (
        f"# {label} Taxonomy\n\n"
        "- `现实判断`: 用户在该维度中容易表现出来的行为、处境或选择方式。\n"
        "- `命理依据`: 日主承载、五行流通、十神主题、合冲刑害、喜忌取向。\n"
        "- `风险边界`: 该维度中容易过度、卡住或消耗的部分。\n"
        "- `行动建议`: 用普通语言说明更适合的节奏、环境、协作方式或取舍。"
    )


def _generic_aspect_output_contract(aspect: str) -> str:
    label = _aspect_label(aspect)
    return (
        f"# {label} Output Contract\n\n"
        "必须输出 JSON object：\n"
        f"- `aspect_key`: 必须为 `{aspect}`。\n"
        "- `title`: 一句话标题，要能让用户直接理解这个维度的主判断。\n"
        f"- `content`: {label}维度的现实表现、命理依据和可对照判断。\n"
        "- `risk`: 风险提醒和边界建议，不能制造恐吓或绝对承诺。\n"
        "- `elements_check`: 必须包含 `日主`、`五行`、`十神`、`合冲刑害`、`喜忌` 五个键。"
    )


def _generic_aspect_style_examples(aspect: str) -> str:
    label = _aspect_label(aspect)
    return (
        f"# {label} Style Examples\n\n"
        "推荐表达：\n"
        f"- “这个{label}维度有优势，但要靠稳定节奏发挥出来：现实里更适合在规则清楚、反馈明确的环境里推进。”\n"
        "- “命理上看到的是伤官或正印这类信号；伤官代表表达和突破，正印代表学习和保护，落到现实里就是说话方式、资源获取方式和压力处理方式不同。”\n"
        "\n避免表达：\n"
        "- “命里注定……”“一定会……”“必然破财/离婚/生病”。\n"
        "- 连续堆叠“正官七杀伤官偏印”但不解释它们对应的现实行为。\n"
        "- “结构承接、可用空间、现实承接感”这类用户读不懂的内部分析词。"
    )


def load_shared_foundation() -> str:
    return _join(SHARED_FOUNDATION_FILES)


def load_explicit_knowledge() -> str:
    return _read(EXPLICIT_KNOWLEDGE_FILE)


def load_section_knowledge(section: SectionName) -> str:
    return _read(f"sections/{section}/judgement-knowledge.md")


def load_section_style_examples(section: SectionName) -> str:
    return _read(f"sections/{section}/style-examples.md")


def load_section_taxonomy(section: SectionName) -> str:
    return _read(f"sections/{section}/taxonomy.md")


def load_section_model_pack(section: SectionName, tone_pack: TonePack) -> str:
    return _read(f"sections/{section}/model-pack-{tone_pack}.md")


def load_section_output_contract(section: SectionName) -> str:
    return _read(f"sections/{section}/output-contract.md")


def load_aspect_section_knowledge(aspect: AspectSectionName) -> str:
    return _load_aspect_file(
        aspect,
        "judgement-knowledge.md",
        (
            f"# {_aspect_label(str(aspect))} Judgement Knowledge\n\n"
            "本专项基于现有四柱 explicit knowledge 做结构化判断：先看日主承载，再看五行流通、十神主题、宫位和合冲刑害。"
            "输出时可以保留命理术语，但每个术语都必须马上翻译为现实可观察的行为、资源、关系、压力和选择方式。"
        ),
    )


def load_aspect_section_style_examples(aspect: AspectSectionName) -> str:
    return _load_aspect_file(aspect, "style-examples.md", _generic_aspect_style_examples(str(aspect)))


def load_aspect_section_taxonomy(aspect: AspectSectionName) -> str:
    return _load_aspect_file(aspect, "taxonomy.md", _generic_aspect_taxonomy(str(aspect)))


def load_aspect_section_model_pack(aspect: AspectSectionName, tone_pack: TonePack) -> str:
    return _load_aspect_file(aspect, f"model-pack-{tone_pack}.md", _generic_aspect_model_pack(str(aspect), tone_pack))


def load_aspect_section_output_contract(aspect: AspectSectionName) -> str:
    aspect_name = str(aspect)
    primary = _aspect_dir(aspect_name)
    content = _read_optional(f"sections/aspects/{primary}/output-contract.md")
    if content is not None and primary == aspect_name:
        return content
    return _generic_aspect_output_contract(primary)


def load_luck_section_knowledge(section: LuckSectionName) -> str:
    return _read(f"sections/luck/{section}/judgement-knowledge.md")


def load_luck_section_style_examples(section: LuckSectionName) -> str:
    return _read(f"sections/luck/{section}/style-examples.md")


def load_luck_section_taxonomy(section: LuckSectionName) -> str:
    return _read(f"sections/luck/{section}/taxonomy.md")


def load_luck_section_model_pack(section: LuckSectionName, tone_pack: TonePack) -> str:
    return _read(f"sections/luck/{section}/model-pack-{tone_pack}.md")


def load_luck_section_output_contract(section: LuckSectionName) -> str:
    return _read(f"sections/luck/{section}/output-contract.md")
