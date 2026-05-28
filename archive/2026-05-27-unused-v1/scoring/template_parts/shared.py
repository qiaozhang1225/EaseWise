from __future__ import annotations

from typing import Any

COMPONENT_LABELS = {
    "palace_door": "\u5bab\u95e8\u5173\u7cfb",
    "god": "\u795e\u4f4d\u6743\u91cd",
    "star": "\u661f\u4f4d\u6743\u91cd",
    "door": "\u95e8\u4f4d\u6743\u91cd",
    "stems": "\u540e\u4e24\u5e72",
    "harms": "\u56db\u5bb3\u4fdd\u7559\u5206",
    "pattern_penalty": "\u7279\u6b8a\u7ec4\u5408\u6263\u5206",
}

RELATION_LABELS = {
    "palace_generates_door": "\u5bab\u751f\u95e8",
    "same_element": "\u540c\u6c14",
    "door_generates_palace": "\u95e8\u751f\u5bab",
    "palace_controls_door": "\u5bab\u514b\u95e8",
    "door_controls_palace": "\u95e8\u514b\u5bab",
    "heaven_generates_earth": "\u5929\u5e72\u751f\u5730\u5e72",
    "earth_generates_heaven": "\u5730\u5e72\u751f\u5929\u5e72",
    "heaven_controls_earth": "\u5929\u5e72\u514b\u5730\u5e72",
    "earth_controls_heaven": "\u5730\u5e72\u514b\u5929\u5e72",
    "unrelated": "\u5173\u7cfb\u5e73",
}

PATTERN_LABELS = {
    "triple_same": "\u4e09\u8fde\u53f7\u653e\u5927",
    "peach_blossom_111_999": "111/999 \u6843\u82b1\u653e\u5927",
    "pair_69_96": "69/96 \u98ce\u9669\u7ec4\u5408",
    "pair_25_95": "25/95 \u91cd\u98ce\u9669\u7ec4\u5408",
    "pair_27_99_92": "27/99/92 \u6270\u52a8\u7ec4\u5408",
    "tail_repeat_bias": "\u5c3e\u4f4d\u91cd\u590d\u504f\u538b",
}

EDGE_FLAG_LABELS = {
    "palace_emptiness": "\u5bab\u7a7a\u4ea1",
    "god_emptiness": "\u795e\u7a7a\u4ea1",
    "star_emptiness": "\u661f\u7a7a\u4ea1",
    "door_emptiness": "\u95e8\u7a7a\u4ea1",
    "trigger_generic_emptiness": "\u5f15\u5e72\u7a7a\u4ea1",
    "heaven_stem_generic_emptiness": "\u5929\u5e72\u7a7a\u4ea1",
    "earth_stem_generic_emptiness": "\u5730\u5e72\u7a7a\u4ea1",
    "god_9_dual_read": "\u795e\u4f4d9\u53cc\u91cd\u8bfb\u53d6",
    "palace_5_special": "\u5bab\u4f4d5\u7279\u4f8b",
    "star_5_special": "\u661f\u4f4d5\u7279\u4f8b",
    "door_5_special": "\u95e8\u4f4d5\u7279\u4f8b",
    "star_2_special": "\u661f\u4f4d2\u7279\u4f8b",
    "door_2_special": "\u95e8\u4f4d2\u7279\u4f8b",
}

CAP_REASON_LABELS = {
    "pair_25_95": "25/95 \u89e6\u53d1\u7ed3\u6784\u5c01\u9876",
    "pair_69_96": "69/96 \u89e6\u53d1\u7ed3\u6784\u5c01\u9876",
    "stacked_27_99_92": "27/99/92 \u591a\u91cd\u53e0\u52a0\u89e6\u53d1\u5c01\u9876",
    "palace_empty_with_door_pressure": "\u5bab\u7a7a\u4ea1\u53e0\u52a0\u95e8\u8feb\u89e6\u53d1\u5c01\u9876",
    "multiple_heavy_harms": "\u591a\u91cd\u91cd\u5bb3\u53e0\u52a0\u89e6\u53d1\u5c01\u9876",
}

