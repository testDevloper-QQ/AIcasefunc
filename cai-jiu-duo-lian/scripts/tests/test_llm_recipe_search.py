"""Tests for LLM recipe JSON parsing."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm_recipe_search import _parse_recipe_json  # noqa: E402


def test_parse_recipe_json_valid():
    raw = """{
      "name": "豆角烧茄子",
      "method": "炒",
      "cook_time": "25min",
      "cost": "约12元",
      "ingredients": [{"name": "豆角", "amount": "200克"}, {"name": "茄子", "amount": "1个"}],
      "steps": ["豆角切段，茄子切条", "热锅少油下茄子煸软", "下豆角同炒，调味出锅"]
    }"""
    data = _parse_recipe_json(raw, ["豆角", "茄子"])
    assert data is not None
    assert data["name"] == "豆角烧茄子"
    assert len(data["steps"]) == 3


def test_parse_recipe_json_rejects_missing_ingredient():
    raw = """{
      "name": "清炒虾仁",
      "ingredients": [{"name": "虾仁", "amount": "200克"}],
      "steps": ["炒虾仁"]
    }"""
    assert _parse_recipe_json(raw, ["豆角", "茄子"]) is None
