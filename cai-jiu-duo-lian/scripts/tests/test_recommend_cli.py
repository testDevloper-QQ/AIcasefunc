"""Tests for recommend_cli."""
from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from recommend_cli import _resolve_skill_root, _split_csv, main  # noqa: E402
from recommend_engine import recommend  # noqa: E402


def test_split_csv():
    assert _split_csv("鸡蛋，番茄, 黄瓜") == ["鸡蛋", "番茄", "黄瓜"]


def test_recommend_cli_flow():
    skill_root = _resolve_skill_root(str(SKILL_ROOT))
    result = recommend(
        skill_root,
        scene="happy",
        ingredients=["鸡蛋", "番茄"],
    )
    assert result["primary"]["name"]


def test_recommend_cli_main_json(capsys):
    buf = StringIO()
    sys.argv = [
        "recommend_cli.py",
        "--ingredients",
        "鸡蛋,番茄",
        "--scene",
        "happy",
        "--skill-root",
        str(SKILL_ROOT),
    ]
    try:
        main()
    except SystemExit as exc:
        assert exc.code != 0
    else:
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["ok"] is True
        assert data["primary"]["name"]


def test_recommend_cli_requires_ingredients(capsys):
    sys.argv = ["recommend_cli.py", "--skill-root", str(SKILL_ROOT)]
    with __import__("pytest").raises(SystemExit):
        main()
