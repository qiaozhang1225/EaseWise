from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable
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
    {"aspect_key": "wealth", "title": "财运"},
    {"aspect_key": "marriage", "title": "婚姻"},
    {"aspect_key": "career", "title": "事业"},
    {"aspect_key": "health", "title": "健康"},
    {"aspect_key": "fortune", "title": "运势"},
    {"aspect_key": "investment", "title": "投资"},
    {"aspect_key": "social", "title": "人际"},
    {"aspect_key": "industry", "title": "行业"},
    {"aspect_key": "fengshui", "title": "风水"},
    {"aspect_key": "family", "title": "家庭"},
    {"aspect_key": "pattern", "title": "格局"},
]
FOUR_PILLARS_ASPECT_ORDER = [item["aspect_key"] for item in FOUR_PILLARS_ASPECTS]
FOUR_PILLARS_ASPECT_ALIASES: dict[str, str] = {
    "love": "marriage",
    "annual_trend": "fortune",
}
FOUR_PILLARS_ASPECT_EXPANSION_ALIASES: dict[str, tuple[str, ...]] = {
    "love": ("marriage",),
    "annual_trend": ("fortune",),
    "family_environment": ("family", "fengshui"),
}

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
SUMMARY_CARD_ORDER = (
    "marriage",
    "wealth",
    "health",
    "risk_window",
    "family_environment",
    "ancestral_environment",
    "favorable_strategy",
    "pattern",
)
SUMMARY_CARD_LABELS = {
    "marriage": "婚恋稳定度",
    "wealth": "财富格局",
    "health": "健康消耗点",
    "risk_window": "风险窗口",
    "family_environment": "早年家庭",
    "ancestral_environment": "祖上环境",
    "favorable_strategy": "喜忌策略",
    "pattern": "命格主轴",
}
RISK_SHEN_SHA_NAMES = {"灾煞", "羊刃", "飞刃", "劫煞", "亡神", "元辰", "五鬼", "勾煞", "绞煞", "魁罡", "阴阳差错"}
RELATIONSHIP_SHEN_SHA_NAMES = {"桃花", "红鸾", "天喜", "孤辰", "寡宿", "阴阳差错"}
ENVIRONMENT_SYMBOLS_BY_BRANCH = {
    "子": ["水边", "低洼处", "流动水气", "夜间或寒湿环境"],
    "丑": ["坟地", "池塘", "井", "庙宇", "湿土杂物处"],
    "寅": ["树林", "高坡", "道路转角", "木器或生发之地"],
    "卯": ["花草", "门窗", "小路", "竹木环境"],
    "辰": ["水库", "河堤", "土坡", "旧宅或湿土环境"],
    "巳": ["火炉", "电器", "路口", "热闹明亮处"],
    "午": ["高地", "阳光强处", "学校礼堂", "马路或开阔地"],
    "未": ["园地", "坟地", "土堆", "旧墙或杂草处"],
    "申": ["道路", "金属器物", "车辆", "机器或变动场"],
    "酉": ["门窗", "金属器物", "小路", "整洁明亮处"],
    "戌": ["高土", "坟地", "庙宇", "仓库或燥土环境"],
    "亥": ["河流", "水沟", "低洼寒湿处", "远行或流动环境"],
}
ELEMENT_SUPPORT_ENVIRONMENTS = {
    "木": "多接触学习、生长、绿植、东方感和长期积累型环境",
    "火": "多接触阳光、表达、曝光、南方感和节奏明快的环境",
    "土": "多接触稳定作息、土地、收纳、组织流程和长期承诺环境",
    "金": "多接触规则、工具、财务纪律、清爽空间和标准化环境",
    "水": "多接触流动信息、复盘、休息、北方感和弹性安排环境",
}
ELEMENT_AVOID_PATTERNS = {
    "木": "少陷入反复开新坑、情绪憋闷或只讲理想不落地",
    "火": "少陷入熬夜、冲动表达、情绪上头或过度曝光",
    "土": "少陷入拖延、过度承担、饮食失衡或被琐事困住",
    "金": "少陷入过度挑剔、硬碰硬、规则压力或冷处理关系",
    "水": "少陷入犹豫、逃避、寒湿懒散或信息过载",
}
ELEMENT_HEALTH_THEMES = {
    "木": "肝胆、筋膜伸展和情绪疏泄",
    "火": "睡眠、心火和循环压力",
    "土": "脾胃、消化和代谢节奏",
    "金": "呼吸、皮肤和干燥敏感",
    "水": "肾水、泌尿和寒湿恢复力",
}
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
    score_result: dict[str, Any] = {}
    score_template = build_review_template(normalized, chart, deterministic_facts)
    result = {
        "input_profile": normalized,
        "chart": chart,
        "deterministic_facts": deterministic_facts,
        "score_result": score_result,
        "score_template": score_template,
    }
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
    aspect_signals = build_aspect_signals(chart, element_counts, interactions, strength, ten_god_counts, favorable)
    shen_sha_context = build_shen_sha_context(chart, input_profile, empty_branches=empty_branches)
    shen_sha_by_pillar = calculate_chart_shen_sha(shen_sha_context, pillars)
    luck_cycles = build_luck_cycles(input_profile, chart=chart)
    summary_highlights = build_summary_highlights(
        chart=chart,
        input_profile=input_profile,
        element_counts=element_counts,
        interactions=interactions,
        strength=strength,
        ten_god_counts=ten_god_counts,
        favorable=favorable,
        empty_branches=empty_branches,
        tombs=tombs,
        shen_sha_by_pillar=shen_sha_by_pillar,
        luck_cycles=luck_cycles,
    )
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
        "summary_highlights": summary_highlights,
        "aspect_signals": aspect_signals,
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


