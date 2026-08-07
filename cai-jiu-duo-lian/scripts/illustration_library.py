"""Illustration material library: book-indexed preload, shared dishes & ingredients."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from ai_illustration_client import build_dish_prompt, build_ingredient_prompt, build_step_prompt
from illustration_jobs import (
    build_jobs_for_recipe,
    dish_asset_rel,
    dish_exists,
    ingredient_asset_rel,
    ingredient_exists,
    step_asset_rel,
    step_exists,
    skill_root_path,
)
from illustration_resolver import (
    DISH_DIR,
    DISH_SHARED_DIR,
    ING_DIR,
    STEP_DIR,
    dish_share_basename,
    find_illustration_asset,
    shared_dish_asset_rel,
)
from recipe_format import guess_ingredient_art_key, filter_cooking_steps, localize_text

LIBRARY_DIR = "data/illustration-library"
BOOKS_FILE = f"{LIBRARY_DIR}/books.yaml"
INGREDIENTS_FILE = f"{LIBRARY_DIR}/ingredients.yaml"
COVERAGE_DIR = f"{LIBRARY_DIR}/coverage"


def library_dir(skill_root: Path | None = None) -> Path:
    return skill_root_path(skill_root) / LIBRARY_DIR


def load_books(skill_root: Path | None = None) -> list[dict[str, Any]]:
    path = library_dir(skill_root) / "books.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("books") or [])


def load_ingredient_catalog(skill_root: Path | None = None) -> list[dict[str, Any]]:
    path = library_dir(skill_root) / "ingredients.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("ingredients") or [])


def save_ingredient_catalog(rows: list[dict[str, Any]], skill_root: Path | None = None) -> Path:
    root = library_dir(skill_root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "ingredients.yaml"
    payload = {"version": 1, "ingredients": rows}
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def recipes_for_book(recipes: list[dict[str, Any]], book_title: str) -> list[dict[str, Any]]:
    title = (book_title or "").strip()
    return [r for r in recipes if ((r.get("source") or {}).get("book") or "").strip() == title]


def book_by_id(books: list[dict[str, Any]], book_id: str) -> dict[str, Any] | None:
    for b in books:
        if b.get("id") == book_id:
            return b
    return None


def collect_ingredient_keys(recipes: list[dict[str, Any]]) -> dict[str, str]:
    """art_key -> preferred display name (longest alias)."""
    keys: dict[str, str] = {}
    for recipe in recipes:
        for ing in recipe.get("ingredients") or []:
            name = (ing.get("name") or "").strip()
            if not name:
                continue
            key = guess_ingredient_art_key(name) or "generic"
            if key not in keys or len(name) > len(keys[key]):
                keys[key] = name
    return keys


def bootstrap_ingredient_catalog(recipes: list[dict[str, Any]], skill_root: Path | None = None) -> Path:
    """Build ingredients.yaml from index + guess_ingredient_art_key."""
    root = skill_root_path(skill_root)
    keys = collect_ingredient_keys(recipes)
    rows: list[dict[str, Any]] = []
    for art_key in sorted(keys):
        display = keys[art_key]
        has_asset = bool(find_illustration_asset(ING_DIR, art_key, root))
        rows.append({
            "artKey": art_key,
            "displayName": display,
            "category": _ingredient_category_guess(display, art_key),
            "aliases": _aliases_for_key(recipes, art_key),
            "assetPath": ingredient_asset_rel(art_key),
            "hasAsset": has_asset,
        })
    return save_ingredient_catalog(rows, root)


def _ingredient_category_guess(display: str, art_key: str) -> str:
    if art_key in {"salt", "sugar", "chilipowder", "turmeric", "cumin", "cinnamon", "coriander",
                   "oregano", "rosemary", "whitepepper", "blackpepper", "spicejar", "ginger", "gingerpaste"}:
        return "seasoning"
    if art_key in {"oil", "soy", "wine", "milk", "yogurt", "limejuice", "honey"}:
        return "condiment"
    return "ingredient"


def _aliases_for_key(recipes: list[dict[str, Any]], art_key: str) -> list[str]:
    names: set[str] = set()
    for recipe in recipes:
        for ing in recipe.get("ingredients") or []:
            name = (ing.get("name") or "").strip()
            if name and (guess_ingredient_art_key(name) or "generic") == art_key:
                names.add(name)
    return sorted(names, key=len, reverse=True)


def dish_asset_exists(recipe: dict[str, Any], skill_root: Path | None) -> bool:
    root = skill_root_path(skill_root)
    rid = (recipe.get("id") or "").strip()
    if rid and dish_exists(rid, root):
        return True
    share = dish_share_basename(recipe.get("name") or "")
    return bool(find_illustration_asset(DISH_SHARED_DIR, share, root))


def audit_book(
    recipes: list[dict[str, Any]],
    book_title: str,
    skill_root: Path | None = None,
) -> dict[str, Any]:
    root = skill_root_path(skill_root)
    pool = recipes_for_book(recipes, book_title)
    missing_dishes: list[str] = []
    missing_steps: list[str] = []
    missing_ingredients: list[str] = []
    shared_dish_groups: dict[str, list[str]] = {}

    seen_ing: set[str] = set()
    seen_dish_share: set[str] = set()

    for recipe in pool:
        rid = recipe.get("id") or ""
        name = recipe.get("name") or ""
        share = dish_share_basename(name)
        shared_dish_groups.setdefault(share, []).append(rid)

        if share not in seen_dish_share:
            seen_dish_share.add(share)
            if not dish_asset_exists(recipe, root):
                missing_dishes.append(f"{share} ({name})")

        for step_num, _text in enumerate(filter_cooking_steps(recipe.get("steps") or []), start=1):
            if not step_exists(rid, step_num, root):
                missing_steps.append(f"{rid} step {step_num}")

        for ing in recipe.get("ingredients") or []:
            iname = (ing.get("name") or "").strip()
            if not iname:
                continue
            key = guess_ingredient_art_key(iname) or "generic"
            if key in seen_ing:
                continue
            seen_ing.add(key)
            if not ingredient_exists(key, root):
                missing_ingredients.append(f"{key} ({iname})")

    duplicate_names = {k: v for k, v in shared_dish_groups.items() if len(v) > 1}

    return {
        "book": book_title,
        "recipeCount": len(pool),
        "uniqueDishShares": len(shared_dish_groups),
        "duplicateDishNames": len(duplicate_names),
        "uniqueIngredientKeys": len(seen_ing),
        "missingDishes": missing_dishes,
        "missingSteps": missing_steps,
        "missingIngredients": missing_ingredients,
        "duplicateDishGroups": duplicate_names,
    }


def build_book_jobs(
    recipes: list[dict[str, Any]],
    book_title: str,
    skill_root: Path | None = None,
    *,
    force: bool = False,
    max_candidates: int = 3,
) -> list[dict[str, Any]]:
    """Deduplicated preload jobs for one book: shared dish + shared ingredients."""
    root = skill_root_path(skill_root)
    pool = recipes_for_book(recipes, book_title)
    jobs: list[dict[str, Any]] = []
    seen_dish_share: set[str] = set()
    seen_ing: set[str] = set()

    for recipe in pool:
        rid = (recipe.get("id") or "").strip()
        name = recipe.get("name") or rid
        share = dish_share_basename(name)

        if share not in seen_dish_share:
            seen_dish_share.add(share)
            need = force or not dish_asset_exists(recipe, root)
            if need:
                canonical = next(r for r in pool if dish_share_basename(r.get("name") or "") == share)
                rel = shared_dish_asset_rel(name)
                jobs.append({
                    "jobId": f"book:{book_title}:dish:{share}",
                    "kind": "dish",
                    "recipeId": canonical.get("id"),
                    "recipeName": name,
                    "shareKey": share,
                    "sharedDish": True,
                    "relPath": rel,
                    "absPath": str((root / rel).resolve()),
                    "prompt": build_dish_prompt(canonical),
                    "maxCandidates": max_candidates,
                    "generator": "host-agent",
                    "instructions": "共享成品图：同名菜仅出一张，落盘到 dishes/shared/{菜名}.png",
                })

        for ing in recipe.get("ingredients") or []:
            iname = (ing.get("name") or "").strip()
            if not iname:
                continue
            key = guess_ingredient_art_key(iname) or "generic"
            if key in seen_ing:
                continue
            seen_ing.add(key)
            if not force and ingredient_exists(key, root):
                continue
            rel = ingredient_asset_rel(key)
            jobs.append({
                "jobId": f"book:{book_title}:ingredient:{key}",
                "kind": "ingredient",
                "recipeId": rid,
                "artKey": key,
                "ingredientName": iname,
                "relPath": rel,
                "absPath": str((root / rel).resolve()),
                "prompt": build_ingredient_prompt(iname, key),
                "maxCandidates": max_candidates,
                "generator": "host-agent",
                "instructions": "共享食材线稿：全库共用 ingredients/{artKey}.png",
            })

        jobs.extend(
            build_jobs_for_recipe(
                recipe,
                root,
                force=force,
                include_steps=True,
                include_ingredients=False,
                include_dish=False,
                max_candidates=max_candidates,
            )
        )
    return jobs


def save_coverage_report(report: dict[str, Any], book_id: str, skill_root: Path | None = None) -> Path:
    root = library_dir(skill_root) / "coverage"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{book_id}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
