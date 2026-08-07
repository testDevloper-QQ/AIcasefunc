#!/usr/bin/env python3
"""Validate Plan B raster illustration coverage (PNG/WebP/JPG only)."""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from illustration_resolver import resolve_dish_illustration, resolve_step_illustration  # noqa: E402
from recommend_engine import load_all_recipes  # noqa: E402
from recipe_format import filter_cooking_steps  # noqa: E402


def main() -> int:
    recipes = load_all_recipes(SKILL_ROOT)
    dish_png = 0
    missing_dish = 0
    missing_steps = 0
    total_steps = 0

    for recipe in recipes:
        url, source = resolve_dish_illustration(recipe, SKILL_ROOT)
        if url and source == "dish":
            dish_png += 1
        else:
            missing_dish += 1

        cooking = filter_cooking_steps(recipe.get("steps") or [])
        total_steps += len(cooking)
        for step_num, text in enumerate(cooking, start=1):
            step_url, _ = resolve_step_illustration(
                text, step_num - 1, SKILL_ROOT, recipe_id=recipe.get("id"), step_index=step_num
            )
            if not step_url:
                missing_steps += 1

    print(f"菜谱: {len(recipes)} 道")
    print(f"Hero PNG: {dish_png} 有 / {missing_dish} 待出图")
    print(f"步骤 PNG: {total_steps - missing_steps} 有 / {missing_steps} 待出图")
    print("OK: 无 SVG 模板依赖；待出图项请用 illustration_jobs_cli + Agent 批量生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