def build_review_template(input_profile: dict[str, Any], chart: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_profile": input_profile,
        "chart": chart,
        "deterministic_facts": facts,
    }


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


def build_aspect_signals(
    chart: dict[str, Any],
    element_counts: dict[str, int],
    interactions: dict[str, list[str]],
    strength: dict[str, Any],
    ten_god_counts: dict[str, int],
    favorable: dict[str, list[str]],
) -> dict[str, Any]:
    sorted_ten_gods = sorted(ten_god_counts.items(), key=lambda item: (-item[1], item[0]))
    dominant_ten_gods = [{"name": key, "count": value} for key, value in sorted_ten_gods[:4] if value > 0]
    pillars = chart.get("pillars", {}) if isinstance(chart.get("pillars"), dict) else {}
    year_pillar = as_pillar_dict(pillars.get("year"))
    month_pillar = as_pillar_dict(pillars.get("month"))
    day_pillar = as_pillar_dict(pillars.get("day"))
    hour_pillar = as_pillar_dict(pillars.get("hour"))
    pattern_candidates = [item["name"] for item in dominant_ten_gods[:2]]
    if strength.get("level") in {"strong", "overstrong"}:
        pattern_candidates.append("身旺取流通")
    elif strength.get("level") in {"weak", "overweak"}:
        pattern_candidates.append("身弱取扶助")
    else:
        pattern_candidates.append("中和看流通")
    return {
        "dominant_ten_gods": dominant_ten_gods,
        "pattern_candidates": pattern_candidates[:4],
        "family_palaces": {
            "year": {"ganzhi": year_pillar.get("ganzhi"), "stem_ten_god": year_pillar.get("stem_ten_god"), "branch_ten_god": year_pillar.get("branch_ten_god")},
            "month": {"ganzhi": month_pillar.get("ganzhi"), "stem_ten_god": month_pillar.get("stem_ten_god"), "branch_ten_god": month_pillar.get("branch_ten_god")},
            "day": {"ganzhi": day_pillar.get("ganzhi"), "branch": day_pillar.get("branch")},
            "hour": {"ganzhi": hour_pillar.get("ganzhi"), "stem_ten_god": hour_pillar.get("stem_ten_god"), "branch_ten_god": hour_pillar.get("branch_ten_god")},
        },
        "career_wealth_signals": {
            "wealth_star_count": ten_god_counts.get("正财", 0) + ten_god_counts.get("偏财", 0),
            "officer_star_count": ten_god_counts.get("正官", 0) + ten_god_counts.get("七杀", 0),
            "output_star_count": ten_god_counts.get("食神", 0) + ten_god_counts.get("伤官", 0),
            "resource_star_count": ten_god_counts.get("正印", 0) + ten_god_counts.get("偏印", 0),
        },
        "environment_signals": {
            "element_counts": element_counts,
            "favorable_elements": favorable.get("favorable", []),
            "unfavorable_elements": favorable.get("unfavorable", []),
            "supportive_interactions": interactions.get("combinations", []) + interactions.get("six_harmonies", []),
            "stress_interactions": interactions.get("clashes", []) + interactions.get("harms", []) + interactions.get("breaks", []),
        },
    }


