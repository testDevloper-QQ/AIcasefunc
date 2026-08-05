#!/usr/bin/env python3
"""Audit illustration coverage for a reference book (material library)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from illustration_library import (  # noqa: E402
    audit_book,
    book_by_id,
    bootstrap_ingredient_catalog,
    load_books,
    save_coverage_report,
    skill_root_path,
)
from recommend_engine import load_all_recipes  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="按书籍审计插画素材库覆盖率")
    parser.add_argument("--book", default="抗炎食谱100例", help="source.book 书名")
    parser.add_argument("--book-id", default="", help="books.yaml 中的 id（可选）")
    parser.add_argument("--bootstrap-ingredients", action="store_true", help="从索引生成 ingredients.yaml")
    parser.add_argument("--save-report", action="store_true", help="写入 data/illustration-library/coverage/")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = skill_root_path()
    recipes = load_all_recipes(root)
    book_title = args.book.strip()

    books = load_books(root)
    if args.book_id:
        meta = book_by_id(books, args.book_id)
        if meta:
            book_title = meta.get("sourceMatch") or meta.get("title") or book_title

    if args.bootstrap_ingredients:
        path = bootstrap_ingredient_catalog(recipes, root)
        print(f"[OK] 已生成食材素材表: {path}")

    report = audit_book(recipes, book_title, root)

    if args.save_report:
        book_id = args.book_id or "anti-inflammatory-100"
        out = save_coverage_report(report, book_id, root)
        print(f"[OK] 覆盖率报告: {out}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"书籍: {report['book']}")
    print(f"菜谱: {report['recipeCount']} 道 | 可共享成品名: {report['uniqueDishShares']}（重名 {report['duplicateDishNames']} 组）")
    print(f"食材 key: {report['uniqueIngredientKeys']} 种")
    print(f"待出图 — 成品: {len(report['missingDishes'])} | 步骤: {len(report['missingSteps'])} | 食材: {len(report['missingIngredients'])}")
    if report["missingIngredients"][:8]:
        print("\n缺失食材示例:")
        for line in report["missingIngredients"][:8]:
            print(f"  - {line}")
        if len(report["missingIngredients"]) > 8:
            print(f"  ... 另有 {len(report['missingIngredients']) - 8} 种")
    return 1 if (report["missingDishes"] or report["missingSteps"] or report["missingIngredients"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
