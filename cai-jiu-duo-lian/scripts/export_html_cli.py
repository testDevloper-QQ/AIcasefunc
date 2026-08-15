#!/usr/bin/env python3
"""Export recommend result as self-contained HTML (base64 images) for WorkBuddy preview."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_embedded_html import write_recommend_embedded_html  # noqa: E402
from recommend_cli import _resolve_skill_root, _split_csv  # noqa: E402
from recommend_engine import recommend  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="导出自包含 HTML（base64 内嵌图，WorkBuddy 预览通道）"
    )
    parser.add_argument("--ingredients", "-i", default="")
    parser.add_argument("--custom", "-c", default="")
    parser.add_argument("--scene", "-s", default="")
    parser.add_argument("--taste", "-t", default="")
    parser.add_argument("--servings", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--skill-root", default="")
    parser.add_argument("--from-json", default="", help="已有 recommend JSON")
    parser.add_argument(
        "--out",
        default="",
        help="输出 HTML 路径（默认 skill/exports/workbuddy-preview.html）",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="不内嵌 base64，改用 file://（一般不用于 WorkBuddy 预览）",
    )
    parser.add_argument(
        "--no-ingredient-art",
        action="store_true",
        help="不嵌入食材小图，缩小体积",
    )
    args = parser.parse_args()

    skill_root = _resolve_skill_root(args.skill_root or None)

    if args.from_json:
        payload = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    else:
        ingredients = _split_csv(args.ingredients)
        custom = _split_csv(args.custom)
        if not ingredients and not custom:
            print("请提供 --from-json 或 --ingredients/--custom", file=sys.stderr)
            return 1
        payload = {
            "ok": True,
            **recommend(
                skill_root,
                scene=args.scene.strip() or None,
                ingredients=ingredients,
                custom_ingredients=custom,
                taste=args.taste.strip(),
                servings_label=args.servings.strip(),
                free_text=args.text.strip(),
            ),
        }

    out = Path(args.out) if args.out else (skill_root / "exports" / "workbuddy-preview.html")
    stats = write_recommend_embedded_html(
        payload,
        skill_root,
        out,
        embed_images=not args.no_embed,
        include_ingredient_art=not args.no_ingredient_art,
    )
    if stats.get("warnOverBytes"):
        print(
            f"[warn] HTML 约 {stats['bytes'] / (1024 * 1024):.1f} MB，建议 --no-ingredient-art 或只导出主推荐",
            file=sys.stderr,
        )
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
