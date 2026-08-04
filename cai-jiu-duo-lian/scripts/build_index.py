#!/usr/bin/env python3
"""Extract recipes from anti-inflammatory cookbook md and emit YAML index files."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "参考书籍" / "抗炎食谱100例 (Anti-Inflammatory Diet Cookbook Simple Recipes to Heal the Immune System and Improving Health) (亚历克斯·巴拉克斯).md"
BOOK_REL = "参考书籍/抗炎食谱100例 (Anti-Inflammatory Diet Cookbook Simple Recipes to Heal the Immune System and Improving Health) (亚历克斯·巴拉克斯).md"

INGREDIENT_ART = {
    "鳄梨": "avocado", "西红柿": "tomato", "番茄": "tomato", "黄瓜": "cucumber",
    "鸡蛋": "egg", "鸡": "chicken", "火鸡": "turkey", "牛肉": "beef", "猪肉": "pork",
    "虾": "shrimp", "虾仁": "shrimp", "三文鱼": "salmon", "鱼": "salmon",
    "菠菜": "spinach", "西兰花": "broccoli", "红薯": "potato", "土豆": "potato",
    "藜麦": "quinoa", "米饭": "rice", "面": "noodle", "豆腐": "tofu",
    "蘑菇": "mushroom", "胡萝卜": "carrot", "玉米": "corn", "柠檬": "lemon",
    "蒜": "garlic", "洋葱": "onion", "核桃": "walnut", "草莓": "strawberry",
    "南瓜": "pumpkin", "西葫芦": "zucchini", "羽衣甘蓝": "kale", "燕麦": "oats",
}

SKIP_TITLES = {"Table of Contents", "Guide", "抗炎食谱100例"}


def parse_servings(text: str) -> int:
    m = re.search(r"份数：(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)~(\d+)人份", text)
    if m:
        return int(m.group(1))
    return 2


def parse_cook_time(text: str) -> str:
    m = re.search(r"烹饪时长：(\d+)分钟", text)
    return f"{m.group(1)}min" if m else "20min"


def guess_method(name: str, steps: list[str]) -> str:
    joined = name + "".join(steps)
    if any(k in joined for k in ("烤", "烤箱")):
        return "烤"
    if any(k in joined for k in ("炒", "煎锅", "煎")):
        return "炒"
    if any(k in joined for k in ("炖", "慢炖", "锅")):
        return "炖"
    if any(k in joined for k in ("凉拌", "沙拉", "搅拌")):
        return "凉拌"
    if "沐昔" in name or "饮" in name:
        return "饮品"
    return "煮"


def guess_line_art(name: str, ingredients: list[dict]) -> str:
    for ing in ingredients:
        for key, art in INGREDIENT_ART.items():
            if key in ing["name"]:
                return f"assets/line-art/{art}.svg"
    for key, art in INGREDIENT_ART.items():
        if key in name:
            return f"assets/line-art/{art}.svg"
    return "assets/line-art/tomato.svg"


def classify_scene(name: str, chapter: str) -> tuple[list[str], list[str]]:
    tags: list[str] = []
    if any(k in name for k in ("沙拉", "凉拌", "沐昔", "饮")):
        scene = ["light-meal"]
        tags.extend(["轻食", "沙拉"])
    elif any(k in name for k in ("能量棒", "吐司", "燕麦", "早餐", "煎蛋")):
        scene = ["bento", "happy"]
        tags.extend(["早餐", "快手"])
    elif "汤" in name or "羹" in name:
        scene = ["seasonal", "happy"]
        tags.append("汤")
    elif any(k in name for k in ("烤", "烤箱")):
        scene = ["bento", "happy"]
        tags.append("烤箱")
    else:
        scene = ["happy"]
        tags.append("家常菜")
    if "沙拉" in chapter or "午餐" in chapter:
        if "light-meal" not in scene:
            scene = ["light-meal"] + [s for s in scene if s != "light-meal"]
    tags.append("抗炎")
    return scene, tags


def parse_recipes(text: str) -> list[dict]:
    parts = re.split(r"\n## ", text)
    recipes: list[dict] = []
    idx = 0
    for part in parts[1:]:
        lines = part.splitlines()
        name = lines[0].strip()
        if not name or name in SKIP_TITLES or len(name) > 40:
            continue
        body = "\n".join(lines[1:])
        if "材料" not in body or "步骤" not in body:
            continue
        mat_sec = body.split("步骤")[0]
        step_sec = body.split("步骤", 1)[1]
        ingredients = []
        for line in mat_sec.splitlines():
            line = line.strip()
            if "：" in line and not line.startswith("烹饪") and not line.startswith("份数"):
                k, v = line.split("：", 1)
                k = k.strip()
                if k and k not in ("材料", "份数", "烹饪时长"):
                    ingredients.append({"name": k, "amount": v.strip()})
        steps = []
        for line in step_sec.splitlines():
            line = line.strip().lstrip("0123456789、.")
            if line and line not in ("---", "享用。"):
                steps.append(line)
        if not ingredients or not steps:
            continue
        chapter = "抗炎食谱100例"
        servings = parse_servings(body)
        scene, tags = classify_scene(name, chapter)
        idx += 1
        recipes.append({
            "id": f"anti-{idx:03d}",
            "name": name,
            "scene": scene,
            "tags": tags,
            "servings": servings,
            "cook_time": parse_cook_time(body),
            "cost": "约20元",
            "method": guess_method(name, steps),
            "ingredients": ingredients[:12],
            "steps": steps[:8],
            "source": {
                "book": "抗炎食谱100例",
                "file": BOOK_REL,
                "chapter": chapter,
            },
            "line_art": guess_line_art(name, ingredients),
        })
    return recipes


def split_by_primary_scene(recipes: list[dict]) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = {
        "light-meal": [], "seasonal": [], "health": [],
        "bento": [], "regional": [], "happy": [],
    }
    for r in recipes:
        primary = r["scene"][0]
        if primary not in buckets:
            primary = "happy"
        entry = {**r, "scene": [primary] + [s for s in r["scene"] if s != primary]}
        entry["id"] = f"{primary[:3]}-{entry['id'].split('-')[-1]}"
        buckets[primary].append(entry)
    return buckets


def write_indexes(buckets: dict[str, list[dict]]) -> None:
    out_dir = ROOT / "data" / "recipe-index"
    for scene, items in buckets.items():
        if not items:
            continue
        path = out_dir / f"{scene}.yaml"
        path.write_text(
            yaml.dump(items, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"wrote {path.name}: {len(items)} recipes")


def main() -> None:
    text = BOOK.read_text(encoding="utf-8")
    recipes = parse_recipes(text)
    print(f"parsed {len(recipes)} recipes from anti-inflammatory book")
    buckets = split_by_primary_scene(recipes)
    # health: anti-inflammatory book entries tagged for 调理场景
    for i, r in enumerate(list(buckets["light-meal"])[:18]):
        r2 = {**r, "id": f"hea-{i+1:03d}", "scene": ["health"], "tags": list(dict.fromkeys(r["tags"] + ["日常参考", "抗炎"]))}
        buckets["health"].append(r2)
    write_indexes(buckets)


if __name__ == "__main__":
    main()
