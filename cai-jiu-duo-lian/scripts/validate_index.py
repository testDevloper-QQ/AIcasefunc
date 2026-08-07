"""Validate recipe index YAML entries."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED_TOP = {
    "id",
    "name",
    "scene",
    "tags",
    "servings",
    "cook_time",
    "cost",
    "method",
    "ingredients",
    "steps",
    "source",
}
REQUIRED_SOURCE = {"book", "file", "chapter"}
VALID_SCENES = {"bento", "light-meal", "seasonal", "regional", "health", "happy"}


def validate_recipe_entry(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOP - entry.keys()
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
        return errors
    if not str(entry["name"]).strip():
        errors.append("name must be non-empty")
    if not isinstance(entry["scene"], list) or not entry["scene"]:
        errors.append("scene must be non-empty list")
    else:
        for s in entry["scene"]:
            if s not in VALID_SCENES:
                errors.append(f"invalid scene: {s}")
    if not isinstance(entry["servings"], int) or entry["servings"] < 1:
        errors.append("servings must be int >= 1")
    if not entry["ingredients"]:
        errors.append("ingredients must be non-empty")
    if not entry["steps"]:
        errors.append("steps must be non-empty")
    src = entry.get("source", {})
    if not REQUIRED_SOURCE.issubset(src.keys()):
        errors.append(f"source missing: {REQUIRED_SOURCE - src.keys()}")
    return errors


def validate_index_file(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return [f"{path}: root must be a list"]
    errors: list[str] = []
    seen: set[str] = set()
    for i, entry in enumerate(data):
        for e in validate_recipe_entry(entry):
            errors.append(f"{path}[{i}]: {e}")
        rid = entry.get("id")
        if rid in seen:
            errors.append(f"{path}: duplicate id {rid}")
        seen.add(rid)
    return errors


if __name__ == "__main__":
    import sys

    root = Path(__file__).resolve().parents[1] / "data" / "recipe-index"
    all_errors: list[str] = []
    for f in sorted(root.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        all_errors.extend(validate_index_file(f))
    if all_errors:
        print("\n".join(all_errors))
        sys.exit(1)
    print("All index files valid.")
