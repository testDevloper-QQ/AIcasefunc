from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_index import validate_recipe_entry, validate_index_file

SAMPLE = {
    "id": "salad-001",
    "name": "鳄梨西红柿沙拉",
    "scene": ["light-meal"],
    "tags": ["沙拉", "轻食"],
    "servings": 1,
    "cook_time": "15min",
    "cost": "约15元",
    "method": "凉拌",
    "ingredients": [{"name": "鳄梨", "amount": "1个"}],
    "steps": ["切块拌匀"],
    "source": {
        "book": "抗炎食谱100例",
        "file": "参考书籍/抗炎食谱100例.md",
        "chapter": "沙拉",
    },
}


def test_valid_entry_passes():
    assert validate_recipe_entry(SAMPLE) == []


def test_missing_name_fails():
    bad = {**SAMPLE, "name": ""}
    errors = validate_recipe_entry(bad)
    assert any("name" in e for e in errors)


def test_sample_yaml_file_passes():
    root = Path(__file__).resolve().parents[2]
    sample = root / "data" / "recipe-index" / "_sample.yaml"
    assert validate_index_file(sample) == []
