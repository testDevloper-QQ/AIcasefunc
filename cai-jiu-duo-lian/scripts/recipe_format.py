"""Normalize recipe output for home cooking: amounts, time limits, step images, QA."""
from __future__ import annotations

import re
from pathlib import Path
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

INGREDIENT_ART: dict[str, str] = {
    "鳄梨": "avocado", "西红柿": "tomato", "番茄": "tomato", "黄瓜": "cucumber",
    "鸡蛋": "egg", "鸡": "chicken", "火鸡": "turkey", "牛肉": "beef", "猪肉": "pork",
    "虾": "shrimp", "虾仁": "shrimp", "三文鱼": "salmon", "鱼": "salmon",
    "菠菜": "spinach", "西兰花": "broccoli", "红薯": "potato", "土豆": "potato",
    "藜麦": "quinoa", "米饭": "rice", "面": "noodle", "豆腐": "tofu",
    "蘑菇": "mushroom", "胡萝卜": "carrot", "玉米": "corn", "柠檬": "lemon",
    "蒜": "garlic", "洋葱": "onion", "核桃": "walnut", "杏仁": "walnut",
    "草莓": "strawberry", "蓝莓": "strawberry", "香蕉": "corn",
    "南瓜": "pumpkin", "西葫芦": "zucchini", "羽衣甘蓝": "kale", "燕麦": "oats",
    "豆角": "greenbean", "四季豆": "greenbean", "长豆角": "greenbean",
    "茄子": "eggplant", "大茄子": "eggplant",
    "鸡肉": "chicken", "鸡胸肉": "chicken", "鸡翅": "chicken", "鸡腿": "chicken",
    "鸡块": "chicken", "鸡丁": "chicken", "鸡肉碎": "chicken", "鸡丝": "chicken",
    "白虾": "shrimp", "明虾": "shrimp", "对虾": "shrimp",
    "水芹": "celery", "芹菜": "celery", "西芹": "celery",
    "彩椒": "pepper", "甜椒": "pepper", "灯笼椒": "pepper", "青椒": "pepper", "红椒": "pepper",
    "白砂糖": "sugar", "白糖": "sugar", "砂糖": "sugar", "冰糖": "sugar", "糖": "sugar",
    "盐": "salt", "精盐": "salt",
    "白胡椒": "whitepepper", "黑胡椒": "blackpepper", "胡椒": "whitepepper", "花椒": "spicejar",
    "姜": "ginger", "生姜": "ginger", "姜片": "ginger",
    "葱": "scallion", "大葱": "scallion", "小葱": "scallion", "青蒜": "scallion",
    "油": "oil", "麻油": "oil", "香油": "oil", "芝麻油": "oil", "橄榄油": "oil", "食用油": "oil",
    "酱油": "soy", "生抽": "soy", "老抽": "soy",
    "米酒": "wine", "料酒": "wine", "黄酒": "wine",
    "牛奶": "milk", "酸奶": "yogurt", "曲奇": "cookie", "饼干": "cookie",
    "吉利丁": "gelatin", "吉利丁片": "gelatin",
    "排骨": "pork", "咸肉": "pork", "春笋": "bamboo", "笋": "bamboo",
    "米": "rice", "大米": "rice", "糯米": "rice",
    "辣椒粉": "chilipowder", "辣椒面": "chilipowder",
    "姜黄粉": "turmeric",
    "孜然粉": "cumin", "小茴香": "cumin",
    "肉桂粉": "cinnamon",
    "干香菜粉": "coriander", "香菜粉": "coriander",
    "牛至": "oregano",
    "迷迭香": "rosemary",
    "青柠汁": "limejuice", "青柠": "limejuice", "柠檬汁": "limejuice",
    "生姜酱": "gingerpaste", "姜蒜酱": "gingerpaste",
    "蜂蜜": "honey",
    "鹰嘴豆粉": "chickpeaflour", "鹰嘴豆": "chickpea",
    "薄荷": "mint", "薄荷叶": "mint",
    "橄榄油": "oil",
}