def build_summary_highlights(
    *,
    chart: dict[str, Any],
    input_profile: dict[str, Any],
    element_counts: dict[str, int],
    interactions: dict[str, list[str]],
    strength: dict[str, Any],
    ten_god_counts: dict[str, int],
    favorable: dict[str, list[str]],
    empty_branches: list[str],
    tombs: list[dict[str, str]],
    shen_sha_by_pillar: dict[str, list[dict[str, Any]]],
    luck_cycles: dict[str, Any],
) -> dict[str, Any]:
    pillars = chart.get("pillars", {}) if isinstance(chart.get("pillars"), dict) else {}
    year_pillar = as_pillar_dict(pillars.get("year"))
    month_pillar = as_pillar_dict(pillars.get("month"))
    day_pillar = as_pillar_dict(pillars.get("day"))
    hour_pillar = as_pillar_dict(pillars.get("hour"))
    gender = str(input_profile.get("gender") or "")
    day_element = str(chart.get("day_master_element") or "")
    day_branch = str(day_pillar.get("branch") or chart.get("day_branch") or "")
    branches = [str(as_pillar_dict(pillars.get(key)).get("branch") or "") for key in PILLAR_KEYS]
    stems = [str(as_pillar_dict(pillars.get(key)).get("stem") or "") for key in PILLAR_KEYS]

    wealth_star_count = ten_god_counts.get("正财", 0) + ten_god_counts.get("偏财", 0)
    officer_star_count = ten_god_counts.get("正官", 0) + ten_god_counts.get("七杀", 0)
    output_star_count = ten_god_counts.get("食神", 0) + ten_god_counts.get("伤官", 0)
    resource_star_count = ten_god_counts.get("正印", 0) + ten_god_counts.get("偏印", 0)
    peer_star_count = ten_god_counts.get("比肩", 0) + ten_god_counts.get("劫财", 0)
    spouse_star_label = "财星" if gender == "male" else "官杀"
    spouse_star_count = wealth_star_count if gender == "male" else officer_star_count
    day_branch_interactions = _branch_interaction_names(day_branch, branches)
    relationship_tags = _pillar_tag_names(shen_sha_by_pillar, "day", RELATIONSHIP_SHEN_SHA_NAMES)
    risk_tags = _all_tag_names(shen_sha_by_pillar, RISK_SHEN_SHA_NAMES)
    wealth_element = CONTROLS.get(day_element, "")
    wealth_tombs = [item for item in tombs if str(item.get("meaning") or "").startswith(wealth_element)]
    element_spread = max(element_counts.values()) - min(element_counts.values()) if element_counts else 0
    high_elements = [element for element, count in element_counts.items() if count == max(element_counts.values())]
    low_elements = [element for element, count in element_counts.items() if count == min(element_counts.values())]
    pattern_candidates = _summary_pattern_candidates(strength, ten_god_counts)
    risk_windows = _build_summary_life_risk_windows(
        chart=chart,
        luck_cycles=luck_cycles,
        interactions=interactions,
        favorable=favorable,
        empty_branches=empty_branches,
    )
    favorable_strategy = _build_summary_favorable_strategy(favorable)
    early_environment = _environment_reading_for_pillars(year_pillar, month_pillar)
    ancestral_environment = _environment_reading_for_pillars(year_pillar)
    special_patterns = _summary_special_patterns(ten_god_counts)

    cards = [
        {
            "key": "marriage",
            "label": SUMMARY_CARD_LABELS["marriage"],
            "level": _summary_level(len(day_branch_interactions) + len(relationship_tags) + (1 if spouse_star_count == 0 else 0)),
            "title": "重大关系要看夫妻宫稳定度和配偶星承接",
            "basis": [
                f"日支夫妻宫为{day_branch or '-'}",
                f"{spouse_star_label}数量为{spouse_star_count}",
                f"夫妻宫相关合冲刑害：{'、'.join(day_branch_interactions) if day_branch_interactions else '未见明显硬冲硬害'}",
                f"关系类神煞：{'、'.join(relationship_tags) if relationship_tags else '未见突出的关系神煞'}",
            ],
            "reading": "用于判断亲密关系是否容易被外部变化、沟通节奏或自我表达牵动，只能写稳定度和多段关系风险，不能写必然几婚。",
            "related_aspects": ["marriage", "family"],
        },
        {
            "key": "wealth",
            "label": SUMMARY_CARD_LABELS["wealth"],
            "level": _summary_level(wealth_star_count + len(wealth_tombs) + (1 if peer_star_count >= 3 else 0)),
            "title": "财富格局先看财星数量、财库和日主承载",
            "basis": [
                f"财星数量为{wealth_star_count}",
                f"比劫数量为{peer_star_count}",
                f"财库线索：{'、'.join(item['branch'] + item['meaning'] for item in wealth_tombs) if wealth_tombs else '未见直接财库'}",
                f"日主状态：{strength.get('label')}",
            ],
            "reading": "用于判断赚钱方式、资源聚拢能力和分财竞争，不能写确定发财或投资收益。",
            "related_aspects": ["wealth", "investment", "career"],
        },
        {
            "key": "health",
            "label": SUMMARY_CARD_LABELS["health"],
            "level": _summary_level((2 if element_spread >= 10 else 1 if element_spread >= 6 else 0) + len(risk_tags)),
            "title": "健康重点看五行偏枯、风险神煞和长期消耗方式",
            "basis": [
                f"五行最重：{'、'.join(high_elements)}，最弱：{'、'.join(low_elements)}",
                f"五行落到生活照护：{_health_theme_text(high_elements + low_elements)}",
                f"风险类神煞：{'、'.join(risk_tags) if risk_tags else '未见突出的高风险神煞'}",
            ],
            "reading": "用于提示容易消耗的生活系统和作息触发因素，不能写疾病诊断、寿命或必然患病。",
            "related_aspects": ["health", "fortune"],
        },
        {
            "key": "risk_window",
            "label": SUMMARY_CARD_LABELS["risk_window"],
            "level": risk_windows[0]["level"] if risk_windows else "low",
            "title": "人生风险窗口看大运流年是否触发忌神、冲刑、空亡或墓库",
            "basis": [
                f"原局合冲刑害：{_risk_interaction_text(interactions)}",
                f"高亮窗口：{risk_windows[0]['age_range'] + ' ' + risk_windows[0]['risk_type'] if risk_windows else '暂无突出的高风险窗口'}",
            ],
            "reading": "用于提示某些阶段更要保守决策、安全管理和减少硬碰硬，不写确定灾难。",
            "related_aspects": ["fortune", "health"],
        },
        {
            "key": "family_environment",
            "label": SUMMARY_CARD_LABELS["family_environment"],
            "level": _summary_level(resource_star_count + peer_star_count + len(_family_stress_interactions(branches))),
            "title": "早年家庭看年柱、月柱、印星和比劫的牵动",
            "basis": [
                f"年柱{year_pillar.get('ganzhi') or '-'}，月柱{month_pillar.get('ganzhi') or '-'}",
                f"印星数量为{resource_star_count}，比劫数量为{peer_star_count}",
                f"年/月相关压力：{'、'.join(_family_stress_interactions(branches)) if _family_stress_interactions(branches) else '未见明显硬性冲害'}",
            ],
            "reading": "用于判断父母、兄弟姐妹、早年家庭氛围和责任分配，不写父母早亡或具体疾病。",
            "related_aspects": ["family"],
        },
        {
            "key": "ancestral_environment",
            "label": SUMMARY_CARD_LABELS["ancestral_environment"],
            "level": _summary_level(len(tombs) + (1 if year_pillar.get("branch") in {"丑", "辰", "未", "戌"} else 0)),
            "title": "祖上和早年环境只按地支象意给倾向",
            "basis": [
                f"年支象意：{ancestral_environment}",
                f"年/月综合环境象意：{early_environment}",
                f"墓库线索：{'、'.join(item['branch'] + item['meaning'] for item in tombs) if tombs else '未见明显墓库'}",
            ],
            "reading": "用于提示小时候住处、祖上或坟地周围环境的象意倾向，不替代现场风水实勘。",
            "related_aspects": ["fengshui", "family"],
        },
        {
            "key": "favorable_strategy",
            "label": SUMMARY_CARD_LABELS["favorable_strategy"],
            "level": "medium",
            "title": "喜忌神决定更顺手的环境和应节制的行为",
            "basis": [
                f"喜用候选：{'、'.join(favorable.get('favorable', [])) or '-'}",
                f"忌神候选：{'、'.join(favorable.get('unfavorable', [])) or '-'}",
                f"适合环境：{'；'.join(favorable_strategy['supportive_environments'])}",
            ],
            "reading": "用于给行动策略，不把喜忌写成绝对吉凶。",
            "related_aspects": ["industry", "fengshui", "pattern"],
        },
        {
            "key": "pattern",
            "label": SUMMARY_CARD_LABELS["pattern"],
            "level": _summary_level(max(ten_god_counts.values()) if ten_god_counts else 0),
            "title": "命格主轴看最突出的十神如何配合日主强弱",
            "basis": [
                f"命格候选：{'、'.join(pattern_candidates)}",
                f"特殊组合：{'、'.join(item['name'] for item in special_patterns) if special_patterns else '未见突出的强组合'}",
                f"主导十神：{_dominant_ten_god_text(ten_god_counts)}",
                f"日主强弱：{strength.get('label')}",
            ],
            "reading": "用于说明资源获取、表达方式、压力处理和成长路径，不能只堆正印、伤官、七杀等术语。",
            "related_aspects": ["pattern", "personality", "career"],
        },
    ]
    return {
        "version": "summary_v2",
        "judgement_policy": "强判断 + 概率表达；不写必然婚灾、确诊疾病、确定灾祸或寿命断语。",
        "card_order": list(SUMMARY_CARD_ORDER),
        "key_judgement_facts": cards,
        "life_risk_windows": risk_windows,
        "special_patterns": special_patterns,
        "favorable_strategy": favorable_strategy,
        "environment_symbols": {
            "early_family": early_environment,
            "ancestral": ancestral_environment,
        },
    }


