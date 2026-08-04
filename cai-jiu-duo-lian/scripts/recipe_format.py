"""Normalize recipe output for home cooking: amounts, time limits, step images, QA."""
from __future__ import annotations

import re
from typing import Any

MAX_COOK_MINUTES = 60
GUIDELINE_REF = "《中国居民膳食指南（2022）》"

# 单餐一人份参考（见 references/dietary-guidelines-cn.md）
DIETARY_PER_MEAL: dict[str, dict[str, float | int]] = {
    "meat": {"default": 75, "min": 50, "max": 100},
    "seafood": {"default": 75, "min": 50, "max": 100},
    "egg": {"default": 50, "min": 50, "max": 50},
    "tofu": {"default": 80, "min": 50, "max": 100},
    "veggie": {"default": 120, "min": 100, "max": 170},
    "staple": {"default": 85, "min": 70, "max": 100},
    "salt": {"default": 2, "min": 0, "max": 2},
    "sugar": {"default": 5, "min": 0, "max": 15},
    "oil": {"default": 10, "min": 8, "max": 10},
    "spice": {"default": 0, "min": 0, "max": 0},
    "default": {"default": 80, "min": 30, "max": 120},
}

MEAT_KEYS = ("肉", "牛", "猪", "羊", "鸡", "鸭", "鹅", "鱼", "虾", "蟹", "贝")
SEAFOOD_KEYS = ("虾", "蟹", "贝", "鱼", "海鲜")
EGG_KEYS = ("蛋",)
TOFU_KEYS = ("豆腐", "豆干", "豆皮")
VEGGIE_KEYS = ("菜", "蔬", "瓜", "茄", "椒", "菇", "菌", "笋", "芽", "芹", "葱", "姜", "蒜")
STAPLE_KEYS = ("米", "面", "粉", "饭", "吐司", "馒头", "饼")
SALT_KEYS = ("盐",)
SUGAR_KEYS = ("糖", "冰糖", "砂糖", "白糖")
OIL_KEYS = ("油", "麻油", "香油", "芝麻油", "橄榄油")
SPICE_KEYS = ("香料", "八角", "桂皮", "花椒", "胡椒", "筚", "山奈", "桂子", "孜然", "辣椒")

STEP_ICON_RULES: list[tuple[str, str]] = [
    (r"切|片|丝|块|剁|改刀", "cut"),
    (r"腌|拌|揉|搓|上味|调味|手拌", "mix"),
    (r"铺|摆|放|码|装|入模|竹|筲", "arrange"),
    (r"烤|炒|煮|炖|蒸|炸|煎|烧|焖|煲|烙|烘干|翻动", "cook"),
    (r"取食|装盘|出锅|淋|点缀|保鲜|浸泡|完成|享用", "finish"),
]

STEP_ICON_FALLBACK = ["prep", "cut", "mix", "cook", "finish"]


def guideline_grams(category: str, servings: int = 1, *, use: str = "default") -> float:
    spec = DIETARY_PER_MEAL.get(category, DIETARY_PER_MEAL["default"])
    value = float(spec[use])
    return value * servings


def parse_cook_time_minutes(cook_time: str | None) -> int:
    if not cook_time:
        return 20
    m = re.search(r"(\d+)\s*(?:min|分钟)?", str(cook_time), re.I)
    return int(m.group(1)) if m else 20


def is_quick_recipe(recipe: dict, max_minutes: int = MAX_COOK_MINUTES) -> bool:
    return parse_cook_time_minutes(recipe.get("cook_time")) <= max_minutes


def _ingredient_category(name: str) -> str:
    n = name or ""
    if any(k in n for k in SALT_KEYS):
        return "salt"
    if any(k in n for k in SUGAR_KEYS):
        return "sugar"
    if any(k in n for k in OIL_KEYS):
        return "oil"
    if any(k in n for k in SPICE_KEYS):
        return "spice"
    if any(k in n for k in EGG_KEYS):
        return "egg"
    if any(k in n for k in TOFU_KEYS):
        return "tofu"
    if any(k in n for k in SEAFOOD_KEYS):
        return "seafood"
    if any(k in n for k in MEAT_KEYS):
        return "meat"
    if any(k in n for k in STAPLE_KEYS):
        return "staple"
    if any(k in n for k in VEGGIE_KEYS):
        return "veggie"
    return "default"