# 用户点选食材 → 索引中可能出现的同义表述（不含易混淆项，如「鸡」不含以免误匹配「鸡蛋」）
INGREDIENT_SYNONYMS: dict[str, list[str]] = {
    "鸡肉": ["鸡肉", "鸡胸肉", "鸡翅", "鸡腿", "鸡块", "鸡丁", "鸡肉碎", "鸡丝", "整鸡", "清远鸡", "文昌鸡"],
    "鸡": ["鸡肉", "鸡胸肉", "鸡翅", "鸡腿", "鸡块", "鸡丁", "鸡肉碎", "鸡丝", "整鸡"],
    "虾": ["虾", "虾仁", "白虾", "明虾", "对虾", "小龙虾"],
    "虾仁": ["虾", "虾仁", "白虾", "明虾", "对虾"],
    "番茄": ["番茄", "西红柿"],
    "西红柿": ["番茄", "西红柿"],
    "土豆": ["土豆", "马铃薯", "洋芋"],
    "马铃薯": ["土豆", "马铃薯", "洋芋"],
    "豆角": ["豆角", "四季豆", "长豆角"],
    "四季豆": ["豆角", "四季豆", "长豆角"],
}


def ingredient_match_terms(user_ingredient: str) -> list[str]:
    name = (user_ingredient or "").strip()
    if not name:
        return []
    terms = {name}
    for key, aliases in INGREDIENT_SYNONYMS.items():
        group = {key, *aliases}
        if name in group:
            terms.update(group)
    return sorted(terms, key=len, reverse=True)


def ingredient_matches_in_text(hay: str, user_ingredient: str) -> bool:
    if not hay or not user_ingredient:
        return False
    for term in ingredient_match_terms(user_ingredient):
        if term and term in hay:
            if user_ingredient in ("鸡肉", "鸡") and term == "鸡" and "鸡蛋" in hay and "鸡肉" not in hay:
                continue
            return True
    return False


def _fahrenheit_to_celsius(f: float) -> int:
    return round((f - 32) * 5 / 9)


# 非烹饪步骤：营养表、无动作冗余句
NUTRITION_STEP_RE = re.compile(
    r"卡路里|千卡|\bkcal\b|"
    r"钠\s*[-—]?\s*毫克|总脂肪|饱和脂肪|反式脂肪|单不饱和|多元不饱和|"
    r"膳食纤维|总碳水化合物|胆固醇\s*[-—]?\s*毫克|"
    r"维生素\s*[A-ZＡ-Ｚ]|维生素[A-CＡ-Ｃ]|"
    r"钾\s*[-—]?\s*毫克|蛋白质\s*\d+\s*克|糖\s*[-—]?\s*克",
    re.I,
)
REDUNDANT_STEP_RE = re.compile(
    r"^(?:即可|趁热|慢慢)?(?:品尝|享用|食用)[。．.!！]?$|"
    r"^装盘享用[。．.!！]?$|"
    r"^[\*\s\.]+$",
    re.I,
)
FOREIGN_UNIT_RE = re.compile(
    r"美国烹饪计量|cups?\b|cup=|盎司＝|"
    r"\b(?:teaspoon|tablespoon|tsp|tbsp|pound|lb|fl\s*oz|quart|pint|inch|in\.)\b",
    re.I,
)


FRACTION_CHARS: dict[str, str] = {
    "¼": "0.25",
    "½": "0.5",
    "¾": "0.75",
    "⅓": "0.333",
    "⅔": "0.667",
}
LIQUID_INGREDIENT_HINTS = ("奶", "油", "汁", "酱", "水", "汤", "酒", "醋", "液", "蜜", "茶", "咖啡")


def _normalize_fractions(text: str) -> str:
    out = text or ""
    for ch, val in FRACTION_CHARS.items():
        out = out.replace(ch, val)
    out = re.sub(
        r"(\d+)\s*/\s*(\d+)",
        lambda m: str(round(float(m.group(1)) / float(m.group(2)), 3)).rstrip("0").rstrip("."),
        out,
    )
    return out


