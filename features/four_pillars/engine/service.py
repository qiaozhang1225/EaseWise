from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from lunar_python import Solar

from .bone_weight import calculate_bone_weight
from .shen_sha import (
    ShenShaContext,
    calculate_chart_shen_sha,
    calculate_target_shen_sha,
    shen_sha_names,
    summarize_chart_shen_sha,
)
from .solar_time import calculate_true_solar_time, default_birth_location, resolve_birth_location

FOUR_PILLARS_ASPECTS: list[dict[str, str]] = [
    {"aspect_key": "personality", "title": "性格"},
    {"aspect_key": "career", "title": "事业"},
    {"aspect_key": "wealth", "title": "财富"},
    {"aspect_key": "love", "title": "婚恋"},
    {"aspect_key": "health", "title": "健康"},
    {"aspect_key": "family_environment", "title": "家庭环境"},
]
FOUR_PILLARS_ASPECT_ORDER = [item["aspect_key"] for item in FOUR_PILLARS_ASPECTS]

PILLAR_KEYS = ("year", "month", "day", "hour")
PILLAR_LABELS = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ELEMENT_BY_STEM = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}
ELEMENT_BY_BRANCH = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}
YIN_YANG_BY_STEM = {
    "甲": "阳",
    "乙": "阴",
    "丙": "阳",
    "丁": "阴",
    "戊": "阳",
    "己": "阴",
    "庚": "阳",
    "辛": "阴",
    "壬": "阳",
    "癸": "阴",
}
HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
SEASON_ELEMENT_BY_MONTH_BRANCH = {
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
    "子": "水",
    "丑": "土",
}
BRANCH_CLASHES = {frozenset(pair): name for pair, name in {
    ("子", "午"): "子午冲",
    ("丑", "未"): "丑未冲",
    ("寅", "申"): "寅申冲",
    ("卯", "酉"): "卯酉冲",
    ("辰", "戌"): "辰戌冲",
    ("巳", "亥"): "巳亥冲",
}.items()}
BRANCH_HARMS = {frozenset(pair): name for pair, name in {
    ("子", "未"): "子未害",
    ("丑", "午"): "丑午害",
    ("寅", "巳"): "寅巳害",
    ("卯", "辰"): "卯辰害",
    ("申", "亥"): "申亥害",
    ("酉", "戌"): "酉戌害",
}.items()}
BRANCH_BREAKS = {frozenset(pair): name for pair, name in {
    ("子", "酉"): "子酉破",
    ("午", "卯"): "午卯破",
    ("辰", "丑"): "辰丑破",
    ("戌", "未"): "戌未破",
    ("寅", "亥"): "寅亥破",
    ("巳", "申"): "巳申破",
}.items()}
BRANCH_SIX_HARMONIES = {frozenset(pair): name for pair, name in {
    ("子", "丑"): "子丑合",
    ("寅", "亥"): "寅亥合",
    ("卯", "戌"): "卯戌合",
    ("辰", "酉"): "辰酉合",
    ("巳", "申"): "巳申合",
    ("午", "未"): "午未合",
}.items()}
STEM_COMBINATIONS = {frozenset(pair): name for pair, name in {
    ("甲", "己"): "甲己合",
    ("乙", "庚"): "乙庚合",
    ("丙", "辛"): "丙辛合",
    ("丁", "壬"): "丁壬合",
    ("戊", "癸"): "戊癸合",
}.items()}
STEM_CLASHES = {frozenset(pair): name for pair, name in {
    ("甲", "庚"): "甲庚冲",
    ("乙", "辛"): "乙辛冲",
    ("丙", "壬"): "丙壬冲",
    ("丁", "癸"): "丁癸冲",
}.items()}
TOMB_BRANCHES = {"辰": "水库", "戌": "火库", "丑": "金库", "未": "木库"}
FIVE_GHOST_BRANCH_BY_MONTH_BRANCH = {
    "子": "辰",
    "丑": "巳",
    "寅": "午",
    "卯": "未",
    "辰": "申",
    "巳": "酉",
    "午": "戌",
    "未": "亥",
    "申": "子",
    "酉": "丑",
    "戌": "寅",
    "亥": "卯",
}
LU_BRANCH_BY_DAY_STEM = {
    "甲": "寅",
    "乙": "卯",
    "丙": "巳",
    "戊": "巳",
    "丁": "午",
    "己": "午",
    "庚": "申",
    "辛": "酉",
    "壬": "亥",
    "癸": "子",
}
TWELVE_LIFE_STAGE_BY_STEM = {
    "甲": {"亥": "长生", "子": "沐浴", "丑": "冠带", "寅": "临官", "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死", "未": "墓", "申": "绝", "酉": "胎", "戌": "养"},
    "乙": {"午": "长生", "巳": "沐浴", "辰": "冠带", "卯": "临官", "寅": "帝旺", "丑": "衰", "子": "病", "亥": "死", "戌": "墓", "酉": "绝", "申": "胎", "未": "养"},
    "丙": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
    "丁": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
    "戊": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
    "己": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
    "庚": {"巳": "长生", "午": "沐浴", "未": "冠带", "申": "临官", "酉": "帝旺", "戌": "衰", "亥": "病", "子": "死", "丑": "墓", "寅": "绝", "卯": "胎", "辰": "养"},
    "辛": {"子": "长生", "亥": "沐浴", "戌": "冠带", "酉": "临官", "申": "帝旺", "未": "衰", "午": "病", "巳": "死", "辰": "墓", "卯": "绝", "寅": "胎", "丑": "养"},
    "壬": {"申": "长生", "酉": "沐浴", "戌": "冠带", "亥": "临官", "子": "帝旺", "丑": "衰", "寅": "病", "卯": "死", "辰": "墓", "巳": "绝", "午": "胎", "未": "养"},
    "癸": {"卯": "长生", "寅": "沐浴", "丑": "冠带", "子": "临官", "亥": "帝旺", "戌": "衰", "酉": "病", "申": "死", "未": "墓", "午": "绝", "巳": "胎", "辰": "养"},
}
TIAN_YI_BRANCHES_BY_DAY_STEM = {
    "甲": ["丑", "未"],
    "戊": ["丑", "未"],
    "庚": ["丑", "未"],
    "乙": ["子", "申"],
    "己": ["子", "申"],
    "丙": ["亥", "酉"],
    "丁": ["亥", "酉"],
    "壬": ["卯", "巳"],
    "癸": ["卯", "巳"],
    "辛": ["寅", "午"],
}
TAI_JI_BRANCHES_BY_DAY_STEM = {
    "甲": ["子", "午"],
    "乙": ["子", "午"],
    "丙": ["卯", "酉"],
    "丁": ["卯", "酉"],
    "戊": ["辰", "戌", "丑", "未"],
    "己": ["辰", "戌", "丑", "未"],
    "庚": ["寅", "亥"],
    "辛": ["寅", "亥"],
    "壬": ["巳", "申"],
    "癸": ["巳", "申"],
}
WEN_CHANG_BRANCH_BY_DAY_STEM = {
    "甲": "巳",
    "乙": "午",
    "丙": "申",
    "丁": "酉",
    "戊": "申",
    "己": "酉",
    "庚": "亥",
    "辛": "子",
    "壬": "寅",
    "癸": "卯",
}
TRINITY_GROUP_TARGETS = (
    ({"申", "子", "辰"}, {"桃花": "酉", "驿马": "寅", "华盖": "辰", "将星": "子", "亡神": "亥"}),
    ({"亥", "卯", "未"}, {"桃花": "子", "驿马": "巳", "华盖": "未", "将星": "卯", "亡神": "寅"}),
    ({"巳", "酉", "丑"}, {"桃花": "午", "驿马": "亥", "华盖": "丑", "将星": "酉", "亡神": "申"}),
    ({"寅", "午", "戌"}, {"桃花": "卯", "驿马": "申", "华盖": "戌", "将星": "午", "亡神": "巳"}),
)


