"""Resolve Skill root from local path or remote git repository."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
DEFAULT_SKILL_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = WEB_DIR / ".skill-cache"


def load_config() -> dict:
    config_path = WEB_DIR / "config.json"
    example_path = WEB_DIR / "config.example.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    if example_path.exists():
        return json.loads(example_path.read_text(encoding="utf-8"))
    return {
        "skillSource": "local",
        "localSkillPath": str(DEFAULT_SKILL_ROOT),
        "gitRepoUrl": "",
        "gitBranch": "main",
        "gitSkillSubPath": "",
    }


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _clone_repo(repo_url: str, branch: str, target: Path) -> None:
    errors: list[str] = []
    for try_branch in [branch, "main", "master"]:
        if try_branch != branch and branch not in ("main", "master"):
            continue
        try:
            if target.exists():
                _refresh_cache(target)
            _run_git(["git", "clone", "--depth", "1", "--branch", try_branch, repo_url, str(target)])
            return
        except subprocess.CalledProcessError as exc:
            errors.append(f"branch={try_branch}: {(exc.stderr or exc.stdout or str(exc)).strip()}")
    raise RuntimeError("Git clone 失败:\n" + "\n".join(errors))


def _pull_repo(branch: str, target: Path) -> None:
    try:
        _run_git(["git", "-C", str(target), "fetch", "origin", branch, "--depth", "1"])
        _run_git(["git", "-C", str(target), "reset", "--hard", f"origin/{branch}"])
    except subprocess.CalledProcessError:
        # fallback: fetch all heads then reset
        _run_git(["git", "-C", str(target), "fetch", "origin", "--depth", "1"])
        _run_git(["git", "-C", str(target), "reset", "--hard", f"origin/{branch}"])


def _git_pull(repo_url: str, branch: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        _clone_repo(repo_url, branch, target)
    else:
        _pull_repo(branch, target)
    return target


def _refresh_cache(cache_path: Path) -> None:
    import shutil
    import time

    if not cache_path.exists():
        return
    backup = cache_path.with_name(cache_path.name + ".old")
    if backup.exists():
        shutil.rmtree(backup, ignore_errors=True)
    try:
        cache_path.rename(backup)
    except OSError:
        shutil.rmtree(cache_path, ignore_errors=True)
        if cache_path.exists():
            raise
    else:
        for _ in range(3):
            shutil.rmtree(backup, ignore_errors=True)
            if not backup.exists():
                break
            time.sleep(0.2)


def _validate_skill_root(skill_root: Path) -> int:
    index_dir = skill_root / "data" / "recipe-index"
    if not index_dir.exists():
        raise FileNotFoundError(
            f"Skill 根目录无效，未找到 data/recipe-index\n"
            f"  路径: {skill_root}\n"
            f"  提示: 检查 gitSkillSubPath 是否指向含 SKILL.md 与 data/recipe-index 的目录"
        )
    if not (skill_root / "SKILL.md").exists():
        raise FileNotFoundError(f"Skill 根目录缺少 SKILL.md: {skill_root}")
    count = len(list(index_dir.glob("*.yaml")))
    if count == 0:
        raise FileNotFoundError(f"索引目录为空: {index_dir}")
    return count


def get_skill_root(force_refresh: bool = False) -> tuple[Path, dict]:
    cfg = load_config()
    source = cfg.get("skillSource", "local")

    if source == "git":
        repo_url = (cfg.get("gitRepoUrl") or "").strip()
        if not repo_url:
            raise ValueError("skillSource=git 但未配置 gitRepoUrl，请在 web/config.json 中填写")
        branch = cfg.get("gitBranch") or "main"
        cache_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        cache_path = CACHE_DIR / cache_name
        if force_refresh and cache_path.exists():
            _refresh_cache(cache_path)
        repo_root = _git_pull(repo_url, branch, cache_path)
        sub = (cfg.get("gitSkillSubPath") or "").strip().replace("\\", "/").strip("/")
        skill_root = repo_root / sub if sub else repo_root
    else:
        local_path = cfg.get("localSkillPath") or ".."
        skill_root = (WEB_DIR / local_path).resolve() if not Path(local_path).is_absolute() else Path(local_path)

    recipe_count = _validate_skill_root(skill_root)
    meta = {
        "source": source,
        "skillRoot": str(skill_root),
        "gitRepoUrl": cfg.get("gitRepoUrl") or "",
        "gitBranch": cfg.get("gitBranch") or "main",
        "recipeCount": recipe_count,
    }
    return skill_root, meta
