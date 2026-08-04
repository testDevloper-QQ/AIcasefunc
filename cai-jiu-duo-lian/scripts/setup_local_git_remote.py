#!/usr/bin/env python3
"""初始化本地 bare 远程仓库，供 Git Skill 链路测试（无需真实 GitHub）。"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
BARE_REPO = SKILL_ROOT.parent / "cai-jiu-duo-lian-remote.git"
GIT = shutil.which("git") or "git"


def run(args: list[str], *, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return (proc.stdout or "").strip()


def main() -> int:
    print("Skill 目录:", SKILL_ROOT)
    print("Bare 远程:", BARE_REPO)

    if not (SKILL_ROOT / "SKILL.md").exists():
        print("[FAIL] 未找到 SKILL.md")
        return 1

    run(["git", "init", "-b", "main"], cwd=SKILL_ROOT)
    run(["git", "add", "-A"], cwd=SKILL_ROOT)

    tree = run([GIT, "write-tree"], cwd=SKILL_ROOT)
    commit = run([GIT, "commit-tree", tree, "-m", "chore: initial skill for git remote test"], cwd=SKILL_ROOT)
    run([GIT, "update-ref", "refs/heads/main", commit], cwd=SKILL_ROOT)

    if BARE_REPO.exists():
        shutil.rmtree(BARE_REPO)
    BARE_REPO.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "--bare", str(BARE_REPO)])

    # 推送 objects 到 bare（file:// 协议）
    repo_url = BARE_REPO.as_uri()
    run([GIT, "push", repo_url, "main"], cwd=SKILL_ROOT)

    config_path = SKILL_ROOT / "web" / "config.json"
    import json

    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    cfg["skillSource"] = "git"
    cfg["gitRepoUrl"] = repo_url
    cfg["gitBranch"] = "main"
    cfg["gitSkillSubPath"] = ""
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    print("[OK] 本地 bare 远程已就绪")
    print(f"   gitRepoUrl: {repo_url}")
    print("[OK] web/config.json 已切换为 skillSource=git")
    print()
    print("下一步: python scripts/test_git_skill.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
