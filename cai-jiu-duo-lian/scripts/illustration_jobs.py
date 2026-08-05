"""Build illustration jobs for Agent-side image generation (Cursor / WorkBuddy)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from ai_illustration_client import MAX_CANDIDATES, build_dish_prompt, build_ingredient_prompt, build_step_prompt
from illustration_resolver import ING_DIR, find_illustration_asset, ILLUSTRATIONS, DISH_DIR, STEP_DIR
from recipe_format import guess_ingredient_art_key, filter_cooking_steps, localize_text

MANIFEST_NAME = "ai-manifest.json"
JobKind = Literal["dish", "step", "ingredient"]


def skill_root_path(skill_root: Path | None = None) -> Path:
    return skill_root or Path(__file__).resolve().parents[1]


def manifest_path(skill_root: Path | None = None) -> Path:
    return skill_root_path(skill_root) / ILLUSTRATIONS / MANIFEST_NAME


def load_manifest(skill_root: Path | None = None) -> dict[str, Any]:
    path = manifest_path(skill_root)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"version": 1, "generator": "agent", "recipes": {}}


def save_manifest(manifest: dict[str, Any], skill_root: Path | None = None) -> None:
    path = manifest_path(skill_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest["updatedAt"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def dish_asset_rel(recipe_id: str) -> str:
    return f"{DISH_DIR}/{recipe_id}.png"


def step_asset_rel(recipe_id: str, step_index: int) -> str:
    return f"{STEP_DIR}/{recipe_id}-step-{step_index}.png"


def ingredient_asset_rel(art_key: str) -> str:
    return f"{ING_DIR}/{art_key}.png"


def dish_exists(recipe_id: str, skill_root: Path | None) -> bool:
    return bool(find_illustration_asset(DISH_DIR, recipe_id, skill_root_path(skill_root)))


def step_exists(recipe_id: str, step_index: int, skill_root: Path | None) -> bool:
    key = f"{recipe_id}-step-{step_index}"
    return bool(find_illustration_asset(STEP_DIR, key, skill_root_path(skill_root)))


def ingredient_exists(art_key: str, skill_root: Path | None) -> bool:
    return bool(find_illustration_asset(ING_DIR, art_key, skill_root_path(skill_root)))


def _recipe_ingredient_keys(recipe: dict[str, Any]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    pairs: list[tuple[str, str]] = []
    for ing in recipe.get("ingredients") or []:
        name = (ing.get("name") or "").strip()
        if not name:
            continue
        key = guess_ingredient_art_key(name) or "generic"
        if key in seen:
            continue
        seen.add(key)
        pairs.append((name, key))
    return pairs


def build_jobs_for_recipe(
    recipe: dict[str, Any],
    skill_root: Path | None = None,
    *,
    force: bool = False,
    include_dish: bool = True,
    include_steps: bool = True,
    include_ingredients: bool = True,
    max_candidates: int = MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Return missing illustration jobs for one recipe."""
    root = skill_root_path(skill_root)
    rid = (recipe.get("id") or "").strip()
    if not rid:
        return []

    jobs: list[dict[str, Any]] = []
    cap = min(max(1, max_candidates), MAX_CANDIDATES)

    if include_dish and (force or not dish_exists(rid, root)):
        rel = dish_asset_rel(rid)
        jobs.append({
            "jobId": f"{rid}:dish",
            "kind": "dish",
            "recipeId": rid,
            "recipeName": recipe.get("name") or rid,
            "relPath": rel,
            "absPath": str((root / rel).resolve()),
            "prompt": build_dish_prompt(recipe),
            "maxCandidates": cap,
            "generator": "host-agent",
            "instructions": (
                "使用宿主 Agent 内置出图能力（Cursor GenerateImage / WorkBuddy 图像工具）生成，"
                "不要用 Python 调外部 OPENAI_API_KEY，除非用户明确要求 headless 批量。"
            ),
        })

    if include_steps:
        for step_num, text in enumerate(filter_cooking_steps(recipe.get("steps") or []), start=1):
            if not force and step_exists(rid, step_num, root):
                continue
            rel = step_asset_rel(rid, step_num)
            jobs.append({
                "jobId": f"{rid}:step:{step_num}",
                "kind": "step",
                "recipeId": rid,
                "recipeName": recipe.get("name") or rid,
                "stepIndex": step_num,
                "stepText": text,
                "relPath": rel,
                "absPath": str((root / rel).resolve()),
                "prompt": build_step_prompt(recipe, step_num, text),
                "maxCandidates": cap,
                "generator": "host-agent",
                "instructions": (
                    "步骤叙事插画：左栏小场景，动作与 stepText 一致。"
                    "禁止营养说明、卡路里表；步骤文案须为中国计量（℃/克/毫升）。"
                ),
            })

    if include_ingredients:
        for name, art_key in _recipe_ingredient_keys(recipe):
            if not force and ingredient_exists(art_key, root):
                continue
            rel = ingredient_asset_rel(art_key)
            jobs.append({
                "jobId": f"{rid}:ingredient:{art_key}",
                "kind": "ingredient",
                "recipeId": rid,
                "recipeName": recipe.get("name") or rid,
                "artKey": art_key,
                "ingredientName": name,
                "relPath": rel,
                "absPath": str((root / rel).resolve()),
                "prompt": build_ingredient_prompt(name, art_key),
                "maxCandidates": cap,
                "generator": "host-agent",
                "instructions": (
                    "食材线稿：单项可识别手绘，适合食材网格 72×72。"
                ),
            })
    return jobs


