from __future__ import annotations

from typing import Any

from scoring.payloads.shared import (
    CAP_REASON_LABELS,
    CAREER_LEVELS,
    CAREER_TYPES,
    COMPONENT_LABELS,
    DOOR_PERSONALITY,
    EDGE_FLAG_LABELS,
    FORTUNE_LEVELS,
    FORTUNE_TYPES,
    GOD_TONE,
    HEALTH_LEVELS,
    HEALTH_TYPES,
    LEARNING_LEVELS,
    LEARNING_TYPES,
    MARRIAGE_LEVELS,
    MARRIAGE_TYPES,
    PATTERN_LABELS,
    RELATION_LABELS,
    RELATIONSHIP_LEVELS,
    RELATIONSHIP_TYPES,
    STABILITY_LEVELS,
    STABILITY_TYPES,
    SUITABLE_JOB_LEVELS,
    SUITABLE_JOB_TYPES,
    WEALTH_LEVELS,
    WEALTH_TYPES,
    _humanize_harm,
    _join_or_none,
    _label,
    _label_list,
    _pick_job_summary,
)

def _pick_suitable_job_level(result: dict[str, Any], final_score: int) -> str:
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    has_cap = bool(result["scoring"]["structural_cap_reasons"])
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    relation = features["palace_door_relation"]

    if final_score >= 95 and heavy_harm_count == 0 and not has_emptiness and not has_cap and relation in {"palace_generates_door", "same_element", "door_generates_palace"} and not detected:
        return "职业适配感很稳"
    if "pair_25_95" in detected or heavy_harm_count >= 3 or final_score < 45:
        return "当前不宜拿它做职业适配主用"
    if heavy_harm_count >= 2 or has_cap or final_score < 65:
        return "职业匹配挑环境和角色"
    if has_emptiness or relation in {"palace_controls_door", "door_controls_palace"} or risk_pairs.intersection({"69", "96", "27", "99", "92"}) or final_score < 80:
        return "能做，但更吃赛道和分工"
    return "职业方向整体可走"


def _pick_suitable_job_type(result: dict[str, Any]) -> str:
    board = result["board"]
    symbols = board["symbols"]
    door = symbols["door"]
    star = symbols["star"]
    god = symbols["god"]

    if door == "开门" or star == "天心" or god in {"值符", "值符+九天"}:
        return "管理统筹型"
    if door == "生门" or star == "天任":
        return "资源运营型"
    if door == "休门" or star == "天辅" or god == "太阴":
        return "研究支持型"
    if door == "景门" or star == "天英" or god == "九天":
        return "外拓展示型"
    if door == "杜门":
        return "流程审核型"
    if door == "惊门" or star == "天柱":
        return "风控排障型"
    if door == "伤门":
        return "强推执行型"
    return "稳守积累型"


def _suitable_job_manifestation(job_type: str) -> str:
    return {
        "管理统筹型": "更容易在需要定方向、抓节奏、整合多方资源的角色里发挥。",
        "资源运营型": "更容易在经营支持、资源整合、日常运营推进这类岗位里稳定出力。",
        "研究支持型": "更适合研究整理、培训学习、内容支持、文档体系化这类细致型岗位。",
        "外拓展示型": "更适合品牌传播、销售拓展、客户展示和对外窗口这类需要外放表达的角色。",
        "流程审核型": "更适合审核合规、行政内勤、流程控制、后台支撑这类规则清晰的岗位。",
        "风控排障型": "更适合风控应急、问题处理、排障收口和异常定位这类救火型岗位。",
        "强推执行型": "更适合强执行、硬推进、需要直面结果和快速落地的岗位。",
        "稳守积累型": "更适合规则清晰、节奏稳定、需要长期积累的方法型岗位。",
    }[job_type]


