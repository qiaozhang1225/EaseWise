from __future__ import annotations

import unittest

from features.phone_qimen.rendering.aspects import build_aspect_prompts
from features.phone_qimen.rendering.phone_summary import build_phone_summary_prompts
from features.phone_qimen.rendering.stability import build_stability_prompts
from features.phone_qimen.scoring.dimensions import score_phone_dimensions
from features.phone_qimen.scoring.total_score.bundle import build_scoring_bundle
from features.phone_qimen.scoring.total_score.engine import load_rules, score_phone


PHONE = "13800138000"
GENDER = "male"


class PhoneQimenPromptReadabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = load_rules()
        cls.scoring_bundle = build_scoring_bundle(score_phone(PHONE, GENDER, cls.rules))
        cls.dimension_result = score_phone_dimensions(PHONE, GENDER, rules=cls.rules)

    def test_phone_summary_prompt_contains_user_readable_rules(self) -> None:
        payload = self.scoring_bundle["score_template"]["phone_summary_facts"]
        system_prompt, user_prompt, json_example = build_phone_summary_prompts(payload)
        combined = f"{system_prompt}\n{user_prompt}"

        self.assertIn("Shared User-Readable Expression", combined)
        self.assertIn("用户能对照的状态、场景和使用建议", combined)
        self.assertIn("必须出现用户能核实的具体场景", combined)
        self.assertIn("不要连续堆叠宫、门、神、星、干支、四害", combined)
        self.assertIn("把专业层翻译成现实表现", combined)
        self.assertIn("推进、合作、回款、关系、情绪或收尾", combined)
        self.assertIn("现实承接感", json_example["elements_check"]["宫"])

    def test_stability_prompt_contains_long_term_usage_scenarios(self) -> None:
        system_prompt, user_prompt, json_example, locked = build_stability_prompts(
            PHONE,
            GENDER,
            rules=self.rules,
        )
        combined = f"{system_prompt}\n{user_prompt}"

        self.assertIn("Shared User-Readable Expression", combined)
        self.assertIn("适不适合主用", combined)
        self.assertIn("长期联系、事业主号、合作收口、资金沉淀", combined)
        self.assertIn("用户能对照的长期使用场景", combined)
        self.assertIn("把专业层翻译成现实表现", combined)
        self.assertEqual(json_example["verdict"], locked["verdict"])
        self.assertIn("主用或辅助使用感", json_example["elements_check"]["整体承接"])

    def test_aspect_prompt_contains_readability_rules_and_correct_field_name(self) -> None:
        package = {"score_result": self.dimension_result, "score_template": {}}
        payload = {
            "aspect_key": "career",
            "title": "事业",
            "score": int(self.dimension_result["dimensions"]["career"]["score"]),
            "dimension_score": self.dimension_result["dimensions"]["career"],
            "board": self.dimension_result["board"],
            "features": self.dimension_result["features"],
            "locked_score": int(self.dimension_result["dimensions"]["career"]["score"]),
        }
        system_prompt, user_prompt, json_example = build_aspect_prompts("career", payload)
        combined = f"{system_prompt}\n{user_prompt}"

        self.assertIn("Shared User-Readable Expression", combined)
        self.assertIn("用户能拿自己的经历对照", combined)
        self.assertIn("风险会落到哪些现实场景", combined)
        self.assertIn("把专业层翻译成现实表现", combined)
        self.assertIn("elements_check 是中间层判断", combined)
        self.assertNotIn("element_checks", combined)
        self.assertIn("现实承接感", json_example["elements_check"]["宫"])
        self.assertEqual(package["score_result"], self.dimension_result)


if __name__ == "__main__":
    unittest.main()
