#!/usr/bin/env python3
"""Tests for home-cooking recipe formatting."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recipe_format import (  # noqa: E402
    MAX_COOK_MINUTES,
    extract_reference_book_hints,
    filter_cooking_steps,
    format_steps,
    is_cooking_step,
    is_quick_recipe,
    localize_amount,
    localize_text,
    normalize_ingredients,
    parse_cook_time_minutes,
    reference_book_match_score,
    validate_home_output,
)
from recommend_engine import recommend  # noqa: E402


DENGYING = {
    "id": "reg-001",
    "name": "灯影牛肉",
    "scene": ["regional"],
    "tags": ["川渝", "牛肉"],
    "servings": 4,
    "cook_time": "480min",
    "ingredients": [
        {"name": "精瘦牛肉", "amount": "100公斤（按比例）"},
        {"name": "盐", "amount": "2公斤（每100公斤肉）"},
        {"name": "糖", "amount": "1公斤（每100公斤肉）"},
    ],
    "steps": ["切薄片", "腌制", "慢烤"],
    "source": {"book": "食遍中国"},
}


def test_commercial_batch_normalized_for_one_person():
    result = normalize_ingredients(DENGYING, 1)
    amounts = " ".join(i["amount"] for i in result)
    assert "100公斤" not in amounts
    assert "2公斤" not in amounts
    assert "1公斤" not in amounts
    beef = next(i for i in result if "牛肉" in i["name"])
    assert "75" in beef["amount"] or "50" in beef["amount"]
    assert "膳食指南" in beef["amount"]


def test_localize_fahrenheit_and_ounce():
    assert "179" in localize_text("预热烤箱至华氏355度。")
    assert "盎司" not in localize_amount("18盎司，去骨")
    assert "510" in localize_amount("18盎司，去骨")
    assert localize_text("杯（cup）,美国烹饪计量单位。") == ""


def test_format_steps_skips_foreign_footnotes():
    steps = format_steps(
        ["预热烤箱至华氏355度。", "杯（cup）,美国烹饪计量单位。", "将红薯放入烤盘。"],
        [{"name": "红薯", "amount": "200克"}],
    )
    assert len(steps) == 2
    assert "℃" in steps[0]["text"]
    assert steps[0].get("stepArtUrl") in (None, "")


def test_filter_cooking_steps_skips_nutrition_and_redundant():
    raw = [
        "预热烤架并刷上一些橄榄油。",
        "加入鹰嘴豆粉，用刮铲搅拌均匀。",
        "即可享用。",
        "卡路里 210 钠 --毫克 总脂肪 3克 钾 --毫克 饱和脂肪 --克 总碳水化合物 22克",
        "维生素A --% 钙 --% 维生素C --% 铁 --%",
        "* * *",
    ]
    cooking = filter_cooking_steps(raw)
    assert len(cooking) == 2
    assert "烤架" in cooking[0]
    assert not any("卡路里" in s or "即可" in s for s in cooking)
    assert not is_cooking_step("即可享用。")
    assert not is_cooking_step("维生素A --% 钙 --%")


def test_localize_teaspoon_tablespoon():
    assert "15毫升" in localize_text("加入1 tablespoon 橄榄油")
    assert "5毫升" in localize_amount("1 teaspoon", "姜黄粉")


def test_localize_yogurt_quarter_cup():
    assert "60毫升" in localize_amount("¼杯", "酸奶")


def test_localize_meat_cup_not_converted_to_ml():
    assert "毫升" not in localize_amount("3杯", "鸡肉碎")
    assert "3杯" in localize_amount("3杯", "鸡肉碎")


def test_reference_book_match_boosts_when_user_mentions_book():
    western = {
        "id": "ben-055",
        "name": "鸡肉烤串",
        "scene": ["bento"],
        "cook_time": "20min",
        "source": {"book": "抗炎食谱100例", "file": "参考书籍/抗炎食谱100例 (Anti-Inflammatory Diet Cookbook).md"},
    }
    chinese = {
        "id": "cn-001",
        "name": "番茄炒蛋",
        "scene": ["bento"],
        "cook_time": "15min",
        "source": {"book": "家常菜", "file": "参考书籍/家常菜.md"},
    }
    from recommend_engine import score_recipe

    base_w = score_recipe(western, "bento", [], "")
    base_c = score_recipe(chinese, "bento", [], "")
    assert abs(base_w - base_c) < 0.01  # no origin-based penalty

    boosted = score_recipe(western, "bento", [], "", free_text="参考《抗炎食谱100例》")
    assert boosted > base_w
    assert reference_book_match_score(western, "抗炎食谱100例") >= 22
    assert "抗炎食谱100例" in extract_reference_book_hints("参考《抗炎食谱100例》做晚餐")


def test_default_scene_is_happy(tmp_path):
    index = tmp_path / "data" / "recipe-index"
    index.mkdir(parents=True)
    (index / "happy.yaml").write_text(
        """
- id: h1
  name: 快乐小食
  scene: [happy]
  tags: [小吃]
  servings: 1
  cook_time: 15min
  cost: 约10元
  method: 煎
  ingredients:
  - name: 鸡蛋
    amount: 1个
  steps: [煎]
  source: {book: test}
- id: r1
  name: 地方老菜
  scene: [regional]
  tags: [川渝]
  servings: 1
  cook_time: 20min
  cost: 约10元
  method: 炒
  ingredients:
  - name: 鸡蛋
    amount: 1个
  steps: [炒]
  source: {book: test}
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "SKILL.md").write_text("# test", encoding="utf-8")
    result = recommend(tmp_path, scene=None, ingredients=["鸡蛋"])
    assert result["primary"]["name"] == "快乐小食"
    assert "快乐餐" in result["why"]


def test_slow_recipe_filtered():
    assert not is_quick_recipe(DENGYING)
    assert parse_cook_time_minutes("45min") == 45
    assert parse_cook_time_minutes("480min") == 480


def test_validate_home_output_flags_bad_amounts():
    bad = {
        "cookTime": "30min",
        "ingredients": [{"name": "盐", "amount": "500克"}],
    }
    issues = validate_home_output(bad)
    assert any("盐" in i for i in issues)


def test_recommend_excludes_over_one_hour(tmp_path):
    index = tmp_path / "data" / "recipe-index"
    index.mkdir(parents=True)
    (index / "regional.yaml").write_text(
        """
- id: slow
  name: 灯影牛肉
  scene: [regional]
  tags: [川渝, 牛肉]
  servings: 4
  cook_time: 480min
  cost: 约80元
  method: 烤
  ingredients:
  - name: 牛肉
    amount: 100公斤
  steps: [慢烤]
  source: {book: 食遍中国}
- id: fast
  name: 快手炒牛肉
  scene: [regional]
  tags: [川渝, 牛肉]
  servings: 2
  cook_time: 25min
  cost: 约20元
  method: 炒
  ingredients:
  - name: 牛肉
    amount: 200克
  - name: 番茄
    amount: 1个
  steps: [切肉, 快炒]
  source: {book: 食遍中国}
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "SKILL.md").write_text("# test", encoding="utf-8")

    result = recommend(tmp_path, scene="regional", ingredients=["牛肉", "番茄"])
    assert result["primary"]["name"] == "快手炒牛肉"
    assert parse_cook_time_minutes(result["primary"]["cookTime"]) <= MAX_COOK_MINUTES
