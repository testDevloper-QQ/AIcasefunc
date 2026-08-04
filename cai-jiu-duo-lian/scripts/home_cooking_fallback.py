"""Generate Chinese home-cooking fallback when index has no ingredient match."""
from __future__ import annotations

from typing import Any

SCENE_LABELS = {
    "bento": "便当",
    "light-meal": "轻食",
    "seasonal": "时令",
    "regional": "地方味",
    "health": "调理",
    "happy": "快乐餐",
}

# Known multi-ingredient home dishes
NAMED_DISHES: dict[frozenset[str], tuple[str, list[str]]] = {
    frozenset({"豆角", "茄子"}): (
        "豆角烧茄子",
        [
            "豆角择洗干净切寸段；茄子切条，用清水稍泡减轻吸油，沥干备用。",
            "热锅少油，下茄子条中火煸至变软微黄，盛出。",
            "留底油爆香蒜末，下豆角中火煸炒 2 分钟至断生。",
            "倒回茄子，加生抽、少许清水，盖盖焖 3 分钟，盐调味，翻炒均匀即可。",
        ],
    ),
    frozenset({"番茄", "鸡蛋"}): (
        "番茄炒蛋",
        [
            "鸡蛋打散，番茄切块，葱切花。",
            "热锅油稍多，倒入蛋液炒至凝固盛出。",
            "留底油炒番茄至出汁，倒回鸡蛋，盐、少许糖调味，撒葱花即可。",
        ],
    ),
    frozenset({"土豆", "茄子"}): (
        "地三鲜（土豆茄子版）",
        [
            "土豆、茄子切滚刀块，青椒切块（可选）。",
            "土豆、茄子分别过油或煎至表面微黄。",
            "留底油，下蒜片爆香，倒入所有食材，加生抽、少许糖、盐，快炒均匀即可。",
        ],
    ),
    frozenset({"黄瓜", "鸡蛋"}): (
        "黄瓜炒蛋",
        [
            "黄瓜切片，鸡蛋打散。",
            "先炒蛋至凝固盛出。",
            "下黄瓜片快炒，倒回鸡蛋，盐调味即可。",
        ],
    ),
}


def _default_steps(ingredients: list[str]) -> list[str]:
    joined = "、".join(ingredients)
    return [
        f"{joined} 洗净切好，备用。",
        "热锅凉油，先下较难熟的食材中火煸炒。",
        "加入其余食材，调入盐、少许生抽（或按口味），翻炒均匀至熟即可。",
    ]


def suggest_dish_name(ingredients: list[str]) -> str:
    key = frozenset(ingredients)
    if key in NAMED_DISHES:
        return NAMED_DISHES[key][0]
    if len(ingredients) == 1:
        return f"{ingredients[0]} 家常小炒"
    return f"{' '.join(ingredients[:2])} 家常小炒"


def suggest_steps(ingredients: list[str]) -> list[str]:
    key = frozenset(ingredients)
    if key in NAMED_DISHES:
        return NAMED_DISHES[key][1]
    return _default_steps(ingredients)


def build_fallback_recipe(
    ingredients: list[str],
    scene: str,
    *,
    servings: int = 2,
) -> dict[str, Any]:
    name = suggest_dish_name(ingredients)
    scene_label = SCENE_LABELS.get(scene, scene)
    ing_rows = []
    for ing in ingredients:
        ing_rows.append({"name": ing, "amount": "约120克" if _is_veggie(ing) else "约75克"})
    ing_rows.extend([
        {"name": "大蒜", "amount": "2瓣"},
        {"name": "生抽", "amount": "1汤匙"},
        {"name": "盐", "amount": "约2克"},
        {"name": "烹调油", "amount": "约10克"},
    ])
    return {
        "id": f"ai-home-{'-'.join(ingredients)}",
        "name": name,
        "scene": [scene],
        "tags": ["AI家常菜", scene_label, *ingredients],
        "servings": servings,
        "cook_time": "25min",
        "cost": "约15元",
        "method": "炒",
        "ingredients": ing_rows,
        "steps": suggest_steps(ingredients),
        "source": {
            "book": "AI 家常菜建议",
            "chapter": f"根据{'、'.join(ingredients)}组合生成",
        },
        "line_art": "",
        "generated": True,
    }


def _is_veggie(name: str) -> bool:
    keys = ("菜", "瓜", "豆", "茄", "椒", "菇", "菌", "笋", "芹", "葱", "姜", "蒜", "萝卜", "芽")
    return any(k in name for k in keys)
