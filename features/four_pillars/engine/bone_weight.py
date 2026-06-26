from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from lunar_python import Solar


DATA_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "structured" / "yuan-tiangang-bone-weight.json"
HOUR_BRANCHES = (
    (23, "子"),
    (1, "丑"),
    (3, "寅"),
    (5, "卯"),
    (7, "辰"),
    (9, "巳"),
    (11, "午"),
    (13, "未"),
    (15, "申"),
    (17, "酉"),
    (19, "戌"),
    (21, "亥"),
)


@dataclass(frozen=True)
class BoneWeightResult:
    total_qian: int
    total_label: str
    summary: str
    fate_pattern: str
    verse: str | None
    year_ganzhi: str
    lunar_month: int
    lunar_day: int
    hour_branch: str
    parts: dict[str, int]
    rules: dict[str, str]
    sources: list[dict[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_qian": self.total_qian,
            "total_label": self.total_label,
            "summary": self.summary,
            "fate_pattern": self.fate_pattern,
            "verse": self.verse,
            "year_ganzhi": self.year_ganzhi,
            "lunar_month": self.lunar_month,
            "lunar_day": self.lunar_day,
            "hour_branch": self.hour_branch,
            "parts": self.parts,
            "rules": self.rules,
            "sources": self.sources,
        }


@lru_cache(maxsize=1)
def load_bone_weight_data() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def format_qian(value: int) -> str:
    liang, qian = divmod(value, 10)
    if liang <= 0:
        return f"{qian}钱"
    if qian == 0:
        return f"{liang}两"
    return f"{liang}两{qian}钱"


def hour_branch_for_datetime(value: datetime) -> str:
    hour = value.hour
    if hour == 23 or hour == 0:
        return "子"
    for start_hour, branch in HOUR_BRANCHES[1:]:
        if start_hour <= hour < start_hour + 2:
            return branch
    return "亥"


def _bone_lunar_for_datetime(value: datetime) -> Any:
    # 称骨资料常以夜子时归次日；这里只影响称骨日期，不改变四柱排盘。
    target = value + timedelta(days=1) if value.hour == 23 else value
    return Solar.fromDate(target).getLunar()


def _effective_lunar_month(lunar: Any) -> int:
    month = int(lunar.getMonth())
    day = int(lunar.getDay())
    if month < 0:
        effective = abs(month)
        if day > 15:
            effective += 1
        return min(effective, 12)
    return month


def calculate_bone_weight(value: datetime) -> BoneWeightResult | None:
    data = load_bone_weight_data()
    lunar = _bone_lunar_for_datetime(value)
    year_ganzhi = str(lunar.getYearInGanZhi())
    lunar_month = _effective_lunar_month(lunar)
    lunar_day = int(lunar.getDay())
    hour_branch = hour_branch_for_datetime(value)

    year_weight = data["year_weights"].get(year_ganzhi)
    month_weight = data["month_weights"].get(str(lunar_month))
    day_weight = data["day_weights"].get(str(lunar_day))
    hour_weight = data["hour_weights"].get(hour_branch)
    if not all(isinstance(item, int) for item in (year_weight, month_weight, day_weight, hour_weight)):
        return None

    parts = {
        "year": int(year_weight),
        "month": int(month_weight),
        "day": int(day_weight),
        "hour": int(hour_weight),
    }
    total = sum(parts.values())
    summary = str(data.get("song_summaries", {}).get(str(total)) or "").strip()
    if not summary:
        return None
    verse = str(data.get("song_verses", {}).get(str(total)) or "").strip() or None
    return BoneWeightResult(
        total_qian=total,
        total_label=format_qian(total),
        summary=summary,
        fate_pattern=summary,
        verse=verse,
        year_ganzhi=year_ganzhi,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_branch=hour_branch,
        parts=parts,
        rules={key: str(value) for key, value in data.get("rules", {}).items()},
        sources=[
            {"title": str(item.get("title") or ""), "url": str(item.get("url") or "")}
            for item in data.get("sources", [])
            if isinstance(item, dict)
        ],
    )