def _summary_special_patterns(ten_god_counts: dict[str, int]) -> list[dict[str, str]]:
    candidates = [
        (
            "伤官见官",
            ten_god_counts.get("伤官", 0) > 0 and ten_god_counts.get("正官", 0) > 0,
            "表达突破和规则压力同时出现，现实里容易因说话方式、制度边界或上级评价起冲突。",
        ),
        (
            "伤官重",
            ten_god_counts.get("伤官", 0) >= 2,
            "伤官代表表达强、主见重，数量偏多时现实里更容易锋芒外露或挑战规则。",
        ),
        (
            "枭神夺食",
            ten_god_counts.get("偏印", 0) > 0 and ten_god_counts.get("食神", 0) > 0,
            "偏印代表敏感钻研，食神代表稳定输出，两者相见时容易想得多、快乐感下降或输出被打断。",
        ),
        (
            "官杀混杂",
            ten_god_counts.get("正官", 0) > 0 and ten_god_counts.get("七杀", 0) > 0,
            "规则责任和竞争压力同时出现，现实里容易既想稳定又被高压目标推着走。",
        ),
        (
            "比劫夺财",
            ten_god_counts.get("比肩", 0) + ten_god_counts.get("劫财", 0) >= 2 and ten_god_counts.get("正财", 0) + ten_god_counts.get("偏财", 0) > 0,
            "比劫代表同辈竞争和自我主张，遇到财星时容易出现合作分账、资源被分走或冲动支出。",
        ),
        (
            "食伤生财",
            ten_god_counts.get("食神", 0) + ten_god_counts.get("伤官", 0) > 0 and ten_god_counts.get("正财", 0) + ten_god_counts.get("偏财", 0) > 0,
            "表达、技能和产品输出能带动资源交换，现实里适合靠专业能力、作品或经营能力赚钱。",
        ),
    ]
    return [
        {"name": name, "meaning": meaning}
        for name, matched, meaning in candidates
        if matched
    ][:5]


