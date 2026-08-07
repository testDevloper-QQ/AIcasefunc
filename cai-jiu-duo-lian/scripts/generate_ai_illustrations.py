#!/usr/bin/env python3
"""Optional headless batch via OPENAI Images API.

Primary path: Agent host image tools (Cursor / WorkBuddy) — see references/agent-illustration-guide.md
  python scripts/illustration_jobs_cli.py --recipe-id hap-023 --pretty
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai_illustration_client import (  # noqa: E402
    MAX_CANDIDATES,
    build_dish_prompt,
    build_step_prompt,
    generate_image_candidates,
    save_png,
    select_best_candidate,
)
from illustration_medium import write_medium_png  # noqa: E402
from recommend_engine import load_all_recipes  # noqa: E402
from recipe_format import filter_cooking_steps, localize_text  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[1]
DISH_DIR = SKILL_ROOT / "assets" / "illustrations" / "dishes"
STEP_DIR = SKILL_ROOT / "assets" / "illustrations" / "steps"
CANDIDATE_DIR = SKILL_ROOT / "assets" / "illustrations" / "_candidates"
MANIFEST_PATH = SKILL_ROOT / "assets" / "illustrations" / "ai-manifest.json"


def _load_manifest() -> dict:
    if MANIFEST_PATH.is_file():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"version": 1, "recipes": {}}


def _save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest["updatedAt"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _recipe_by_id(recipes: list[dict], recipe_id: str) -> dict | None:
    for r in recipes:
        if r.get("id") == recipe_id:
            return r
    return None


def _generate_dish(recipe: dict, *, candidates: int, force: bool, dry_run: bool) -> dict | None:
    rid = recipe["id"]
    final_path = DISH_DIR / f"{rid}.png"
    if final_path.is_file() and not force:
        return {"path": str(final_path.relative_to(SKILL_ROOT)).replace("\\", "/"), "skipped": True}

    prompt = build_dish_prompt(recipe)
    if dry_run:
        print(f"[dry-run] dish {rid}: {prompt[:120]}…")
        return {"prompt": prompt, "dryRun": True}

    cand_dir = CANDIDATE_DIR / rid / "dish"
    cand_dir.mkdir(parents=True, exist_ok=True)
    blobs = generate_image_candidates(prompt, candidates=candidates)
    cand_paths: list[Path] = []
    for i, blob in enumerate(blobs, start=1):
        p = save_png(blob, cand_dir / f"candidate-{i}.png", kind="dish")
        cand_paths.append(p)

    winner = select_best_candidate(cand_paths)
    write_medium_png(winner, final_path, "dish")
    rel = str(final_path.relative_to(SKILL_ROOT)).replace("\\", "/")
    print(f"  dish → {rel} (selected from {len(cand_paths)} candidate(s))")
    return {
        "path": rel,
        "prompt": prompt,
        "candidates": [p.name for p in cand_paths],
        "selected": winner.name,
    }


def _generate_steps(recipe: dict, *, candidates: int, force: bool, dry_run: bool) -> dict[str, dict]:
    rid = recipe["id"]
    out: dict[str, dict] = {}
    for step_num, text in enumerate(filter_cooking_steps(recipe.get("steps") or []), start=1):
        final_path = STEP_DIR / f"{rid}-step-{step_num}.png"
        if final_path.is_file() and not force:
            out[str(step_num)] = {
                "path": str(final_path.relative_to(SKILL_ROOT)).replace("\\", "/"),
                "skipped": True,
            }
            continue

        prompt = build_step_prompt(recipe, step_num, text)
        if dry_run:
            print(f"[dry-run] step {rid}-{step_num}: {text[:60]}…")
            out[str(step_num)] = {"prompt": prompt, "dryRun": True}
            continue

        cand_dir = CANDIDATE_DIR / rid / f"step-{step_num}"
        cand_dir.mkdir(parents=True, exist_ok=True)
        blobs = generate_image_candidates(prompt, candidates=candidates)
        cand_paths: list[Path] = []
        for i, blob in enumerate(blobs, start=1):
            p = save_png(blob, cand_dir / f"candidate-{i}.png", kind="step")
            cand_paths.append(p)

        winner = select_best_candidate(cand_paths)
        write_medium_png(winner, final_path, "step")
        rel = str(final_path.relative_to(SKILL_ROOT)).replace("\\", "/")
        print(f"  step {step_num} → {rel} (selected from {len(cand_paths)} candidate(s))")
        out[str(step_num)] = {
            "path": rel,
            "text": text,
            "prompt": prompt,
            "candidates": [p.name for p in cand_paths],
            "selected": winner.name,
        }
    return out


def generate_for_recipe(
    recipe: dict,
    *,
    candidates: int = 1,
    force: bool = False,
    dry_run: bool = False,
    skip_steps: bool = False,
) -> dict:
    rid = recipe.get("id") or "?"
    name = recipe.get("name") or rid
    print(f"▶ {rid} {name}")
    dish_meta = _generate_dish(recipe, candidates=candidates, force=force, dry_run=dry_run)
    steps_meta = {} if skip_steps else _generate_steps(recipe, candidates=candidates, force=force, dry_run=dry_run)
    return {"dish": dish_meta, "steps": steps_meta}


def main() -> int:
    parser = argparse.ArgumentParser(description="AI batch illustration generator (Plan B P2)")
    parser.add_argument("--recipe-id", action="append", dest="recipe_ids", help="Single recipe id (repeatable)")
    parser.add_argument("--ids", help="Comma-separated recipe ids")
    parser.add_argument("--top", type=int, default=0, help="Generate for first N recipes in index")
    parser.add_argument("--all", action="store_true", help="All index recipes (may be expensive)")
    parser.add_argument(
        "--candidates",
        type=int,
        default=1,
        help=f"Alternatives per image (1–{MAX_CANDIDATES}, default 1)",
    )
    parser.add_argument("--force", action="store_true", help="Regenerate even if PNG exists")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts only")
    parser.add_argument("--dish-only", action="store_true", help="Skip step illustrations")
    args = parser.parse_args()

    candidates = min(max(1, args.candidates), MAX_CANDIDATES)
    recipes = load_all_recipes(SKILL_ROOT)

    targets: list[dict] = []
    id_list: list[str] = list(args.recipe_ids or [])
    if args.ids:
        id_list.extend(x.strip() for x in args.ids.split(",") if x.strip())

    if id_list:
        for rid in id_list:
            r = _recipe_by_id(recipes, rid)
            if r:
                targets.append(r)
            else:
                print(f"WARN: recipe id not found: {rid}", file=sys.stderr)
    elif args.all:
        targets = recipes
    elif args.top > 0:
        targets = recipes[: args.top]
    else:
        parser.error("Specify --recipe-id, --ids, --top N, or --all")

    manifest = _load_manifest()
    for recipe in targets:
        rid = recipe["id"]
        try:
            manifest.setdefault("recipes", {})[rid] = generate_for_recipe(
                recipe,
                candidates=candidates,
                force=args.force,
                dry_run=args.dry_run,
                skip_steps=args.dish_only,
            )
        except Exception as exc:
            print(f"ERROR {rid}: {exc}", file=sys.stderr)
            manifest.setdefault("recipes", {})[rid] = {"error": str(exc)}

    if not args.dry_run:
        _save_manifest(manifest)
        print(f"Manifest → {MANIFEST_PATH.relative_to(SKILL_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