def _parse_amount(amount: str) -> tuple[float | None, str | None]:
    if not amount or "适量" in amount or "少许" in amount:
        return None, None
    m = re.search(r"([\d.]+)\s*(公斤|千克|kg|克|g|斤|两|ml|毫升|个|只|根|片|块|汤匙|茶匙)", amount, re.I)
    if not m:
        return None, None
    value = float(m.group(1))
    unit = m.group(2).lower()
    return value, unit


def _to_grams(value: float, unit: str) -> float:
    if unit in ("公斤", "千克", "kg"):
        return value * 1000
    if unit == "斤":
        return value * 500
    if unit == "两":
        return value * 50
    if unit in ("克", "g"):
        return value
    return value


def _format_home_amount(grams: float, category: str) -> str:
    if category == "spice" or grams <= 0:
        return "适量"
    if category == "egg" and 45 <= grams <= 55:
        return "1个（约50克）"
    if grams >= 500 and abs(grams % 500) < 0.01:
        jin = grams / 500
        return f"约{jin:g}斤" if jin >= 1 else f"约{int(grams)}克"
    if grams >= 100:
        return f"约{int(round(grams))}克"
    if grams >= 10:
        return f"约{int(round(grams))}克"
    return f"约{grams:.0f}克" if grams >= 1 else "少许"


def _is_commercial_batch(amount: str, value: float | None, unit: str | None) -> bool:
    if not amount:
        return False
    if "每100公斤" in amount or ("按比例" in amount and value and value >= 10):
        return True
    if value is None:
        return False
    grams = _to_grams(value, unit or "克")
    if unit in ("公斤", "千克", "kg") and value >= 1:
        return True
    if unit == "斤" and value >= 10:
        return True
    if grams >= 2000:
        return True
    return False


def _scale_parsed_amount(value: float, unit: str, ratio: float, category: str) -> str:
    if unit in ("个", "只") and category == "egg":
        scaled = max(1, round(value * ratio))
        return f"约{scaled}个"
    if unit in ("个", "只", "根", "片", "块"):
        scaled = max(1, round(value * ratio))
        return f"约{scaled}{unit}"
    grams = _to_grams(value, unit) * ratio
    return _format_home_amount(grams, category)


def _clamp_to_guideline(grams: float, category: str, servings: int) -> float:
    spec = DIETARY_PER_MEAL.get(category, DIETARY_PER_MEAL["default"])
    max_g = float(spec["max"]) * servings
    min_g = float(spec["min"]) * servings
    if category == "spice":
        return 0
    if grams > max_g:
        return max_g
    if grams < min_g and category in ("meat", "seafood", "veggie", "staple"):
        return float(spec["default"]) * servings
    return grams


def normalize_ingredients(recipe: dict, target_servings: int | None) -> list[dict[str, str]]:
    ingredients = recipe.get("ingredients") or []
    if not ingredients:
        return []

    base = recipe.get("servings") or 2
    target = target_servings or base
    ratio = target / base if base else 1.0
    note_suffix = f"（已按{GUIDELINE_REF}家庭份量换算）"

    normalized: list[dict[str, str]] = []
    for ing in ingredients:
        name = ing.get("name", "")
        raw_amount = ing.get("amount", "")
        category = _ingredient_category(name)
        value, unit = _parse_amount(raw_amount)
        note = ""

        if _is_commercial_batch(raw_amount, value, unit):
            home_g = guideline_grams(category, target)
            amount = _format_home_amount(home_g, category)
            note = note_suffix
        elif value is not None and unit is not None:
            grams = _to_grams(value, unit)
            if grams > 1500 and category in ("meat", "seafood", "veggie", "tofu", "staple"):
                home_g = guideline_grams(category, target)
                amount = _format_home_amount(home_g, category)
                note = note_suffix
            elif unit in ("个", "只", "根", "片", "块", "汤匙", "茶匙"):
                amount = _scale_parsed_amount(value, unit, ratio, category)
            else:
                scaled_g = _clamp_to_guideline(grams * ratio, category, target)
                if scaled_g != grams * ratio:
                    note = note_suffix
                if category in ("salt", "sugar", "oil") and scaled_g > guideline_grams(category, target, use="max"):
                    scaled_g = guideline_grams(category, target, use="max")
                    note = note_suffix
                amount = _format_home_amount(scaled_g, category)
        elif "适量" in raw_amount or "少许" in raw_amount:
            amount = raw_amount.split("（")[0].strip() or "适量"
        else:
            amount = raw_amount

        if note and note not in amount:
            amount = f"{amount}{note}"
        normalized.append({"name": name, "amount": amount})
    return normalized


