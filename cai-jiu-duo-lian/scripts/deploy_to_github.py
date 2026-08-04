#!/usr/bin/env python3
"""将菜就多练 Skill 部署到 GitHub 远程仓库 AIcasefunc。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REMOTE_URL = "https://github.com/testDevloper-QQ/AIcasefunc.git"
SKILL_SUBDIR = "cai-jiu-duo-lian"
GIT = "git"

EXCLUDE_DIRS = {
    ".git",
    ".skill-cache",
    "__pycache__",
    ".pytest_cache",
    "web/.skill-cache",
    "参考书籍",
}
# 不影响用户侧使用 Skill 的内部/本地文档，不提交远程
EXCLUDE_FILES = {
    "skill生成需求背景.md",
}


def run(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


EXCLUDE_GLOBS_IN_TREE = ("*.pdf", "*.epub", "*.docx")


def _should_skip_top(name: str) -> bool:
    return name in EXCLUDE_DIRS or name in EXCLUDE_FILES or name.startswith(".")


def verify_packaging(target_dir: Path) -> list[str]:
    """Return list of violations if excluded content leaked into deploy tree."""
    violations: list[str] = []
    for name in EXCLUDE_FILES:
        if (target_dir / name).exists():
            violations.append(f"不应包含文件: {name}")
    for name in EXCLUDE_DIRS - {".git", ".skill-cache", "__pycache__", ".pytest_cache", "web/.skill-cache"}:
        p = target_dir / name
        if p.exists():
            violations.append(f"不应包含目录: {name}/")
    cache = target_dir / "web" / ".skill-cache"
    if cache.exists():
        violations.append("不应包含目录: web/.skill-cache/")
    for ext in (".pdf", ".epub", ".docx"):
        for hit in target_dir.rglob(f"*{ext}"):
            if hit.is_file():
                violations.append(f"不应包含: {hit.relative_to(target_dir)}")
    return violations


def copy_skill(target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)

    skipped: list[str] = []
    copied: list[str] = []
    for item in SKILL_ROOT.iterdir():
        name = item.name
        if _should_skip_top(name):
            skipped.append(name)
            continue
        dest = target_dir / name
        if item.is_dir():
            shutil.copytree(
                item,
                dest,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".pytest_cache", ".skill-cache",
                    "*.pdf", "*.epub", "*.docx",
                ),
            )
        else:
            shutil.copy2(item, dest)
        copied.append(name)

    print("[pack] 已排除:", ", ".join(skipped) if skipped else "(无)")
    print("[pack] 已复制:", ", ".join(copied))

    violations = verify_packaging(target_dir)
    if violations:
        print("[FAIL] 打包校验未通过:")
        for v in violations:
            print(f"  - {v}")
        raise RuntimeError("打包包含不应提交的内容，已中止")
    print("[pack] 校验通过：未包含内部文档、参考书籍、缓存与大文件")

    # 远程 config 使用 git 自引用
    config_path = target_dir / "web" / "config.json"
    cfg = {
        "skillSource": "git",
        "localSkillPath": "..",
        "gitRepoUrl": REMOTE_URL,
        "gitBranch": "main",
        "gitSkillSubPath": SKILL_SUBDIR,
    }
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    run([GIT, "add", "-A"], cwd=repo)
    status = run([GIT, "status", "--porcelain"], cwd=repo)
    if not status.stdout.strip():
        print("[INFO] 无变更，跳过提交")
        return
    tree = run([GIT, "write-tree"], cwd=repo).stdout.strip()
    parent = run([GIT, "rev-parse", "HEAD"], cwd=repo, check=False).stdout.strip()
    commit_args = [GIT, "commit-tree", tree, "-m", message]
    if parent:
        commit_args.extend(["-p", parent])
    commit = run(commit_args, cwd=repo).stdout.strip()
    run([GIT, "update-ref", "HEAD", commit], cwd=repo)


def main() -> int:
    print("=" * 50)
    print("部署 Skill 到 GitHub")
    print("=" * 50)
    print(f"远程: {REMOTE_URL}")
    print(f"子目录: {SKILL_SUBDIR}/")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "AIcasefunc"
        print("[1/4] 克隆远程仓库 …")
        clone = run([GIT, "clone", REMOTE_URL, str(work)], check=False)
        if clone.returncode != 0:
            err = (clone.stderr or clone.stdout or "").strip()
            print(f"[FAIL] 克隆失败: {err}")
            print("提示: 请确认网络可达，且已配置 GitHub 凭据（HTTPS 或 SSH）")
            return 1

        skill_target = work / SKILL_SUBDIR
        print("[2/4] 复制 Skill 文件 …")
        copy_skill(skill_target)

        print("[3/4] 提交 …")
        commit_all(work, f"feat: add {SKILL_SUBDIR} skill")

        print("[4/4] 推送到 GitHub …")
        push = run([GIT, "push", "origin", "main"], cwd=work, check=False)
        if push.returncode != 0:
            err = (push.stderr or push.stdout or "").strip()
            print(f"[FAIL] 推送失败: {err}")
            print("提示: 运行 gh auth login 或配置 Git 凭据后重试")
            return 1

    # 更新本地 config
    local_config = SKILL_ROOT / "web" / "config.json"
    cfg = json.loads(local_config.read_text(encoding="utf-8"))
    cfg.update({
        "skillSource": "git",
        "gitRepoUrl": REMOTE_URL,
        "gitBranch": "main",
        "gitSkillSubPath": SKILL_SUBDIR,
    })
    local_config.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    print("[OK] 部署完成")
    print(f"     仓库: {REMOTE_URL}")
    print(f"     Skill 路径: {SKILL_SUBDIR}/")
    print("[OK] 本地 web/config.json 已更新")
    print()
    print("验证: python scripts/test_git_skill.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
