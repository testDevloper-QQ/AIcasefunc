#!/usr/bin/env python3
"""验证 Git 远程 Skill 能否被正确拉取并推荐。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recommend_engine import load_all_recipes, recommend  # noqa: E402
from skill_loader import get_skill_root, load_config  # noqa: E402


def main() -> int:
    cfg = load_config()
    print("=" * 50)
    print("菜就多练 — Git Skill 验证")
    print("=" * 50)
    print("当前 config.json:")
    print(json.dumps(cfg, ensure_ascii=False, indent=2))
    print()

    if cfg.get("skillSource") != "git":
        print("[FAIL] skillSource 不是 git，请先在 web/config.json 中设置:")
        print('   "skillSource": "git"')
        print('   "gitRepoUrl": "你的仓库地址"')
        return 1

    if not (cfg.get("gitRepoUrl") or "").strip():
        print("[FAIL] gitRepoUrl 为空，请填写远程仓库地址")
        return 1

    try:
        print("正在拉取 Skill …")
        skill_root, meta = get_skill_root(force_refresh=True)
        recipes = load_all_recipes(skill_root)
        print(f"[OK] Skill 根目录: {meta['skillRoot']}")
        print(f"[OK] 索引文件数: {len(list((skill_root / 'data' / 'recipe-index').glob('*.yaml')))}")
        print(f"[OK] 菜谱条目数: {len(recipes)}")
        print()

        result = recommend(
            skill_root,
            scene="light-meal",
            ingredients=["番茄", "鸡蛋"],
            servings_label="一人食",
        )
        print("[OK] 试推荐成功:")
        print(f"   主推荐: {result['primary']['name']}")
        print(f"   出处: 《{result['primary']['source']['book']}》")
        if result.get("alternates"):
            print(f"   备选: {', '.join(r['name'] for r in result['alternates'])}")
        print()
        print("=" * 50)
        print("Git Skill 链路验证通过。可运行: python scripts/web_server.py")
        print("=" * 50)
        return 0
    except Exception as exc:
        print(f"[FAIL] 失败: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