def localize_amount(amount: str, ingredient_name: str = "") -> str:
    if not amount:
        return amount
    text = _normalize_fractions(amount)
    name = ingredient_name or ""
    is_liquid = any(h in name for h in LIQUID_INGREDIENT_HINTS)
    # 盎司 → 克
    def oz_repl(m: re.Match[str]) -> str:
        grams = round(float(m.group(1)) * 28.35)
        return f"约{grams}克"
    text = re.sub(r"([\d.]+)\s*盎司", oz_repl, text)
    text = re.sub(
        r"([\d.]+)\s*(?:pound|lb|磅)\b",
        lambda m: f"约{round(float(m.group(1)) * 454)}克",
        text,
        flags=re.I,
    )
    # cup → 毫升（液体语境）或克
    def cup_repl(m: re.Match[str]) -> str:
        val = float(m.group(1))
        return f"约{round(val * 240)}毫升"

    if is_liquid:
        text = re.sub(r"([\d.]+)\s*(?:cup|Cup|杯)", cup_repl, text, flags=re.I)
    else:
        text = re.sub(r"([\d.]+)\s*(?:cup|Cup|杯)", lambda m: f"约{m.group(1)}杯", text, flags=re.I)
    text = re.sub(
        r"([\d.]+)\s*(?:teaspoon|tsp|茶匙)",
        lambda m: f"约{round(float(m.group(1)) * 5)}毫升",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"([\d.]+)\s*(?:tablespoon|tbsp|汤匙)",
        lambda m: f"约{round(float(m.group(1)) * 15)}毫升",
        text,
        flags=re.I,
    )
    return text


def localize_text(text: str) -> str:
    if not text:
        return text
    if FOREIGN_UNIT_RE.search(text):
        if re.search(r"美国烹饪计量|cups?\b|cup=|盎司＝", text, re.I):
            return ""
    out = text.strip()

    def f_repl(m: re.Match[str]) -> str:
        c = _fahrenheit_to_celsius(float(m.group(1)))
        return f"约{c}℃"

    out = re.sub(r"华氏\s*(\d+)\s*度", f_repl, out)
    out = re.sub(r"(\d+)\s*°?\s*F\b", f_repl, out, flags=re.I)
    out = re.sub(r"在华氏\s*(\d+)\s*度", lambda m: f"在约{_fahrenheit_to_celsius(float(m.group(1)))}℃", out)
    out = re.sub(r"([\d.]+)\s*盎司", lambda m: f"约{round(float(m.group(1)) * 28.35)}克", out)
    out = re.sub(
        r"([\d.]+)\s*(?:pound|lb|磅)\b",
        lambda m: f"约{round(float(m.group(1)) * 454)}克",
        out,
        flags=re.I,
    )
    out = re.sub(r"([\d.]+)\s*(?:cup|Cup|杯)", lambda m: f"约{round(float(m.group(1)) * 240)}毫升", out, flags=re.I)
    out = re.sub(
        r"([\d.]+)\s*(?:teaspoon|tsp|茶匙)",
        lambda m: f"约{round(float(m.group(1)) * 5)}毫升",
        out,
        flags=re.I,
    )
    out = re.sub(
        r"([\d.]+)\s*(?:tablespoon|tbsp|汤匙)",
        lambda m: f"约{round(float(m.group(1)) * 15)}毫升",
        out,
        flags=re.I,
    )
    return out.strip()


def is_cooking_step(text: str) -> bool:
    """True when step is an actionable cooking instruction (not nutrition / filler)."""
    t = (text or "").strip()
    if not t:
        return False
    if REDUNDANT_STEP_RE.match(t):
        return False
    if NUTRITION_STEP_RE.search(t):
        return False
    if t.count("毫克") >= 2:
        return False
    if ("维生素" in t or "钙" in t or "铁" in t) and "%" in t:
        return False
    return True


def filter_cooking_steps(steps: list[Any]) -> list[str]:
    """Return localized, actionable cooking steps only."""
    out: list[str] = []
    for raw in steps or []:
        text = raw if isinstance(raw, str) else (raw.get("text") if isinstance(raw, dict) else "")
        localized = localize_text(str(text or ""))
        if localized and is_cooking_step(localized):
            out.append(localized)
    return out


