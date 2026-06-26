from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from features.four_pillars.engine.bone_weight import calculate_bone_weight, load_bone_weight_data
from features.four_pillars.engine.service import build_chart, build_chart_display, build_deterministic_facts


class BoneWeightCalculationTest(unittest.TestCase):
    def test_data_tables_are_complete(self) -> None:
        data = load_bone_weight_data()
        self.assertEqual(len(data["year_weights"]), 60)
        self.assertEqual(len(data["month_weights"]), 12)
        self.assertEqual(len(data["day_weights"]), 30)
        self.assertEqual(len(data["hour_weights"]), 12)

        possible_totals = {
            year + month + day + hour
            for year in data["year_weights"].values()
            for month in data["month_weights"].values()
            for day in data["day_weights"].values()
            for hour in data["hour_weights"].values()
        }
        missing = sorted(total for total in possible_totals if str(total) not in data["song_summaries"])
        self.assertEqual(missing, [])

    def test_calculates_regular_datetime(self) -> None:
        value = datetime(1989, 5, 22, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        result = calculate_bone_weight(value)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.total_qian, 48)
        self.assertEqual(result.total_label, "4两8钱")
        self.assertEqual(result.year_ganzhi, "己巳")
        self.assertEqual(result.lunar_month, 4)
        self.assertEqual(result.lunar_day, 18)
        self.assertEqual(result.hour_branch, "巳")

    def test_calculates_1989_may_22_chen_hour_song(self) -> None:
        value = datetime(1989, 5, 22, 8, 55, tzinfo=ZoneInfo("Asia/Shanghai"))
        result = calculate_bone_weight(value)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.total_qian, 41)
        self.assertEqual(result.total_label, "4两1钱")
        self.assertEqual(result.fate_pattern, "聪明富贵，做事有成")
        self.assertEqual(result.verse, "此命推来事不同，为人能干亦凡庸，中年还有逍遥福，不比前时运未通")

    def test_night_zi_uses_next_lunar_day_for_date_weight(self) -> None:
        value = datetime(1989, 5, 22, 23, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        result = calculate_bone_weight(value)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.lunar_day, 19)
        self.assertEqual(result.hour_branch, "子")

    def test_chart_display_profile_contains_extended_info(self) -> None:
        input_profile = {
            "gender": "male",
            "birth_date": "1989-05-22",
            "birth_time": "10:00",
            "timezone": "Asia/Shanghai",
            "birth_place": "上海",
            "name": "测试用户",
        }
        chart = build_chart(input_profile)
        facts = build_deterministic_facts(chart, input_profile)
        display = build_chart_display(input_profile, chart, facts)
        profile = display["profile"]

        self.assertEqual(profile["name"], "测试用户")
        self.assertEqual(profile["structure_label"], "乾造")
        self.assertEqual(profile["constellation"], "双子")
        self.assertEqual(profile["lunar_date"], "1989年4月18巳时")
        self.assertEqual(profile["solar_term_context"], "立夏后芒种前")
        self.assertEqual(profile["xiu"], "心宿东方苍龙")
        self.assertTrue(profile["tai_yuan"])
        self.assertTrue(profile["tai_xi"])
        self.assertTrue(profile["ming_gong"])
        self.assertTrue(profile["shen_gong"])
        self.assertEqual(profile["life_gua"], "坤卦西四命")
        self.assertEqual(profile["empty_branches_text"], "戌亥申酉")
        self.assertEqual(profile["bone_weight"]["total_label"], "4两8钱")


if __name__ == "__main__":
    unittest.main()
