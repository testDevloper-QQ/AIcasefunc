"""Recommend recipes from Skill YAML index."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from recipe_format import (
    GUIDELINE_REF,
    MAX_COOK_MINUTES,
    enrich_ingredients,
    format_cook_time_cn,
    format_steps,
    is_quick_recipe,
    normalize_ingredients,
    parse_cook_time_minutes,
    validate_home_output,
)

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
    return sum(1 for u in user_ingredients if u and u in hay)


DEFAULT_SCENE = "happy"


def _custom_ingredient_boost(recipe: dict, custom_ingredients: list[str], scene: str) -> float:
    if not custom_ingredients:
        return 0.0
    hay = recipe.get("name", "") + " ".join(recipe.get("tags", [])) + " ".join(
        i.get("name", "") for i in recipe.get("ingredients", [])
    )
    hits = sum(1 for u in custom_ingredients if u and (u in hay or any(u in tag for tag in recipe.get("tags", []))))
    if scene == "regional" and "regional" in (recipe.get("scene") or []):
        return hits * 4
    return hits * 2


def score_recipe(
    recipe: dict,
    scene: str | None,
    ingredients: list[str],
    taste: str,
    custom_ingredients: list[str] | None = None,
) -> float:
    score = 0.0
    scenes = recipe.get("scene") or []
    effective = scene or DEFAULT_SCENE
    if effective in scenes:
        score += 10
    else:
        score -= 3
    score += _ingredient_match(recipe, ingredients) * 5
    score += _custom_ingredient_boost(recipe, custom_ingredients or [], effective)
    if taste:
        tags = " ".join(recipe.get("tags", [])) + recipe.get("name", "") + recipe.get("method", "")
        if any(k in tags for k in taste.replace("，", " ").split()):
            score += 3
    minutes = parse_cook_time_minutes(recipe.get("cook_time"))
    if minutes <= 30:
        score += 2
    elif minutes <= MAX_COOK_MINUTES:
        score += 1
    return score


def format_recipe(recipe: dict, skill_root: Path, target_servings: int | None) -> dict:
    src = recipe.get("source") or {}
    line_art = recipe.get("line_art") or ""
    art_url = ""
    if line_art:
        rel = line_art.replace("\\", "/").lstrip("/")
        if (skill_root / rel).exists():
            art_url = f"/skill-assets/{rel}"

    ingredients = enrich_ingredients(normalize_ingredients(recipe, target_servings), skill_root)
    steps = format_steps(recipe.get("steps") or [], ingredients, skill_root)
    cook_time = recipe.get("cook_time") or "20min"
    cook_time_display = format_cook_time_cn(cook_time)

    formatted = {
        "id": recipe.get("id"),
        "name": recipe.get("name"),
        "scene": recipe.get("scene", []),
        "tags": recipe.get("tags", []),
        "cookTime": cook_time,
        "cookTimeDisplay": cook_time_display,
        "cost": recipe.get("cost"),
        "method": recipe.get("method"),
        "servings": target_servings or recipe.get("servings"),
        "ingredients": ingredients,
        "steps": steps,
        "source": {
            "book": src.get("book"),
            "chapter": src.get("chapter"),
        },
        "lineArtUrl": art_url,
        "heroImageUrl": art_url,
        "disclaimer": "仅供参考，非医疗建议" if "health" in (recipe.get("scene") or []) else None,
    }
    qa = validate_home_output(formatted, servings=target_servings or recipe.get("servings") or 1)
    if qa:
        formatted["qualityNotes"] = qa
    return formatted


def _resolve_scene(scene: str | None) -> str:
    return scene or DEFAULT_SCENE


def recommend(
    skill_root: Path,
    *,
    scene: str | None,
    ingredients: list[str],
    taste: str = "",
    servings_label: str = "",
    free_text: str = "",
    custom_ingredients: list[str] | None = None,
) -> dict:
    recipes = load_all_recipes(skill_root)
    if not recipes:
        raise ValueError("索引为空，请检查 data/recipe-index")

    custom = [x.strip() for x in (custom_ingredients or []) if x and x.strip()]
    all_ingredients = list(dict.fromkeys([*ingredients, *custom]))
    effective_scene = _resolve_scene(scene)
    target = SERVINGS_MAP.get(servings_label)
    combined_taste = " ".join(filter(None, [taste, free_text]))

    quick = [r for r in recipes if is_quick_recipe(r)]
    pool = quick if quick else recipes

    ranked = sorted(
        pool,
        key=lambda r: score_recipe(r, effective_scene, all_ingredients, combined_taste, custom),
        reverse=True,
    )
    top = [
        r for r in ranked
        if score_recipe(r, effective_scene, all_ingredients, combined_taste, custom) > 0
    ][:3]
    if not top:
        top = ranked[:3]

    primary = format_recipe(top[0], skill_root, target)
    alternates = [format_recipe(r, skill_root, target) for r in top[1:3]]

    why_parts = []
    if effective_scene:
        scene_labels = {
            "bento": "便当", "light-meal": "轻食", "seasonal": "时令",
            "regional": "地方味", "health": "调理", "happy": "快乐餐",
        }
        why_parts.append(f"符合「{scene_labels.get(effective_scene, effective_scene)}」饮食偏好")
    if all_ingredients:
        why_parts.append(f"尽量用上你选的 {'、'.join(all_ingredients)}")
    if not scene:
        why_parts.append("未选场景，默认按「快乐餐」推荐")
    why_parts.append(f"烹饪时间均在 {MAX_COOK_MINUTES} 分钟内")
    why_parts.append(f"份量已对标{GUIDELINE_REF}核验")
    if not why_parts:
        why_parts.append("根据索引综合匹配")

    return {
        "primary": primary,
        "alternates": alternates,
        "why": "，".join(why_parts) + "。",
    }