def extract_reference_book_hints(*texts: str) -> list[str]:
    """Pull likely cookbook / reference-book phrases from user free text."""
    hay = " ".join(t.strip() for t in texts if t and str(t).strip())
    if not hay:
        return []
    hints: list[str] = []
    for m in re.finditer(r"[《「]([^》」]+)[》」]", hay):
        hints.append(m.group(1).strip())
    for m in re.finditer(r"(?:参考|来自|指定|按照|用|看)\s*[《「]?([^，。,.；;]{2,40})", hay):
        hints.append(m.group(1).strip())
    if re.search(r"食谱|cookbook|Cookbook|书", hay, re.I):
        hints.append(hay)
    for m in re.finditer(r"[A-Za-z][A-Za-z\s\-]{3,}", hay):
        hints.append(m.group(0).strip())
    deduped = list(dict.fromkeys(h for h in hints if len(h) >= 2))
    return deduped


def reference_book_match_score(recipe: dict[str, Any], *texts: str) -> float:
    """Boost when recipe source matches user-mentioned reference book (any origin)."""
    hints = extract_reference_book_hints(*texts)
    if not hints:
        return 0.0
    src = recipe.get("source") or {}
    book = str(src.get("book") or "")
    chapter = str(src.get("chapter") or "")
    file_path = str(src.get("file") or "")
    corpus = f"{book} {chapter} {file_path}"
    score = 0.0
    for hint in hints:
        h = hint.strip()
        if not h:
            continue
        if h in corpus:
            score += 25
        elif book and (h in book or book in h):
            score += 22
        elif len(h) >= 3 and h[: min(6, len(h))] in corpus:
            score += 15
        elif file_path and h.lower() in file_path.lower():
            score += 18
    return score


def format_cook_time_cn(cook_time: str | None) -> str:
    minutes = parse_cook_time_minutes(cook_time)
    if minutes == 0:
        return "免火或即食"
    return f"{minutes}分钟"


def guess_ingredient_art_key(name: str) -> str | None:
    for key in sorted(INGREDIENT_ART.keys(), key=len, reverse=True):
        if key in name:
            return INGREDIENT_ART[key]
    cat = _ingredient_category(name)
    if cat == "salt":
        return "salt"
    if cat == "sugar":
        return "sugar"
    if cat == "oil":
        return "oil"
    if cat == "spice":
        return "spicejar"
    return "generic"


def _art_url_with_cache_bust(url: str, skill_root: Path | None) -> str:
    if not url or not skill_root:
        return url
    rel = url.replace("/skill-assets/", "").split("?", 1)[0]
    path = skill_root / rel
    if path.is_file():
        return f"{url.split('?', 1)[0]}?v={int(path.stat().st_mtime)}"
    return ""


def ingredient_art_url(name: str, skill_root: Path | None) -> tuple[str, str]:
    """Return (art_key, url). URL empty when no dedicated asset (never generic fallback)."""
    from illustration_resolver import resolve_ingredient_illustration

    art = guess_ingredient_art_key(name) or ""
    if art == "generic" and not any(k in (name or "") for k in ("覆盆子", "通用", "其他")):
        return art, ""
    url = resolve_ingredient_illustration(name, art, skill_root) if art else ""
    url = _art_url_with_cache_bust(url, skill_root)
    return art, url


def enrich_ingredients(ingredients: list[dict[str, str]], skill_root: Path | None) -> list[dict[str, str]]:
    enriched = []
    for ing in ingredients:
        name = ing.get("name", "")
        amount = localize_amount(ing.get("amount", ""), name)
        art_key, art_url = ingredient_art_url(name, skill_root)
        row: dict[str, str] = {
            "name": name,
            "amount": amount,
            "artUrl": art_url,
        }
        if art_key and art_url:
            row["artKey"] = art_key
        enriched.append(row)
    return enriched


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
        amount = localize_amount(amount, name)
        normalized.append({"name": name, "amount": amount})
    return normalized


def format_steps(
    steps: list[str],
    ingredients: list[dict] | None = None,
    skill_root: Path | None = None,
    recipe_id: str | None = None,
) -> list[dict[str, Any]]:
    from illustration_resolver import resolve_step_illustration

    formatted = []
    cooking_steps = filter_cooking_steps(steps)
    for step_num, text in enumerate(cooking_steps, start=1):
        step_art_url, scene_id = resolve_step_illustration(
            text,
            step_num - 1,
            skill_root,
            recipe_id=recipe_id,
            step_index=step_num,
        )
        formatted.append({
            "index": step_num,
            "text": text,
            "sceneId": scene_id,
            "stepArtUrl": step_art_url or None,
            "stepIllustrationUrl": step_art_url or None,
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