def _build_summary_life_risk_windows(
    *,
    chart: dict[str, Any],
    luck_cycles: dict[str, Any],
    interactions: dict[str, list[str]],
    favorable: dict[str, list[str]],
    empty_branches: list[str],
) -> list[dict[str, Any]]:
    pillars = chart.get("pillars", {}) if isinstance(chart.get("pillars"), dict) else {}
    original_stems = [str(as_pillar_dict(pillars.get(key)).get("stem") or "") for key in PILLAR_KEYS]
    original_branches = [str(as_pillar_dict(pillars.get(key)).get("branch") or "") for key in PILLAR_KEYS]
    original_stems = [item for item in original_stems if item in STEMS]
    original_branches = [item for item in original_branches if item in BRANCHES]
    base_risks = set(interactions.get("clashes", []) + interactions.get("harms", []) + interactions.get("breaks", []) + interactions.get("stem_clashes", []))
    unfavorable_elements = set(favorable.get("unfavorable", []))
    windows: list[dict[str, Any]] = []
    for cycle in luck_cycles.get("cycles", []):
        if not isinstance(cycle, dict):
            continue
        for year_item in cycle.get("year_items", []):
            if not isinstance(year_item, dict):
                continue
            added_stems = [str(cycle.get("stem") or ""), str(year_item.get("stem") or "")]
            added_branches = [str(cycle.get("branch") or ""), str(year_item.get("branch") or "")]
            added_stems = [item for item in added_stems if item in STEMS]
            added_branches = [item for item in added_branches if item in BRANCHES]
            combined = detect_interactions(original_stems + added_stems, original_branches + added_branches)
            combined_risks = set(combined.get("clashes", []) + combined.get("harms", []) + combined.get("breaks", []) + combined.get("stem_clashes", []))
            new_risks = sorted(combined_risks - base_risks)
            trigger_tags: list[str] = []
            basis: list[str] = []
            priority_weight = 0
            if str(cycle.get("ganzhi") or "") and str(cycle.get("ganzhi") or "") == str(year_item.get("ganzhi") or ""):
                trigger_tags.append("岁运并临")
                basis.append(f"大运与流年同为{cycle.get('ganzhi')}")
                priority_weight += 5
            added_elements = [
                str(cycle.get("stem_element") or ""),
                str(cycle.get("branch_element") or ""),
                str(year_item.get("stem_element") or ""),
                str(year_item.get("branch_element") or ""),
            ]
            unfavorable_hits = [element for element in added_elements if element and element in unfavorable_elements]
            if unfavorable_hits:
                trigger_tags.append("忌神加强")
                basis.append(f"忌神元素被大运/流年触发：{'、'.join(dict.fromkeys(unfavorable_hits))}")
                priority_weight += 3
            if new_risks:
                trigger_tags.append("刑冲补齐")
                basis.append(f"新增合冲刑害压力：{'、'.join(new_risks)}")
                priority_weight += 3
            empty_hits = [branch for branch in added_branches if branch in empty_branches]
            if empty_hits:
                trigger_tags.append("空亡触发")
                basis.append(f"空亡地支被触发：{'、'.join(dict.fromkeys(empty_hits))}")
                priority_weight += 2
            tomb_hits = [branch for branch in added_branches if branch in TOMB_BRANCHES]
            if tomb_hits:
                trigger_tags.append("墓库触发")
                basis.append(f"墓库地支被触发：{'、'.join(branch + TOMB_BRANCHES[branch] for branch in dict.fromkeys(tomb_hits))}")
                priority_weight += 2
            risk_shen_sha = _risk_shen_sha_for_luck(cycle, year_item)
            if risk_shen_sha:
                trigger_tags.extend(name for name in risk_shen_sha if name not in trigger_tags)
                basis.append(f"风险类神煞：{'、'.join(risk_shen_sha)}")
                priority_weight += min(4, len(risk_shen_sha))
            if priority_weight < 4:
                continue
            year = int(year_item.get("year") or 0)
            age = int(year_item.get("age") or 0)
            windows.append(
                {
                    "start_year": year,
                    "end_year": year,
                    "start_age": age,
                    "end_age": age,
                    "age_range": f"{age}岁" if age else f"{year}年",
                    "risk_type": _risk_window_type(trigger_tags),
                    "level": "high" if priority_weight >= 8 else "medium",
                    "trigger_tags": list(dict.fromkeys(trigger_tags)),
                    "basis": basis,
                    "reality_focus": "这一年更适合保守决策、注意安全与健康管理，减少关系和规则上的硬碰硬。",
                    "priority_weight": priority_weight,
                }
            )
    windows.sort(key=lambda item: (-int(item.get("priority_weight") or 0), int(item.get("start_year") or 9999)))
    return [{key: value for key, value in item.items() if key != "priority_weight"} for item in windows[:5]]


