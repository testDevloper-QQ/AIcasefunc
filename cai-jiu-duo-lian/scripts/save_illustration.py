#!/usr/bin/env python3
"""Register an Agent-generated illustration into the skill asset library."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from illustration_jobs import commit_illustration, skill_root_path  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="保存 Agent 出图到 skill 资产路径")
    parser.add_argument("--recipe-id", required=True)
    parser.add_argument("--kind", required=True, choices=["dish", "step", "ingredient"])
    parser.add_argument("--from", dest="source", required=True, help="Agent 生成的本地图片路径")
    parser.add_argument("--step-index", type=int, default=0)
    parser.add_argument("--art-key", default="", help="ingredient 专用：art key 文件名")
    parser.add_argument("--candidate", type=int, default=1, help="选中的备选序号 1-3")
    parser.add_argument("--generator", default="host-agent", help="cursor | workbuddy | host-agent")
    parser.add_argument("--prompt", default="", help="可选，记录 prompt")
    parser.add_argument("--shared-dish-name", default="", help="同时写入 dishes/shared/{菜名}.png 供同名菜共用")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    result = commit_illustration(
        recipe_id=args.recipe_id,
        kind=args.kind,  # type: ignore[arg-type]
        source_file=args.source,
        skill_root=skill_root_path(),
        step_index=args.step_index or None,
        art_key=args.art_key or None,
        shared_dish_name=args.shared_dish_name or None,
        selected_candidate=args.candidate,
        prompt=args.prompt or None,
        generator=args.generator,
    )
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
