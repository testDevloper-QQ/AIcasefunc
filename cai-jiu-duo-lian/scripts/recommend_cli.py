#!/usr/bin/env python3
"""Agent 侧推荐 CLI：无需启动 Web 服务，直接输出 JSON。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    indent = 2 if args.pretty else None
    print(json.dumps(payload, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
