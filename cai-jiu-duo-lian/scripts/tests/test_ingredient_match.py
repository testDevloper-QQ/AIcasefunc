"""Tests for ingredient matching and AI home-cooking fallback."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from home_cooking_fallback import build_fallback_recipe  # noqa: E402
from recommend_engine import (  # noqa: E402
    _ingredient_match_count,
    recommend,
)

SKILL_ROOT = Path(__file__).resolve().parents[2]


def test_no_豆角_in_index():
    from recommend_engine import load_all_recipes

    recipes = load_all_recipes(SKILL_ROOT)
    assert all("豆角" not in (r.get("name", "") + " ".join(i.get("name", "") for i in r.get("ingredients", []))) for r in recipes)


def test_fallback_dish_name_for_greenbean_eggplant():
    recipe = build_fallback_recipe(["豆角", "茄子"], "seasonal", servings=2)
    assert "茄子" in recipe["name"] or "豆角" in recipe["name"]


def test_seasonal_greenbean_eggplant_uses_fallback():
    result = recommend(
        SKILL_ROOT,
        scene="seasonal",
        ingredients=[],
        custom_ingredients=["豆角", "茄子"],
    )
    assert result["usedFallback"] is True
    assert result["primary"]["name"] == "豆角烧茄子"
    assert "豆角" in result["primary"]["name"] or any("豆角" in i["name"] for i in result["primary"]["ingredients"])
    assert any("茄子" in i["name"] for i in result["primary"]["ingredients"])
    assert result["primary"]["heroArts"]
    assert "greenbean" in result["primary"]["heroArts"][0] or "eggplant" in " ".join(result["primary"]["heroArts"])


def test_tomato_egg_index_match_not_shrimp():
    result = recommend(
        SKILL_ROOT,
        scene="seasonal",
        ingredients=["番茄", "鸡蛋"],
    )
    name = result["primary"]["name"]
    hay = name + " ".join(i["name"] for i in result["primary"]["ingredients"])
    assert "番茄" in hay or "鸡蛋" in hay
    assert "虾仁" not in name or ("番茄" in hay and "鸡蛋" in hay)


def test_zero_match_scores_negative():
    from recommend_engine import load_all_recipes, score_recipe

    recipes = load_all_recipes(SKILL_ROOT)
    shrimp = next(r for r in recipes if r.get("name") == "水芹炒虾仁")
    assert _ingredient_match_count(shrimp, ["豆角", "茄子"]) == 0
    assert score_recipe(shrimp, "seasonal", ["豆角", "茄子"], "") < 0