def _suitable_job_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    relation = features["palace_door_relation"]
    job_type = _pick_suitable_job_type(result)
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if any(item["area"] == area for item in areas):
            return
        areas.append({"area": area, "reason": reason, "scenario": scenario})

    if job_type == "管理统筹型":
        add_area("统筹控盘", "更适合需要定方向、拆任务和盯进度的岗位。", "项目推进、跨部门协同和平台型岗位里更明显。")
        add_area("对外协同", "除了自己会做，更重要的是能不能把多方节奏接起来。", "商务协同、资源对接和多角色配合时更明显。")
    elif job_type == "资源运营型":
        add_area("资源整合", "核心优势在把已有资源接住、排顺、用起来。", "经营支持、运营推进和资源统筹时更明显。")
        add_area("落地续航", "不只是想法对不对，更看长期执行能不能跟上。", "日常运营、流程执行和持续迭代里更明显。")
    elif job_type == "研究支持型":
        add_area("内容整理", "更适合把信息梳顺、拆清、沉淀成可复用结构。", "研究、文档、培训和资料体系化工作里更明显。")
        add_area("细节准确度", "真正拉开差距的是细节有没有守住。", "校对、复盘、分析和支持岗位里更明显。")
    elif job_type == "外拓展示型":
        add_area("对外表达", "更吃展示、传播和让外界快速接收信息的能力。", "品牌传播、销售展示和外部拓展场景里更明显。")
        add_area("节奏转化", "不只是讲得出去，还要能转成结果。", "前台岗位、客户沟通和业务转化里更明显。")
    elif job_type == "流程审核型":
        add_area("规则执行", "核心优势在守规则、控流程和盯闭环。", "合规审核、行政内勤和后台控制场景里更明显。")
        add_area("后台稳定度", "更适合后端支撑，而不是前台冲锋。", "文档流程、内控稽核和中后台岗位里更明显。")
    elif job_type == "风控排障型":
        add_area("风险识别", "对异常、问题和隐患更敏感，容易先看到不对劲的地方。", "风控、质控、应急和故障定位场景里更明显。")
        add_area("高压收口", "真正拉开差距的是压力一来还能不能快速收住局面。", "事故处理、排障响应和临场决策时更明显。")
    elif job_type == "强推执行型":
        add_area("结果推进", "更适合硬推进、抢节点、盯结果的工作方式。", "执行落地、销售推进和一线攻坚时更明显。")
        add_area("承压边界", "推进力有，但太硬时也更容易和环境或人产生摩擦。", "强目标场景和正面硬碰的岗位里更明显。")
    else:
        add_area("长期积累", "更适合规则清晰、节奏稳定、能长期磨出来的岗位。", "方法型、流程型和慢积累路线里更明显。")
        add_area("岗位清晰度", "岗位越清晰，发挥越稳定。", "职责明确、变化较少的环境里更明显。")

    if harms["emptiness"] or relation in {"palace_controls_door", "door_controls_palace"}:
        add_area("平台匹配", "不是完全不能做，而是更吃平台承载和环境支持。", "换平台、换团队或角色不清晰时更明显。")
    if harms["tomb"] or symbols["door"] == "死门" or symbols["star"] == "天芮":
        add_area("长期落点", "前面能做不代表后面省心，长期续航和后段落点更值得盯。", "长期项目、后段复盘和稳定任职阶段更明显。")
    if harms["door_pressure"] or harms["punishment_hit"] or symbols["god"] == "白虎":
        add_area("承压方式", "压力一上来，原本的职业优势也可能变成职业成本。", "赶节点、扛结果和高压岗位里更明显。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92", "69", "96"}) or final_score < 75:
        add_area("角色边界", "岗位越模糊、边界越乱，代价越容易被放大。", "多头汇报、职责冲突和边界模糊的岗位里更明显。")
    return areas