@dataclass(frozen=True)
class FourPillarsInput:
    gender: str
    birth_date: str
    birth_time: str
    timezone: str = "Asia/Shanghai"
    birth_place: str | None = None
    name: str | None = None


STEMS_BY_BRANCH_PARITY = {
    "子": ("甲", "丙", "戊", "庚", "壬"),
    "丑": ("乙", "丁", "己", "辛", "癸"),
    "寅": ("甲", "丙", "戊", "庚", "壬"),
    "卯": ("乙", "丁", "己", "辛", "癸"),
    "辰": ("甲", "丙", "戊", "庚", "壬"),
    "巳": ("乙", "丁", "己", "辛", "癸"),
    "午": ("甲", "丙", "戊", "庚", "壬"),
    "未": ("乙", "丁", "己", "辛", "癸"),
    "申": ("甲", "丙", "戊", "庚", "壬"),
    "酉": ("乙", "丁", "己", "辛", "癸"),
    "戌": ("甲", "丙", "戊", "庚", "壬"),
    "亥": ("乙", "丁", "己", "辛", "癸"),
}


def build_four_pillars_review(payload: FourPillarsInput | dict[str, Any], *, include_markdown: bool = True) -> dict[str, Any]:
    normalized = _normalize_input(payload)
    chart = build_chart(normalized)
    deterministic_facts = build_deterministic_facts(chart, normalized)
    score_result = score_chart(deterministic_facts)
    score_template = build_score_template(normalized, chart, deterministic_facts, score_result)
    result = {
        "input_profile": normalized,
        "chart": chart,
        "deterministic_facts": deterministic_facts,
        "score_result": score_result,
        "score_template": score_template,
    }
    if include_markdown:
        result["score_markdown"] = build_score_markdown(result)
    return result


def build_chart(input_profile: dict[str, Any]) -> dict[str, Any]:
    birth_dt = _parse_birth_datetime(input_profile)
    solar = Solar.fromDate(birth_dt)
    lunar = solar.getLunar()
    bazi = list(lunar.getBaZi())
    year, month, day, hour = bazi
    pillars = {
        "year": _build_pillar("year", year, list(lunar.getBaZiShiShenGan())[0], list(lunar.getBaZiShiShenZhi())[0]),
        "month": _build_pillar("month", month, list(lunar.getBaZiShiShenGan())[1], list(lunar.getBaZiShiShenZhi())[1]),
        "day": _build_pillar("day", day, "日主", "日支"),
        "hour": _build_pillar("hour", hour, list(lunar.getBaZiShiShenGan())[3], list(lunar.getBaZiShiShenZhi())[3]),
    }
    day_stem = day[0]
    day_branch = day[1]
    hidden_ten_gods = {
        pillar_key: [
            {"stem": hidden_stem, "ten_god": ten_god(day_stem, hidden_stem), "element": ELEMENT_BY_STEM[hidden_stem]}
            for hidden_stem in HIDDEN_STEMS[pillar["branch"]]
        ]
        for pillar_key, pillar in pillars.items()
    }
    return {
        "solar_datetime": birth_dt.isoformat(),
        "lunar_date": lunar.toString(),
        "lunar_full_text": lunar.toFullString(),
        "year_ganzhi": year,
        "month_ganzhi": month,
        "day_ganzhi": day,
        "hour_ganzhi": hour,
        "year_ganzhi_by_lichun": lunar.getYearInGanZhiByLiChun(),
        "day_master": day_stem,
        "day_branch": day_branch,
        "day_master_element": ELEMENT_BY_STEM[day_stem],
        "day_master_yin_yang": YIN_YANG_BY_STEM[day_stem],
        "pillars": pillars,
        "hidden_ten_gods": hidden_ten_gods,
        "ba_zi_wuxing": list(lunar.getBaZiWuXing()),
        "ba_zi_na_yin": list(lunar.getBaZiNaYin()),
    }


def build_shen_sha_context(
    chart: dict[str, Any],
    input_profile: dict[str, Any] | None = None,
    *,
    empty_branches: list[str] | tuple[str, ...] | None = None,
) -> ShenShaContext:
    pillars = chart.get("pillars") if isinstance(chart.get("pillars"), dict) else {}
    year_pillar = as_pillar_dict(pillars.get("year"))
    month_pillar = as_pillar_dict(pillars.get("month"))
    day_pillar = as_pillar_dict(pillars.get("day"))
    day_ganzhi = str(day_pillar.get("ganzhi") or chart.get("day_ganzhi") or "")
    year_ganzhi = str(year_pillar.get("ganzhi") or chart.get("year_ganzhi") or "")
    month_ganzhi = str(month_pillar.get("ganzhi") or chart.get("month_ganzhi") or "")
    ba_zi_na_yin = chart.get("ba_zi_na_yin") if isinstance(chart.get("ba_zi_na_yin"), list) else []
    year_na_yin = str(chart.get("year_na_yin") or (ba_zi_na_yin[0] if ba_zi_na_yin else "")).strip()
    return ShenShaContext(
        year_stem=str(year_pillar.get("stem") or (year_ganzhi[0] if len(year_ganzhi) >= 2 else "")),
        year_branch=str(year_pillar.get("branch") or (year_ganzhi[1] if len(year_ganzhi) >= 2 else "")),
        month_branch=str(month_pillar.get("branch") or (month_ganzhi[1] if len(month_ganzhi) >= 2 else "")).strip(),
        day_stem=str(chart.get("day_master") or day_pillar.get("stem") or (day_ganzhi[0] if len(day_ganzhi) >= 2 else "")),
        day_branch=str(chart.get("day_branch") or day_pillar.get("branch") or (day_ganzhi[1] if len(day_ganzhi) >= 2 else "")),
        day_ganzhi=day_ganzhi,
        year_na_yin=year_na_yin or None,
        gender=str((input_profile or {}).get("gender") or "") or None,
        empty_branches=tuple(str(item) for item in (empty_branches or resolve_empty_branches(day_ganzhi)) if str(item).strip()),
    )


