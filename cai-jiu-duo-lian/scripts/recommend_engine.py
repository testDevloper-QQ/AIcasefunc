"""Recommend recipes from Skill YAML index."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from home_cooking_fallback import build_fallback_recipe
from recipe_format import (
    GUIDELINE_REF,
    MAX_COOK_MINUTES,
    enrich_ingredients,
    format_cook_time_cn,
    format_steps,
    ingredient_art_url,
    is_quick_recipe,
    normalize_ingredients,
    parse_cook_time_minutes,
    validate_home_output,
)

SERVINGS_MAP = {"一人食": 1, "二人家庭": 2, "多人家庭": 4}
DEFAULT_SCENE = "happy"


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


def _recipe_haystack(recipe: dict) -> str:
    return " ".join([
        recipe.get("name", ""),
        " ".join(recipe.get("tags", [])),
        " ".join(i.get("name", "") for i in recipe.get("ingredients", [])),
    ])


def _ingredient_match_count(recipe: dict, user_ingredients: list[str]) -> int:
    if not user_ingredients:
        return 0
    hay = _recipe_haystack(recipe)
    return sum(1 for u in user_ingredients if u and u in hay)


def _matches_all_user_ingredients(recipe: dict, user_ingredients: list[str]) -> bool:
    if not user_ingredients:
        return True
    return _ingredient_match_count(recipe, user_ingredients) == len(user_ingredients)


def score_recipe(
    recipe: dict,
    scene: str | None,
    user_ingredients: list[str],
    taste: str,
) -> float:
    score = 0.0
    scenes = recipe.get("scene") or []
    effective = scene or DEFAULT_SCENE
    match_count = _ingredient_match_count(recipe, user_ingredients)

    if user_ingredients:
        if match_count == 0:
            return -100.0
        score += match_count * 20
        if _matches_all_user_ingredients(recipe, user_ingredients):
            score += 25

    if effective in scenes:
        score += 8
    elif user_ingredients:
        score -= 2
    else:
        score -= 3

    if taste:
        hay = _recipe_haystack(recipe) + (recipe.get("method") or "")
        if any(k in hay for k in taste.replace("，", " ").split()):
            score += 3

    minutes = parse_cook_time_minutes(recipe.get("cook_time"))
    if minutes <= 30:
        score += 2
    elif minutes <= MAX_COOK_MINUTES:
        score += 1
    return score


def _hero_arts(recipe: dict, skill_root: Path, user_ingredients: list[str]) -> list[str]:
    arts: list[str] = []
    line_art = (recipe.get("line_art") or "").replace("\\", "/").lstrip("/")
    if line_art and (skill_root / line_art).exists():
        arts.append(f"/skill-assets/{line_art}")

    for ing in recipe.get("ingredients") or []:
        url = ingredient_art_url(ing.get("name", ""), skill_root)
        if url and url not in arts:
            arts.append(url)

    for name in user_ingredients:
        url = ingredient_art_url(name, skill_root)
        if url and url not in arts:
            arts.append(url)

    return arts[:4]


def format_recipe(
    recipe: dict,
    skill_root: Path,
    target_servings: int | None,
    user_ingredients: list[str] | None = None,
) -> dict:
    src = recipe.get("source") or {}
    hero_arts = _hero_arts(recipe, skill_root, user_ingredients or [])
    art_url = hero_arts[0] if hero_arts else ""

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
        "heroArts": hero_arts,
        "generated": bool(recipe.get("generated")),
        "disclaimer": "仅供参考，非医疗建议" if "health" in (recipe.get("scene") or []) else None,
    }
    if formatted["generated"]:
        formatted["disclaimer"] = "索引未收录该食材组合，以下为 AI 家常菜建议，请按口味调整。"
    qa = validate_home_output(formatted, servings=target_servings or recipe.get("servings") or 1)
    if qa:
        formatted["qualityNotes"] = qa
    return formatted


def _resolve_scene(scene: str | None) -> str:
    return scene or DEFAULT_SCENE


def _filter_by_ingredients(pool: list[dict], user_ingredients: list[str]) -> list[dict]:
    if not user_ingredients:
        return pool
    return [r for r in pool if _matches_all_user_ingredients(r, user_ingredients)]


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
    ingredient_pool = _filter_by_ingredients(pool, all_ingredients)

    used_fallback = False
    if all_ingredients and not ingredient_pool:
        servings = target or 2
        ingredient_pool = [
            build_fallback_recipe(all_ingredients, effective_scene, servings=servings)
        ]
        used_fallback = True

    ranked = sorted(
        ingredient_pool,
        key=lambda r: score_recipe(r, effective_scene, all_ingredients, combined_taste),
        reverse=True,
    )
    top = [r for r in ranked if score_recipe(r, effective_scene, all_ingredients, combined_taste) > 0][:3]
    if not top:
        top = ranked[:3]

    primary = format_recipe(top[0], skill_root, target, all_ingredients)
    alternates = [format_recipe(r, skill_root, target, all_ingredients) for r in top[1:3]]

    why_parts = []
    if effective_scene:
        scene_labels = {
            "bento": "便当", "light-meal": "轻食", "seasonal": "时令",
            "regional": "地方味", "health": "调理", "happy": "快乐餐",
        }
        why_parts.append(f"符合「{scene_labels.get(effective_scene, effective_scene)}」饮食偏好")
    if all_ingredients:
        if used_fallback:
            why_parts.append(
                f"索引暂无含 {'、'.join(all_ingredients)} 的菜谱，已按中国家常菜生成「{primary['name']}」"
            )
        else:
            why_parts.append(f"食材对应：{'、'.join(all_ingredients)} 均在推荐菜中出现")
    if not scene:
        why_parts.append("未选场景，默认按「快乐餐」推荐")
    why_parts.append(f"烹饪时间均在 {MAX_COOK_MINUTES} 分钟内")
    why_parts.append(f"份量已对标{GUIDELINE_REF}核验")

    return {
        "primary": primary,
        "alternates": alternates,
        "why": "，".join(why_parts) + "。",
        "usedFallback": used_fallback,
    }
