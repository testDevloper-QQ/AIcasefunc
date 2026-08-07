#!/usr/bin/env python3
"""List illustration jobs for host Agent (Cursor / WorkBuddy) to generate with native image tools."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from illustration_jobs import build_jobs_for_recipe, skill_root_path  # noqa: E402
from illustration_library import build_book_jobs, load_books, book_by_id  # noqa: E402
from recommend_engine import load_all_recipes, recommend  # noqa: E402

SKILL_ROOT = skill_root_path()


def _pick_recipes(args: argparse.Namespace) -> list[dict]:
    all_recipes = load_all_recipes(SKILL_ROOT)
    if args.from_recommend:
        ing = [x.strip() for x in (args.ingredients or "").split(",") if x.strip()]
        custom = [x.strip() for x in (args.custom or "").split(",") if x.strip()]
        if not ing and not custom:
            raise SystemExit("--from-recommend 需要 --ingredients 或 --custom")
        result = recommend(
            SKILL_ROOT,
            scene=args.scene or None,
            ingredients=ing,
            custom_ingredients=custom,
        )
        picked = [result["primary"], *(result.get("alternates") or [])]
        by_id = {r.get("id"): r for r in all_recipes if r.get("id")}
        return [by_id[r["id"]] for r in picked if r.get("id") in by_id]

    ids: list[str] = list(args.recipe_ids or [])
    if args.ids:
        ids.extend(x.strip() for x in args.ids.split(",") if x.strip())
    if ids:
        out = []
        for rid in ids:
            match = next((r for r in all_recipes if r.get("id") == rid), None)
            if match:
                out.append(match)
            else:
                print(f"WARN: recipe not found: {rid}", file=sys.stderr)
        return out
    if args.top > 0:
        return all_recipes[: args.top]
    if args.all_recipes:
        return all_recipes
    raise SystemExit("Specify --recipe-id, --ids, --top, --all, or --from-recommend")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="输出待生成插画任务 JSON，供 Cursor/WorkBuddy Agent 用内置出图能力执行",
    )
    parser.add_argument("--recipe-id", action="append", dest="recipe_ids")
    parser.add_argument("--ids")
    parser.add_argument("--top", type=int, default=0)
    parser.add_argument("--all", dest="all_recipes", action="store_true")
    parser.add_argument("--from-recommend", action="store_true")
    parser.add_argument("--scene")
    parser.add_argument("--ingredients")
    parser.add_argument("--custom")
    parser.add_argument("--book", default="", help="按 source.book 批量输出预生成任务（素材库）")
    parser.add_argument("--book-id", default="", help="books.yaml 中的 id")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dish-only", action="store_true")
    parser.add_argument("--candidates", type=int, default=1)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    jobs: list[dict] = []
    if args.book or args.book_id:
        all_recipes = load_all_recipes(SKILL_ROOT)
        book_title = (args.book or "抗炎食谱100例").strip()
        books = load_books(SKILL_ROOT)
        if args.book_id:
            meta = book_by_id(books, args.book_id)
            if meta:
                book_title = meta.get("sourceMatch") or meta.get("title") or book_title
        jobs = build_book_jobs(
            all_recipes,
            book_title,
            SKILL_ROOT,
            force=args.force,
            max_candidates=args.candidates,
        )
    else:
        for recipe in _pick_recipes(args):
            jobs.extend(
                build_jobs_for_recipe(
                    recipe,
                    SKILL_ROOT,
                    force=args.force,
                    include_steps=not args.dish_only,
                    max_candidates=args.candidates,
                )
            )

    payload = {
        "ok": True,
        "mode": "host-agent",
        "skillRoot": str(SKILL_ROOT),
        "jobCount": len(jobs),
        "jobs": jobs,
        "agentWorkflow": [
            "1. 对 jobs[] 中每项，用宿主内置出图（Cursor GenerateImage / WorkBuddy 图像工具）",
            "2. 每张图最多生成 maxCandidates 个备选，选最好的一张",
            "3. python scripts/save_illustration.py --recipe-id ID --kind dish|step|ingredient --from 路径.png [--step-index N] [--art-key KEY] [--shared-dish-name 菜名]",
            "4. 按书预生成: python scripts/audit_illustration_library.py --book 抗炎食谱100例",
            "5. 网页 Ctrl+F5 或重新 recommend 即可看到新插画",
        ],
    }
    indent = 2 if args.pretty else None
    print(json.dumps(payload, ensure_ascii=False, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