def _suitable_job_deduction_reasons(result: dict[str, Any]) -> list[str]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    relation = features["palace_door_relation"]
    reasons: list[str] = []

    def add_reason(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    if symbols["door"] == "开门":
        add_reason("开门更利对外推进、项目带动和把事情往前推。")
    if symbols["door"] == "生门":
        add_reason("生门让职业发挥更偏务实承接，适合把资源、结果和长期推进接起来。")
    if symbols["door"] == "休门":
        add_reason("休门更利研究整理、内容沉淀和需要细水长流打磨的岗位。")
    if symbols["door"] == "景门":
        add_reason("景门更利展示传播、对外表达和前台曝光场景。")
    if symbols["door"] == "杜门":
        add_reason("杜门更适合规则、流程、审核和后台支撑类岗位。")
    if symbols["door"] == "惊门":
        add_reason("惊门会把风险识别、问题反应和应急处理能力放大。")
    if symbols["door"] == "伤门":
        add_reason("伤门更利强执行、硬推进和直接面对结果的工作方式。")

    if symbols["star"] == "天心":
        add_reason("天心偏规划、判断和统筹，适合带结构、定节奏的工作。")
    if symbols["star"] == "天任":
        add_reason("天任偏务实承载和稳定落地，适合运营执行与长期推进。")
    if symbols["star"] == "天辅":
        add_reason("天辅利研究、教学、内容整理和把信息梳顺。")
    if symbols["star"] == "天英":
        add_reason("天英会把展示感、传播感和舞台感带进职业表达。")
    if symbols["star"] == "天柱":
        add_reason("天柱利查错、较真、排障和盯问题点。")

    if symbols["god"] == "值符":
        add_reason("值符会放大主见、控盘感和带队气场。")
    if symbols["god"] == "太阴":
        add_reason("太阴更利细节观察、内在判断和不声张的稳定承接。")
    if symbols["god"] == "九天":
        add_reason("九天更适合外拓、拉空间和对外扩张类角色。")
    if symbols["god"] == "腾蛇":
        add_reason("腾蛇让职业发挥更敏感于异常、变化和隐藏问题。")
    if symbols["god"] == "白虎":
        add_reason("白虎会把高压、较硬和正面扛结果的职业气质放大。")

    if relation in {"palace_generates_door", "same_element", "door_generates_palace"}:
        add_reason("宫门关系顺，说明岗位发挥和外部平台更容易彼此接住。")
    if relation in {"palace_controls_door", "door_controls_palace"}:
        add_reason("宫门关系带克，说明职业发挥更吃平台、环境和分工匹配。")
    if harms["emptiness"]:
        add_reason("空亡会让岗位承接感打折，更怕职责虚、平台虚或角色落不实。")
    if harms["tomb"]:
        add_reason("入墓更像职业后段发沉，长期做下来更容易出现掉速和消耗。")
    if harms["punishment_hit"]:
        add_reason("击刑会放大岗位摩擦、压力反复和执行过程中的硬碰硬。")
    if set(patterns["risk_pairs"]).intersection({"69", "96"}):
        add_reason("69/96 这类风险组合会把推进力和职业成本同时放大。")
    if set(patterns["risk_pairs"]).intersection({"27", "99", "92"}):
        add_reason("27/99/92 这类扰动组合会让岗位边界和外部干扰更容易改写发挥质量。")
    if not reasons:
        add_reason("整体盘面没有把职业适配打穿，但更吃岗位清晰度和角色分工。")
    return reasons


def _suitable_job_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _suitable_job_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "岗位匹配"

    if level == "职业适配感很稳":
        return "如果你看重职业匹配、角色发挥和长期定位，这个号可以长期坚持使用。"
    if level == "职业方向整体可走":
        return f"可以继续长期使用，职业方向整体可走，但关键节点仍建议留意{area_text}。"
    if level == "能做，但更吃赛道和分工":
        return f"可以继续使用，但更吃赛道选择、岗位分工和平台匹配，尤其在{area_text}上别想当然。"
    if level == "职业匹配挑环境和角色":
        return f"如果你当前特别看重职业定位清晰、发挥稳定和少走弯路，这个号不建议当职业适配主用，至少要先把{area_text}看清。"
    return f"如果你很在意职业适配、长期定位和少折腾，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_suitable_job_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    relation = features["palace_door_relation"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])

    level = _pick_suitable_job_level(result, final_score)
    job_type = _pick_suitable_job_type(result)
    watch_areas = _suitable_job_watch_areas(result, final_score)
    deduction_reasons = _suitable_job_deduction_reasons(result)

    primary_driver = "统筹层"
    if job_type == "资源运营型":
        primary_driver = "资源层"
    elif job_type == "研究支持型":
        primary_driver = "研究层"
    elif job_type == "外拓展示型":
        primary_driver = "展示层"
    elif job_type == "流程审核型":
        primary_driver = "流程层"
    elif job_type == "风控排障型":
        primary_driver = "应急层"
    elif job_type == "强推执行型":
        primary_driver = "执行层"
    elif job_type == "稳守积累型":
        primary_driver = "积累层"

    secondary_driver = "平台层"
    if primary_driver != "平台层" and (harms["emptiness"] or relation in {"palace_controls_door", "door_controls_palace"}):
        secondary_driver = "平台层"
    elif primary_driver != "承压层" and (harms["door_pressure"] or harms["punishment_hit"] or symbols["god"] == "白虎" or risk_pairs.intersection({"69", "96"})):
        secondary_driver = "承压层"
    elif primary_driver != "落点层" and (harms["tomb"] or symbols["door"] == "死门" or symbols["star"] == "天芮"):
        secondary_driver = "落点层"
    elif primary_driver != "边界层" and risk_pairs.intersection({"27", "99", "92"}):
        secondary_driver = "边界层"
    elif primary_driver != "协同层" and symbols["god"] in {"太阴", "六合", "值符", "值符+九天"}:
        secondary_driver = "协同层"

    return {
        "level": level,
        "type": job_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _suitable_job_manifestation(job_type),
        "advice": _suitable_job_advice(level, result, final_score),
        "score_gap": max(0, 100 - final_score),
        "watch_areas": watch_areas,
        "deduction_reasons": deduction_reasons,
        "facts": {
            "score_after_structural_cap": final_score,
            "confidence": scoring["confidence"],
            "palace_door_relation": _label(RELATION_LABELS, features["palace_door_relation"]),
            "stem_pair_relation": _label(RELATION_LABELS, features["stem_pair_relation"]),
            "door": symbols["door"],
            "star": symbols["star"],
            "god": symbols["god"],
            "door_personality": DOOR_PERSONALITY.get(symbols["door"], "有自己的推进方式和岗位节奏"),
            "god_tone": GOD_TONE.get(symbols["god"], "明显的内在驱动力"),
            "four_harms": {
                "emptiness": _humanize_harm(harms["emptiness"], harms["emptiness_layers"], labels),
                "door_pressure": _humanize_harm(harms["door_pressure"], [], labels),
                "tomb": _humanize_harm(harms["tomb"], harms["tomb_layers"], labels),
                "punishment_hit": _humanize_harm(harms["punishment_hit"], harms["punishment_layers"], labels),
            },
            "pattern_flags": _label_list(PATTERN_LABELS, patterns["detected"]),
            "risk_pairs": patterns["risk_pairs"],
            "structural_cap_reasons": _label_list(CAP_REASON_LABELS, scoring["structural_cap_reasons"]),
            "tags": scoring["tags"],
        },
        "model_pack": {
            "allowed_levels": SUITABLE_JOB_LEVELS,
            "allowed_types": SUITABLE_JOB_TYPES,
            "rendering_goal": "Explain which kinds of roles this number matches better, where the role-fit deductions are strongest, what kind of work scenes are less matched, and whether it still suits long-term use when the user cares about job fit.",
            "client_tone": "Professional but readable. Keep a teacher-like tone, explain role fit, practical blockers, environment match and end with a clear keep-or-adjust verdict.",
        },
    }
