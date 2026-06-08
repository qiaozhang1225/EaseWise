from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from lunar_python import Solar

FOUR_PILLARS_ASPECTS: list[dict[str, str]] = [
    {"aspect_key": "personality", "title": "性格"},
    {"aspect_key": "career", "title": "事业"},
    {"aspect_key": "wealth", "title": "财富"},
    {"aspect_key": "love", "title": "婚恋"},
    {"aspect_key": "health", "title": "健康"},
    {"aspect_key": "family_environment", "title": "家庭环境"},
]
FOUR_PILLARS_ASPECT_ORDER = [item["aspect_key"] for item in FOUR_PILLARS_ASPECTS]

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


@dataclass(frozen=True)
class FourPillarsInput:
    gender: str
    birth_date: str
    birth_time: str
    timezone: str = "Asia/Shanghai"
    birth_place: str | None = None
    name: str | None = None


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
    gender_value = 1 if str(input_profile.get("gender")) == "male" else 0
    yun = lunar.getEightChar().getYun(gender_value)
    current_year = int(reference_year or datetime.now(birth_dt.tzinfo).year)
    cycles: list[dict[str, Any]] = []
    current_cycle_key: str | None = None
    for item in yun.getDaYun():
        start_year = int(item.getStartYear())
        end_year = int(item.getEndYear())
        ganzhi = str(item.getGanZhi() or "").strip()
        cycle = {
            "cycle_key": _luck_cycle_key(start_year, end_year, ganzhi),
            "start_year": start_year,
            "end_year": end_year,
            "start_age": int(item.getStartAge()),
            "end_age": int(item.getEndAge()),
            "ganzhi": ganzhi,
            "display_ganzhi": ganzhi or "起运前",
            "is_current": start_year <= current_year <= end_year,
            "stem": ganzhi[0] if len(ganzhi) >= 2 else None,
            "branch": ganzhi[1] if len(ganzhi) >= 2 else None,
            "stem_ten_god": ten_god(day_stem, ganzhi[0]) if len(ganzhi) >= 2 else None,
            "stem_element": ELEMENT_BY_STEM.get(ganzhi[0]) if len(ganzhi) >= 2 else None,
            "branch_element": ELEMENT_BY_BRANCH.get(ganzhi[1]) if len(ganzhi) >= 2 else None,
            "year_items": [_build_luck_year_item(liu_nian, day_stem, current_year) for liu_nian in item.getLiuNian()],
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
    birth_date = str(data.get("birth_date") or "").strip()
    birth_time = str(data.get("birth_time") or "").strip()
    timezone_name = str(data.get("timezone") or "Asia/Shanghai").strip() or "Asia/Shanghai"
    _parse_birth_datetime({"birth_date": birth_date, "birth_time": birth_time, "timezone": timezone_name})
    return {
        "gender": gender,
        "birth_date": birth_date,
        "birth_time": birth_time,
        "timezone": timezone_name,
        "birth_place": _optional_text(data.get("birth_place")),
        "name": _optional_text(data.get("name")),
    }


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


def _build_luck_year_item(liu_nian: Any, day_stem: str, current_year: int) -> dict[str, Any]:
    year = int(liu_nian.getYear())
    ganzhi = str(liu_nian.getGanZhi())
    stem = ganzhi[0]
    branch = ganzhi[1]
    return {
        "year": year,
        "age": int(liu_nian.getAge()),
        "ganzhi": ganzhi,
        "stem": stem,
        "branch": branch,
        "stem_ten_god": ten_god(day_stem, stem),
        "stem_element": ELEMENT_BY_STEM[stem],
        "branch_element": ELEMENT_BY_BRANCH[branch],
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
    special_tags = _luck_special_tags(chart, facts, added_branches)
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
            )
        },
        "selected_year": dict(year_item) if year_item else None,
        "combined_interactions": combined_interactions,
        "empty_branch_hits": [branch for branch in added_branches if branch in facts.get("empty_branches", [])],
        "tomb_hits": [{"branch": branch, "meaning": TOMB_BRANCHES[branch]} for branch in added_branches if branch in TOMB_BRANCHES],
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


def _luck_special_tags(chart: dict[str, Any], facts: dict[str, Any], branches: list[str]) -> list[dict[str, str]]:
    month_branch = str(chart.get("pillars", {}).get("month", {}).get("branch") or "")
    day_stem = str(chart.get("day_master") or "")
    five_ghost_branch = FIVE_GHOST_BRANCH_BY_MONTH_BRANCH.get(month_branch)
    lu_branch = LU_BRANCH_BY_DAY_STEM.get(day_stem)
    tags: list[dict[str, str]] = []
    for branch in branches:
        if branch == five_ghost_branch:
            tags.append({"tag": "五鬼", "branch": branch, "meaning": "偏财机会与是非损耗同时上升"})
        if branch == lu_branch:
            tags.append({"tag": "禄神", "branch": branch, "meaning": "职位、收入、贵人与稳定承接增强"})
        if branch in facts.get("empty_branches", []):
            tags.append({"tag": "空亡", "branch": branch, "meaning": "计划落空感或兑现力下降"})
        if branch in TOMB_BRANCHES:
            tags.append({"tag": "墓库", "branch": branch, "meaning": TOMB_BRANCHES[branch]})
    return tags
