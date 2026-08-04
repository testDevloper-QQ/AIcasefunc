"""Generate Chinese home-cooking fallback when index has no ingredient match."""
from __future__ import annotations

from typing import Any

from llm_recipe_search import search_and_generate_recipe

SCENE_LABELS = {
    "bento": "便当",
    "light-meal": "轻食",
    "seasonal": "时令",
    "regional": "地方味",
    "health": "调理",
    "happy": "快乐餐",
}

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
}


def _template_fallback(ingredients: list[str], scene: str, servings: int) -> dict[str, Any]:
    key = frozenset(ingredients)
    if key in NAMED_DISHES:
        name, steps = NAMED_DISHES[key]
    elif len(ingredients) == 1:
        name = f"{ingredients[0]} 家常小炒"
        steps = [
            f"{ingredients[0]} 洗净切好，备用。",
            "热锅凉油，下食材中火煸炒至断生。",
            "调入盐、少许生抽，翻炒均匀即可。",
        ]
    else:
        name = f"{' '.join(ingredients[:2])} 家常小炒"
        joined = "、".join(ingredients)
        steps = [
            f"{joined} 洗净切好，备用。",
            "热锅凉油，先下较难熟的食材中火煸炒。",
            "加入其余食材，调入盐、少许生抽，翻炒均匀至熟即可。",
        ]

    scene_label = SCENE_LABELS.get(scene, scene)
    ing_rows = [{"name": ing, "amount": "约120克" if _is_veggie(ing) else "约75克"} for ing in ingredients]
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
        "steps": steps,
        "source": {
            "book": "AI 家常菜建议（离线模板）",
            "chapter": f"根据{'、'.join(ingredients)}组合生成",
        },
        "line_art": "",
        "generated": True,
        "llmGenerated": False,
    }


def build_fallback_recipe(
    ingredients: list[str],
    scene: str,
    *,
    servings: int = 2,
) -> dict[str, Any]:
    llm_recipe = search_and_generate_recipe(ingredients, scene, servings=servings)
    if llm_recipe:
        return llm_recipe
    return _template_fallback(ingredients, scene, servings)


def _is_veggie(name: str) -> bool:
    keys = ("菜", "瓜", "豆", "茄", "椒", "菇", "菌", "笋", "芹", "葱", "姜", "蒜", "萝卜", "芽")
    return any(k in name for k in keys)
