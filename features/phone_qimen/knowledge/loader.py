from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable, Literal

AspectSectionName = Literal[
    "career",
    "wealth",
    "love",
    "health",
    "acad",
    "fortune",
    "investment",
    "travel",
    "social",
    "family",
    "personality",
    "fengshui",
]
SectionName = Literal["phone_summary", "stability"]
TonePack = Literal["customer", "professional"]

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = ROOT / "knowledge"

SHARED_FOUNDATION_FILES = (
    "shared/model-baseline.md",
    "shared/interpretation-boundaries.md",
    "shared/user-readable-expression.md",
    "shared/professional-terms.md",
)


def resolve_knowledge_path(relative_path: str) -> Path:
    return KNOWLEDGE_ROOT / relative_path


@lru_cache(maxsize=None)
def _read(relative_path: str) -> str:
    return resolve_knowledge_path(relative_path).read_text(encoding="utf-8").strip()


def _join(relative_paths: Iterable[str]) -> str:
    return "\n\n".join(_read(path) for path in relative_paths)


def load_shared_foundation() -> str:
    return _join(SHARED_FOUNDATION_FILES)


def load_section_knowledge(section: SectionName) -> str:
    return _read(f"sections/{section}/judgement-knowledge.md")


def load_section_style_examples(section: SectionName) -> str:
    return _read(f"sections/{section}/style-examples.md")


def load_section_taxonomy(section: SectionName) -> str:
    return _read(f"sections/{section}/taxonomy.md")


def load_section_output_contract(section: SectionName) -> str:
    return _read(f"sections/{section}/output-contract.md")


def load_section_model_pack(section: SectionName, tone_pack: TonePack) -> str:
    return _read(f"sections/{section}/model-pack-{tone_pack}.md")


def load_aspect_section_knowledge(aspect: AspectSectionName) -> str:
    return _read(f"sections/aspects/{aspect}/judgement-knowledge.md")


def load_aspect_section_style_examples(aspect: AspectSectionName) -> str:
    return _read(f"sections/aspects/{aspect}/style-examples.md")


def load_aspect_section_taxonomy(aspect: AspectSectionName) -> str:
    return _read(f"sections/aspects/{aspect}/taxonomy.md")


def load_aspect_section_output_contract(aspect: AspectSectionName) -> str:
    return _read(f"sections/aspects/{aspect}/output-contract.md")


def load_aspect_section_model_pack(aspect: AspectSectionName, tone_pack: TonePack) -> str:
    return _read(f"sections/aspects/{aspect}/model-pack-{tone_pack}.md")
