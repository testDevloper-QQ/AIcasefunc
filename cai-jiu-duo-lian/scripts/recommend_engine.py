"""Recommend recipes from Skill YAML index."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SERVINGS_MAP = {"一人食": 1, "二人家庭": 2, "多人家庭": 4}


def load_all_recipes(skill_root: Path) -> list[dict[str, Any]]:
    index_dir = skill_root / "data" / "recipe-index"
    recipes: list[dict[str, Any]] = []
    for f in sorted(index_dir.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        items = yaml.safe_load(f.read_text(encoding="utf-8"))
        if isinstance(items, list):
            recipes.extend(items)
    return recipes


def _ingredient_match(recipe: dict, user_ingredients: list[str]) -> int:
    if not user_ingredients:
        return 0
    hay = recipe.get("name", "") + " ".join(
        i.get("name", "") for i in recipe.get("ingredients", [])
    ) + " ".join(recipe.get("tags", []))
    return sum(1 for u in user_ingredients if u in hay)


def _scale_servings(recipe: dict, target: int | None) -> list[dict]:
    ingredients = recipe.get("ingredients", [])
    if not target or not ingredients:
        return ingredients
    base = recipe.get("servings") or 2
    if base == target:
        return ingredients
    ratio = target / base
    scaled = []
    for ing in ingredients:
        amount = ing.get("amount", "")
        scaled.append({"name": ing.get("name", ""), "amount": f"{amount}（按{target}人份调整，原{base}人份×{ratio:.1f}）"})
    return scaled


def score_recipe(
    recipe: dict,
    scene: str | None,
    ingredients: list[str],
    taste: str,
) -> float:
    score = 0.0
    scenes = recipe.get("scene") or []
    if scene:
        if scene in scenes:
            score += 10
        else:
            score -= 3
    score += _ingredient_match(recipe, ingredients) * 5
    if taste:
        tags = " ".join(recipe.get("tags", [])) + recipe.get("name", "") + recipe.get("method", "")
        if any(k in tags for k in taste.replace("，", " ").split()):
            score += 3
    score += min(len(recipe.get("steps", [])), 5) * 0.1
    return score


def format_recipe(recipe: dict, skill_root: Path, target_servings: int | None) -> dict:
    src = recipe.get("source") or {}
    line_art = recipe.get("line_art") or ""
    art_url = ""
    if line_art:
        rel = line_art.replace("\\", "/").lstrip("/")
        if (skill_root / rel).exists():
            art_url = f"/skill-assets/{rel}"
    return {
        "id": recipe.get("id"),
        "name": recipe.get("name"),
        "scene": recipe.get("scene", []),
        "tags": recipe.get("tags", []),
        "cookTime": recipe.get("cook_time"),
        "cost": recipe.get("cost"),
        "method": recipe.get("method"),
        "servings": target_servings or recipe.get("servings"),
        "ingredients": _scale_servings(recipe, target_servings),
        "steps": recipe.get("steps", []),
        "source": {
            "book": src.get("book"),
            "chapter": src.get("chapter"),
        },
        "lineArtUrl": art_url,
        "disclaimer": "仅供参考，非医疗建议" if "health" in (recipe.get("scene") or []) else None,
    }


def recommend(
    skill_root: Path,
    *,
    scene: str | None,
    ingredients: list[str],
    taste: str = "",
    servings_label: str = "",
    free_text: str = "",
) -> dict:
    recipes = load_all_recipes(skill_root)
    if not recipes:
        raise ValueError("索引为空，请检查 data/recipe-index")

    target = SERVINGS_MAP.get(servings_label)
    combined_taste = " ".join(filter(None, [taste, free_text]))

    ranked = sorted(
        recipes,
        key=lambda r: score_recipe(r, scene, ingredients, combined_taste),
        reverse=True,
    )
    top = [r for r in ranked if score_recipe(r, scene, ingredients, combined_taste) > 0][:3]
    if not top:
        top = ranked[:3]

    primary = format_recipe(top[0], skill_root, target)
    alternates = [format_recipe(r, skill_root, target) for r in top[1:3]]

    why_parts = []
    if scene:
        why_parts.append(f"符合「{scene}」饮食偏好")
    if ingredients:
        why_parts.append(f"尽量用上你选的 {'、'.join(ingredients)}")
    if not why_parts:
        why_parts.append("根据索引综合匹配")

    return {
        "primary": primary,
        "alternates": alternates,
        "why": "，".join(why_parts) + "。",
    }