def commit_illustration(
    *,
    recipe_id: str,
    kind: JobKind,
    source_file: str | Path,
    skill_root: Path | None = None,
    step_index: int | None = None,
    art_key: str | None = None,
    selected_candidate: int = 1,
    prompt: str | None = None,
    generator: str = "host-agent",
    shared_dish_name: str | None = None,
) -> dict[str, Any]:
    """Copy Agent-generated image into the canonical asset path and update manifest."""
    root = skill_root_path(skill_root)
    src = Path(source_file)
    if not src.is_file():
        raise FileNotFoundError(f"source image not found: {src}")

    if kind == "dish":
        rel = dish_asset_rel(recipe_id)
        meta_key = "dish"
    elif kind == "step":
        if not step_index:
            raise ValueError("step_index required for kind=step")
        rel = step_asset_rel(recipe_id, step_index)
        meta_key = "steps"
    elif kind == "ingredient":
        if not art_key:
            raise ValueError("art_key required for kind=ingredient")
        rel = ingredient_asset_rel(art_key)
        meta_key = "ingredients"
    else:
        raise ValueError(f"unknown kind: {kind}")

    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    dest.write_bytes(data)

    extra_urls: list[str] = []
    if kind == "dish" and shared_dish_name:
        from illustration_resolver import shared_dish_asset_rel

        share_rel = shared_dish_asset_rel(shared_dish_name)
        share_dest = root / share_rel
        share_dest.parent.mkdir(parents=True, exist_ok=True)
        share_dest.write_bytes(data)
        extra_urls.append(f"/skill-assets/{share_rel.replace(chr(92), '/')}")

    manifest = load_manifest(root)
    recipes = manifest.setdefault("recipes", {})
    entry = recipes.setdefault(recipe_id, {})
    record = {
        "path": rel.replace("\\", "/"),
        "generator": generator,
        "selectedCandidate": selected_candidate,
        "prompt": prompt,
    }
    if kind == "dish":
        entry["dish"] = record
    elif kind == "step":
        entry.setdefault("steps", {})[str(step_index)] = record
    else:
        entry.setdefault("ingredients", {})[art_key or ""] = record
    save_manifest(manifest, root)

    return {
        "ok": True,
        "recipeId": recipe_id,
        "kind": kind,
        "stepIndex": step_index,
        "artKey": art_key,
        "relPath": rel.replace("\\", "/"),
        "url": f"/skill-assets/{rel.replace(chr(92), '/')}",
        "sharedUrls": extra_urls,
    }
