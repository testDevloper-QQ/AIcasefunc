"""Resolve hand-drawn journal illustrations: dish hero, step narrative, ingredient."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ILLUSTRATIONS = "assets/illustrations"
DISH_DIR = f"{ILLUSTRATIONS}/dishes"
DISH_SHARED_DIR = f"{DISH_DIR}/shared"
STEP_DIR = f"{ILLUSTRATIONS}/steps"
ING_DIR = f"{ILLUSTRATIONS}/ingredients"

IMAGE_EXTENSIONS = (".png", ".webp", ".jpg", ".jpeg")


def dish_share_basename(recipe_name: str) -> str:
    name = (recipe_name or "").strip()
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "", name)
    return safe or "unnamed"


def shared_dish_asset_rel(recipe_name: str) -> str:
    return f"{DISH_SHARED_DIR}/{dish_share_basename(recipe_name)}.png"

STEP_ILLUSTRATION_RULES: list[tuple[str, str]] = [
    (r"冷冻|冷藏|冰镇|放入冰箱", "freezer_chill"),
    (r"搅拌|打沙|料理机|破壁|沐昔|榨汁", "blender_pour"),
    (r"烤箱|预热|烘烤|烘焙", "oven_bake"),
    (r"蒸|蒸笼|上汽", "steam_basket"),
    (r"粥|七分熟|米粒|糯米|混合煮|大米.*煮", "pot_porridge_simmer"),
    (r"加盐|调味即可|少许盐|再加.*盐", "pot_season_finish"),
    (r"腌|腌制|上味|用酱油|用.*调味.*分钟", "board_marinate"),
    (r"洗净|清洗|浸泡|泡水", "prep_wash"),
    (r"切|切片|切丝|切块|切丁|剁|改刀|去皮|手撕|撕成", "board_cut"),
    (r"炒|翻炒|煸|锅铲|颠锅", "wok_stir_fry"),
    (r"煎|烙|两面金黄", "wok_pan_fry"),
    (r"拌|手抓|揉|搓", "bowl_mix"),
    (r"炖|煲|小火|大火|出沙|再煮", "pot_boil_simmer"),
    (r"出锅|完成|享用|装盘|上桌|取食|点缀|淋", "plate_serve"),
]

STEP_ILLUSTRATION_FALLBACK = [
    "default_prep",
    "board_cut",
    "pot_boil_simmer",
    "wok_stir_fry",
    "plate_serve",
]


def skill_asset_url(rel: str, skill_root: Path | None) -> str:
    """Return web URL for a skill asset if the file exists."""
    root = skill_root or Path(__file__).resolve().parents[1]
    rel_norm = rel.replace("\\", "/").lstrip("/")
    path = root / rel_norm
    if path.is_file():
        return f"/skill-assets/{rel_norm}"
    return ""


def find_illustration_asset(base_dir: str, basename: str, skill_root: Path | None) -> str:
    """Resolve raster illustration (PNG/WebP/JPG only — no SVG fallback)."""
    for ext in IMAGE_EXTENSIONS:
        url = skill_asset_url(f"{base_dir}/{basename}{ext}", skill_root)
        if url:
            return url
    return ""


def resolve_dish_illustration(recipe: dict[str, Any], skill_root: Path | None = None) -> tuple[str, str]:
    """
    Resolve hero dish illustration.
    Order: `{recipe_id}.png` → `dishes/shared/{菜名}.png` → missing.
    Returns (url, source) where source is 'dish' | 'shared' | 'missing'.
    """
    root = skill_root or Path(__file__).resolve().parents[1]
    recipe_id = (recipe.get("id") or "").strip()
    if recipe_id:
        url = find_illustration_asset(DISH_DIR, recipe_id, root)
        if url:
            return url, "dish"

    from illustration_resolver import dish_share_basename

    share = dish_share_basename(recipe.get("name") or "")
    if share:
        url = find_illustration_asset(DISH_SHARED_DIR, share, root)
        if url:
            return url, "shared"
    return "", "missing"


def resolve_step_illustration(
    step_text: str,
    index: int,
    skill_root: Path | None = None,
    *,
    recipe_id: str | None = None,
    step_index: int | None = None,
) -> tuple[str, str]:
    """
    Resolve narrative step illustration.
    Priority: AI PNG `{recipe_id}-step-{n}` only — no SVG scene fallback.
    Returns (url, scene_id).
    """
    root = skill_root or Path(__file__).resolve().parents[1]
    text = step_text or ""

    if recipe_id and step_index:
        key = f"{recipe_id}-step-{step_index}"
        url = find_illustration_asset(STEP_DIR, key, root)
        if url:
            return url, key

    # 无 PNG 时返回空，由前端显示「待出图」
    for pattern, scene_id in STEP_ILLUSTRATION_RULES:
        if re.search(pattern, text):
            return "", scene_id
    scene_id = STEP_ILLUSTRATION_FALLBACK[index % len(STEP_ILLUSTRATION_FALLBACK)]
    return "", scene_id


def resolve_ingredient_illustration(name: str, art_key: str, skill_root: Path | None = None) -> str:
    """Raster ingredient art only — no line-art SVG fallback."""
    root = skill_root or Path(__file__).resolve().parents[1]
    if art_key:
        url = find_illustration_asset(ING_DIR, art_key, root)
        if url:
            return url
    return ""
