from __future__ import annotations

from dataclasses import dataclass
from typing import Any

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
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

TOMB_BRANCHES = {"辰": "水库", "戌": "火库", "丑": "金库", "未": "木库"}
TIAN_YI_BRANCHES_BY_STEM = {
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
TAI_JI_BRANCHES_BY_STEM = {
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
WEN_CHANG_BRANCH_BY_STEM = {
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
GUO_YIN_BRANCH_BY_STEM = {
    "甲": "戌",
    "乙": "亥",
    "丙": "丑",
    "丁": "寅",
    "戊": "丑",
    "己": "寅",
    "庚": "辰",
    "辛": "巳",
    "壬": "未",
    "癸": "申",
}
JIN_YU_BRANCH_BY_STEM = {
    "甲": "辰",
    "乙": "巳",
    "丙": "未",
    "戊": "未",
    "丁": "申",
    "己": "申",
    "庚": "戌",
    "辛": "亥",
    "壬": "丑",
    "癸": "寅",
}
FU_XING_BRANCHES_BY_STEM = {
    "甲": ["寅", "子"],
    "丙": ["寅", "子"],
    "乙": ["卯", "丑"],
    "癸": ["卯", "丑"],
    "戊": ["申"],
    "己": ["未"],
    "丁": ["亥"],
    "庚": ["午"],
    "辛": ["巳"],
    "壬": ["辰"],
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
YANG_REN_BRANCH_BY_DAY_STEM = {
    "甲": "卯",
    "乙": "寅",
    "丙": "午",
    "丁": "巳",
    "戊": "午",
    "己": "巳",
    "庚": "酉",
    "辛": "申",
    "壬": "子",
    "癸": "亥",
}
FEI_REN_BRANCH_BY_DAY_STEM = {
    "甲": "酉",
    "乙": "申",
    "丙": "子",
    "丁": "丑",
    "戊": "子",
    "己": "丑",
    "庚": "卯",
    "辛": "辰",
    "壬": "午",
    "癸": "未",
}

TIAN_DE_TARGET_BY_MONTH_BRANCH = {
    "寅": "丁",
    "卯": "申",
    "辰": "壬",
    "巳": "辛",
    "午": "亥",
    "未": "甲",
    "申": "癸",
    "酉": "寅",
    "戌": "丙",
    "亥": "乙",
    "子": "巳",
    "丑": "庚",
}
TIAN_DE_HE_TARGET_BY_MONTH_BRANCH = {
    "寅": "壬",
    "卯": "巳",
    "辰": "丁",
    "巳": "丙",
    "午": "寅",
    "未": "己",
    "申": "戊",
    "酉": "亥",
    "戌": "辛",
    "亥": "庚",
    "子": "申",
    "丑": "乙",
}
YUE_DE_STEM_BY_MONTH_BRANCH = {
    "寅": "丙",
    "午": "丙",
    "戌": "丙",
    "申": "壬",
    "子": "壬",
    "辰": "壬",
    "亥": "甲",
    "卯": "甲",
    "未": "甲",
    "巳": "庚",
    "酉": "庚",
    "丑": "庚",
}
YUE_DE_HE_STEM_BY_MONTH_BRANCH = {
    "寅": "辛",
    "午": "辛",
    "戌": "辛",
    "申": "丁",
    "子": "丁",
    "辰": "丁",
    "亥": "己",
    "卯": "己",
    "未": "己",
    "巳": "乙",
    "酉": "乙",
    "丑": "乙",
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
TIAN_YI_MEDICINE_BRANCH_BY_MONTH_BRANCH = {
    "寅": "丑",
    "卯": "寅",
    "辰": "卯",
    "巳": "辰",
    "午": "巳",
    "未": "午",
    "申": "未",
    "酉": "申",
    "戌": "酉",
    "亥": "戌",
    "子": "亥",
    "丑": "子",
}

TRINITY_TARGETS_BY_BRANCH_GROUP = (
    (
        {"申", "子", "辰"},
        {"桃花": "酉", "驿马": "寅", "华盖": "辰", "将星": "子", "亡神": "亥", "劫煞": "巳"},
    ),
    (
        {"亥", "卯", "未"},
        {"桃花": "子", "驿马": "巳", "华盖": "未", "将星": "卯", "亡神": "寅", "劫煞": "申"},
    ),
    (
        {"巳", "酉", "丑"},
        {"桃花": "午", "驿马": "亥", "华盖": "丑", "将星": "酉", "亡神": "申", "劫煞": "寅"},
    ),
    (
        {"寅", "午", "戌"},
        {"桃花": "卯", "驿马": "申", "华盖": "戌", "将星": "午", "亡神": "巳", "劫煞": "亥"},
    ),
)
ZAI_SHA_BRANCH_BY_YEAR_BRANCH = {
    "申": "午",
    "子": "午",
    "辰": "午",
    "亥": "酉",
    "卯": "酉",
    "未": "酉",
    "寅": "子",
    "午": "子",
    "戌": "子",
    "巳": "卯",
    "酉": "卯",
    "丑": "卯",
}
GU_CHEN_GUA_SU_BY_YEAR_BRANCH_GROUP = (
    ({"亥", "子", "丑"}, {"孤辰": "寅", "寡宿": "戌"}),
    ({"寅", "卯", "辰"}, {"孤辰": "巳", "寡宿": "丑"}),
    ({"巳", "午", "未"}, {"孤辰": "申", "寡宿": "辰"}),
    ({"申", "酉", "戌"}, {"孤辰": "亥", "寡宿": "未"}),
)
HONG_LUAN_BRANCH_BY_YEAR_BRANCH = {
    "子": "卯",
    "丑": "寅",
    "寅": "丑",
    "卯": "子",
    "辰": "亥",
    "巳": "戌",
    "午": "酉",
    "未": "申",
    "申": "未",
    "酉": "午",
    "戌": "巳",
    "亥": "辰",
}
TIAN_XI_BRANCH_BY_YEAR_BRANCH = {
    "子": "酉",
    "丑": "申",
    "寅": "未",
    "卯": "午",
    "辰": "巳",
    "巳": "辰",
    "午": "卯",
    "未": "寅",
    "申": "丑",
    "酉": "子",
    "戌": "亥",
    "亥": "戌",
}
YUAN_CHEN_BRANCH_BY_YEAR_BRANCH_YANG_MALE_YIN_FEMALE = {
    "子": "未",
    "丑": "申",
    "寅": "酉",
    "卯": "戌",
    "辰": "亥",
    "巳": "子",
    "午": "丑",
    "未": "寅",
    "申": "卯",
    "酉": "辰",
    "戌": "巳",
    "亥": "午",
}
YUAN_CHEN_BRANCH_BY_YEAR_BRANCH_YIN_MALE_YANG_FEMALE = {
    "子": "巳",
    "丑": "午",
    "寅": "未",
    "卯": "申",
    "辰": "酉",
    "巳": "戌",
    "午": "亥",
    "未": "子",
    "申": "丑",
    "酉": "寅",
    "戌": "卯",
    "亥": "辰",
}

TIAN_SHE_DAY_BY_SEASON_BRANCHES = (
    ({"寅", "卯", "辰"}, "戊寅"),
    ({"巳", "午", "未"}, "甲午"),
    ({"申", "酉", "戌"}, "戊申"),
    ({"亥", "子", "丑"}, "甲子"),
)
KUI_GANG_DAYS = {"戊戌", "庚辰", "庚戌", "壬辰"}
YIN_YANG_CHA_CUO_DAYS = {
    "丙子",
    "丙午",
    "丁丑",
    "丁未",
    "戊寅",
    "戊申",
    "辛卯",
    "辛酉",
    "壬辰",
    "壬戌",
    "癸巳",
    "癸亥",
}
TONG_ZI_SEASON_TARGETS = (
    ({"寅", "卯", "辰", "申", "酉", "戌"}, {"寅", "子"}, "春秋寅子"),
    ({"巳", "午", "未", "亥", "子", "丑"}, {"卯", "未", "辰"}, "冬夏卯未辰"),
)
TONG_ZI_TARGETS_BY_NA_YIN_ELEMENT = {
    "金": {"午", "卯"},
    "木": {"午", "卯"},
    "水": {"酉", "戌"},
    "火": {"酉", "戌"},
    "土": {"辰", "巳"},
}
TONG_ZI_TARGET_KEYS = {"day", "hour", "dayun", "liunian"}

SHEN_SHA_META = {
    "天乙贵人": ("support", "人缘、贵人和外部支持"),
    "太极贵人": ("support", "学习、玄学、专研和稳定福气"),
    "福星贵人": ("support", "平安、福气、生活承接和贵人助力"),
    "文昌": ("talent", "学习、文书、表达和考试能力"),
    "国印贵人": ("support", "规则、资质、印信和组织背书"),
    "金舆": ("wealth", "配偶资源、交通载体和物质承接"),
    "天德贵人": ("support", "保护、福德和风险缓冲"),
    "月德贵人": ("support", "保护、善意和风险缓冲"),
    "天德合": ("support", "天德的协同保护信号"),
    "月德合": ("support", "月德的协同保护信号"),
    "禄神": ("wealth", "职位、收入、根气和承接力"),
    "羊刃": ("risk", "强硬、竞争、冲动和承载压力"),
    "飞刃": ("risk", "冲动、意外和对抗压力"),
    "桃花": ("relationship", "吸引力、外缘、审美和关系机会"),
    "驿马": ("movement", "移动、迁移、奔波和变化"),
    "华盖": ("talent", "艺术、专研、孤独感和精神兴趣"),
    "将星": ("support", "领导力、权柄和组织控制力"),
    "亡神": ("risk", "心机、隐藏压力和复杂是非"),
    "劫煞": ("risk", "竞争、破耗、对抗和突发阻力"),
    "灾煞": ("risk", "安全、健康和突发风险提醒"),
    "元辰": ("risk", "人情、酒色、冲动消费和社交损耗"),
    "孤辰": ("relationship", "独立、孤独感和亲缘淡薄"),
    "寡宿": ("relationship", "独立、婚缘浅和亲密疏离"),
    "红鸾": ("relationship", "喜庆、感情机会和关系推进"),
    "天喜": ("relationship", "喜庆、感情机会和关系推进"),
    "勾煞": ("risk", "牵连、阻碍和关系纠葛"),
    "绞煞": ("risk", "牵连、阻碍和关系纠葛"),
    "天医": ("health", "医药、照护、研究和健康议题"),
    "五鬼": ("risk", "偏财机会与是非损耗并见"),
    "童子": ("spiritual", "玄学、宗教缘分、敏感体质和关系压力的辅助信号"),
    "空亡": ("structure", "兑现力、稳定度和外显度下降"),
    "墓库": ("structure", "收藏、蓄积、迟滞和开库触发"),
    "天赦": ("support", "宽解、缓冲和转圜机会"),
    "魁罡": ("risk", "刚强、果断、权威和冲撞压力"),
    "阴阳差错": ("relationship", "关系错位、沟通拧巴和时机偏差"),
}
SHEN_SHA_DISPLAY_ORDER = {
    "天乙贵人": 10,
    "太极贵人": 20,
    "福星贵人": 30,
    "天德贵人": 40,
    "月德贵人": 41,
    "天德合": 42,
    "月德合": 43,
    "文昌": 50,
    "国印贵人": 51,
    "金舆": 60,
    "禄神": 61,
    "天喜": 70,
    "红鸾": 71,
    "童子": 72,
    "天医": 80,
    "华盖": 90,
    "将星": 100,
    "桃花": 110,
    "驿马": 120,
    "孤辰": 130,
    "寡宿": 131,
    "魁罡": 140,
    "天赦": 150,
    "羊刃": 200,
    "飞刃": 201,
    "亡神": 210,
    "劫煞": 211,
    "灾煞": 212,
    "元辰": 213,
    "勾煞": 214,
    "绞煞": 215,
    "五鬼": 216,
    "阴阳差错": 220,
    "空亡": 900,
    "墓库": 910,
}
SHEN_SHA_CATEGORY_ORDER = {
    "support": 10,
    "talent": 20,
    "wealth": 30,
    "relationship": 40,
    "spiritual": 45,
    "movement": 50,
    "health": 55,
    "risk": 60,
    "life_stage": 80,
    "structure": 90,
    "other": 99,
}


@dataclass(frozen=True)
class ShenShaContext:
    year_stem: str
    year_branch: str
    month_branch: str
    day_stem: str
    day_branch: str
    day_ganzhi: str
    year_na_yin: str | None = None
    gender: str | None = None
    empty_branches: tuple[str, ...] = ()


def calculate_target_shen_sha(
    context: ShenShaContext,
    *,
    target_stem: str | None = None,
    target_branch: str | None = None,
    target_ganzhi: str | None = None,
    target_key: str | None = None,
) -> list[dict[str, Any]]:
    stem = str(target_stem or "").strip()
    branch = str(target_branch or "").strip()
    ganzhi = str(target_ganzhi or (stem + branch if stem and branch else "")).strip()
    if not stem and len(ganzhi) >= 2:
        stem = ganzhi[0]
    if not branch and len(ganzhi) >= 2:
        branch = ganzhi[1]
    result: list[dict[str, Any]] = []

    _add_stem_based_branch_rules(result, context, stem=stem, branch=branch, ganzhi=ganzhi)
    _add_month_based_rules(result, context, stem=stem, branch=branch, ganzhi=ganzhi)
    _add_branch_group_rules(result, context, branch=branch, ganzhi=ganzhi)
    _add_year_branch_rules(result, context, branch=branch, ganzhi=ganzhi)
    _add_tong_zi_rules(result, context, branch=branch, target_key=target_key)
    _add_day_stem_rules(result, context, branch=branch, ganzhi=ganzhi)
    _add_common_structural_rules(result, context, branch=branch, ganzhi=ganzhi)
    if target_key == "day":
        _add_day_pillar_rules(result, context, ganzhi=ganzhi)

    return sort_shen_sha_details(_dedupe(result))


def calculate_chart_shen_sha(
    context: ShenShaContext,
    pillars: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for key in ("year", "month", "day", "hour"):
        pillar = pillars.get(key) if isinstance(pillars.get(key), dict) else {}
        result[key] = calculate_target_shen_sha(
            context,
            target_stem=str(pillar.get("stem") or ""),
            target_branch=str(pillar.get("branch") or ""),
            target_ganzhi=str(pillar.get("ganzhi") or ""),
            target_key=key,
        )
    return result


def shen_sha_names(details: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(str(item.get("name") or "") for item in details if str(item.get("name") or "").strip()))


def summarize_chart_shen_sha(pillar_details: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    categories: dict[str, list[str]] = {}
    for details in pillar_details.values():
        for item in details:
            name = str(item.get("name") or "")
            category = str(item.get("category") or "other")
            if not name:
                continue
            counts[name] = counts.get(name, 0) + 1
            categories.setdefault(category, [])
            if name not in categories[category]:
                categories[category].append(name)
    return {
        "counts": dict(sorted(counts.items())),
        "categories": {key: values for key, values in sorted(categories.items())},
    }


def sort_shen_sha_details(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for _, item in sorted(
            enumerate(items),
            key=lambda indexed: (
                SHEN_SHA_DISPLAY_ORDER.get(str(indexed[1].get("name") or ""), 500),
                SHEN_SHA_CATEGORY_ORDER.get(str(indexed[1].get("category") or "other"), 99),
                indexed[0],
            ),
        )
    ]


def _add_stem_based_branch_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    stem: str,
    branch: str,
    ganzhi: str,
) -> None:
    rules = (
        ("天乙贵人", TIAN_YI_BRANCHES_BY_STEM, "以日/年干查地支"),
        ("太极贵人", TAI_JI_BRANCHES_BY_STEM, "以日/年干查地支"),
        ("福星贵人", FU_XING_BRANCHES_BY_STEM, "以日/年干查地支"),
        ("文昌", WEN_CHANG_BRANCH_BY_STEM, "以日/年干查地支"),
        ("国印贵人", GUO_YIN_BRANCH_BY_STEM, "以日/年干查地支"),
        ("金舆", JIN_YU_BRANCH_BY_STEM, "以日/年干查地支"),
    )
    for basis, basis_value in (("day_stem", context.day_stem), ("year_stem", context.year_stem)):
        for name, rule_map, rule_text in rules:
            target = rule_map.get(basis_value)
            targets = target if isinstance(target, list) else [target]
            if branch in targets:
                _append(result, name, basis=basis, basis_value=basis_value, target="branch", target_value=branch, rule=rule_text)


def _add_month_based_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    stem: str,
    branch: str,
    ganzhi: str,
) -> None:
    month_rules = (
        ("天德贵人", TIAN_DE_TARGET_BY_MONTH_BRANCH, "以月支查四柱干支"),
        ("天德合", TIAN_DE_HE_TARGET_BY_MONTH_BRANCH, "以月支查四柱干支"),
        ("月德贵人", YUE_DE_STEM_BY_MONTH_BRANCH, "以月支查四柱天干"),
        ("月德合", YUE_DE_HE_STEM_BY_MONTH_BRANCH, "以月支查四柱天干"),
        ("天医", TIAN_YI_MEDICINE_BRANCH_BY_MONTH_BRANCH, "以月支查地支"),
        ("五鬼", FIVE_GHOST_BRANCH_BY_MONTH_BRANCH, "以月令后推五位查地支"),
    )
    for name, rule_map, rule_text in month_rules:
        target = rule_map.get(context.month_branch)
        if _matches_target(target, stem=stem, branch=branch, ganzhi=ganzhi):
            _append(
                result,
                name,
                basis="month_branch",
                basis_value=context.month_branch,
                target=_target_type(target),
                target_value=str(target),
                rule=rule_text,
            )


def _add_branch_group_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    branch: str,
    ganzhi: str,
) -> None:
    for basis, basis_value in (("day_branch", context.day_branch), ("year_branch", context.year_branch)):
        targets = _trinity_targets(basis_value)
        for name, target_branch in targets.items():
            if branch == target_branch:
                _append(
                    result,
                    name,
                    basis=basis,
                    basis_value=basis_value,
                    target="branch",
                    target_value=branch,
                    rule="以年/日支三合组查地支",
                )


def _add_year_branch_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    branch: str,
    ganzhi: str,
) -> None:
    if branch == ZAI_SHA_BRANCH_BY_YEAR_BRANCH.get(context.year_branch):
        _append(result, "灾煞", basis="year_branch", basis_value=context.year_branch, target="branch", target_value=branch, rule="以年支查地支")
    lonely_targets = _lonely_targets(context.year_branch)
    for name, target_branch in lonely_targets.items():
        if branch == target_branch:
            _append(result, name, basis="year_branch", basis_value=context.year_branch, target="branch", target_value=branch, rule="以年支查地支")
    if branch == HONG_LUAN_BRANCH_BY_YEAR_BRANCH.get(context.year_branch):
        _append(result, "红鸾", basis="year_branch", basis_value=context.year_branch, target="branch", target_value=branch, rule="以年支查地支")
    if branch == TIAN_XI_BRANCH_BY_YEAR_BRANCH.get(context.year_branch):
        _append(result, "天喜", basis="year_branch", basis_value=context.year_branch, target="branch", target_value=branch, rule="以年支查地支")

    yuan_chen_branch = _yuan_chen_branch(context)
    if branch and branch == yuan_chen_branch:
        _append(result, "元辰", basis="year_branch_gender", basis_value=f"{context.year_branch}/{context.gender or ''}", target="branch", target_value=branch, rule="以年支、年干阴阳和性别查地支")

    gou_jiao = _gou_jiao_targets(context)
    for name, target_branch in gou_jiao.items():
        if branch == target_branch:
            _append(result, name, basis="year_branch_gender", basis_value=f"{context.year_branch}/{context.gender or ''}", target="branch", target_value=branch, rule="以年支、年干阴阳和性别查地支")


def _add_tong_zi_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    branch: str,
    target_key: str | None,
) -> None:
    if not branch or target_key not in TONG_ZI_TARGET_KEYS:
        return
    matched_rules: list[str] = []
    for season_branches, target_branches, rule_name in TONG_ZI_SEASON_TARGETS:
        if context.month_branch in season_branches and branch in target_branches:
            matched_rules.append(rule_name)
            break
    na_yin_element = _na_yin_element(context.year_na_yin)
    if na_yin_element and branch in TONG_ZI_TARGETS_BY_NA_YIN_ELEMENT.get(na_yin_element, set()):
        matched_rules.append(f"{na_yin_element}命逢{branch}")
    if not matched_rules:
        return
    _append(
        result,
        "童子",
        basis="month_branch_year_na_yin",
        basis_value="/".join(item for item in (context.month_branch, str(context.year_na_yin or "")) if item),
        target="branch",
        target_value=branch,
        rule="；".join(matched_rules),
    )


def _add_day_stem_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    branch: str,
    ganzhi: str,
) -> None:
    if branch == LU_BRANCH_BY_DAY_STEM.get(context.day_stem):
        _append(result, "禄神", basis="day_stem", basis_value=context.day_stem, target="branch", target_value=branch, rule="以日干查地支")
    if branch == YANG_REN_BRANCH_BY_DAY_STEM.get(context.day_stem):
        _append(result, "羊刃", basis="day_stem", basis_value=context.day_stem, target="branch", target_value=branch, rule="以日干查地支")
    if branch == FEI_REN_BRANCH_BY_DAY_STEM.get(context.day_stem):
        _append(result, "飞刃", basis="day_stem", basis_value=context.day_stem, target="branch", target_value=branch, rule="以日干查地支")


def _add_common_structural_rules(
    result: list[dict[str, Any]],
    context: ShenShaContext,
    *,
    branch: str,
    ganzhi: str,
) -> None:
    if branch in context.empty_branches:
        _append(result, "空亡", basis="day_ganzhi", basis_value=context.day_ganzhi, target="branch", target_value=branch, rule="以日柱旬空查地支")
    if branch in TOMB_BRANCHES:
        _append(
            result,
            "墓库",
            basis="branch",
            basis_value=branch,
            target="branch",
            target_value=branch,
            rule=TOMB_BRANCHES[branch],
            meaning=TOMB_BRANCHES[branch],
        )


def _add_day_pillar_rules(result: list[dict[str, Any]], context: ShenShaContext, *, ganzhi: str) -> None:
    if not ganzhi:
        return
    for branches, target_ganzhi in TIAN_SHE_DAY_BY_SEASON_BRANCHES:
        if context.month_branch in branches and ganzhi == target_ganzhi:
            _append(result, "天赦", basis="month_branch_day_ganzhi", basis_value=context.month_branch, target="ganzhi", target_value=ganzhi, rule="以季节月支查日柱")
            break
    if ganzhi in KUI_GANG_DAYS:
        _append(result, "魁罡", basis="day_ganzhi", basis_value=ganzhi, target="ganzhi", target_value=ganzhi, rule="查日柱干支")
    if ganzhi in YIN_YANG_CHA_CUO_DAYS:
        _append(result, "阴阳差错", basis="day_ganzhi", basis_value=ganzhi, target="ganzhi", target_value=ganzhi, rule="查日柱干支")


def _append(
    result: list[dict[str, Any]],
    name: str,
    *,
    basis: str,
    basis_value: str,
    target: str,
    target_value: str,
    rule: str,
    meaning: str | None = None,
) -> None:
    category, default_meaning = SHEN_SHA_META.get(name, ("other", "辅助神煞信号"))
    result.append(
        {
            "name": name,
            "category": category,
            "basis": basis,
            "basis_value": basis_value,
            "target": target,
            "target_value": target_value,
            "rule": rule,
            "meaning": meaning or default_meaning,
        }
    )


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = (
            str(item.get("name") or ""),
            str(item.get("basis") or ""),
            str(item.get("basis_value") or ""),
            str(item.get("target") or ""),
            str(item.get("target_value") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _matches_target(target: str | None, *, stem: str, branch: str, ganzhi: str) -> bool:
    if not target:
        return False
    if target in STEMS:
        return stem == target
    if target in BRANCHES:
        return branch == target
    return ganzhi == target


def _target_type(target: str | None) -> str:
    if target in STEMS:
        return "stem"
    if target in BRANCHES:
        return "branch"
    return "ganzhi"


def _trinity_targets(branch: str) -> dict[str, str]:
    for branches, targets in TRINITY_TARGETS_BY_BRANCH_GROUP:
        if branch in branches:
            return targets
    return {}


def _lonely_targets(branch: str) -> dict[str, str]:
    for branches, targets in GU_CHEN_GUA_SU_BY_YEAR_BRANCH_GROUP:
        if branch in branches:
            return targets
    return {}


def _is_yang_male_or_yin_female(context: ShenShaContext) -> bool | None:
    if context.gender not in {"male", "female"}:
        return None
    stem_yin_yang = YIN_YANG_BY_STEM.get(context.year_stem)
    if stem_yin_yang not in {"阳", "阴"}:
        return None
    return (context.gender == "male" and stem_yin_yang == "阳") or (context.gender == "female" and stem_yin_yang == "阴")


def _yuan_chen_branch(context: ShenShaContext) -> str | None:
    is_yang_male_or_yin_female = _is_yang_male_or_yin_female(context)
    if is_yang_male_or_yin_female is None:
        return None
    if is_yang_male_or_yin_female:
        return YUAN_CHEN_BRANCH_BY_YEAR_BRANCH_YANG_MALE_YIN_FEMALE.get(context.year_branch)
    return YUAN_CHEN_BRANCH_BY_YEAR_BRANCH_YIN_MALE_YANG_FEMALE.get(context.year_branch)


def _gou_jiao_targets(context: ShenShaContext) -> dict[str, str]:
    is_yang_male_or_yin_female = _is_yang_male_or_yin_female(context)
    if is_yang_male_or_yin_female is None or context.year_branch not in BRANCHES:
        return {}
    forward = _shift_branch(context.year_branch, 3)
    backward = _shift_branch(context.year_branch, -3)
    if is_yang_male_or_yin_female:
        return {"勾煞": forward, "绞煞": backward}
    return {"绞煞": forward, "勾煞": backward}


def _shift_branch(branch: str, offset: int) -> str:
    return BRANCHES[(BRANCHES.index(branch) + offset) % len(BRANCHES)]


def _na_yin_element(na_yin: str | None) -> str:
    value = str(na_yin or "")
    for element in ("木", "火", "土", "金", "水"):
        if element in value:
            return element
    return ""
