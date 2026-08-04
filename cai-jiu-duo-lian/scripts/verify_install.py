#!/usr/bin/env python3
"""验证 Skill 安装并打印四种使用场景的输入示例。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recommend_engine import load_all_recipes, recommend  # noqa: E402
from skill_loader import get_skill_root  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[1]

EXAMPLES = [
    {
        "title": "1. 场景驱动",
        "desc": "先定饮食偏好，再出菜",
        "chat": "轻食，一人食，想吃点清爽的",
        "cli": "python scripts/recommend_cli.py -s light-meal -i 黄瓜,鸡蛋 --servings 一人食 --pretty",
    },
    {
        "title": "2. 食材驱动",
        "desc": "按冰箱现有食材找做法",
        "chat": "有鸡蛋、番茄、黄瓜，能做什么",
        "cli": "python scripts/recommend_cli.py -i 鸡蛋,番茄,黄瓜 --pretty",
    },
    {
        "title": "3. 指定需求",
        "desc": "指定便当、菜名或用途",
        "chat": "想做一份便当，明天带饭，有鸡胸肉和米饭",
        "cli": 'python scripts/recommend_cli.py -s bento -i 米饭,鸡胸肉 --text "明天带饭" --pretty',
    },
    {
        "title": "4. 默认快乐餐",
        "desc": "不选场景，快速解馋（未选场景时的默认行为）",
        "chat": "有鸡蛋和番茄，来道快手的",
        "cli": "python scripts/recommend_cli.py -i 鸡蛋,番茄 --pretty",
    },
]


def print_welcome(skill_root: Path, recipe_count: int) -> None:
    print()
    print("=" * 56)
    print("  菜就多练 — 安装成功！")
    print("=" * 56)
    print(f"  Skill 路径: {skill_root}")
    print(f"  菜谱索引:   {recipe_count} 道")
    print()
    print("  试试以下四种场景的输入示例：")
    print()
    for ex in EXAMPLES:
        print(f"  【{ex['title']}】{ex['desc']}")
        print(f"    对话: {ex['chat']}")
        print(f"    CLI:  {ex['cli']}")
        print()
    print("  网页表单: python scripts/ensure_web_server.py")
    print("  详细说明: references/getting-started.md")
    print("=" * 56)
    print()


def main() -> int:
    try:
        skill_root, meta = get_skill_root()
        recipes = load_all_recipes(skill_root)
        if len(recipes) < 1:
            print("[FAIL] 索引为空", file=sys.stderr)
            return 1

        result = recommend(
            skill_root,
            scene="happy",
            ingredients=["鸡蛋", "番茄"],
            servings_label="一人食",
        )
        print("[OK] Skill 安装验证通过")
        print(json.dumps({"ok": True, "skillRoot": str(skill_root), "recipeCount": len(recipes), "meta": meta}, ensure_ascii=False))
        print_welcome(skill_root, len(recipes))
        print(f"[OK] 试推荐: {result['primary']['name']}（《{result['primary']['source']['book']}》）")
        return 0
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
