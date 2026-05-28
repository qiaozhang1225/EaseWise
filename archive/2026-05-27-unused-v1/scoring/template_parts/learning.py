from __future__ import annotations

from typing import Any

from scoring.template_parts.shared import (
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

def _pick_learning_level(result: dict[str, Any], final_score: int) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    heavy_harm_count = int(harms["door_pressure"]) + int(harms["tomb"]) + int(harms["punishment_hit"])
    has_emptiness = bool(harms["emptiness_layers"])
    has_cap = bool(result["scoring"]["structural_cap_reasons"])
    disturbance = bool(detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}))
    pressure = bool(harms["door_pressure"] or detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or symbols["god"] == "白虎")
    good_learning = bool(
        symbols["star"] in {"天辅", "天心", "天任"}
        or symbols["door"] in {"休门", "生门", "杜门"}
        or symbols["god"] in {"太阴", "六合", "九地"}
    )

    if final_score >= 95 and good_learning and heavy_harm_count == 0 and not has_emptiness and not has_cap and not disturbance and symbols["star"] != "天芮" and symbols["door"] != "死门":
        return "学习承接感很稳"
    if "pair_25_95" in detected or heavy_harm_count >= 3 or final_score < 45:
        return "当前不宜把它当学习主用"
    if heavy_harm_count >= 2 or symbols["star"] == "天芮" or symbols["door"] == "死门" or (pressure and has_emptiness) or final_score < 65:
        return "学习波动偏明显"
    if has_emptiness or has_cap or disturbance or pressure or final_score < 80:
        return "学得进，但更吃节奏和方法"
    return "学习整体可守"


def _pick_learning_type(result: dict[str, Any]) -> str:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])

    if harms["tomb"] or symbols["door"] == "死门" or symbols["star"] == "天芮":
        return "前强后沉型"
    if harms["punishment_hit"] or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        return "反复卡顿型"
    if harms["door_pressure"] or symbols["god"] == "白虎" or symbols["door"] == "伤门" or detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        return "压力回拉型"
    if symbols["door"] == "惊门" or symbols["god"] in {"腾蛇", "玄武"} or symbols["star"] == "天柱":
        return "专注敏感型"
    if symbols["door"] in {"开门", "景门"} or symbols["god"] in {"九天", "值符+九天"} or symbols["star"] == "天英":
        return "输出驱动型"
    if symbols["star"] == "天任" or symbols["door"] in {"生门", "杜门"} or symbols["god"] == "九地":
        return "慢热沉淀型"
    if symbols["star"] == "天辅" or symbols["star"] == "天心" or symbols["door"] == "休门" or symbols["god"] == "太阴":
        return "方法整合型"
    return "系统吸收型"


def _learning_manifestation(learning_type: str) -> str:
    return {
        "系统吸收型": "更容易把零散信息串成框架，适合系统学习、归纳整理和按步骤吃透。",
        "方法整合型": "不是靠死背，而是更擅长找方法、抓重点、梳理顺序，学会以后还能转成自己的理解。",
        "慢热沉淀型": "前面不一定最快，但只要节奏稳、重复够，后劲和留存会越来越明显。",
        "输出驱动型": "一旦有任务、结果或表达场景，学习动力会明显上来，边学边用时更容易出效果。",
        "专注敏感型": "不是完全学不进去，而是注意力、节奏和情绪一被带乱，效率就容易一阵高一阵低。",
        "压力回拉型": "平时未必没能力，但压力一上来就更容易急、硬、耗，学得会但不一定学得轻松。",
        "反复卡顿型": "容易出现学了又断、断了又补、前面懂一点后面又散掉，节奏反复感更强。",
        "前强后沉型": "开头不一定差，但越往后越容易发沉、掉速，真正难的是后段留存和长期复盘。",
    }[learning_type]