def _build_summary_favorable_strategy(favorable: dict[str, list[str]]) -> dict[str, Any]:
    favorable_elements = list(favorable.get("favorable", []))
    unfavorable_elements = list(favorable.get("unfavorable", []))
    return {
        "favorable_elements": favorable_elements,
        "unfavorable_elements": unfavorable_elements,
        "supportive_environments": [ELEMENT_SUPPORT_ENVIRONMENTS[element] for element in favorable_elements if element in ELEMENT_SUPPORT_ENVIRONMENTS],
        "avoid_patterns": [ELEMENT_AVOID_PATTERNS[element] for element in unfavorable_elements if element in ELEMENT_AVOID_PATTERNS],
        "useful_actions": ["先稳作息和现金流", "把合作边界说清楚", "选择能放大喜用元素的行业、空间和节奏"],
    }


def _summary_pattern_candidates(strength: dict[str, Any], ten_god_counts: dict[str, int]) -> list[str]:
    sorted_items = sorted(ten_god_counts.items(), key=lambda item: (-item[1], item[0]))
    candidates = [name for name, count in sorted_items[:3] if count > 0]
    level = str(strength.get("level") or "")
    if level in {"strong", "overstrong"}:
        candidates.append("身旺取流通")
    elif level in {"weak", "overweak"}:
        candidates.append("身弱取扶助")
    else:
        candidates.append("中和看流通")
    return candidates[:4]