def build_chart_display(
    input_profile: dict[str, Any],
    chart: dict[str, Any],
    facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    birth_dt = _parse_birth_datetime(input_profile)
    lunar = Solar.fromDate(birth_dt).getLunar()
    solar = lunar.getSolar()
    eight_char = lunar.getEightChar()
    ba_zi_na_yin = list(lunar.getBaZiNaYin())
    pillars = chart.get("pillars") if isinstance(chart.get("pillars"), dict) else {}
    day_stem = str(chart.get("day_master") or chart.get("day_ganzhi", " ")[0]).strip()
    day_branch = str(chart.get("day_branch") or chart.get("day_ganzhi", "  ")[1]).strip()
    year_branch = str(pillars.get("year", {}).get("branch") or chart.get("year_ganzhi", "  ")[1]).strip()
    month_branch = str(pillars.get("month", {}).get("branch") or chart.get("month_ganzhi", "  ")[1]).strip()
    empty_branches = []
    if isinstance(facts, dict):
        empty_branches = [str(item) for item in facts.get("empty_branches", []) if str(item).strip()]
    shen_sha_context = build_shen_sha_context(chart, input_profile, empty_branches=empty_branches)
    chart_shen_sha = calculate_chart_shen_sha(shen_sha_context, {key: as_pillar_dict(pillars.get(key)) for key in PILLAR_KEYS})
    bone_weight = calculate_bone_weight(birth_dt)
    true_solar_display = str(as_dict(input_profile.get("true_solar_time")).get("display_text") or "").strip()
    if not true_solar_display:
        true_solar_display = birth_dt.strftime("%Y-%m-%d %H:%M")

    return {
        "profile": {
            "name": input_profile.get("name"),
            "gender_label": "男命" if str(input_profile.get("gender")) == "male" else "女命",
            "structure_label": "乾造" if str(input_profile.get("gender")) == "male" else "坤造",
            "zodiac": _lunar_zodiac(lunar),
            "solar_datetime_text": birth_dt.strftime("%Y-%m-%d %H:%M"),
            "lunar_date": _lunar_short_text(lunar),
            "lunar_full_text": str(chart.get("lunar_full_text") or lunar.toFullString()),
            "birth_place": input_profile.get("birth_place"),
            "timezone": str(input_profile.get("timezone") or "Asia/Shanghai"),
            "solar_term_context": _solar_term_context(lunar),
            "input_mode": input_profile.get("input_mode") or "solar",
            "standard_birth_datetime": input_profile.get("standard_birth_datetime"),
            "effective_birth_datetime": input_profile.get("effective_birth_datetime"),
            "true_solar_time": input_profile.get("true_solar_time"),
            "birth_location": input_profile.get("birth_location"),
            "true_solar_time_text": true_solar_display,
            "constellation": str(_safe_call(solar, "getXingZuo") or "").strip() or None,
            "xiu": _xiu_text(lunar),
            "tai_yuan": _ganzhi_with_nayin(_safe_call(eight_char, "getTaiYuan"), _safe_call(eight_char, "getTaiYuanNaYin")),
            "tai_xi": _ganzhi_with_nayin(_safe_call(eight_char, "getTaiXi"), _safe_call(eight_char, "getTaiXiNaYin")),
            "ming_gong": _ganzhi_with_nayin(_safe_call(eight_char, "getMingGong"), _safe_call(eight_char, "getMingGongNaYin")),
            "shen_gong": _ganzhi_with_nayin(_safe_call(eight_char, "getShenGong"), _safe_call(eight_char, "getShenGongNaYin")),
            "life_gua": _life_gua_text(birth_dt.year, str(input_profile.get("gender") or "")),
            "empty_branches_text": _chart_empty_branches_text(eight_char),
            "pillar_xun_kong_text": _pillar_xun_kong_text(eight_char),
            "bone_weight": bone_weight.to_dict() if bone_weight else None,
        },
        "pillars": {
            key: _build_display_pillar(
                key=key,
                pillar=as_pillar_dict(pillars.get(key)),
                eight_char=eight_char,
                na_yin_fallback=ba_zi_na_yin[index] if index < len(ba_zi_na_yin) else "",
                day_stem=day_stem,
                day_branch=day_branch,
                year_branch=year_branch,
                month_branch=month_branch,
                empty_branches=empty_branches,
                shen_sha_details=chart_shen_sha.get(key, []),
            )
            for index, key in enumerate(PILLAR_KEYS)
        },
        "element_status": resolve_element_status(month_branch),
    }


def build_deterministic_facts(chart: dict[str, Any], input_profile: dict[str, Any]) -> dict[str, Any]:
    pillars = chart["pillars"]
    stems = [pillars[key]["stem"] for key in ("year", "month", "day", "hour")]
    branches = [pillars[key]["branch"] for key in ("year", "month", "day", "hour")]
    element_counts = count_elements(stems, branches)
    interactions = detect_interactions(stems, branches)
    day_master_element = chart["day_master_element"]
    strength = estimate_day_master_strength(day_master_element, branches[1], element_counts)
    favorable = resolve_favorable_elements(day_master_element, strength)
    empty_branches = resolve_empty_branches(chart["day_ganzhi"])
    tombs = [{"branch": branch, "meaning": TOMB_BRANCHES[branch]} for branch in branches if branch in TOMB_BRANCHES]
    ten_god_counts = count_ten_gods(chart)
    aspect_scores = build_aspect_scores(element_counts, interactions, strength, ten_god_counts)
    shen_sha_context = build_shen_sha_context(chart, input_profile, empty_branches=empty_branches)
    shen_sha_by_pillar = calculate_chart_shen_sha(shen_sha_context, pillars)
    luck_cycles = build_luck_cycles(input_profile, chart=chart)
    return {
        "input_summary": {
            "gender": input_profile["gender"],
            "birth_date": input_profile["birth_date"],
            "birth_time": input_profile["birth_time"],
            "timezone": input_profile["timezone"],
            "birth_place": input_profile.get("birth_place"),
            "name": input_profile.get("name"),
        },
        "day_master": {
            "stem": chart["day_master"],
            "element": day_master_element,
            "yin_yang": chart["day_master_yin_yang"],
            "strength": strength,
            "favorable_elements": favorable["favorable"],
            "unfavorable_elements": favorable["unfavorable"],
        },
        "element_counts": element_counts,
        "ten_god_counts": ten_god_counts,
        "interactions": interactions,
        "empty_branches": empty_branches,
        "tombs": tombs,
        "shen_sha": {
            "by_pillar": shen_sha_by_pillar,
            "summary": summarize_chart_shen_sha(shen_sha_by_pillar),
        },
        "aspect_scores": aspect_scores,
        "luck_cycles": luck_cycles,
    }


def build_luck_cycles(
    input_profile: dict[str, Any],
    *,
    chart: dict[str, Any] | None = None,
    reference_year: int | None = None,
) -> dict[str, Any]:
    birth_dt = _parse_birth_datetime(input_profile)
    solar = Solar.fromDate(birth_dt)
    lunar = solar.getLunar()
    resolved_chart = chart or build_chart(input_profile)
    day_stem = str(resolved_chart["day_master"])
    shen_sha_context = build_shen_sha_context(
        resolved_chart,
        input_profile,
        empty_branches=resolve_empty_branches(str(resolved_chart.get("day_ganzhi") or "")),
    )
    gender_value = 1 if str(input_profile.get("gender")) == "male" else 0
    yun = lunar.getEightChar().getYun(gender_value)
    current_year = int(reference_year or datetime.now(birth_dt.tzinfo).year)
    cycles: list[dict[str, Any]] = []
    current_cycle_key: str | None = None
    for item in yun.getDaYun(13):
        start_year = int(item.getStartYear())
        end_year = int(item.getEndYear())
        ganzhi = str(item.getGanZhi() or "").strip()
        stem = ganzhi[0] if len(ganzhi) >= 2 else None
        branch = ganzhi[1] if len(ganzhi) >= 2 else None
        shen_sha_details = calculate_target_shen_sha(
            shen_sha_context,
            target_stem=stem,
            target_branch=branch,
            target_ganzhi=ganzhi,
            target_key="dayun",
        )
        cycle = {
            "cycle_key": _luck_cycle_key(start_year, end_year, ganzhi),
            "start_year": start_year,
            "end_year": end_year,
            "start_age": int(item.getStartAge()),
            "end_age": int(item.getEndAge()),
            "ganzhi": ganzhi,
            "display_ganzhi": ganzhi or "小运",
            "is_current": start_year <= current_year <= end_year,
            "stem": stem,
            "branch": branch,
            "stem_ten_god": ten_god(day_stem, stem) if stem else None,
            "stem_element": ELEMENT_BY_STEM.get(stem) if stem else None,
            "branch_element": ELEMENT_BY_BRANCH.get(branch) if branch else None,
            "di_shi": TWELVE_LIFE_STAGE_BY_STEM.get(day_stem, {}).get(branch, "") if branch else "",
            "xun_kong": "".join(resolve_empty_branches(ganzhi)) if ganzhi else "",
            "shen_sha": shen_sha_names(shen_sha_details),
            "shen_sha_details": shen_sha_details,
            "year_items": [
                _build_luck_year_item(liu_nian, day_stem, current_year, shen_sha_context=shen_sha_context)
                for liu_nian in item.getLiuNian()
            ],
        }
        if cycle["is_current"]:
            current_cycle_key = str(cycle["cycle_key"])
        cycles.append(cycle)
    return {
        "current_year": current_year,
        "current_cycle_key": current_cycle_key,
        "start_year": int(yun.getStartYear()),
        "start_month": int(yun.getStartMonth()),
        "start_day": int(yun.getStartDay()),
        "start_hour": int(yun.getStartHour()),
        "cycles": cycles,
    }


def build_dayun_facts(package: dict[str, Any], cycle_key: str) -> dict[str, Any]:
    chart = package["chart"]
    facts = package["deterministic_facts"]
    cycle = _find_luck_cycle(facts, cycle_key)
    if cycle is None:
        raise ValueError("luck_cycle_not_found")
    return _build_luck_render_facts(package, cycle=cycle, year_item=None)


def build_liunian_facts(package: dict[str, Any], cycle_key: str, year: int) -> dict[str, Any]:
    facts = package["deterministic_facts"]
    cycle = _find_luck_cycle(facts, cycle_key)
    if cycle is None:
        raise ValueError("luck_cycle_not_found")
    year_item = _find_luck_year(cycle, year)
    if year_item is None:
        raise ValueError("luck_year_not_found")
    return _build_luck_render_facts(package, cycle=cycle, year_item=year_item)


def score_chart(facts: dict[str, Any]) -> dict[str, Any]:
    strength = facts["day_master"]["strength"]
    interactions = facts["interactions"]
    score = 72
    if strength["level"] == "balanced":
        score += 8
    elif strength["level"] in {"weak", "strong"}:
        score -= 3
    else:
        score -= 8
    score -= min(16, len(interactions["clashes"]) * 4 + len(interactions["harms"]) * 3 + len(interactions["breaks"]) * 2)
    score += min(8, len(interactions["combinations"]) * 2 + len(interactions["six_harmonies"]) * 2)
    score = max(30, min(96, score))
    return {
        "final_score": score,
        "score_band": score_band(score),
        "strength_level": strength["level"],
        "risk_count": len(interactions["clashes"]) + len(interactions["harms"]) + len(interactions["breaks"]),
        "supportive_count": len(interactions["combinations"]) + len(interactions["six_harmonies"]),
        "aspect_scores": facts["aspect_scores"],
    }


def build_score_template(input_profile: dict[str, Any], chart: dict[str, Any], facts: dict[str, Any], score_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_profile": input_profile,
        "chart": chart,
        "deterministic_facts": facts,
        "score_summary": score_result,
    }


def build_score_markdown(package: dict[str, Any]) -> str:
    chart = package["chart"]
    facts = package["deterministic_facts"]
    score = package["score_result"]
    pillars = chart["pillars"]
    lines = [
        "# 四柱八字评测事实包",
        "",
        f"- 综合分：{score['final_score']}（{score['score_band']}）",
        f"- 四柱：{pillars['year']['ganzhi']} 年、{pillars['month']['ganzhi']} 月、{pillars['day']['ganzhi']} 日、{pillars['hour']['ganzhi']} 时",
        f"- 日主：{chart['day_master']}（{chart['day_master_element']}，{chart['day_master_yin_yang']}）",
        f"- 旺衰初判：{facts['day_master']['strength']['label']}",
        f"- 喜用候选：{'、'.join(facts['day_master']['favorable_elements'])}",
        f"- 需要节制：{'、'.join(facts['day_master']['unfavorable_elements'])}",
        "",
        "## 五行计数",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in facts["element_counts"].items())
    return "\n".join(lines)


def _normalize_input(payload: FourPillarsInput | dict[str, Any]) -> dict[str, Any]:
    data = payload.__dict__ if isinstance(payload, FourPillarsInput) else dict(payload)
    gender = str(data.get("gender") or "").strip()
    if gender not in {"male", "female"}:
        raise ValueError("invalid_gender")
    input_mode = str(data.get("input_mode") or "solar").strip() or "solar"
    birth_date, birth_time, source_meta = _resolve_standard_birth_datetime(data, input_mode)
    location = resolve_birth_location(data.get("birth_location") or data.get("birth_place"))
    timezone_name = str(data.get("timezone") or location.timezone or "Asia/Shanghai").strip() or "Asia/Shanghai"
    standard_dt = _parse_birth_datetime({"birth_date": birth_date, "birth_time": birth_time, "timezone": timezone_name})
    true_solar = calculate_true_solar_time(standard_dt, location)
    return {
        "gender": gender,
        "birth_date": true_solar["true_date"],
        "birth_time": true_solar["true_time"],
        "timezone": timezone_name,
        "birth_place": _optional_text(data.get("birth_place")) or location.display_name,
        "name": _optional_text(data.get("name")),
        "input_mode": input_mode,
        "standard_birth_date": birth_date,
        "standard_birth_time": birth_time,
        "standard_birth_datetime": true_solar["standard_datetime"],
        "effective_birth_datetime": true_solar["true_datetime"],
        "true_solar_time": true_solar,
        "birth_location": location.to_dict(),
        "input_source": source_meta,
    }


def _resolve_standard_birth_datetime(data: dict[str, Any], input_mode: str) -> tuple[str, str, dict[str, Any]]:
    if input_mode == "lunar":
        lunar_input = data.get("lunar_input") if isinstance(data.get("lunar_input"), dict) else data
        year = int(lunar_input.get("year"))
        month = int(lunar_input.get("month"))
        day = int(lunar_input.get("day"))
        hour = int(lunar_input.get("hour", 0))
        minute = int(lunar_input.get("minute", 0))
        is_leap = bool(lunar_input.get("is_leap_month"))
        lunar_month = -month if is_leap else month
        solar = Solar.fromLunar(year, lunar_month, day, hour, minute, 0) if hasattr(Solar, "fromLunar") else None
        if solar is None:
            from lunar_python import Lunar

            solar = Lunar.fromYmdHms(year, lunar_month, day, hour, minute, 0).getSolar()
        return solar.toYmd(), f"{solar.getHour():02d}:{solar.getMinute():02d}", {"mode": "lunar", "lunar_input": dict(lunar_input)}
    if input_mode == "bazi":
        bazi_input = data.get("bazi_input") if isinstance(data.get("bazi_input"), dict) else {}
        candidate = _resolve_bazi_candidate(bazi_input)
        return candidate["birth_date"], candidate["birth_time"], {"mode": "bazi", "bazi_input": dict(bazi_input), "candidate": candidate}
    calendar_input = data.get("calendar_input") if isinstance(data.get("calendar_input"), dict) else {}
    birth_date = str(data.get("birth_date") or calendar_input.get("birth_date") or "").strip()
    birth_time = str(data.get("birth_time") or calendar_input.get("birth_time") or "").strip()
    return birth_date, birth_time, {"mode": "solar"}


def _resolve_bazi_candidate(bazi_input: dict[str, Any]) -> dict[str, Any]:
    year = _normalize_ganzhi(str(bazi_input.get("year") or ""))
    month = _normalize_ganzhi(str(bazi_input.get("month") or ""))
    day = _normalize_ganzhi(str(bazi_input.get("day") or ""))
    hour = _normalize_ganzhi(str(bazi_input.get("hour") or ""))
    base_year = int(bazi_input.get("base_year") or 1801)
    items = Solar.fromBaZi(year, month, day, hour, base_year=base_year)
    if not items:
        raise ValueError("bazi_candidate_not_found")
    if bazi_input.get("candidate_index") is not None:
        selected = items[int(bazi_input.get("candidate_index") or 0)]
    else:
        target_year = int(bazi_input.get("target_year") or datetime.now().year)
        selected = min(items, key=lambda item: abs(int(item.getYear()) - target_year))
    return {
        "birth_date": selected.toYmd(),
        "birth_time": f"{selected.getHour():02d}:{selected.getMinute():02d}",
        "solar_datetime": selected.toYmdHms(),
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
    }


def _normalize_ganzhi(value: str) -> str:
    text = value.strip()
    if len(text) != 2 or text[0] not in STEMS or text[1] not in BRANCHES:
        raise ValueError("invalid_ganzhi")
    return text


def _parse_birth_datetime(input_profile: dict[str, Any]) -> datetime:
    try:
        tzinfo = ZoneInfo(str(input_profile.get("timezone") or "Asia/Shanghai"))
    except Exception as exc:
        raise ValueError("invalid_timezone") from exc
    try:
        date_part = str(input_profile["birth_date"])
        time_part = str(input_profile["birth_time"])
        return datetime.fromisoformat(f"{date_part}T{time_part}:00").replace(tzinfo=tzinfo)
    except Exception as exc:
        raise ValueError("invalid_birth_datetime") from exc


def _build_pillar(position: str, ganzhi: str, stem_ten_god: str, branch_ten_god: str) -> dict[str, Any]:
    stem, branch = ganzhi[0], ganzhi[1]
    return {
        "position": position,
        "ganzhi": ganzhi,
        "stem": stem,
        "branch": branch,
        "stem_element": ELEMENT_BY_STEM[stem],
        "branch_element": ELEMENT_BY_BRANCH[branch],
        "stem_yin_yang": YIN_YANG_BY_STEM[stem],
        "hidden_stems": HIDDEN_STEMS[branch],
        "stem_ten_god": stem_ten_god,
        "branch_ten_god": branch_ten_god,
    }


def as_pillar_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _build_display_pillar(
    *,
    key: str,
    pillar: dict[str, Any],
    eight_char: Any,
    na_yin_fallback: str,
    day_stem: str,
    day_branch: str,
    year_branch: str,
    month_branch: str,
    empty_branches: list[str],
    shen_sha_details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    suffix = {"year": "Year", "month": "Month", "day": "Day", "hour": "Time"}[key]
    ganzhi = str(pillar.get("ganzhi") or "").strip()
    stem = str(pillar.get("stem") or (ganzhi[0] if len(ganzhi) >= 2 else "")).strip()
    branch = str(pillar.get("branch") or (ganzhi[1] if len(ganzhi) >= 2 else "")).strip()
    hidden_stems_raw = _safe_list_call(eight_char, f"get{suffix}HideGan") or list(HIDDEN_STEMS.get(branch, []))
    branch_ten_gods = _safe_list_call(eight_char, f"get{suffix}ShiShenZhi")
    if not branch_ten_gods:
        branch_ten_gods = [ten_god(day_stem, item) for item in hidden_stems_raw if item in ELEMENT_BY_STEM]
    hidden_stems = [
        {
            "stem": hidden_stem,
            "element": ELEMENT_BY_STEM.get(hidden_stem, ""),
            "ten_god": branch_ten_gods[index] if index < len(branch_ten_gods) else ten_god(day_stem, hidden_stem),
        }
        for index, hidden_stem in enumerate(hidden_stems_raw)
        if hidden_stem in ELEMENT_BY_STEM
    ]
    resolved_shen_sha_details = (
        shen_sha_details
        if shen_sha_details is not None
        else resolve_display_shen_sha_details(
            branch=branch,
            day_stem=day_stem,
            day_branch=day_branch,
            year_branch=year_branch,
            month_branch=month_branch,
            empty_branches=empty_branches,
        )
    )
    return {
        "key": key,
        "label": PILLAR_LABELS[key],
        "ganzhi": ganzhi,
        "stem": stem,
        "branch": branch,
        "stem_element": ELEMENT_BY_STEM.get(stem, ""),
        "branch_element": ELEMENT_BY_BRANCH.get(branch, ""),
        "stem_ten_god": str(pillar.get("stem_ten_god") or ("日主" if key == "day" else "")).strip() or "-",
        "branch_ten_gods": [item for item in branch_ten_gods if str(item).strip()],
        "hidden_stems": hidden_stems,
        "na_yin": str(_safe_call(eight_char, f"get{suffix}NaYin") or na_yin_fallback or "").strip(),
        "xun_kong": str(_safe_call(eight_char, f"get{suffix}XunKong") or "").strip(),
        "di_shi": str(_safe_call(eight_char, f"get{suffix}DiShi") or "").strip(),
        "self_sitting": resolve_self_sitting(stem, branch),
        "shen_sha": shen_sha_names(resolved_shen_sha_details),
        "shen_sha_details": resolved_shen_sha_details,
    }


def resolve_self_sitting(stem: str, branch: str) -> str:
    return TWELVE_LIFE_STAGE_BY_STEM.get(stem, {}).get(branch, "")


def resolve_element_status(month_branch: str) -> list[dict[str, str]]:
    prosperous = SEASON_ELEMENT_BY_MONTH_BRANCH.get(month_branch)
    if not prosperous:
        return [{"element": element, "status": ""} for element in ("木", "火", "土", "金", "水")]
    status_by_element = {
        prosperous: "旺",
        GENERATES[prosperous]: "相",
        _generates_me(prosperous): "休",
        _controls_me(prosperous): "囚",
        CONTROLS[prosperous]: "死",
    }
    return [
        {"element": element, "status": status}
        for status in ("旺", "相", "休", "囚", "死")
        for element, item_status in status_by_element.items()
        if item_status == status
    ]


def resolve_display_shen_sha(
    *,
    branch: str,
    day_stem: str,
    day_branch: str,
    year_branch: str,
    month_branch: str,
    empty_branches: list[str],
    stem: str = "",
    ganzhi: str = "",
    year_stem: str = "",
    day_ganzhi: str = "",
    gender: str | None = None,
) -> list[str]:
    return shen_sha_names(
        resolve_display_shen_sha_details(
            branch=branch,
            day_stem=day_stem,
            day_branch=day_branch,
            year_branch=year_branch,
            month_branch=month_branch,
            empty_branches=empty_branches,
            stem=stem,
            ganzhi=ganzhi,
            year_stem=year_stem,
            day_ganzhi=day_ganzhi,
            gender=gender,
        )
    )


def resolve_display_shen_sha_details(
    *,
    branch: str,
    day_stem: str,
    day_branch: str,
    year_branch: str,
    month_branch: str,
    empty_branches: list[str],
    stem: str = "",
    ganzhi: str = "",
    year_stem: str = "",
    day_ganzhi: str = "",
    gender: str | None = None,
) -> list[dict[str, Any]]:
    context = ShenShaContext(
        year_stem=year_stem,
        year_branch=year_branch,
        month_branch=month_branch,
        day_stem=day_stem,
        day_branch=day_branch,
        day_ganzhi=day_ganzhi,
        gender=gender,
        empty_branches=tuple(empty_branches),
    )
    return calculate_target_shen_sha(context, target_stem=stem, target_branch=branch, target_ganzhi=ganzhi)


def ten_god(day_stem: str, target_stem: str) -> str:
    if day_stem == target_stem:
        return "比肩"
    day_element = ELEMENT_BY_STEM[day_stem]
    target_element = ELEMENT_BY_STEM[target_stem]
    same_yin_yang = YIN_YANG_BY_STEM[day_stem] == YIN_YANG_BY_STEM[target_stem]
    if target_element == day_element:
        return "比肩" if same_yin_yang else "劫财"
    if GENERATES[day_element] == target_element:
        return "食神" if same_yin_yang else "伤官"
    if GENERATES[target_element] == day_element:
        return "偏印" if same_yin_yang else "正印"
    if CONTROLS[day_element] == target_element:
        return "偏财" if same_yin_yang else "正财"
    if CONTROLS[target_element] == day_element:
        return "七杀" if same_yin_yang else "正官"
    return "未知"


def count_elements(stems: list[str], branches: list[str]) -> dict[str, int]:
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for stem in stems:
        counts[ELEMENT_BY_STEM[stem]] += 2
    for branch in branches:
        counts[ELEMENT_BY_BRANCH[branch]] += 2
        for hidden_stem in HIDDEN_STEMS[branch]:
            counts[ELEMENT_BY_STEM[hidden_stem]] += 1
    return counts


def detect_interactions(stems: list[str], branches: list[str]) -> dict[str, list[str]]:
    stem_pairs = list(_pairs(stems))
    branch_pairs = list(_pairs(branches))
    return {
        "combinations": sorted({STEM_COMBINATIONS[pair] for pair in stem_pairs if pair in STEM_COMBINATIONS}),
        "stem_clashes": sorted({STEM_CLASHES[pair] for pair in stem_pairs if pair in STEM_CLASHES}),
        "six_harmonies": sorted({BRANCH_SIX_HARMONIES[pair] for pair in branch_pairs if pair in BRANCH_SIX_HARMONIES}),
        "clashes": sorted({BRANCH_CLASHES[pair] for pair in branch_pairs if pair in BRANCH_CLASHES}),
        "harms": sorted({BRANCH_HARMS[pair] for pair in branch_pairs if pair in BRANCH_HARMS}),
        "breaks": sorted({BRANCH_BREAKS[pair] for pair in branch_pairs if pair in BRANCH_BREAKS}),
    }


def estimate_day_master_strength(day_element: str, month_branch: str, element_counts: dict[str, int]) -> dict[str, Any]:
    same = element_counts[day_element]
    resource = element_counts[_generates_me(day_element)]
    pressure = element_counts[_controls_me(day_element)]
    wealth_output = element_counts[GENERATES[day_element]] + element_counts[CONTROLS[day_element]]
    season_bonus = 4 if SEASON_ELEMENT_BY_MONTH_BRANCH.get(month_branch) == day_element else 0
    index = same * 2 + resource + season_bonus - pressure - wealth_output // 2
    if index >= 20:
        level = "overstrong"
        label = "日主偏旺，需要泄秀或财官来流通"
    elif index >= 13:
        level = "strong"
        label = "日主有根有助，承载力较强"
    elif index >= 8:
        level = "balanced"
        label = "日主中和，喜忌需要看结构流通"
    elif index >= 3:
        level = "weak"
        label = "日主偏弱，需要印比扶助"
    else:
        level = "overweak"
        label = "日主过弱，先看扶身与环境承接"
    return {"index": index, "level": level, "label": label}


def resolve_favorable_elements(day_element: str, strength: dict[str, Any]) -> dict[str, list[str]]:
    support = [day_element, _generates_me(day_element)]
    drain = [GENERATES[day_element], CONTROLS[day_element], _controls_me(day_element)]
    if strength["level"] in {"weak", "overweak"}:
        return {"favorable": support, "unfavorable": drain}
    if strength["level"] in {"strong", "overstrong"}:
        return {"favorable": drain, "unfavorable": support}
    return {"favorable": [GENERATES[day_element], _generates_me(day_element)], "unfavorable": []}


def resolve_empty_branches(day_ganzhi: str) -> list[str]:
    jiazi = [STEMS[index % 10] + BRANCHES[index % 12] for index in range(60)]
    try:
        index = jiazi.index(day_ganzhi)
    except ValueError:
        return []
    xun_start = (index // 10) * 10
    used_branches = {jiazi[item][1] for item in range(xun_start, xun_start + 10)}
    return [branch for branch in BRANCHES if branch not in used_branches]


def count_ten_gods(chart: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pillar in chart["pillars"].values():
        for key in ("stem_ten_god", "branch_ten_god"):
            value = str(pillar.get(key) or "")
            if value and value not in {"日主", "日支"}:
                counts[value] = counts.get(value, 0) + 1
    for items in chart["hidden_ten_gods"].values():
        for item in items:
            value = str(item.get("ten_god") or "")
            if value:
                counts[value] = counts.get(value, 0) + 1
    return counts


def build_aspect_scores(element_counts: dict[str, int], interactions: dict[str, list[str]], strength: dict[str, Any], ten_god_counts: dict[str, int]) -> dict[str, dict[str, Any]]:
    risk_penalty = len(interactions["clashes"]) * 4 + len(interactions["harms"]) * 3 + len(interactions["breaks"]) * 2
    flow_bonus = len(interactions["combinations"]) * 2 + len(interactions["six_harmonies"]) * 2
    base = 68 + flow_bonus - risk_penalty
    strength_bonus = 6 if strength["level"] == "balanced" else 2 if strength["level"] in {"strong", "weak"} else -4
    profiles = {
        "personality": ten_god_counts.get("比肩", 0) + ten_god_counts.get("食神", 0),
        "career": ten_god_counts.get("正官", 0) + ten_god_counts.get("七杀", 0) + element_counts.get("木", 0) // 3,
        "wealth": ten_god_counts.get("正财", 0) + ten_god_counts.get("偏财", 0),
        "love": ten_god_counts.get("正官", 0) + ten_god_counts.get("正财", 0),
        "health": -risk_penalty,
        "family_environment": len(interactions["six_harmonies"]) - len(interactions["harms"]),
    }
    result: dict[str, dict[str, Any]] = {}
    for aspect_key in FOUR_PILLARS_ASPECT_ORDER:
        raw_score = base + strength_bonus + int(profiles.get(aspect_key, 0)) * 2
        score = max(35, min(95, raw_score))
        result[aspect_key] = {"score": score, "level": score_band(score)}
    return result


def score_band(score: int) -> str:
    if score >= 85:
        return "high"
    if score >= 72:
        return "good"
    if score >= 60:
        return "mixed"
    return "risk"


def _pairs(items: list[str]):
    for left_index in range(len(items)):
        for right_index in range(left_index + 1, len(items)):
            yield frozenset((items[left_index], items[right_index]))


def _generates_me(element: str) -> str:
    for source, target in GENERATES.items():
        if target == element:
            return source
    return element


def _controls_me(element: str) -> str:
    for source, target in CONTROLS.items():
        if target == element:
            return source
    return element


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _safe_call(source: Any, method_name: str) -> Any:
    method = getattr(source, method_name, None)
    if not callable(method):
        return None
    try:
        return method()
    except Exception:
        return None


def _safe_list_call(source: Any, method_name: str) -> list[str]:
    value = _safe_call(source, method_name)
    if not isinstance(value, list):
        try:
            value = list(value) if value is not None else []
        except Exception:
            value = []
    return [str(item).strip() for item in value if str(item).strip()]


def _lunar_zodiac(lunar: Any) -> str | None:
    value = _safe_call(lunar, "getYearShengXiaoByLiChun") or _safe_call(lunar, "getYearShengXiao")
    text = str(value or "").strip()
    return text or None


def _solar_term_context(lunar: Any) -> str | None:
    previous = _safe_call(lunar, "getPrevJie") or _safe_call(lunar, "getPrevJieQi")
    next_item = _safe_call(lunar, "getNextJie") or _safe_call(lunar, "getNextJieQi")
    previous_name = str(_safe_call(previous, "getName") or previous or "").strip()
    next_name = str(_safe_call(next_item, "getName") or next_item or "").strip()
    if previous_name and next_name:
        return f"{previous_name}后{next_name}前"
    if previous_name:
        return f"{previous_name}后"
    if next_name:
        return f"{next_name}前"
    return None


def _ganzhi_with_nayin(ganzhi: Any, nayin: Any) -> str | None:
    ganzhi_text = str(ganzhi or "").strip()
    nayin_text = str(nayin or "").strip()
    if ganzhi_text and nayin_text:
        return f"{ganzhi_text}（{nayin_text}）"
    return ganzhi_text or None


def _xiu_text(lunar: Any) -> str | None:
    xiu = str(_safe_call(lunar, "getXiu") or "").strip()
    if not xiu:
        return None
    gong = str(_safe_call(lunar, "getGong") or "").strip()
    beast_by_gong = {"东": "东方苍龙", "南": "南方朱雀", "西": "西方白虎", "北": "北方玄武"}
    return f"{xiu}宿{beast_by_gong.get(gong, gong)}"


def _lunar_short_text(lunar: Any) -> str:
    year = str(_safe_call(lunar, "getYear") or "").strip()
    month_raw = int(_safe_call(lunar, "getMonth") or 0)
    day = str(_safe_call(lunar, "getDay") or "").strip()
    time_zhi = str(_safe_call(lunar, "getTimeZhi") or "").strip()
    month_prefix = "闰" if month_raw < 0 else ""
    month = str(abs(month_raw) or "").strip()
    if year and month and day and time_zhi:
        return f"{year}年{month_prefix}{month}月{day}{time_zhi}时"
    return str(_safe_call(lunar, "toString") or "").strip()


def _pillar_xun_kong_text(eight_char: Any) -> str | None:
    rows = [
        ("年", _safe_call(eight_char, "getYearXunKong")),
        ("月", _safe_call(eight_char, "getMonthXunKong")),
        ("日", _safe_call(eight_char, "getDayXunKong")),
        ("时", _safe_call(eight_char, "getTimeXunKong")),
    ]
    text = "、".join(f"{label}{value}" for label, value in rows if str(value or "").strip())
    return text or None


def _chart_empty_branches_text(eight_char: Any) -> str | None:
    values = [
        str(_safe_call(eight_char, "getYearXunKong") or "").strip(),
        str(_safe_call(eight_char, "getMonthXunKong") or "").strip(),
        str(_safe_call(eight_char, "getDayXunKong") or "").strip(),
    ]
    branches: list[str] = []
    for value in values:
        for char in value:
            if char in BRANCHES and char not in branches:
                branches.append(char)
    return "".join(branches) or None


def _life_gua_text(year: int, gender: str) -> str | None:
    if gender not in {"male", "female"}:
        return None
    last_two = year % 100
    if year >= 2000:
        number = (99 - last_two) % 9 if gender == "male" else (last_two + 6) % 9
    else:
        number = (100 - last_two) % 9 if gender == "male" else (last_two - 4) % 9
    if number == 0:
        number = 9
    if number == 5:
        number = 2 if gender == "male" else 8
    gua_names = {
        1: "坎",
        2: "坤",
        3: "震",
        4: "巽",
        6: "乾",
        7: "兑",
        8: "艮",
        9: "离",
    }
    name = gua_names.get(number)
    group = "东四命" if number in {1, 3, 4, 9} else "西四命"
    return f"{name}卦{group}" if name else None


def _trinity_targets(branch: str) -> dict[str, str]:
    for branches, targets in TRINITY_GROUP_TARGETS:
        if branch in branches:
            return targets
    return {}


def _build_luck_year_item(
    liu_nian: Any,
    day_stem: str,
    current_year: int,
    *,
    shen_sha_context: ShenShaContext,
) -> dict[str, Any]:
    year = int(liu_nian.getYear())
    ganzhi = str(liu_nian.getGanZhi())
    stem = ganzhi[0]
    branch = ganzhi[1]
    shen_sha_details = calculate_target_shen_sha(
        shen_sha_context,
        target_stem=stem,
        target_branch=branch,
        target_ganzhi=ganzhi,
        target_key="liunian",
    )
    return {
        "year": year,
        "age": int(liu_nian.getAge()),
        "ganzhi": ganzhi,
        "stem": stem,
        "branch": branch,
        "stem_ten_god": ten_god(day_stem, stem),
        "stem_element": ELEMENT_BY_STEM[stem],
        "branch_element": ELEMENT_BY_BRANCH[branch],
        "di_shi": TWELVE_LIFE_STAGE_BY_STEM.get(day_stem, {}).get(branch, ""),
        "xun_kong": "".join(resolve_empty_branches(ganzhi)),
        "shen_sha": shen_sha_names(shen_sha_details),
        "shen_sha_details": shen_sha_details,
        "is_current": year == current_year,
    }


def _luck_cycle_key(start_year: int, end_year: int, ganzhi: str) -> str:
    suffix = ganzhi if ganzhi else "start"
    return f"dy_{start_year}_{end_year}_{suffix}"


def _find_luck_cycle(facts: dict[str, Any], cycle_key: str) -> dict[str, Any] | None:
    luck_cycles = facts.get("luck_cycles") if isinstance(facts.get("luck_cycles"), dict) else {}
    for cycle in luck_cycles.get("cycles", []):
        if isinstance(cycle, dict) and str(cycle.get("cycle_key") or "") == cycle_key:
            return cycle
    return None


def _find_luck_year(cycle: dict[str, Any], year: int) -> dict[str, Any] | None:
    for item in cycle.get("year_items", []):
        if isinstance(item, dict) and int(item.get("year") or 0) == int(year):
            return item
    return None


def _build_luck_render_facts(
    package: dict[str, Any],
    *,
    cycle: dict[str, Any],
    year_item: dict[str, Any] | None,
) -> dict[str, Any]:
    chart = package["chart"]
    facts = package["deterministic_facts"]
    original_stems = [chart["pillars"][key]["stem"] for key in ("year", "month", "day", "hour")]
    original_branches = [chart["pillars"][key]["branch"] for key in ("year", "month", "day", "hour")]
    added_stems = [str(cycle.get("stem") or "")]
    added_branches = [str(cycle.get("branch") or "")]
    if year_item:
        added_stems.append(str(year_item.get("stem") or ""))
        added_branches.append(str(year_item.get("branch") or ""))
    added_stems = [item for item in added_stems if item in STEMS]
    added_branches = [item for item in added_branches if item in BRANCHES]
    combined_interactions = detect_interactions(original_stems + added_stems, original_branches + added_branches)
    special_tags = _luck_special_tags(cycle, year_item)
    return {
        "render_type": "liunian" if year_item else "dayun",
        "input_summary": facts.get("input_summary", {}),
        "locked_chart": {
            "year_ganzhi": chart.get("year_ganzhi"),
            "month_ganzhi": chart.get("month_ganzhi"),
            "day_ganzhi": chart.get("day_ganzhi"),
            "hour_ganzhi": chart.get("hour_ganzhi"),
            "day_master": chart.get("day_master"),
            "day_master_element": chart.get("day_master_element"),
        },
        "base_score": package.get("score_result", {}),
        "day_master": facts.get("day_master", {}),
        "base_element_counts": facts.get("element_counts", {}),
        "base_ten_god_counts": facts.get("ten_god_counts", {}),
        "base_interactions": facts.get("interactions", {}),
        "selected_cycle": {
            key: cycle.get(key)
            for key in (
                "cycle_key",
                "start_year",
                "end_year",
                "start_age",
                "end_age",
                "ganzhi",
                "display_ganzhi",
                "stem",
                "branch",
                "stem_ten_god",
                "stem_element",
                "branch_element",
                "is_current",
                "shen_sha",
                "shen_sha_details",
            )
        },
        "selected_year": dict(year_item) if year_item else None,
        "combined_interactions": combined_interactions,
        "empty_branch_hits": [branch for branch in added_branches if branch in facts.get("empty_branches", [])],
        "tomb_hits": [{"branch": branch, "meaning": TOMB_BRANCHES[branch]} for branch in added_branches if branch in TOMB_BRANCHES],
        "luck_shen_sha": {
            "dayun": cycle.get("shen_sha_details", []),
            "liunian": year_item.get("shen_sha_details", []) if year_item else [],
        },
        "special_tags": special_tags,
        "favorable_element_hits": [
            element
            for element in _elements_for_luck_items(cycle, year_item)
            if element in facts.get("day_master", {}).get("favorable_elements", [])
        ],
        "unfavorable_element_hits": [
            element
            for element in _elements_for_luck_items(cycle, year_item)
            if element in facts.get("day_master", {}).get("unfavorable_elements", [])
        ],
    }


def _elements_for_luck_items(cycle: dict[str, Any], year_item: dict[str, Any] | None) -> list[str]:
    values = [
        str(cycle.get("stem_element") or ""),
        str(cycle.get("branch_element") or ""),
    ]
    if year_item:
        values.extend([str(year_item.get("stem_element") or ""), str(year_item.get("branch_element") or "")])
    return [item for item in values if item]


def _luck_special_tags(cycle: dict[str, Any], year_item: dict[str, Any] | None) -> list[dict[str, str]]:
    tags: list[dict[str, str]] = []
    for source, details in (
        ("dayun", cycle.get("shen_sha_details", [])),
        ("liunian", year_item.get("shen_sha_details", []) if year_item else []),
    ):
        if not isinstance(details, list):
            continue
        for item in details:
            if not isinstance(item, dict):
                continue
            tag = str(item.get("name") or "").strip()
            if not tag:
                continue
            tags.append(
                {
                    "tag": tag,
                    "source": source,
                    "target": str(item.get("target") or ""),
                    "target_value": str(item.get("target_value") or ""),
                    "meaning": str(item.get("meaning") or ""),
                }
            )
    return tags