def _learning_watch_areas(result: dict[str, Any], final_score: int) -> list[dict[str, str]]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    areas: list[dict[str, str]] = []

    def add_area(area: str, reason: str, scenario: str) -> None:
        if any(item["area"] == area for item in areas):
            return
        areas.append({"area": area, "reason": reason, "scenario": scenario})

    if symbols["door"] in {"惊门", "伤门"} or symbols["god"] in {"腾蛇", "玄武"} or harms["punishment_hit"] or detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_area("专注节奏", "注意力和情绪一被带动，学习效率就容易一段高一段低。", "碎片输入、任务切换频繁和被外界打断时更明显。")
    if symbols["star"] in {"天辅", "天心"} or symbols["door"] in {"休门", "杜门"} or symbols["god"] == "太阴":
        add_area("学习方法", "真正拉开差距的不是愿不愿学，而是有没有框架、顺序和提炼能力。", "系统学习、做笔记、搭框架和拆重点时更明显。")
    if harms["tomb"] or harms["emptiness"] or symbols["star"] == "天芮" or symbols["door"] == "死门":
        add_area("复盘沉淀", "前面学得进不代表后面留得住，后段留存和重复提取更容易掉。", "课程后段、长期项目和考试前回收时更明显。")
    if symbols["door"] in {"开门", "景门"} or symbols["god"] in {"九天", "值符+九天"} or symbols["star"] == "天英":
        add_area("输出转化", "输入和表达之间有时会脱节，懂了不一定马上讲得出或用得稳。", "讲解、答题、实操和交付阶段更明显。")
    if harms["door_pressure"] or symbols["god"] == "白虎" or detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}) or final_score < 75:
        add_area("承压续航", "一旦压力上来，注意力、记忆稳定度和坚持度容易一起受影响。", "连续学习、赶节点和高标准要求阶段更明显。")
    if not areas:
        add_area("学习节奏", "整体不是没有学习力，而是更吃稳定节奏和持续推进。", "需要长期持续投入的学习任务里更值得留意。")
    return areas