def _branch_interaction_names(branch: str, branches: list[str]) -> list[str]:
    if branch not in BRANCHES:
        return []
    names: list[str] = []
    for other in branches:
        if other == branch or other not in BRANCHES:
            continue
        pair = frozenset((branch, other))
        for source in (BRANCH_CLASHES, BRANCH_HARMS, BRANCH_BREAKS, BRANCH_SIX_HARMONIES):
            name = source.get(pair)
            if name and name not in names:
                names.append(name)
    return names


def _family_stress_interactions(branches: list[str]) -> list[str]:
    family_branches = [branch for branch in branches[:2] if branch in BRANCHES]
    names: list[str] = []
    for branch in family_branches:
        for name in _branch_interaction_names(branch, branches):
            if name.endswith(("冲", "害", "破")) and name not in names:
                names.append(name)
    return names


def _pillar_tag_names(shen_sha_by_pillar: dict[str, list[dict[str, Any]]], pillar_key: str, allowed_names: set[str]) -> list[str]:
    details = shen_sha_by_pillar.get(pillar_key, [])
    names: list[str] = []
    if not isinstance(details, list):
        return names
    for item in details:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "")
        if name in allowed_names and name not in names:
            names.append(name)
    return names


def _all_tag_names(shen_sha_by_pillar: dict[str, list[dict[str, Any]]], allowed_names: set[str]) -> list[str]:
    names: list[str] = []
    for pillar_key in PILLAR_KEYS:
        for name in _pillar_tag_names(shen_sha_by_pillar, pillar_key, allowed_names):
            if name not in names:
                names.append(name)
    return names


