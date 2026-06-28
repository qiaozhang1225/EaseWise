from features.four_pillars.engine import (
    FOUR_PILLARS_ASPECT_ORDER,
    build_four_pillars_review,
    expand_four_pillars_aspect_keys,
    normalize_four_pillars_aspect_key,
)
from features.four_pillars.rendering import build_four_pillars_product_view


def test_four_pillars_aspect_order_is_twelve_dimension_contract():
    assert FOUR_PILLARS_ASPECT_ORDER == [
        "personality",
        "wealth",
        "marriage",
        "career",
        "health",
        "fortune",
        "investment",
        "social",
        "industry",
        "fengshui",
        "family",
        "pattern",
    ]


def test_four_pillars_aspect_aliases_keep_legacy_unlocks_usable():
    assert normalize_four_pillars_aspect_key("love") == "marriage"
    assert normalize_four_pillars_aspect_key("annual_trend") == "fortune"
    assert normalize_four_pillars_aspect_key("family_environment") == "family"
    assert expand_four_pillars_aspect_keys(["love", "family_environment", "annual_trend"]) == [
        "marriage",
        "family",
        "fengshui",
        "fortune",
    ]


def test_four_pillars_review_facts_and_product_view_include_twelve_aspects():
    package = build_four_pillars_review(
        {
            "gender": "male",
            "birth_date": "1990-05-17",
            "birth_time": "08:30",
            "timezone": "Asia/Shanghai",
            "birth_place": "北京",
        },
        include_markdown=False,
    )

    assert package["score_result"] == {}
    assert "score_markdown" not in package
    assert "aspect_scores" not in package["deterministic_facts"]
    assert isinstance(package["deterministic_facts"]["aspect_signals"], dict)
    public_view = build_four_pillars_product_view(package)
    assert "score" not in public_view
    assert "score_band" not in public_view
    assert [item["aspect_key"] for item in public_view["aspects"]] == FOUR_PILLARS_ASPECT_ORDER
    assert all("score" not in item for item in public_view["aspects"])


def test_four_pillars_summary_highlights_cover_v2_judgement_contract():
    package = build_four_pillars_review(
        {
            "gender": "male",
            "birth_date": "1990-05-17",
            "birth_time": "08:30",
            "timezone": "Asia/Shanghai",
            "birth_place": "北京",
        },
        include_markdown=False,
    )

    highlights = package["deterministic_facts"]["summary_highlights"]
    judgement_keys = [item["key"] for item in highlights["key_judgement_facts"]]

    assert highlights["version"] == "summary_v2"
    assert len(judgement_keys) >= 6
    for required_key in (
        "marriage",
        "wealth",
        "health",
        "risk_window",
        "family_environment",
        "ancestral_environment",
        "favorable_strategy",
        "pattern",
    ):
        assert required_key in judgement_keys
    assert highlights["favorable_strategy"]["favorable_elements"]
    assert highlights["environment_symbols"]["ancestral"]
    assert {item["name"] for item in highlights["special_patterns"]} & {"伤官见官", "枭神夺食", "比劫夺财", "食伤生财"}


def test_four_pillars_summary_highlights_include_luck_risk_window_triggers():
    package = build_four_pillars_review(
        {
            "gender": "male",
            "birth_date": "1990-05-17",
            "birth_time": "08:30",
            "timezone": "Asia/Shanghai",
            "birth_place": "北京",
        },
        include_markdown=False,
    )

    windows = package["deterministic_facts"]["summary_highlights"]["life_risk_windows"]
    trigger_tags = {tag for item in windows for tag in item["trigger_tags"]}

    assert windows
    assert trigger_tags & {"岁运并临", "忌神加强", "刑冲补齐", "墓库触发", "空亡触发"}
    assert all("reality_focus" in item for item in windows)
