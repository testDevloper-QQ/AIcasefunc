#!/usr/bin/env python3
"""Agent 侧推荐 CLI：无需启动 Web 服务，直接输出 JSON。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Windows 终端默认 GBK，含 SVG data URL / 中文时须 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chat_output import render_recommend_markdown  # noqa: E402
from export_embedded_html import write_recommend_embedded_html  # noqa: E402
from recommend_engine import recommend  # noqa: E402
from skill_loader import get_skill_root  # noqa: E402

DEFAULT_SKILL_ROOT = Path(__file__).resolve().parents[1]


def _split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.replace("，", ",").split(",") if x.strip()]


def _resolve_skill_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).resolve()
        if not (root / "SKILL.md").exists():
            print(f"无效的 skill 根目录（缺少 SKILL.md）: {root}", file=sys.stderr)
            sys.exit(1)
        return root
    try:
        root, _meta = get_skill_root()
        return root
    except Exception:
        if (DEFAULT_SKILL_ROOT / "SKILL.md").exists():
            return DEFAULT_SKILL_ROOT
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="菜就多练 — Agent 推荐 CLI（无需 Web 服务）")
    parser.add_argument("--ingredients", "-i", default="", help="食材，逗号分隔，如 鸡蛋,番茄")
    parser.add_argument("--custom", "-c", default="", help="自定义食材，逗号分隔")
    parser.add_argument("--scene", "-s", default="", help="场景：bento/light-meal/seasonal/regional/health/happy")
    parser.add_argument("--taste", "-t", default="", help="口味偏好")
    parser.add_argument("--servings", default="", help="一人食 / 二人家庭 / 多人家庭")
    parser.add_argument("--text", default="", help="补充说明")
    parser.add_argument("--skill-root", default="", help="Skill 根目录（默认自动解析）")
    parser.add_argument("--pretty", action="store_true", help="格式化 JSON 输出")
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="输出对话 Markdown（须与 Step 4 相同用户参数）；默认 image-mode=present",
    )
    parser.add_argument(
        "--image-mode",
        choices=("present", "path", "http"),
        default="present",
        help="--markdown 时：present=文案+present_files 清单（WorkBuddy 默认）；"
        "path/http=Markdown ![](…)（Cursor 等）",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8765",
        help="--image-mode http 时的 Web 根地址",
    )
    parser.add_argument(
        "--export-html",
        action="store_true",
        help="导出自包含 HTML（base64 内嵌图，WorkBuddy HTML 预览通道）",
    )
    parser.add_argument(
        "--export-html-out",
        default="",
        help="--export-html 输出路径（默认 exports/workbuddy-preview.html）",
    )
    parser.add_argument(
        "--export-html-no-ingredient-art",
        action="store_true",
        help="导出 HTML 时跳过食材小图以缩小体积",
    )
    args = parser.parse_args()

    ingredients = _split_csv(args.ingredients)
    custom = _split_csv(args.custom)
    if not ingredients and not custom:
        print("请至少提供 --ingredients 或 --custom", file=sys.stderr)
        sys.exit(1)

    skill_root = _resolve_skill_root(args.skill_root or None)
    scene = args.scene.strip() or None

    result = recommend(
        skill_root,
        scene=scene,
        ingredients=ingredients,
        custom_ingredients=custom,
        taste=args.taste.strip(),
        servings_label=args.servings.strip(),
        free_text=args.text.strip(),
    )

    payload = {"ok": True, "skillRoot": str(skill_root), **result}

    if args.export_html:
        out = (
            Path(args.export_html_out)
            if args.export_html_out
            else (skill_root / "exports" / "workbuddy-preview.html")
        )
        stats = write_recommend_embedded_html(
            payload,
            skill_root,
            out,
            embed_images=True,
            include_ingredient_art=not args.export_html_no_ingredient_art,
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    if args.markdown:
        print(
            render_recommend_markdown(
                payload,
                skill_root,
                image_mode=args.image_mode,
                base_url=args.base_url,
            )
        )
        return

    indent = 2 if args.pretty else None
    print(json.dumps(payload, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