STABILITY_LEVELS = ["整体比较稳", "整体偏稳", "有一定波动，但还能用", "波动感比较明显", "长期使用会比较折腾"]
STABILITY_TYPES = ["整体顺接型", "平台承载型", "执行反复型", "结果发沉型", "外强内虚型", "关系牵动型", "慢性消耗型", "前强后弱型"]
CAREER_LEVELS = ["事业推进感很稳", "事业整体可推", "能做，但更吃环境和方式", "推进阻力偏明显", "当前不宜硬冲"]
CAREER_TYPES = ["稳推积累型", "平台承载型", "执行反复型", "后段掉速型", "权责压力型", "人事牵动型", "高压消耗型", "外强内虚型"]
MARRIAGE_LEVELS = ["婚姻承接感很稳", "婚姻整体可守", "能走下去，但更吃相处方式", "关系扰动偏明显", "当前不宜在婚姻上硬扛"]
MARRIAGE_TYPES = ["稳定陪伴型", "慢热磨合型", "沟通拉扯型", "桃花扰动型", "权责失衡型", "外界牵动型", "高压消耗型", "前合后松型"]
WEALTH_LEVELS = ["财运承接感很稳", "财运整体可做", "能进财，但更吃节奏和方法", "进财波动偏明显", "当前不宜把它当财运主用"]
WEALTH_TYPES = ["稳守积累型", "资源整合型", "平台承载型", "现金流波动型", "合作分利型", "外财扰动型", "高压消耗型", "前强后漏型"]
FORTUNE_LEVELS = ["运势起势很顺", "运势整体可走", "有起伏，但还能借势", "运势波动偏明显", "当前不宜硬扛运势"]
FORTUNE_TYPES = ["顺流承接型", "平台放大型", "前通后滞型", "关系牵动型", "风险回拉型", "消耗承压型", "外放起伏型", "低开反复型"]
HEALTH_LEVELS = ["健康承压感很稳", "健康整体可守", "有消耗，但还可控", "健康负担偏明显", "当前不宜长期硬扛"]
HEALTH_TYPES = ["节律稳定型", "压力消耗型", "恢复偏慢型", "睡眠波动型", "情绪牵动型", "火气偏旺型", "慢性内耗型", "反复折腾型"]
RELATIONSHIP_LEVELS = ["人际感情承接感很稳", "人际感情整体可守", "有来有往，但更吃分寸和边界", "人际感情扰动偏明显", "当前不宜在人际感情上硬扛"]
RELATIONSHIP_TYPES = ["人缘承接型", "慢热走心型", "边界敏感型", "桃花牵动型", "强势压场型", "情绪反复型", "外热内耗型", "疏离回避型"]
LEARNING_LEVELS = ["学习承接感很稳", "学习整体可守", "学得进，但更吃节奏和方法", "学习波动偏明显", "当前不宜把它当学习主用"]
LEARNING_TYPES = ["系统吸收型", "方法整合型", "慢热沉淀型", "输出驱动型", "专注敏感型", "压力回拉型", "反复卡顿型", "前强后沉型"]
SUITABLE_JOB_LEVELS = ["职业适配感很稳", "职业方向整体可走", "能做，但更吃赛道和分工", "职业匹配挑环境和角色", "当前不宜拿它做职业适配主用"]
SUITABLE_JOB_TYPES = ["管理统筹型", "资源运营型", "研究支持型", "外拓展示型", "流程审核型", "风控排障型", "强推执行型", "稳守积累型"]
BOARD_DESCRIPTION_SECTION_ORDER = ["盘面基础结构", "核心关系判断", "专业盘面描述", "现实落点"]

DOOR_PERSONALITY = {
    "\u4f11\u95e8": "\u6162\u70ed\u3001\u514b\u5236\u3001\u91cd\u89c2\u5bdf",
    "\u751f\u95e8": "\u52a1\u5b9e\u3001\u91cd\u7ed3\u679c\u3001\u91cd\u843d\u5730",
    "\u5f00\u95e8": "\u4e3b\u52a8\u3001\u5916\u653e\u3001\u63a8\u52a8\u529b\u5f3a",
    "\u666f\u95e8": "\u5728\u610f\u8868\u8fbe\u4e0e\u53cd\u9988",
    "\u60ca\u95e8": "\u53cd\u5e94\u5feb\u3001\u8b66\u89c9\u9ad8\u3001\u6613\u7d27\u7ef7",
    "\u675c\u95e8": "\u8c28\u614e\u3001\u4fdd\u5b88\u3001\u9632\u5907\u5fc3\u91cd",
    "\u4f24\u95e8": "\u76f4\u63a5\u3001\u8f83\u771f\u3001\u5bb9\u6613\u786c\u78b0\u786c",
    "\u6b7b\u95e8": "\u6536\u7740\u6765\u3001\u538b\u5f97\u4f4f\u3001\u5bb9\u6613\u95f7\u7740\u625b",
}

GOD_TONE = {
    "\u503c\u7b26": "\u4e3b\u89c1\u548c\u638c\u63a7\u611f",
    "\u503c\u7b26+\u4e5d\u5929": "\u4e3b\u89c1\u3001\u5916\u6269\u548c\u51b2\u52b2",
    "\u516d\u5408": "\u8bb2\u5173\u7cfb\u3001\u8bb2\u914d\u5408",
    "\u592a\u9634": "\u7ec6\u817b\u3001\u987e\u8651\u591a\u3001\u5fc3\u601d\u6df1",
    "\u4e5d\u5929": "\u60f3\u505a\u5927\u3001\u60f3\u62c9\u5f00\u7a7a\u95f4",
    "\u4e5d\u5730": "\u504f\u7a33\u3001\u504f\u6162\u3001\u504f\u5b88",
    "\u7384\u6b66": "\u9632\u5907\u5f3a\u3001\u5185\u5fc3\u4e0d\u8f7b\u6613\u5916\u9732",
    "\u87e3\u86c7": "\u591a\u60f3\u3001\u591a\u7ed5\u3001\u5bb9\u6613\u654f\u611f",
    "\u767d\u864e": "\u538b\u529b\u611f\u91cd\u3001\u5bb9\u6613\u8f83\u786c",
}

