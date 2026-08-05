"""Tests for Plan B illustration resolver."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from illustration_resolver import (  # noqa: E402
    resolve_dish_illustration,
    resolve_step_illustration,
)
from recipe_format import format_steps  # noqa: E402
from recommend_engine import recommend  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[2]


def test_resolve_sea014_dish_missing_without_png():
    url, source = resolve_dish_illustration({"id": "sea-014", "name": "丝瓜风鸡粥", "method": "煮", "tags": ["粥"]}, SKILL_ROOT)
    if url:
        assert url.endswith(".png") or url.endswith(".webp")
        assert source == "dish"
    else:
        assert source == "missing"


def test_resolve_no_svg_template_fallback():
    url, source = resolve_dish_illustration({"id": "x-1", "name": "彩椒炒虾", "method": "炒"}, SKILL_ROOT)
    assert source == "missing"
    assert url == ""


def test_resolve_step_marinate_and_porridge():
    url1, sid1 = resolve_step_illustration("鸡胸肉洗净，撕成丝状，用酱油腌制5分钟", 0, SKILL_ROOT)
    assert sid1 == "board_marinate"
    assert url1 == "" or url1.endswith(".png")

    url2, sid2 = resolve_step_illustration("大米和糯米混合煮粥，至七分熟时放入鸡丝", 1, SKILL_ROOT)
    assert sid2 == "pot_porridge_simmer"
    assert url2 == "" or url2.endswith(".png")


def test_format_steps_use_skill_asset_urls_or_pending():
    steps = format_steps(
        ["鸡胸肉洗净，用酱油腌制5分钟。", "大米煮粥至七分熟。"],
        [{"name": "鸡胸肉", "amount": "适量"}],
        SKILL_ROOT,
        recipe_id="test-r1",
    )
    assert len(steps) == 2
    for s in steps:
        url = s.get("stepArtUrl") or ""
        assert url == "" or url.startswith("/skill-assets/")


def test_recommend_chicken_hero_png_or_missing():
    result = recommend(SKILL_ROOT, scene="seasonal", ingredients=["鸡肉"])
    hero = result["primary"].get("heroIllustrationUrl") or result["primary"].get("heroCompositeUrl")
    if hero:
        assert hero.startswith("/skill-assets/")
        assert hero.endswith(".png") or hero.endswith(".webp")
    else:
        assert result["primary"].get("heroIllustrationSource") == "missing"
