from __future__ import annotations

import json
import unittest

from features.four_pillars.engine import build_dayun_facts, build_four_pillars_review, build_liunian_facts
from features.four_pillars.engine.service import FOUR_PILLARS_ASPECT_ORDER
from features.four_pillars.rendering.service import (
    build_aspect_locked_facts,
    build_aspect_prompts,
    build_dayun_prompts,
    build_liunian_prompts,
    build_summary_prompts,
    fallback_aspect_from_facts,
    is_fallback_aspect_payload,
    public_dayun_output,
    public_summary_output,
)


FORBIDDEN_PUBLIC_EXAMPLE_TERMS = (
    "结构承接",
    "可用空间",
    "可用之处",
    "现实承接感",
    "底层结构",
    "后段承接",
)
FORBIDDEN_SUMMARY_EXAMPLE_CLAIMS = (
    "必然离婚",
    "确诊疾病",
    "一定灾祸",
    "寿命",
    "死亡",
)
FORBIDDEN_SUMMARY_FIXED_EXAMPLES = (
    "这张命盘机会不弱，但关系、健康和阶段风险要提前管理",
    "这张盘的主轴不是单纯好坏，而是机会、表达和压力同时出现",
    "重大关系容易被距离、家庭事务或沟通方式牵动",
    "身体风险更像长期消耗，不是单点疾病结论",
)
FORBIDDEN_GENERIC_EXAMPLE_TERMS = (
    "一段专项综合评价",
    "一段专项风险提醒",
    "一段十年主轴判断",
    "一段机会判断",
    "一段风险判断",
    "关系备注",
    "事业备注",
    "财富备注",
    "健康备注",
)


def _flatten_text(value: object) -> str:
    if isinstance(value, dict):
        return "\n".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_flatten_text(item) for item in value)
    return str(value or "")


class FourPillarsPromptReadabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = build_four_pillars_review(
            {
                "gender": "male",
                "birth_date": "1990-05-17",
                "birth_time": "08:30",
                "timezone": "Asia/Shanghai",
                "birth_place": "北京",
            },
            include_markdown=False,
        )

    def test_summary_prompt_contains_professional_term_protocol(self) -> None:
        system_prompt, user_prompt, json_example = build_summary_prompts(self.package, tone_pack="customer")
        combined = f"{system_prompt}\n{user_prompt}"

        self.assertIn("四柱 explicit knowledge 摘录与综评合断规则", combined)
        self.assertIn("Chart Summary Explicit Rule Pack", combined)
        self.assertIn("日主强弱与喜忌", combined)
        self.assertIn("婚恋合断", combined)
        self.assertIn("财富合断", combined)
        self.assertIn("健康合断", combined)
        self.assertIn("风险窗口合断", combined)
        self.assertIn("家庭与环境象意", combined)
        self.assertIn("专业词第一次出现要马上解释", combined)
        self.assertIn("控量规则", combined)
        self.assertIn("320-520 个中文字符", combined)
        self.assertIn("每项 content 不超过 80 字", combined)
        self.assertIn("summary_highlights", combined)
        self.assertNotIn('"luck_cycles"', user_prompt)
        self.assertLess(len(user_prompt), 25000)
        self.assertIn("comprehensive_text` 是主文案", combined)
        self.assertIn("一整段综合评述", combined)
        self.assertIn("time_highlights", combined)
        self.assertIn("comprehensive_text", json_example)
        self.assertIn("time_highlights", json_example)
        self.assertIn("key_judgements", json_example)
        self.assertIn("life_risk_windows", json_example)
        self.assertIn("favorable_strategy", json_example)
        self.assertEqual(json_example["title"], "")
        self.assertEqual(json_example["comprehensive_text"], "")
        self.assertIn("伤官", combined)
        for term in FORBIDDEN_PUBLIC_EXAMPLE_TERMS:
            self.assertNotIn(term, _flatten_text(json_example))
        for claim in FORBIDDEN_SUMMARY_EXAMPLE_CLAIMS:
            self.assertNotIn(claim, _flatten_text(json_example))
        for fixed_example in FORBIDDEN_SUMMARY_FIXED_EXAMPLES:
            self.assertNotIn(fixed_example, _flatten_text(json_example))

    def test_public_summary_output_keeps_old_summary_compatible(self) -> None:
        output = public_summary_output(
            {
                "title": "旧版标题",
                "risk": "旧版风险",
                "usage_guidance": "旧版建议",
                "elements_check": {
                    "日主": "日主说明",
                    "五行": "五行说明",
                    "十神": "十神说明",
                    "合冲刑害": "合冲说明",
                    "喜忌": "喜忌说明",
                },
            }
        )

        self.assertEqual(output["title"], "旧版标题")
        self.assertEqual(output["comprehensive_text"], "")
        self.assertEqual(output["key_judgements"], [])
        self.assertEqual(output["life_risk_windows"], [])
        self.assertEqual(output["time_highlights"], [])
        self.assertEqual(output["favorable_strategy"]["favorable_elements"], [])

    def test_aspect_prompt_contains_professional_term_protocol(self) -> None:
        system_prompt, user_prompt, json_example = build_aspect_prompts(
            self.package,
            aspect_key="pattern",
            tone_pack="customer",
        )
        combined = f"{system_prompt}\n{user_prompt}"

        self.assertIn("专业词不是禁用词", combined)
        self.assertIn("不能只写“伤官明显”“空亡较重”“格局不错”", combined)
        self.assertIn("伤官、正印、七杀、财星、官杀、比劫、夫妻宫、墓库、禄神、空亡、格局", combined)
        self.assertNotIn("score 必须", combined)
        self.assertNotIn("title、score、content", combined)
        self.assertNotIn("score", json_example)
        self.assertIn("Explicit Rule Pack", combined)
        self.assertNotIn('"score_template"', user_prompt)
        self.assertNotIn('"luck_cycles"', user_prompt)
        self.assertNotIn('"year_items"', user_prompt)
        self.assertLess(len(user_prompt), 20000)
        self.assertEqual(json_example["title"], "")
        self.assertEqual(json_example["content"], "")
        self.assertEqual(json_example["risk"], "")
        for term in FORBIDDEN_PUBLIC_EXAMPLE_TERMS:
            self.assertNotIn(term, _flatten_text(json_example))
        for term in FORBIDDEN_GENERIC_EXAMPLE_TERMS:
            self.assertNotIn(term, _flatten_text(json_example))

    def test_aspect_locked_facts_are_compact_and_dimension_scoped(self) -> None:
        for aspect_key in FOUR_PILLARS_ASPECT_ORDER:
            locked_facts = build_aspect_locked_facts(self.package, aspect_key)
            text = json.dumps(locked_facts, ensure_ascii=False, indent=2)
            self.assertIn("deterministic_facts", locked_facts)
            self.assertIn("summary_highlights", locked_facts["deterministic_facts"])
            self.assertIn("aspect_signals", locked_facts["deterministic_facts"])
            self.assertNotIn('"score_template"', text)
            self.assertNotIn('"product_view"', text)
            self.assertNotIn('"luck_cycles"', text)
            self.assertNotIn('"year_items"', text)
            if aspect_key == "fortune":
                self.assertIn("luck_context", locked_facts["deterministic_facts"])
                self.assertLess(len(text), 30000)
            else:
                self.assertNotIn("luck_context", locked_facts["deterministic_facts"])
                self.assertLess(len(text), 20000)

    def test_all_aspect_prompts_stay_under_budget(self) -> None:
        for aspect_key in FOUR_PILLARS_ASPECT_ORDER:
            system_prompt, user_prompt, json_example = build_aspect_prompts(
                self.package,
                aspect_key=aspect_key,
                tone_pack="customer",
            )
            total_chars = len(system_prompt) + len(user_prompt) + len(json.dumps(json_example, ensure_ascii=False))
            self.assertLess(total_chars, 30000, aspect_key)
            if aspect_key == "fortune":
                self.assertLess(len(user_prompt), 30000, aspect_key)
            else:
                self.assertLess(len(user_prompt), 20000, aspect_key)

    def test_luck_prompts_include_professional_term_protocol(self) -> None:
        cycles = self.package["deterministic_facts"]["luck_cycles"]["cycles"]
        cycle_key = str(cycles[0]["cycle_key"])
        year = int(cycles[0]["year_items"][0]["year"])

        dayun_facts = build_dayun_facts(self.package, cycle_key)
        dayun_system, dayun_user, dayun_example = build_dayun_prompts(dayun_facts, tone_pack="customer")
        dayun_combined = f"{dayun_system}\n{dayun_user}"
        self.assertIn("专业词", dayun_combined)
        self.assertIn("第一次出现必须马上解释成现实含义", dayun_combined)
        self.assertIn("Dayun Explicit Rule Pack", dayun_combined)
        self.assertIn("trend_tendency", dayun_example)
        self.assertNotIn("score_tendency", dayun_example)

        liunian_facts = build_liunian_facts(self.package, cycle_key, year)
        liunian_system, liunian_user, liunian_example = build_liunian_prompts(liunian_facts, tone_pack="customer")
        liunian_combined = f"{liunian_system}\n{liunian_user}"
        self.assertIn("专业词", liunian_combined)
        self.assertIn("第一次出现必须马上解释成现实含义", liunian_combined)
        self.assertIn("Liunian Explicit Rule Pack", liunian_combined)

        for example in (dayun_example, liunian_example):
            for term in FORBIDDEN_PUBLIC_EXAMPLE_TERMS:
                self.assertNotIn(term, _flatten_text(example))
            for term in FORBIDDEN_GENERIC_EXAMPLE_TERMS:
                self.assertNotIn(term, _flatten_text(example))

    def test_fallback_aspect_payload_detection(self) -> None:
        fallback = fallback_aspect_from_facts(self.package["deterministic_facts"], "wealth")
        self.assertTrue(is_fallback_aspect_payload(fallback, "wealth"))
        self.assertFalse(
            is_fallback_aspect_payload(
                {
                    "aspect_key": "wealth",
                    "title": "财运需要先稳现金流，再看偏财机会",
                    "content": "财星代表现实资源，命盘里要同时看日主承载和食伤生财。",
                    "risk": "合伙和人情账要清楚。",
                },
                "wealth",
            )
        )

    def test_dayun_output_renames_legacy_score_tendency(self) -> None:
        output = public_dayun_output(
            {
                "cycle_key": "cycle",
                "cycle_ganzhi": "甲子",
                "title": "阶段趋势",
                "score_tendency": "旧字段趋势内容",
                "core_theme": "主轴",
                "opportunities": "机会",
                "risks": "风险",
                "action_guidance": "建议",
                "elements_check": {"原局": "1", "大运": "2", "十神": "3", "五行": "4", "合冲刑害": "5", "喜忌": "6"},
            }
        )

        self.assertEqual(output["trend_tendency"], "旧字段趋势内容")
        self.assertNotIn("score_tendency", output)


if __name__ == "__main__":
    unittest.main()
