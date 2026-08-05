"""Tests for illustration material library."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from illustration_library import audit_book, build_book_jobs, recipes_for_book  # noqa: E402
from illustration_resolver import dish_share_basename, resolve_dish_illustration  # noqa: E402
from recommend_engine import load_all_recipes  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[2]


def test_dish_share_basename():
    assert dish_share_basename("香烤全鸡") == "香烤全鸡"


def test_audit_anti_inflammatory_book():
    recipes = load_all_recipes(SKILL_ROOT)
    pool = recipes_for_book(recipes, "抗炎食谱100例")
    assert len(pool) >= 100
    report = audit_book(recipes, "抗炎食谱100例", SKILL_ROOT)
    assert report["recipeCount"] == len(pool)
    assert report["uniqueIngredientKeys"] > 50


def test_build_book_jobs_deduplicates_ingredients():
    recipes = load_all_recipes(SKILL_ROOT)
    jobs = build_book_jobs(recipes, "抗炎食谱100例", SKILL_ROOT, force=True)
    ing_jobs = [j for j in jobs if j["kind"] == "ingredient"]
    keys = [j["artKey"] for j in ing_jobs]
    assert len(keys) == len(set(keys))


def test_resolve_shared_dish_when_id_missing(tmp_path: Path):
    share_dir = tmp_path / "assets" / "illustrations" / "dishes" / "shared"
    share_dir.mkdir(parents=True)
    (share_dir / "测试菜.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    url, source = resolve_dish_illustration({"id": "x-1", "name": "测试菜"}, tmp_path)
    assert source == "shared"
    assert url.endswith("测试菜.png")
