#!/usr/bin/env python3
"""Format recommend JSON as WorkBuddy/Cursor inline Markdown with embedded images."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chat_output import render_recommend_markdown  # noqa: E402
from recommend_cli import _resolve_skill_root, _split_csv  # noqa: E402
from recommend_engine import recommend  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="输出 WorkBuddy 内联 Markdown（含嵌入插画）")
    parser.add_argument("--ingredients", "-i", default="")
    parser.add_argument("--custom", "-c", default="")
    parser.add_argument("--scene", "-s", default="")
    parser.add_argument("--taste", "-t", default="")
    parser.add_argument("--servings", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--skill-root", default="")
    parser.add_argument("--from-json", default="", help="已有 recommend JSON 文件路径")
    parser.add_argument(
        "--image-mode",
        choices=("path", "http"),
        default="path",
        help="path=绝对路径（WorkBuddy 默认）；http=127.0.0.1:8765/skill-assets（需 Web 服务）",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
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

    md = render_recommend_markdown(
        payload,
        skill_root,
        image_mode=args.image_mode,
        base_url=args.base_url,
    )
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