def pick_step_icon(step_text: str, index: int, total: int) -> str:
    for pattern, icon in STEP_ICON_RULES:
        if re.search(pattern, step_text):
            return icon
    if total <= len(STEP_ICON_FALLBACK):
        return STEP_ICON_FALLBACK[min(index, len(STEP_ICON_FALLBACK) - 1)]
    return STEP_ICON_FALLBACK[index % len(STEP_ICON_FALLBACK)]


def format_steps(steps: list[str]) -> list[dict[str, Any]]:
    total = len(steps)
    formatted = []
    for i, text in enumerate(steps):
        icon = pick_step_icon(text, i, total)
        formatted.append({
            "text": text,
            "icon": f"/icons/steps/{icon}.svg",
        })
    return formatted


def validate_home_output(recipe: dict, servings: int = 1) -> list[str]:
    """Quality checks aligned with 中国居民膳食指南（2022） per-meal ranges."""
    issues: list[str] = []
    minutes = parse_cook_time_minutes(recipe.get("cookTime") or recipe.get("cook_time"))
    if minutes > MAX_COOK_MINUTES:
        issues.append(f"烹饪时间 {minutes} 分钟超过 {MAX_COOK_MINUTES} 分钟上限")

    for ing in recipe.get("ingredients") or []:
        amount = ing.get("amount", "")
        value, unit = _parse_amount(amount)
        if value is None:
            continue
        grams = _to_grams(value, unit or "克")
        cat = _ingredient_category(ing.get("name", ""))
        spec = DIETARY_PER_MEAL.get(cat, DIETARY_PER_MEAL["default"])
        max_g = float(spec["max"]) * servings
        min_g = float(spec["min"]) * servings

        if cat == "salt" and grams > max_g:
            issues.append(f"盐 {amount} 超出{GUIDELINE_REF}单餐建议（≤{spec['max']}g/人）")
        elif cat == "sugar" and grams > max_g:
            issues.append(f"糖 {amount} 超出{GUIDELINE_REF}单餐建议（≤{spec['max']}g/人）")
        elif cat == "oil" and grams > max_g:
            issues.append(f"油脂 {amount} 超出{GUIDELINE_REF}单餐建议（≤{spec['max']}g/人）")
        elif cat in ("meat", "seafood") and grams > max_g:
            issues.append(
                f"{ing.get('name')} {amount} 超出{GUIDELINE_REF}鱼禽肉蛋单餐建议（{spec['min']}-{spec['max']}g/人）"
            )
        elif cat == "veggie" and (grams > max_g or (grams < min_g and grams > 0)):
            issues.append(
                f"{ing.get('name')} {amount} 偏离{GUIDELINE_REF}蔬菜单餐建议（{spec['min']}-{spec['max']}g/人）"
            )
        elif cat == "staple" and grams > max_g:
            issues.append(
                f"{ing.get('name')} {amount} 超出{GUIDELINE_REF}谷薯单餐建议（{spec['min']}-{spec['max']}g/人）"
            )
        elif grams >= 2000:
            issues.append(f"{ing.get('name')} {amount} 疑似批量配方未按{GUIDELINE_REF}换算")

    return issues


def cap_cook_time_display(cook_time: str | None) -> str:
    minutes = parse_cook_time_minutes(cook_time)
    if minutes > MAX_COOK_MINUTES:
        return f"{MAX_COOK_MINUTES}min内（原配方耗时较长，已不推荐完整流程）"
    return cook_time or "20min"
