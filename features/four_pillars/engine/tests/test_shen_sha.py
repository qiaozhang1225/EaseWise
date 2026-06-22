from __future__ import annotations

import unittest

from features.four_pillars.engine.shen_sha import (
    BRANCHES,
    STEMS,
    ShenShaContext,
    calculate_target_shen_sha,
    shen_sha_names,
)


class ShenShaCalculationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.context = ShenShaContext(
            year_stem="甲",
            year_branch="子",
            month_branch="寅",
            day_stem="甲",
            day_branch="子",
            day_ganzhi="甲子",
            year_na_yin="海中金",
            gender="male",
            empty_branches=("戌", "亥"),
        )

    def names_for(self, ganzhi: str, target_key: str | None = None) -> list[str]:
        return shen_sha_names(
            calculate_target_shen_sha(
                self.context,
                target_stem=ganzhi[0],
                target_branch=ganzhi[1],
                target_ganzhi=ganzhi,
                target_key=target_key,
            )
        )

    def test_core_lookup_rules(self) -> None:
        self.assertIn("天乙贵人", self.names_for("丁丑"))
        self.assertIn("文昌", self.names_for("乙巳"))
        self.assertIn("福星贵人", self.names_for("甲寅"))
        self.assertIn("禄神", self.names_for("甲寅"))
        self.assertIn("桃花", self.names_for("丁酉"))
        self.assertIn("驿马", self.names_for("戊寅"))
        self.assertIn("空亡", self.names_for("乙亥"))

    def test_month_and_year_branch_rules(self) -> None:
        self.assertIn("天德贵人", self.names_for("丁丑"))
        self.assertIn("天德合", self.names_for("壬申"))
        self.assertIn("天医", self.names_for("丁丑"))
        self.assertIn("红鸾", self.names_for("乙卯"))
        self.assertIn("天喜", self.names_for("丁酉"))

    def test_all_stem_branch_pairs_are_supported(self) -> None:
        checked = 0
        for stem in STEMS:
            for branch in BRANCHES:
                calculate_target_shen_sha(
                    self.context,
                    target_stem=stem,
                    target_branch=branch,
                    target_ganzhi=stem + branch,
                    target_key="liunian",
                )
                checked += 1
        self.assertEqual(checked, 120)

    def test_day_pillar_only_rules(self) -> None:
        day_names = self.names_for("戊寅", target_key="day")
        luck_names = self.names_for("戊寅", target_key="liunian")
        self.assertIn("天赦", day_names)
        self.assertNotIn("天赦", luck_names)

    def test_tong_zi_supports_season_and_year_na_yin_rules(self) -> None:
        self.assertIn("童子", self.names_for("壬子", target_key="hour"))

        context = ShenShaContext(
            year_stem="己",
            year_branch="巳",
            month_branch="巳",
            day_stem="壬",
            day_branch="午",
            day_ganzhi="壬午",
            year_na_yin="大林木",
            gender="male",
            empty_branches=("申", "酉"),
        )
        names = shen_sha_names(
            calculate_target_shen_sha(
                context,
                target_stem="壬",
                target_branch="午",
                target_ganzhi="壬午",
                target_key="day",
            )
        )
        self.assertLess(names.index("童子"), names.index("将星"))

    def test_1989_05_22_hour_examples_include_missing_labels(self) -> None:
        context = ShenShaContext(
            year_stem="己",
            year_branch="巳",
            month_branch="巳",
            day_stem="壬",
            day_branch="午",
            day_ganzhi="壬午",
            year_na_yin="大林木",
            gender="male",
            empty_branches=("申", "酉"),
        )
        chen_names = shen_sha_names(
            calculate_target_shen_sha(
                context,
                target_stem="甲",
                target_branch="辰",
                target_ganzhi="甲辰",
                target_key="hour",
            )
        )
        self.assertIn("福星贵人", chen_names)
        self.assertIn("寡宿", chen_names)
        self.assertIn("天喜", chen_names)
        self.assertLess(chen_names.index("寡宿"), chen_names.index("墓库"))


if __name__ == "__main__":
    unittest.main()
