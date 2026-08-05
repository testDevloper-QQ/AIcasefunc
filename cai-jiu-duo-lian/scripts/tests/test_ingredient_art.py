"""Tests for ingredient grid hand-drawn art."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recipe_format import enrich_ingredients, guess_ingredient_art_key  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[2]

SHRIMP_RECIPE_ING = [
    {"name": "水芹", "amount": "1把"},
    {"name": "白虾", "amount": "适量"},
    {"name": "彩椒", "amount": "各半个"},
    {"name": "糖", "amount": "少许"},
    {"name": "盐", "amount": "少许"},
    {"name": "白胡椒", "amount": "少许"},
]


def test_shrimp_recipe_ingredient_art_is_raster_or_pending():
    rows = enrich_ingredients(SHRIMP_RECIPE_ING, SKILL_ROOT)
    assert len(rows) == 6
    for row in rows:
        url = row.get("artUrl") or ""
        assert url == "" or (url.startswith("/skill-assets/") and "/assets/illustrations/" in url)


def test_seasoning_art_keys():
    assert guess_ingredient_art_key("糖") == "sugar"
    assert guess_ingredient_art_key("白胡椒") == "whitepepper"
    assert guess_ingredient_art_key("水芹") == "celery"