def _learning_deduction_reasons(result: dict[str, Any]) -> list[str]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])
    reasons: list[str] = []

    def add_reason(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    if symbols["star"] == "天辅":
        add_reason("天辅在学习层更重方法、归纳和把零散内容梳成框架。")
    if symbols["star"] == "天心":
        add_reason("天心利逻辑、判断和抓重点，适合做结构化理解。")
    if symbols["star"] == "天任":
        add_reason("天任偏稳扎稳打，学习上更吃长期沉淀和慢慢累积。")
    if symbols["star"] == "天芮":
        add_reason("天芮落学习层时，更像杂、散、拖和问题点偏多，不是完全学不进，而是更容易被细碎问题绊住。")
    if symbols["door"] == "休门":
        add_reason("休门更利吸收、静下来理解和慢慢吃透。")
    if symbols["door"] == "生门":
        add_reason("生门让学习更偏务实和结果导向，边学边用时更容易进入状态。")
    if symbols["door"] == "杜门":
        add_reason("杜门利静心钻研，但也意味着节奏更不能被频繁打断。")
    if symbols["door"] == "惊门":
        add_reason("惊门会把注意力波动、临场紧绷和碎片切换放大。")
    if symbols["door"] == "死门":
        add_reason("死门更容易让学习后段发沉，出现懂得慢、启动难或越学越闷的感觉。")
    if symbols["god"] == "太阴":
        add_reason("太阴利细节、内化和默默打磨，适合走细学深学路线。")
    if symbols["god"] == "六合":
        add_reason("六合利配合、借力和在互动中吸收，适合通过讨论或协同把知识接住。")
    if symbols["god"] == "腾蛇":
        add_reason("腾蛇会把多想、绕和注意力拉扯带进学习过程。")
    if symbols["god"] == "白虎":
        add_reason("白虎让学习更吃压力管理，一紧就容易硬、急、耗。")
    if harms["emptiness"]:
        add_reason("空亡会让学习承接感出现前面听懂、后面落不实的抽空感。")
    if harms["tomb"]:
        add_reason("入墓更像后段发沉，课程越往后越要靠复盘和重复提取来稳住。")
    if harms["punishment_hit"]:
        add_reason("击刑会放大学了又断、断了又补、节奏反复的感觉。")
    if detected.intersection({"pair_27_99_92", "peach_blossom_111_999"}) or risk_pairs.intersection({"27", "99", "92"}):
        add_reason("外部扰动组合会让注意力更容易被关系、人情或环境噪音带偏。")
    if detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"}):
        add_reason("69/96 这类风险组合会把推进冲劲和稳定吸收之间的拉扯放大。")
    if not reasons:
        add_reason("整体盘面没有把学习力打穿，但更适合按节奏、按结构去稳稳吸收。")
    return reasons


def _learning_advice(level: str, result: dict[str, Any], final_score: int) -> str:
    watch_areas = _learning_watch_areas(result, final_score)
    area_text = "、".join(item["area"] for item in watch_areas[:2]) or "学习节奏"

    if level == "学习承接感很稳":
        return "如果你看重学习效率、系统吸收和长期沉淀，这个号可以长期坚持使用。"
    if level == "学习整体可守":
        return f"可以继续长期使用，学习层整体可守，但关键节点仍建议留意{area_text}。"
    if level == "学得进，但更吃节奏和方法":
        return f"可以继续使用，但更吃学习方法、节奏管理和复盘习惯，尤其在{area_text}上别放任。"
    if level == "学习波动偏明显":
        return f"如果你当前特别看重专注度、吸收效率和长期沉淀，这个号不建议当学习主用，至少要先把{area_text}看清。"
    return f"如果你很在意学习效率、稳定专注和少反复，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"


def _build_learning_payload(result: dict[str, Any], final_score: int, labels: dict[str, str]) -> dict[str, Any]:
    board = result["board"]
    features = result["features"]
    harms = features["harms"]
    patterns = features["patterns"]
    scoring = result["scoring"]
    symbols = board["symbols"]
    detected = set(patterns["detected"])
    risk_pairs = set(patterns["risk_pairs"])

    level = _pick_learning_level(result, final_score)
    learning_type = _pick_learning_type(result)
    watch_areas = _learning_watch_areas(result, final_score)
    deduction_reasons = _learning_deduction_reasons(result)

    primary_driver = "方法层"
    if learning_type == "输出驱动型":
        primary_driver = "输出层"
    elif learning_type == "专注敏感型":
        primary_driver = "专注层"
    elif learning_type == "压力回拉型":
        primary_driver = "承压层"
    elif learning_type == "反复卡顿型":
        primary_driver = "节奏层"
    elif learning_type == "前强后沉型":
        primary_driver = "沉淀层"
    elif learning_type == "慢热沉淀型":
        primary_driver = "沉淀层"

    secondary_driver = "节奏层"
    if primary_driver != "专注层" and (symbols["door"] == "惊门" or symbols["god"] in {"腾蛇", "玄武"} or harms["punishment_hit"]):
        secondary_driver = "专注层"
    elif primary_driver != "沉淀层" and (harms["tomb"] or harms["emptiness"] or symbols["star"] == "天芮" or symbols["door"] == "死门"):
        secondary_driver = "沉淀层"
    elif primary_driver != "承压层" and (harms["door_pressure"] or symbols["god"] == "白虎" or detected.intersection({"pair_69_96"}) or risk_pairs.intersection({"69", "96"})):
        secondary_driver = "承压层"
    elif primary_driver != "方法层" and (symbols["star"] in {"天辅", "天心"} or symbols["door"] in {"休门", "杜门"} or symbols["god"] == "太阴"):
        secondary_driver = "方法层"

    return {
        "level": level,
        "type": learning_type,
        "primary_driver": primary_driver,
        "secondary_driver": secondary_driver,
        "manifestation": _learning_manifestation(learning_type),
        "advice": _learning_advice(level, result, final_score),
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
            "door_personality": DOOR_PERSONALITY.get(symbols["door"], "有自己的学习节奏和用力方式"),
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
            "allowed_levels": LEARNING_LEVELS,
            "allowed_types": LEARNING_TYPES,
            "rendering_goal": "Explain whether this number supports long-term learning absorption, focus, method and review stability, where it gets dragged down, and whether it still suits long-term use when the user cares about learning efficiency.",
            "client_tone": "Professional but readable. Keep a teacher-like tone, explain learning method, focus, review, practical blockers and end with a clear keep-or-adjust verdict.",
        },
    }