LEARNING_SYMBOLS = {"\u5929\u8f85", "\u5929\u5fc3", "\u5929\u4efb", "\u4f11\u95e8", "\u751f\u95e8", "\u592a\u9634", "\u516d\u5408"}
COMPONENT_ORDER = ("palace_door", "god", "star", "door", "stems", "harms", "pattern_penalty")
NEUTRAL_PAIR_SCOPE = "relationship_only"
NEUTRAL_PAIR_NOTE = "\u5408\u5341\u683c\u53ea\u5728\u5a5a\u59fb\u6216\u4eb2\u5bc6\u5173\u7cfb\u5c42\u53c2\u8003\uff0c\u4e0d\u7eb3\u5165\u7efc\u5408\u3001\u4e8b\u4e1a\u3001\u8d22\u8fd0\u3001\u5065\u5eb7\u6216\u8bc4\u5206\u7ed3\u8bba\u3002"


def _humanize_layers(layers: list[str], labels: dict[str, str]) -> str:
    if not layers:
        return "\u65e0"
    return "\u3001".join(labels.get(layer, layer) for layer in layers)


def _humanize_harm(present: bool, layers: list[str], labels: dict[str, str]) -> str:
    if not present:
        return "\u65e0"
    if layers:
        return f"\u6709\uff08{_humanize_layers(layers, labels)}\uff09"
    return "\u6709"


def _join_or_none(values: list[str]) -> str:
    cleaned = [value for value in values if value]
    return "\u3001".join(cleaned) if cleaned else "\u65e0"


def _score_band(score: int) -> str:
    if score >= 85:
        return "\u6574\u4f53\u504f\u5f3a"
    if score >= 70:
        return "\u6574\u4f53\u4e2d\u4e0a"
    if score >= 55:
        return "\u6574\u4f53\u4e2d\u7b49"
    if score >= 40:
        return "\u6574\u4f53\u504f\u5f31"
    return "\u6574\u4f53\u627f\u538b"


def _aspect(key: str, title: str, summary: str, signals: list[str]) -> dict[str, Any]:
    return {"key": key, "title": title, "summary": summary, "signals": [signal for signal in signals if signal]}


def _label(mapping: dict[str, str], value: str) -> str:
    return mapping.get(value, value)


def _label_list(mapping: dict[str, str], values: list[str]) -> list[str]:
    return [_label(mapping, value) for value in values]


def _pick_job_summary(door: str, star: str, god: str) -> str:
    if door == "\u5f00\u95e8" or star == "\u5929\u5fc3" or god in {"\u503c\u7b26", "\u503c\u7b26+\u4e5d\u5929"}:
        return "\u66f4\u9002\u5408\u7ba1\u7406\u7edf\u7b79\u3001\u9879\u76ee\u63a8\u8fdb\u3001\u5bf9\u5916\u534f\u540c\u7c7b\u89d2\u8272\u3002"
    if door == "\u751f\u95e8" or star == "\u5929\u4efb":
        return "\u66f4\u9002\u5408\u7ecf\u8425\u652f\u6301\u3001\u8d44\u6e90\u6574\u5408\u3001\u8fd0\u8425\u6267\u884c\u7c7b\u89d2\u8272\u3002"
    if door == "\u4f11\u95e8" or star == "\u5929\u8f85" or god == "\u592a\u9634":
        return "\u66f4\u9002\u5408\u6587\u6848\u7814\u7a76\u3001\u57f9\u8bad\u5b66\u4e60\u3001\u5185\u5bb9\u6574\u7406\u7c7b\u89d2\u8272\u3002"
    if door == "\u666f\u95e8" or star == "\u5929\u82f1" or god == "\u4e5d\u5929":
        return "\u66f4\u9002\u5408\u54c1\u724c\u4f20\u64ad\u3001\u5bf9\u5916\u62d3\u5c55\u3001\u5c55\u793a\u7c7b\u89d2\u8272\u3002"
    if door == "\u675c\u95e8":
        return "\u66f4\u9002\u5408\u5ba1\u6838\u5408\u89c4\u3001\u884c\u653f\u5185\u52e4\u3001\u6587\u6863\u6d41\u7a0b\u3001\u540e\u53f0\u652f\u6301\u7c7b\u89d2\u8272\u3002"
    if door == "\u60ca\u95e8":
        return "\u66f4\u9002\u5408\u98ce\u63a7\u5e94\u6025\u3001\u95ee\u9898\u5904\u7406\u3001\u6392\u969c\u7c7b\u89d2\u8272\u3002"
    if door == "\u4f24\u95e8":
        return "\u66f4\u9002\u5408\u6267\u884c\u843d\u5730\u3001\u5f3a\u63a8\u8fdb\u3001\u8981\u76f4\u9762\u7ed3\u679c\u7684\u89d2\u8272\u3002"
    return "\u66f4\u9002\u5408\u89c4\u5219\u6e05\u6670\u3001\u8282\u594f\u7a33\u5b9a\u3001\u80fd\u957f\u671f\u79ef\u7d2f\u7684\u65b9\u6cd5\u578b\u5c97\u4f4d\u3002"
