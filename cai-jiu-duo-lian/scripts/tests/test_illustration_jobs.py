"""Tests for Agent-side illustration job pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_build_jobs_skips_existing_dish(tmp_path: Path):
    from illustration_jobs import build_jobs_for_recipe, dish_asset_rel

    root = tmp_path
    recipe = {"id": "r1", "name": "测试菜", "method": "炒", "steps": ["步骤一"]}
    dish_path = root / dish_asset_rel("r1")
    dish_path.parent.mkdir(parents=True, exist_ok=True)
    dish_path.write_bytes(b"\x89PNG")

    jobs = build_jobs_for_recipe(recipe, root, include_steps=True)
    kinds = [j["kind"] for j in jobs]
    assert "dish" not in kinds
    assert any(j["kind"] == "step" for j in jobs)


def test_commit_illustration_dish(tmp_path: Path):
    from illustration_jobs import commit_illustration, dish_exists

    root = tmp_path
    src = tmp_path / "gen.png"
    src.write_bytes(b"\x89PNG\r\n\x1a\n")
    result = commit_illustration(
        recipe_id="r99",
        kind="dish",
        source_file=src,
        skill_root=root,
        generator="cursor",
    )
    assert result["ok"]
    assert dish_exists("r99", root)
    assert result["url"].endswith("r99.png")


def test_jobs_cli_importable():
    import illustration_jobs_cli  # noqa: F401

    assert hasattr(illustration_jobs_cli, "main")