def _risk_shen_sha_for_luck(cycle: dict[str, Any], year_item: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for details in (cycle.get("shen_sha_details", []), year_item.get("shen_sha_details", [])):
        if not isinstance(details, list):
            continue
        for item in details:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "")
            if name in RISK_SHEN_SHA_NAMES and name not in names:
                names.append(name)
    return names


def _environment_reading_for_pillars(*pillars: dict[str, Any]) -> str:
    symbols: list[str] = []
    for pillar in pillars:
        branch = str(pillar.get("branch") or "")
        for symbol in ENVIRONMENT_SYMBOLS_BY_BRANCH.get(branch, []):
            if symbol not in symbols:
                symbols.append(symbol)
    return "、".join(symbols[:6]) if symbols else "环境象意不突出"


def _health_theme_text(elements: list[str]) -> str:
    themes: list[str] = []
    for element in elements:
        theme = ELEMENT_HEALTH_THEMES.get(element)
        if theme and theme not in themes:
            themes.append(theme)
    return "；".join(themes[:4]) if themes else "以作息、饮食和压力管理为主"


def _dominant_ten_god_text(ten_god_counts: dict[str, int]) -> str:
    items = [(name, count) for name, count in sorted(ten_god_counts.items(), key=lambda item: (-item[1], item[0])) if count > 0]
    return "、".join(f"{name}{count}" for name, count in items[:4]) if items else "十神不突出"


def _summary_level(weight: int) -> str:
    if weight >= 4:
        return "high"
    if weight >= 2:
        return "medium"
    return "low"


def _risk_interaction_text(interactions: dict[str, list[str]]) -> str:
    risks = interactions.get("clashes", []) + interactions.get("harms", []) + interactions.get("breaks", []) + interactions.get("stem_clashes", [])
    return "、".join(risks) if risks else "原局未见明显硬冲硬害"


def _risk_window_type(trigger_tags: list[str]) -> str:
    if "岁运并临" in trigger_tags:
        return "阶段压力与身份变化"
    if "忌神加强" in trigger_tags:
        return "长期消耗与保守决策"
    if any(tag in RISK_SHEN_SHA_NAMES for tag in trigger_tags):
        return "安全、是非与健康管理"
    if "刑冲补齐" in trigger_tags:
        return "关系变动与计划反复"
    return "阶段性风险管理"


def normalize_four_pillars_aspect_key(aspect_key: str) -> str:
    normalized = str(aspect_key or "").strip().lower()
    if normalized == "family_environment":
        return "family"
    return FOUR_PILLARS_ASPECT_ALIASES.get(normalized, normalized)


def expand_four_pillars_aspect_keys(aspect_keys: Iterable[str]) -> list[str]:
    expanded: list[str] = []
    for raw_key in aspect_keys:
        normalized = str(raw_key or "").strip().lower()
        candidates = FOUR_PILLARS_ASPECT_EXPANSION_ALIASES.get(normalized, (normalize_four_pillars_aspect_key(normalized),))
        for candidate in candidates:
            if candidate in FOUR_PILLARS_ASPECT_ORDER and candidate not in expanded:
                expanded.append(candidate)
    return expanded


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
