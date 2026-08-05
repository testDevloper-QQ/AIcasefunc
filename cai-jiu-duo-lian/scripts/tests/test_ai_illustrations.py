"""Tests for AI illustration pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_illustration_client import (  # noqa: E402
    MAX_CANDIDATES,
    build_dish_prompt,
    build_ingredient_prompt,
    build_step_prompt,
    select_best_candidate,
)
from illustration_resolver import find_illustration_asset, resolve_step_illustration  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[2]
DISH_DIR = SKILL_ROOT / "assets" / "illustrations" / "dishes"
STEP_DIR = SKILL_ROOT / "assets" / "illustrations" / "steps"


def test_max_candidates_is_three():
    assert MAX_CANDIDATES == 3


def test_build_dish_prompt_contains_name():
    p = build_dish_prompt({"name": "火鸡肉馅甜椒", "method": "烤", "ingredients": [{"name": "甜椒"}]})
    assert "火鸡肉馅甜椒" in p or "Finished dish" in p
    assert "watercolor" in p.lower() or "water" in p.lower()


def test_build_step_prompt_contains_action():
    p = build_step_prompt({"name": "火鸡肉馅甜椒"}, 1, "将烤箱预热至约177℃。")
    assert "177" in p or "oven" in p.lower() or "step" in p.lower()


def test_build_ingredient_prompt_line_art():
    p = build_ingredient_prompt("辣椒粉", "chilipowder")
    assert "line art" in p.lower()
    assert "chilipowder" in p


def test_select_best_candidate_picks_largest(tmp_path: Path):
    small = tmp_path / "candidate-1.png"
    large = tmp_path / "candidate-2.png"
    small.write_bytes(b"x" * 100)
    large.write_bytes(b"x" * 500)
    assert select_best_candidate([small, large]) == large


def test_resolve_recipe_specific_step_png(tmp_path: Path, monkeypatch):
    """When {id}-step-{n}.png exists, prefer over generic scene SVG."""
    rid = "test-recipe-001"
    png = STEP_DIR / f"{rid}-step-1.png"
    created = False
    if not png.is_file():
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\n")
        created = True
    try:
        url, sid = resolve_step_illustration(
            "任意文字",
            0,
            SKILL_ROOT,
            recipe_id=rid,
            step_index=1,
        )
        assert url.endswith(f"{rid}-step-1.png")
        assert sid == f"{rid}-step-1"
    finally:
        if created:
            png.unlink(missing_ok=True)


def test_find_illustration_prefers_png_over_svg(tmp_path: Path):
    base = tmp_path / "assets" / "illustrations" / "dishes"
    base.mkdir(parents=True)
    (base / "demo.svg").write_text("<svg/>", encoding="utf-8")
    (base / "demo.png").write_bytes(b"\x89PNG")

    url = find_illustration_asset("assets/illustrations/dishes", "demo", tmp_path)
    assert url.endswith("demo.png")


def test_generate_ai_module_importable():
    import generate_ai_illustrations  # noqa: F401

    assert hasattr(generate_ai_illustrations, "main")
